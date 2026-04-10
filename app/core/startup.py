"""
app/core/startup.py — 認証システム有効時の起動時 DB 初期化

main.py からは bootstrap_db() を呼ぶだけでよい。

責務:
  1. data ディレクトリ作成 (SQLite ファイル置き場)
  2. 全モデルを Base.metadata に登録して create_all
  3. 起動時簡易カラムマイグレーション
  4. runtime_config を DB から読み込む

将来の拡張ポイント:
  - seed データ投入が必要になった場合はここに seed_initial_data() を追加する
  - Alembic 移行後は step 3 を "alembic upgrade head" に差し替えるだけでよい
  - 読み取り専用レプリカが追加された場合はここで接続先を切り替える
"""
import logging
import os

logger = logging.getLogger(__name__)


def bootstrap_db() -> None:
    """
    ENABLE_AUTH_SYSTEM=true の場合に起動時に一度だけ呼ぶ。
    べき等設計: 何度呼んでも安全。
    """
    # 1. data ディレクトリ (SQLite ファイル保存先)
    os.makedirs("data", exist_ok=True)
    logger.info("startup: data directory ready")

    # 2. モデルを Base.metadata に登録してからテーブル作成
    #    app.db.models の import 副作用でモデルクラスが Base に登録される
    from app.db.base import Base
    from app.db.session import engine
    import app.db.models as _models  # noqa: F401 — モデルを Base.metadata に登録

    Base.metadata.create_all(bind=engine)
    logger.info("startup: tables created (create_all)")

    # 3. 旧 DB への後付けカラムマイグレーション
    from app.db.migrations import run_migrations
    run_migrations(engine)

    # 4. runtime_config を DB から読み込む (メンテナンスモード・告知バーなど)
    from app.core import runtime_config
    from app.db.session import SessionLocal
    with SessionLocal() as db:
        runtime_config.load_from_db(db)
    logger.info("startup: runtime_config loaded from db")

    # 5. 初回管理者ブートストラップ (ADMIN_BOOTSTRAP_ENABLED=true の場合のみ)
    #    管理者が1人も存在しない場合に環境変数の認証情報で admin アカウントを1件作成する。
    #    べき等設計: 既存 admin がいれば何もしない。
    from app.core.config import settings
    if settings.ADMIN_BOOTSTRAP_ENABLED:
        from app.core.admin_bootstrap import bootstrap_admin
        with SessionLocal() as db:
            bootstrap_admin(db)
    else:
        logger.debug("startup: admin bootstrap disabled (ADMIN_BOOTSTRAP_ENABLED=false)")
