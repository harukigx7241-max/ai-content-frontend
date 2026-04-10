"""
app/invite/service.py — 招待コード ビジネスロジック

責務:
  - 招待コードの生成 (管理者 / 一般ユーザー)
  - 招待コードの検証 (登録時)
  - 招待使用の記録 (InviteUse) & 招待元ユーザーへの XP 付与
  - マイページ向けサマリー
  - 管理画面向けコード一覧

設計方針:
  - XP 付与は try_award 経由で安全に行う
  - 段階1 (invite_registered) = 登録時に付与
  - 段階2 (invite_approved)   = 管理者承認時に admin/service.py 経由で付与
  - auto_approve コードの場合: 段階1・段階2 を登録時に両方付与
  - 二重付与防止: approve 時は related_entity_id で事前チェック (admin/service.py 側)

将来拡張:
  TODO: Phase N+ クールダウン制御 (1日N枚まで等)
  TODO: Phase N+ 招待品質スコアの計算
  TODO: Phase N+ 招待ランキング集計
  TODO: Phase N+ キャンペーン別コード管理
"""
import secrets
import string
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.invite import InviteCode, InviteUse
from app.db.models.user import User

# 混同しやすい文字 (0/O, 1/I/L) を除外したコード文字集合
_CODE_CHARS = (
    string.ascii_uppercase.replace("O", "").replace("I", "")
    + string.digits.replace("0", "").replace("1", "")
)


# ── コード生成ユーティリティ ───────────────────────────────────────

def _generate_unique_code(db: Session, length: int = 8) -> str:
    """重複しない招待コードを生成する。最大10回リトライ。"""
    for _ in range(10):
        code = "".join(secrets.choice(_CODE_CHARS) for _ in range(length))
        exists = db.execute(
            select(InviteCode.id).where(InviteCode.code == code).limit(1)
        ).first()
        if not exists:
            return code
    raise RuntimeError("招待コードの生成に失敗しました。再試行してください")


def _is_usable(code: InviteCode) -> bool:
    """コードが使用可能かどうかを DB クエリなしで判定。"""
    if code.status != "active":
        return False
    if code.used_count >= code.max_uses:
        return False
    if code.expires_at and code.expires_at < datetime.now(timezone.utc):
        return False
    return True


# ── 検証 ─────────────────────────────────────────────────────────

def validate_code_or_raise(db: Session, code_str: str) -> InviteCode:
    """
    招待コードを検証し、使用可能なら InviteCode を返す。
    無効・期限切れ・上限超過の場合は HTTPException(400) を投げる。
    """
    code_str = code_str.strip().upper()
    code = db.execute(
        select(InviteCode).where(InviteCode.code == code_str)
    ).scalar_one_or_none()

    if not code:
        raise HTTPException(400, "招待コードが無効または存在しません")
    if not _is_usable(code):
        raise HTTPException(400, "この招待コードは使用できません（期限切れ・上限到達・無効）")
    return code


# ── 使用記録 & XP付与 ─────────────────────────────────────────────

def record_code_use(db: Session, code: InviteCode, invited_user_id: int) -> None:
    """
    招待コード使用を記録する。
    - InviteUse を作成
    - used_count インクリメント (上限到達で expired に遷移)
    - 招待元ユーザーに invite_registered XP を付与 (段階1)
    - auto_approve コードの場合は invite_approved XP も付与 (段階2を登録時に前倒し)
    """
    from app.core.config import settings

    inviter_user_id = code.created_by_user_id

    db.add(InviteUse(
        code_id=code.id,
        invited_user_id=invited_user_id,
        inviter_user_id=inviter_user_id,
    ))

    code.used_count = (code.used_count or 0) + 1
    if code.used_count >= code.max_uses:
        code.status = "expired"
    db.commit()

    # 段階1: 招待登録 XP
    if inviter_user_id and settings.ENABLE_GAMIFICATION:
        from app.gamification import service as _gami
        from app.gamification.constants import XPEvent as _XPE
        _gami.try_award(db, inviter_user_id, _XPE.INVITE_REGISTERED, ref_id=invited_user_id)

    # 段階2 (前倒し): auto_approve コードなら承認 XP も即時付与
    if code.auto_approve and inviter_user_id and settings.ENABLE_GAMIFICATION:
        from app.gamification import service as _gami
        from app.gamification.constants import XPEvent as _XPE
        _gami.try_award(db, inviter_user_id, _XPE.INVITE_APPROVED, ref_id=invited_user_id)


# ── 管理者コード発行 ──────────────────────────────────────────────

def generate_admin_code(db: Session, admin_id: int, data) -> dict:
    """
    管理者が招待コードを発行する。レベル制限なし。
    data は AdminInviteCodeCreateRequest。
    """
    code_str = data.code.strip().upper() if data.code else _generate_unique_code(db)

    # 手動指定の場合は重複チェック
    if data.code:
        exists = db.execute(
            select(InviteCode.id).where(InviteCode.code == code_str).limit(1)
        ).first()
        if exists:
            raise HTTPException(400, f"招待コード '{code_str}' はすでに使用されています")

    code = InviteCode(
        code=code_str,
        created_by_user_id=admin_id,
        created_by_role="admin",
        is_admin_code=True,
        max_uses=data.max_uses,
        auto_approve=data.auto_approve,
        expires_at=data.expires_at,
        label=data.label,
        notes=data.notes,
    )
    db.add(code)
    db.commit()
    db.refresh(code)
    return _to_dict(code)


# ── 一般ユーザーコード発行 ────────────────────────────────────────

def generate_user_code(db: Session, user: User) -> dict:
    """
    一般ユーザーが招待コードを発行する。
    発行可能枠は LEVEL_BENEFITS.invite_codes に基づく。
    TODO: Phase N+ クールダウン (1日の発行上限)
    """
    from app.gamification.xp_service import get_benefits

    benefits  = get_benefits(user.level or 1)
    max_codes = benefits.get("invite_codes", 0)

    if max_codes <= 0:
        raise HTTPException(403, "招待コードを発行するには Lv5 以上が必要です")

    # 現在のアクティブコード数チェック
    active_count: int = db.execute(
        select(func.count()).where(
            InviteCode.created_by_user_id == user.id,
            InviteCode.status == "active",
        )
    ).scalar() or 0

    if active_count >= max_codes:
        raise HTTPException(
            400,
            f"Lv{user.level} では招待コードを最大 {max_codes} 個まで発行できます。"
            "既存のアクティブコードが上限に達しています",
        )

    code = InviteCode(
        code=_generate_unique_code(db),
        created_by_user_id=user.id,
        created_by_role="user",
        is_admin_code=False,
        max_uses=1,           # 一般ユーザーコードは 1回限り
        auto_approve=False,   # 一般ユーザーコードは自動承認不可
    )
    db.add(code)
    db.commit()
    db.refresh(code)
    return _to_dict(code)


# ── 自分のコード一覧 ──────────────────────────────────────────────

def get_my_codes(db: Session, user_id: int) -> list[dict]:
    """自分が発行した招待コード一覧 (発行日時降順)。"""
    codes = db.execute(
        select(InviteCode)
        .where(InviteCode.created_by_user_id == user_id)
        .order_by(InviteCode.created_at.desc())
    ).scalars().all()
    return [_to_dict(c) for c in codes]


# ── マイページ向けサマリー ────────────────────────────────────────

def get_my_summary(db: Session, user: User) -> dict:
    """マイページ向けの招待サマリーを返す。"""
    from app.core.config import settings
    from app.gamification.constants import LEVEL_BENEFITS
    from app.gamification.xp_service import get_benefits

    benefits  = get_benefits(user.level or 1)
    max_codes = benefits.get("invite_codes", 0)

    # 次の招待枠解放レベルを探す
    next_unlock_level: Optional[int] = None
    for lv in sorted(LEVEL_BENEFITS.keys()):
        if LEVEL_BENEFITS[lv].get("invite_codes", 0) > max_codes:
            next_unlock_level = lv
            break

    codes = get_my_codes(db, user.id)
    active_codes_count = sum(1 for c in codes if c["status"] == "active")

    # 招待使用ログから人数を集計
    use_rows = db.execute(
        select(InviteUse).where(InviteUse.inviter_user_id == user.id)
    ).scalars().all()
    total_invited = len(use_rows)

    total_approved = 0
    if use_rows:
        invited_ids = [u.invited_user_id for u in use_rows]
        total_approved = db.execute(
            select(func.count()).where(
                User.id.in_(invited_ids),
                User.status == "approved",
            )
        ).scalar() or 0

    # 招待 XP 合計
    xp_earned = 0
    if settings.ENABLE_GAMIFICATION:
        from app.db.models.xp_event import XpEvent
        from app.gamification.constants import XPEvent as _XPE
        xp_earned = db.execute(
            select(func.sum(XpEvent.xp_delta)).where(
                XpEvent.user_id == user.id,
                XpEvent.event_type.in_([_XPE.INVITE_REGISTERED, _XPE.INVITE_APPROVED]),
            )
        ).scalar() or 0

    return {
        "can_issue":              max_codes > 0,
        "max_codes":              max_codes,
        "active_codes_count":     active_codes_count,
        "next_unlock_level":      next_unlock_level,
        "total_invited":          total_invited,
        "total_approved":         total_approved,
        "xp_earned_from_invites": xp_earned,
        "codes":                  codes,
    }


# ── 管理画面向け ──────────────────────────────────────────────────

def get_all_codes_admin(db: Session) -> list[dict]:
    """
    全招待コード一覧 (管理者向け)。
    発行者の display_name を LEFT JOIN で取得する。
    """
    rows = db.execute(
        select(InviteCode, User.display_name)
        .outerjoin(User, InviteCode.created_by_user_id == User.id)
        .order_by(InviteCode.created_at.desc())
    ).all()
    return [_to_admin_dict(code, creator_name) for code, creator_name in rows]


def deactivate_code(db: Session, code_id: int) -> dict:
    """招待コードを手動無効化する (管理者用)。"""
    code = db.get(InviteCode, code_id)
    if not code:
        raise HTTPException(404, "招待コードが見つかりません")
    if code.status == "inactive":
        raise HTTPException(400, "すでに無効化されています")
    code.status = "inactive"
    db.commit()
    db.refresh(code)
    return _to_dict(code)


# ── 内部ヘルパー ──────────────────────────────────────────────────

def _to_dict(code: InviteCode) -> dict:
    return {
        "id":                  code.id,
        "code":                code.code,
        "created_by_user_id":  code.created_by_user_id,
        "created_by_role":     code.created_by_role,
        "is_admin_code":       code.is_admin_code,
        "max_uses":            code.max_uses,
        "used_count":          code.used_count,
        "auto_approve":        code.auto_approve,
        "status":              code.status,
        "expires_at":          code.expires_at,
        "label":               code.label,
        "notes":               code.notes,
        "created_at":          code.created_at,
    }


def _to_admin_dict(code: InviteCode, creator_name: Optional[str]) -> dict:
    d = _to_dict(code)
    d["created_by_display_name"] = creator_name
    return d
