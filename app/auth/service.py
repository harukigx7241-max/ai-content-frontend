"""
app/auth/service.py — 認証ビジネスロジック

責務:
  - ユーザー登録 / ログイン / パスワード変更
  - DB 操作を含む。router からは本 service の関数だけを呼ぶ。
  - パスワードハッシュ / JWT 生成は core/security.py に委譲。
"""
import logging
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.core.security import hash_password, timing_safe_verify, create_access_token
from app.db.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, ChangePasswordRequest

# ステータス別のエラーメッセージ
_STATUS_MESSAGES: dict[str, str] = {
    "pending": "アカウントは現在承認待ちです。管理者の承認をお待ちください",
    "rejected": "このアカウントの登録は承認されませんでした。詳細はお問い合わせください",
    "suspended": "このアカウントは停止されています。詳細はお問い合わせください",
}


def register_user(db: Session, data: RegisterRequest) -> User:
    """
    新規ユーザーを登録する。
    - sns_platform + sns_handle 重複は 400 エラー。
    - ADMIN_SNS_PLATFORM + ADMIN_SNS_HANDLE に一致する場合は role=admin, status=approved で登録。
    - invite_code が指定された場合: 検証し auto_approve フラグを反映。
    """
    exists = db.query(User).filter(
        User.sns_platform == data.sns_platform,
        User.sns_handle == data.sns_handle,
    ).first()
    if exists:
        raise HTTPException(400, "このSNSアカウントはすでに登録されています")

    # 管理者の自動設定 (環境変数で指定された最初の管理者)
    is_admin = bool(
        settings.ADMIN_SNS_PLATFORM
        and settings.ADMIN_SNS_HANDLE
        and data.sns_platform == settings.ADMIN_SNS_PLATFORM
        and data.sns_handle.lower() == settings.ADMIN_SNS_HANDLE.lower()
    )

    # Phase 8: 招待コードの検証 (任意)
    invite_code_obj = None
    if data.invite_code:
        from app.invite import service as _invite_svc
        invite_code_obj = _invite_svc.validate_code_or_raise(db, data.invite_code)

    auto_approve_via_invite = (invite_code_obj is not None and invite_code_obj.auto_approve)
    now = datetime.now(timezone.utc)

    user = User(
        sns_platform=data.sns_platform,
        sns_handle=data.sns_handle,
        display_name=data.display_name,
        profile_url=data.profile_url,
        password_hash=hash_password(data.password),
        status="approved" if (is_admin or auto_approve_via_invite) else "pending",
        role="admin" if is_admin else "user",
        invited_by_user_id=invite_code_obj.created_by_user_id if invite_code_obj else None,
        approved_at=now if (is_admin or auto_approve_via_invite) else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 招待コードの使用記録 & XP付与 (失敗しても登録自体は成功扱い)
    if invite_code_obj:
        try:
            from app.invite import service as _invite_svc
            _invite_svc.record_code_use(db, invite_code_obj, user.id)
        except Exception as e:
            logger.warning("招待記録失敗 (user_id=%s): %s", user.id, e)

    return user


def login_user(db: Session, data: LoginRequest) -> tuple[User, str]:
    """
    ログイン処理。
    - ユーザー不在・パスワード不一致は同一エラー文言 (ユーザー存在漏洩防止)。
    - status != approved は 403 + ステータス別メッセージ。
    - 成功時は last_login_at を更新して (user, JWT) を返す。
    """
    user = db.query(User).filter(
        User.sns_platform == data.sns_platform,
        User.sns_handle == data.sns_handle,
    ).first()

    # timing_safe_verify: user が None でもダミーハッシュで検証し処理時間を均等化
    if not timing_safe_verify(data.password, user.password_hash if user else None):
        raise HTTPException(401, "SNSアカウントまたはパスワードが正しくありません")

    if user.status != "approved":
        msg = _STATUS_MESSAGES.get(user.status, "ログインできません")
        raise HTTPException(403, msg)

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(user.id, user.role)
    return user, token


def change_password(db: Session, user: User, data: ChangePasswordRequest) -> None:
    """パスワード変更。現在のパスワード照合必須。"""
    if not timing_safe_verify(data.current_password, user.password_hash):
        raise HTTPException(400, "現在のパスワードが正しくありません")
    if data.new_password != data.new_password_confirm:
        raise HTTPException(400, "新しいパスワードが一致しません")

    user.password_hash = hash_password(data.new_password)
    # bootstrap で設定された初回変更フラグをクリアする
    if getattr(user, "must_change_password", False):
        user.must_change_password = False
    db.commit()

    # TODO: Phase 3+ ここでセッションを無効化する (全デバイスログアウト)
