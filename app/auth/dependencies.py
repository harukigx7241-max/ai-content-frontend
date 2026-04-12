"""
app/auth/dependencies.py — FastAPI 依存性注入 (認証 DI)

【Phase 2 更新】
  ロール定義を app.core.roles に集約。
  新しい依存性を追加:
    require_member   : ログイン済みメンバー全員
    require_paid     : 有料会員以上
    require_master   : マスター会員以上
    require_admin    : 管理者以上 (admin + headquarters)
    require_hq       : 管理本部のみ
    role_guard(role) : 任意ロールを指定するファクトリ関数

【依存チェーン】
  require_hq      → require_admin → get_current_user → cookie
  require_master  → get_current_user
  require_paid    → get_current_user
  require_member  → get_current_user

【エラーコード】
  401 : 未ログイン・トークン期限切れ・ユーザー不在
  403 : アカウント未承認 / ロール不足
"""
import logging
from typing import Callable, Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.roles import (
    ADMIN_ROLES,
    HQ_ROLES,
    MASTER_ROLES,
    MEMBER_ROLES,
    PAID_ROLES,
    RoleRank,
    RoleValue,
    get_role_meta,
)
from app.core.security import decode_access_token
from app.db.models.user import User
from app.db.session import get_db

logger = logging.getLogger(__name__)

_COOKIE_NAME = "pguild_token"


# ─────────────────────────────────────────────────────────────────────────────
# 基本認証
# ─────────────────────────────────────────────────────────────────────────────

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    認証必須の依存性。
    - Cookie なし / 期限切れ / 不正 → 401
    - status != approved              → 403
    """
    token = request.cookies.get(_COOKIE_NAME)
    if not token:
        logger.debug(
            "get_current_user: Cookie '%s' not found. path=%s",
            _COOKIE_NAME, request.url.path,
        )
        raise HTTPException(401, "ログインが必要です")

    payload = decode_access_token(token)  # 不正・期限切れは HTTPException(401)
    user_id = int(payload["sub"])

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "ユーザーが見つかりません")
    if user.status != "approved":
        raise HTTPException(403, "アカウントが有効ではありません")

    return user


def get_current_user_soft(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    認証なしでもアクセス可能なルート用。
    未ログイン時は None を返す。ページルーティング等で使用。
    """
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# ロール別依存性
# ─────────────────────────────────────────────────────────────────────────────

def require_member(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    ログイン済みメンバー全員 (ゲスト除く)。
    status=approved であれば全ロールが通過する。
    """
    if current_user.role not in MEMBER_ROLES:
        # ゲスト相当のロールが DB に入っている異常ケース
        raise HTTPException(403, "会員登録が必要です")
    return current_user


def require_paid(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    有料会員以上 (member_paid / member_master / admin / headquarters)。
    無料会員は 403 + アップグレード促進メッセージ。
    """
    if current_user.role not in PAID_ROLES:
        meta = get_role_meta(RoleValue.MEMBER_PAID)
        raise HTTPException(
            403,
            f"有料プランへのアップグレードが必要です。{meta.description}",
        )
    return current_user


def require_master(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    マスター会員以上 (member_master / admin / headquarters)。
    """
    if current_user.role not in MASTER_ROLES:
        meta = get_role_meta(RoleValue.MEMBER_MASTER)
        raise HTTPException(
            403,
            f"マスタープランへのアップグレードが必要です。{meta.description}",
        )
    return current_user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    管理者権限チェック (admin + headquarters)。
    ─ 後方互換: Phase 1 以前と同じシグネチャ。
    """
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(403, "管理者権限が必要です")
    return current_user


def require_hq(
    current_user: User = Depends(require_admin),
) -> User:
    """
    管理本部のみ (headquarters)。
    require_admin を経由するため admin のチェックも自動で通過する。
    """
    if current_user.role not in HQ_ROLES:
        raise HTTPException(403, "管理本部の権限が必要です")
    return current_user


# ─────────────────────────────────────────────────────────────────────────────
# ファクトリ: 任意ロールガード
# ─────────────────────────────────────────────────────────────────────────────

def role_guard(required_role: str) -> Callable:
    """
    任意ロールを指定するガード依存性のファクトリ関数。

    使い方:
        @router.get("/foo")
        async def foo(user = Depends(role_guard(RoleValue.MEMBER_PAID))):
            ...
    """
    def _guard(current_user: User = Depends(get_current_user)) -> User:
        if not RoleRank.gte(current_user.role, required_role):
            meta = get_role_meta(required_role)
            raise HTTPException(
                403,
                f"この機能は {meta.label} 以上のメンバーが利用できます。"
                f"{meta.upgrade_hint}",
            )
        return current_user
    return _guard


# ─────────────────────────────────────────────────────────────────────────────
# ヘルパー: ロールチェック (例外を出さないバリアント)
# ─────────────────────────────────────────────────────────────────────────────

def has_role(user: Optional[User], required_role: str) -> bool:
    """
    Optional[User] に対してロールチェックを行う。
    依存性として使わず、テンプレート / ビジネスロジック内で使う。
    """
    if user is None:
        return RoleRank.gte(RoleValue.GUEST, required_role)
    return RoleRank.gte(user.role, required_role)


def is_admin_user(user: Optional[User]) -> bool:
    """admin または headquarters かどうか確認する。"""
    return user is not None and user.role in ADMIN_ROLES


def is_hq_user(user: Optional[User]) -> bool:
    """headquarters かどうか確認する。"""
    return user is not None and user.role in HQ_ROLES
