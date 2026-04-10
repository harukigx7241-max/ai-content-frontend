"""
app/core/config.py
共通設定クラス。環境変数で上書き可能。
TODO: Phase 1+ で pydantic-settings に移行してもよい。
"""
import os
import secrets  # noqa: F401 (used for future token generation helpers)


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
    # Phase 3 - 管理ダッシュボード
    ENABLE_ADMIN_DASHBOARD: bool = os.getenv("ENABLE_ADMIN_DASHBOARD", "true").lower() == "true"
    # Phase 5 - コミュニティ（公開広場）ENABLE_COMMUNITY=false で無効化可能
    ENABLE_COMMUNITY: bool = os.getenv("ENABLE_COMMUNITY", "true").lower() == "true"
    # Phase 7 - ゲーミフィケーション（XP/バッジ）ENABLE_GAMIFICATION=false で無効化可能
    ENABLE_GAMIFICATION: bool = os.getenv("ENABLE_GAMIFICATION", "true").lower() == "true"
    # TODO: Phase 5 - 招待コードシステム
    ENABLE_INVITE_SYSTEM: bool = False

    # ── CORS ────────────────────────────────────────────────────────────
    # BACKEND_CORS_ORIGINS: カンマ区切りで許可オリジンを列挙する
    # 例: BACKEND_CORS_ORIGINS=https://example.com,https://app.example.com
    # 未設定の場合は ["*"] (開発用デフォルト)。本番では必ず明示すること。
    _cors_raw: str = os.getenv("BACKEND_CORS_ORIGINS", "")
    BACKEND_CORS_ORIGINS: list = (
        [o.strip() for o in _cors_raw.split(",") if o.strip()]
        if _cors_raw.strip()
        else ["*"]
    )

    # ── Phase 2: 認証システム設定 ────────────────────────────────────────
    # ENABLE_AUTH_SYSTEM は以下で上書き (上の False 定義を env-driven に変更)
    ENABLE_AUTH_SYSTEM: bool = os.getenv("ENABLE_AUTH_SYSTEM", "true").lower() == "true"  # type: ignore[assignment]

    DB_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/pguild.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "pguild-dev-secret-CHANGE-IN-PRODUCTION")
    JWT_EXPIRE_DAYS: int = int(os.getenv("JWT_EXPIRE_DAYS", "7"))
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"

    # 管理者の自動昇格: 登録時に一致したユーザーを role=admin, status=approved にする
    ADMIN_SNS_PLATFORM: str = os.getenv("ADMIN_SNS_PLATFORM", "")
    ADMIN_SNS_HANDLE: str = os.getenv("ADMIN_SNS_HANDLE", "")


# グローバルシングルトン
settings = Settings()
