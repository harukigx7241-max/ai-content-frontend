"""
app/auth/service.py — 認証ビジネスロジック

責務:
  - ユーザー登録 / ログイン / パスワード変更
  - DB 操作を含む。router からは本 service の関数だけを呼ぶ。
  - パスワードハッシュ / JWT 生成は core/security.py に委譲。
"""
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

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

    user = User(
        sns_platform=data.sns_platform,
        sns_handle=data.sns_handle,
        display_name=data.display_name,
        profile_url=data.profile_url,
        password_hash=hash_password(data.password),
        status="approved" if is_admin else "pending",
        role="admin" if is_admin else "user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
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
    db.commit()

    # TODO: Phase 3+ ここでセッションを無効化する (全デバイスログアウト)
