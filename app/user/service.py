"""
app/user/service.py — 一般ユーザーの自己操作サービス

責務:
  - プロフィール更新 (display_name / profile_url)
  - 利用状況サマリー取得 (DB で取れる範囲)

認証 (login/register/password) は app/auth/service.py に残す。
将来の拡張ポイント:
  TODO: Phase N+ sns_handle 変更フロー (重複チェック + セッション再発行)
  TODO: Phase N+ 通知設定の更新
  TODO: Phase N+ アカウント削除リクエスト
"""
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.schemas.user import ProfileUpdateRequest


def update_profile(db: Session, user: User, data: ProfileUpdateRequest) -> User:
    """
    プロフィールを更新する。None フィールドはスキップ (PATCH セマンティクス)。
    profile_url / bio に空文字 "" を渡すと削除する。
    """
    if data.display_name is not None:
        user.display_name = data.display_name

    if data.profile_url is not None:
        # 空文字は None に変換して URL を削除
        user.profile_url = data.profile_url.strip() or None

    if data.bio is not None:
        # 空文字は None に変換して bio を削除
        user.bio = data.bio.strip() or None

    db.commit()
    db.refresh(user)
    return user


def get_stats(user: User) -> dict:
    """
    ユーザーの利用状況サマリーを返す。
    現時点では DB で取得可能な値のみ。
    生成回数・お気に入り数はフロントの localStorage から補完する。
    """
    return {
        "user_id": user.id,
        "created_at": user.created_at,
        "last_login_at": user.last_login_at,
    }
