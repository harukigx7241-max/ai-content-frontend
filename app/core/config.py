"""
app/core/config.py
共通設定クラス。環境変数で上書き可能。

【Phase 1 追加】
- LLM API キー設定 (OPENAI / ANTHROPIC / GEMINI)
- 全サービスの ENABLE_* フラグ (APIキー未設定でも例外で落ちない)
- API 予算・使用量制御設定
"""
import os
import secrets  # noqa: F401 (used for future token generation helpers)


def _bool(key: str, default: str = "false") -> bool:
    return os.getenv(key, default).lower() == "true"


class Settings:
    # ── アプリ基本情報 ──────────────────────────────────────────────
    APP_NAME: str = os.getenv("APP_NAME", "プロンプトギルド")
    APP_VERSION: str = "2.0.0"

    # ── メンテナンスモード ──────────────────────────────────────────
    ENABLE_MAINTENANCE_MODE: bool = _bool("ENABLE_MAINTENANCE_MODE")
    MAINTENANCE_MESSAGE: str = os.getenv(
        "MAINTENANCE_MESSAGE",
        "現在メンテナンス中です。しばらくお待ちください。",
    )

    # ── 告知バー ────────────────────────────────────────────────────
    ENABLE_NOTICE_BANNER: bool = _bool("ENABLE_NOTICE_BANNER")
    NOTICE_BANNER_TEXT: str = os.getenv("NOTICE_BANNER_TEXT", "")
    NOTICE_BANNER_LINK: str = os.getenv("NOTICE_BANNER_LINK", "")

    # ── Phase 1 機能フラグ (後方互換用キルスイッチ) ─────────────────
    ENABLE_PHASE1_FEATURES: bool = _bool("ENABLE_PHASE1_FEATURES", "true")

    # ── 既存機能フラグ ──────────────────────────────────────────────
    ENABLE_ADMIN_DASHBOARD: bool = _bool("ENABLE_ADMIN_DASHBOARD", "true")
    ENABLE_COMMUNITY: bool       = _bool("ENABLE_COMMUNITY", "true")
    ENABLE_GAMIFICATION: bool    = _bool("ENABLE_GAMIFICATION", "true")
    ENABLE_INVITE_SYSTEM: bool   = False  # 将来 env-driven に変更予定

    # ── CORS ────────────────────────────────────────────────────────
    _cors_raw: str = os.getenv("BACKEND_CORS_ORIGINS", "")
    BACKEND_CORS_ORIGINS: list[str] = (
        [o.strip() for o in _cors_raw.split(",") if o.strip()]
        if _cors_raw.strip()
        else ["*"]
    )

    # ── 認証設定 ────────────────────────────────────────────────────
    ENABLE_AUTH_SYSTEM: bool = _bool("ENABLE_AUTH_SYSTEM", "true")
    DB_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/pguild.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "pguild-dev-secret-CHANGE-IN-PRODUCTION")
    JWT_EXPIRE_DAYS: int = int(os.getenv("JWT_EXPIRE_DAYS", "7"))
    COOKIE_SECURE: bool = _bool("COOKIE_SECURE")

    ADMIN_SNS_PLATFORM: str = os.getenv("ADMIN_SNS_PLATFORM", "")
    ADMIN_SNS_HANDLE: str   = os.getenv("ADMIN_SNS_HANDLE", "")

    # 初回管理者ブートストラップ
    ADMIN_BOOTSTRAP_ENABLED: bool     = _bool("ADMIN_BOOTSTRAP_ENABLED")
    ADMIN_BOOTSTRAP_PLATFORM: str     = os.getenv("ADMIN_BOOTSTRAP_PLATFORM", "X")
    ADMIN_BOOTSTRAP_HANDLE: str       = os.getenv("ADMIN_BOOTSTRAP_HANDLE", "admin")
    ADMIN_BOOTSTRAP_DISPLAY_NAME: str = os.getenv("ADMIN_BOOTSTRAP_DISPLAY_NAME", "管理者")
    ADMIN_BOOTSTRAP_PASSWORD: str     = os.getenv("ADMIN_BOOTSTRAP_PASSWORD", "")

    # ────────────────────────────────────────────────────────────────
    # Phase 1: LLM API キー設定
    # 未設定でも例外で落ちない。API 機能は FREE tier に自動降格。
    # ────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str  = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str    = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str   = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str   = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # 優先プロバイダー: auto = 設定済みのものを自動選択
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")

    # ────────────────────────────────────────────────────────────────
    # Phase 1: サービス別 ENABLE フラグ
    #
    # デフォルト true の機能: APIキー未設定なら FREE tier で動作
    # デフォルト false の機能: APIキー必須 or 未完成
    # ────────────────────────────────────────────────────────────────

    # プロンプト生成コア (既存 generate_service ラッパー)
    ENABLE_PROMPT_FORGE: bool = _bool("ENABLE_PROMPT_FORGE", "true")

    # プロンプト診断 (FREE=ルールベース / API=LLM診断)
    ENABLE_PROMPT_DOCTOR: bool = _bool("ENABLE_PROMPT_DOCTOR", "true")

    # ギルドガイド AI (FREE=スクリプトヒント / API=LLM文脈対応)
    ENABLE_GUILD_GUIDE_AI: bool = _bool("ENABLE_GUILD_GUIDE_AI", "true")

    # ワークショップマスター AI (API専用・未完成のためデフォルト false)
    ENABLE_WORKSHOP_MASTER_AI: bool = _bool("ENABLE_WORKSHOP_MASTER_AI", "false")

    # トレンドリフレッシュ (FREE=ファイルベース / 将来 web scraping)
    ENABLE_TREND_REFRESH: bool = _bool("ENABLE_TREND_REFRESH", "true")

    # 日本語品質チェック (FREE=ルールベース / API=LLM添削)
    ENABLE_LANGUAGE_QUALITY_AI: bool = _bool("ENABLE_LANGUAGE_QUALITY_AI", "true")

    # キャンペーン工房 (FREE=テンプレ / API=LLM生成)
    ENABLE_CAMPAIGN_FORGE: bool = _bool("ENABLE_CAMPAIGN_FORGE", "true")

    # 記事下書き自動生成 (API専用・未完成のためデフォルト false)
    ENABLE_ARTICLE_DRAFT_AI: bool = _bool("ENABLE_ARTICLE_DRAFT_AI", "false")

    # 画像生成 (FREE=プロンプト生成のみ / API=実際に画像生成)
    ENABLE_IMAGE_GENERATION: bool = _bool("ENABLE_IMAGE_GENERATION", "true")
    ENABLE_IMAGE_API_CALL: bool   = _bool("ENABLE_IMAGE_API_CALL", "false")
    IMAGE_API_PROVIDER: str       = os.getenv("IMAGE_API_PROVIDER", "dalle")  # dalle | sd | none

    # API 利用量・コスト可視化ダッシュボード
    ENABLE_API_USAGE_DASHBOARD: bool = _bool("ENABLE_API_USAGE_DASHBOARD", "true")

    # 混雑状況表示 (FREE=静的ステータス / API=リアルタイム)
    ENABLE_CONGESTION_DISPLAY: bool = _bool("ENABLE_CONGESTION_DISPLAY", "true")

    # プロモーションプランナー (FREE=テンプレ / API=LLM生成)
    ENABLE_PROMOTION_PLANNER: bool = _bool("ENABLE_PROMOTION_PLANNER", "true")

    # ギルド書記AI — 広場投稿文・キャプション生成 (FREE=テンプレ / API=LLM生成)
    ENABLE_GUILD_SCRIBE_AI: bool = _bool("ENABLE_GUILD_SCRIBE_AI", "true")

    # ────────────────────────────────────────────────────────────────
    # Phase 1: API 予算・制限設定
    # ────────────────────────────────────────────────────────────────

    # 月次トークン上限 (0 = 無制限)
    API_MONTHLY_TOKEN_LIMIT: int = int(os.getenv("API_MONTHLY_TOKEN_LIMIT", "0"))

    # 月次概算コスト上限 (USD, 0 = 無制限)
    API_MONTHLY_COST_LIMIT_USD: float = float(os.getenv("API_MONTHLY_COST_LIMIT_USD", "0"))

    # 日次トークン上限 (0 = 無制限)
    API_DAILY_TOKEN_LIMIT: int = int(os.getenv("API_DAILY_TOKEN_LIMIT", "0"))

    # 日次概算コスト上限 (USD, 0 = 無制限)
    API_DAILY_COST_LIMIT_USD: float = float(os.getenv("API_DAILY_COST_LIMIT_USD", "0"))

    # 警告しきい値 (上限の何%で警告を出すか)
    API_WARN_THRESHOLD_PCT: int = int(os.getenv("API_WARN_THRESHOLD_PCT", "80"))

    # 上限超過時の動作: "disable" | "fallback" | "notify_only"
    API_OVER_LIMIT_ACTION: str = os.getenv("API_OVER_LIMIT_ACTION", "fallback")

    # 管理者通知メール (上限超過時、空白は通知なし)
    ADMIN_ALERT_EMAIL: str = os.getenv("ADMIN_ALERT_EMAIL", "")

    # ────────────────────────────────────────────────────────────────
    # Phase 13: API 制御
    # ────────────────────────────────────────────────────────────────

    # 高コストサービス一覧 (カンマ区切り)
    API_HIGH_COST_SERVICES: str = os.getenv(
        "API_HIGH_COST_SERVICES",
        "workshop_master_ai,article_draft_ai,image_generation",
    )

    # ロール別 API 制限
    # 無料会員の API 呼び出し許可: true = 許可 / false = FREE tier のみ
    API_ALLOW_FREE_MEMBER: bool = _bool("API_ALLOW_FREE_MEMBER", "true")
    # 有料会員の API 呼び出し許可
    API_ALLOW_PAID_MEMBER: bool = _bool("API_ALLOW_PAID_MEMBER", "true")

    # ── Phase 17: 管理者専用集客工房 ───────────────────────────────
    ENABLE_ADMIN_GROWTH_MULTI_CHANNEL: bool = _bool("ENABLE_ADMIN_GROWTH_MULTI_CHANNEL", "true")
    ENABLE_ADMIN_GROWTH_LAUNCH_PACK: bool   = _bool("ENABLE_ADMIN_GROWTH_LAUNCH_PACK", "true")
    ENABLE_ADMIN_GROWTH_PROMO_CALENDAR: bool = _bool("ENABLE_ADMIN_GROWTH_PROMO_CALENDAR", "true")
    ENABLE_ADMIN_GROWTH_HOOK_LIBRARY: bool  = _bool("ENABLE_ADMIN_GROWTH_HOOK_LIBRARY", "true")
    ENABLE_ADMIN_GROWTH_VARIATION: bool     = _bool("ENABLE_ADMIN_GROWTH_VARIATION", "true")
    ENABLE_ADMIN_GROWTH_PROMO_SCORE: bool   = _bool("ENABLE_ADMIN_GROWTH_PROMO_SCORE", "true")

    # ── Phase 16: サブスクリプション / 課金 ────────────────────────
    # Stripe シークレットキー (未設定 = 課金機能無効・スタブモード)
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    # Stripe 公開キー (フロントエンドへ渡す)
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    # Stripe Webhook シークレット
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    # 有料プラン価格 ID (Stripe Product Price ID)
    STRIPE_PRICE_PAID_MONTHLY: str = os.getenv("STRIPE_PRICE_PAID_MONTHLY", "")
    STRIPE_PRICE_PAID_YEARLY: str = os.getenv("STRIPE_PRICE_PAID_YEARLY", "")
    STRIPE_PRICE_MASTER_MONTHLY: str = os.getenv("STRIPE_PRICE_MASTER_MONTHLY", "")
    STRIPE_PRICE_MASTER_YEARLY: str = os.getenv("STRIPE_PRICE_MASTER_YEARLY", "")
    # 課金機能の有効/無効 (Stripe キー未設定時は自動で false)
    ENABLE_BILLING: bool = _bool("ENABLE_BILLING", "false")
    # トライアル日数 (0 = トライアルなし)
    BILLING_TRIAL_DAYS: int = int(os.getenv("BILLING_TRIAL_DAYS", "0"))


# グローバルシングルトン
settings = Settings()
