"""
app/core/feature_flags.py
機能フラグの一元管理。settings から読み込む。
フロントエンドへは /api/system/config 経由で公開される。

【Phase 1 追加】
- 全サービスの ENABLE_* フラグ追加
- is_enabled(flag_name) ヘルパー
- has_api_key() / preferred_api() ヘルパー
"""
from __future__ import annotations

from app.core.config import settings


class FeatureFlags:
    # ── インフラ系 ─────────────────────────────────────────────────
    MAINTENANCE_MODE: bool = settings.ENABLE_MAINTENANCE_MODE
    NOTICE_BANNER: bool    = settings.ENABLE_NOTICE_BANNER

    # ── システム機能 ────────────────────────────────────────────────
    PHASE1_FEATURES: bool  = settings.ENABLE_PHASE1_FEATURES
    AUTH_SYSTEM: bool      = settings.ENABLE_AUTH_SYSTEM
    ADMIN_DASHBOARD: bool  = settings.ENABLE_ADMIN_DASHBOARD
    COMMUNITY: bool        = settings.ENABLE_COMMUNITY
    GAMIFICATION: bool     = settings.ENABLE_GAMIFICATION
    INVITE_SYSTEM: bool    = settings.ENABLE_INVITE_SYSTEM

    # ── Phase 1: サービス別フラグ ──────────────────────────────────
    PROMPT_FORGE: bool        = settings.ENABLE_PROMPT_FORGE
    PROMPT_DOCTOR: bool       = settings.ENABLE_PROMPT_DOCTOR
    GUILD_GUIDE_AI: bool      = settings.ENABLE_GUILD_GUIDE_AI
    WORKSHOP_MASTER_AI: bool  = settings.ENABLE_WORKSHOP_MASTER_AI
    TREND_REFRESH: bool       = settings.ENABLE_TREND_REFRESH
    LANGUAGE_QUALITY_AI: bool = settings.ENABLE_LANGUAGE_QUALITY_AI
    CAMPAIGN_FORGE: bool      = settings.ENABLE_CAMPAIGN_FORGE
    ARTICLE_DRAFT_AI: bool    = settings.ENABLE_ARTICLE_DRAFT_AI
    IMAGE_GENERATION: bool    = settings.ENABLE_IMAGE_GENERATION
    IMAGE_API_CALL: bool      = settings.ENABLE_IMAGE_API_CALL
    API_USAGE_DASHBOARD: bool = settings.ENABLE_API_USAGE_DASHBOARD
    CONGESTION_DISPLAY: bool  = settings.ENABLE_CONGESTION_DISPLAY
    PROMOTION_PLANNER: bool   = settings.ENABLE_PROMOTION_PLANNER
    GUILD_SCRIBE_AI: bool     = settings.ENABLE_GUILD_SCRIBE_AI

    # ── ヘルパーメソッド ────────────────────────────────────────────

    def is_enabled(self, flag_name: str) -> bool:
        """
        フラグ名 (文字列) でフラグの ON/OFF を確認する。
        例: flags.is_enabled("PROMPT_DOCTOR")
        存在しないフラグ名は True を返す (安全側・フォールバック許可)。
        """
        return bool(getattr(self, flag_name, True))

    def has_api_key(self) -> bool:
        """少なくとも1つの LLM API キーが設定されているか確認する。"""
        return bool(
            settings.OPENAI_API_KEY
            or settings.ANTHROPIC_API_KEY
            or settings.GEMINI_API_KEY
        )

    def preferred_api(self) -> str:
        """
        優先 API プロバイダー名を返す。
        LLM_PROVIDER=auto の場合は設定済みキーを優先度順で選択。
        """
        if settings.LLM_PROVIDER != "auto":
            return settings.LLM_PROVIDER
        if settings.ANTHROPIC_API_KEY:
            return "anthropic"
        if settings.OPENAI_API_KEY:
            return "openai"
        if settings.GEMINI_API_KEY:
            return "gemini"
        return "none"

    def as_dict(self) -> dict:
        """フロントエンド向けに辞書形式で返す。"""
        return {
            "maintenance": self.MAINTENANCE_MODE,
            "notice_banner": {
                "enabled": self.NOTICE_BANNER,
                "text": settings.NOTICE_BANNER_TEXT if self.NOTICE_BANNER else "",
                "link": settings.NOTICE_BANNER_LINK if self.NOTICE_BANNER else "",
            },
            "api": {
                "has_key": self.has_api_key(),
                "provider": self.preferred_api(),
            },
            "features": {
                "phase1": self.PHASE1_FEATURES,
                "auth_system": self.AUTH_SYSTEM,
                "admin_dashboard": self.ADMIN_DASHBOARD,
                "community": self.COMMUNITY,
                "gamification": self.GAMIFICATION,
                "invite_system": self.INVITE_SYSTEM,
                # Phase 1 services
                "prompt_forge": self.PROMPT_FORGE,
                "prompt_doctor": self.PROMPT_DOCTOR,
                "guild_guide_ai": self.GUILD_GUIDE_AI,
                "workshop_master_ai": self.WORKSHOP_MASTER_AI,
                "trend_refresh": self.TREND_REFRESH,
                "language_quality_ai": self.LANGUAGE_QUALITY_AI,
                "campaign_forge": self.CAMPAIGN_FORGE,
                "article_draft_ai": self.ARTICLE_DRAFT_AI,
                "image_generation": self.IMAGE_GENERATION,
                "image_api_call": self.IMAGE_API_CALL,
                "api_usage_dashboard": self.API_USAGE_DASHBOARD,
                "congestion_display": self.CONGESTION_DISPLAY,
                "promotion_planner": self.PROMOTION_PLANNER,
                "guild_scribe_ai": self.GUILD_SCRIBE_AI,
            },
        }


# グローバルシングルトン
flags = FeatureFlags()
