"""
app/core/config.py
共通設定クラス。環境変数で上書き可能。
TODO: Phase 1+ で pydantic-settings に移行してもよい。
"""
import os


class Settings:
    # ── アプリ基本情報 ──────────────────────────────────────────────
    APP_NAME: str = os.getenv("APP_NAME", "副業AIプロンプトプロ")
    APP_VERSION: str = "2.0.0"

    # ── メンテナンスモード ──────────────────────────────────────────
    # 環境変数 ENABLE_MAINTENANCE_MODE=true でオン
    ENABLE_MAINTENANCE_MODE: bool = os.getenv("ENABLE_MAINTENANCE_MODE", "false").lower() == "true"
    MAINTENANCE_MESSAGE: str = os.getenv(
        "MAINTENANCE_MESSAGE",
        "現在メンテナンス中です。しばらくお待ちください。",
    )

    # ── 告知バー ────────────────────────────────────────────────────
    # 環境変数 ENABLE_NOTICE_BANNER=true でオン
    ENABLE_NOTICE_BANNER: bool = os.getenv("ENABLE_NOTICE_BANNER", "false").lower() == "true"
    NOTICE_BANNER_TEXT: str = os.getenv("NOTICE_BANNER_TEXT", "")
    NOTICE_BANNER_LINK: str = os.getenv("NOTICE_BANNER_LINK", "")

    # ── Phase 1 機能フラグ ───────────────────────────────────────────
    # Phase 1 の強化機能を一括で無効化できるキルスイッチ
    ENABLE_PHASE1_FEATURES: bool = os.getenv("ENABLE_PHASE1_FEATURES", "true").lower() == "true"

    # ── 将来機能フラグ（全て無効）──────────────────────────────────
    # TODO: Phase 1 - 認証システム
    ENABLE_AUTH_SYSTEM: bool = False
    # TODO: Phase 2 - 管理画面
    ENABLE_ADMIN_DASHBOARD: bool = False
    # TODO: Phase 3 - コミュニティ（公開広場）
    ENABLE_COMMUNITY: bool = False
    # TODO: Phase 4 - ゲーミフィケーション（XP/バッジ）
    ENABLE_GAMIFICATION: bool = False
    # TODO: Phase 5 - 招待コードシステム
    ENABLE_INVITE_SYSTEM: bool = False


# グローバルシングルトン
settings = Settings()
