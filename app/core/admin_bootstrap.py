"""
app/core/admin_bootstrap.py — 初回管理者ブートストラップ

起動時に管理者ユーザーが1人も存在しない場合、環境変数から読み込んだ認証情報で
管理者アカウントを1件だけ作成する。既存の管理者がいれば何もしない（べき等）。

使い方 (.env に設定):
  ADMIN_BOOTSTRAP_ENABLED=true
  ADMIN_BOOTSTRAP_PLATFORM=X
  ADMIN_BOOTSTRAP_HANDLE=admin
  ADMIN_BOOTSTRAP_DISPLAY_NAME=管理者
  ADMIN_BOOTSTRAP_PASSWORD=admin123   ← 初回ログイン後に必ず変更すること！

初回ログイン後にすべきこと:
  1. マイページ → 設定 → パスワード変更 でパスワードを変更する
  2. .env の ADMIN_BOOTSTRAP_ENABLED を false に変更する (または削除する)
  3. サービスを再起動してブートストラップが無効になったことを確認する

設計方針:
  - ADMIN_BOOTSTRAP_PASSWORD が空の場合は作成を拒否してログ警告を出す
  - 既存管理者が1件でもいれば何もしない (既存DBを壊さない)
  - パスワードは bcrypt でハッシュ化して保存 (平文で DB に保存しない)
  - 作成時に must_change_password=True を設定し、ログイン後の変更を促す

TODO: must_change_password フラグを活用した「強制パスワード変更画面」は Phase N+ で実装予定
"""
import logging

from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger(__name__)


def bootstrap_admin(db: Session) -> None:
    """
    管理者ユーザーが存在しなければ環境変数の認証情報で作成する。

    呼び出し元: app/core/startup.py の bootstrap_db()
    条件: settings.ADMIN_BOOTSTRAP_ENABLED=True かつ ADMIN_BOOTSTRAP_PASSWORD が非空
    べき等: 既存 admin がいれば何もしない
    """
    # パスワード未設定はスキップ (環境変数のセットし忘れを防ぐ)
    if not settings.ADMIN_BOOTSTRAP_PASSWORD:
        logger.warning(
            "bootstrap_admin: ADMIN_BOOTSTRAP_PASSWORD が未設定です。"
            "管理者アカウントの作成をスキップします。"
        )
        return

    # 既存管理者チェック (べき等保証)
    from app.db.models.user import User
    existing_admin = db.query(User).filter(User.role == "admin").first()
    if existing_admin:
        logger.info(
            "bootstrap_admin: 管理者ユーザーが既に存在します (id=%s, %s:%s)。スキップします。",
            existing_admin.id,
            existing_admin.sns_platform,
            existing_admin.sns_handle,
        )
        return

    # 管理者アカウントを作成
    from app.core.security import hash_password
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    admin = User(
        sns_platform=settings.ADMIN_BOOTSTRAP_PLATFORM,
        sns_handle=settings.ADMIN_BOOTSTRAP_HANDLE,
        display_name=settings.ADMIN_BOOTSTRAP_DISPLAY_NAME,
        password_hash=hash_password(settings.ADMIN_BOOTSTRAP_PASSWORD),
        role="admin",
        status="approved",
        approved_at=now,
        must_change_password=True,  # 初回ログイン後のパスワード変更を促す
    )
    db.add(admin)
    db.commit()

    logger.warning(
        "bootstrap_admin: 管理者アカウントを作成しました。"
        " platform=%s, handle=%s, display_name=%s"
        " ★ 初回ログイン後に必ずパスワードを変更し、"
        " ADMIN_BOOTSTRAP_ENABLED=false に設定してください ★",
        settings.ADMIN_BOOTSTRAP_PLATFORM,
        settings.ADMIN_BOOTSTRAP_HANDLE,
        settings.ADMIN_BOOTSTRAP_DISPLAY_NAME,
    )
