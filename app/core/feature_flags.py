"""
app/core/feature_flags.py
機能フラグの一元管理。settings から読み込む。
フロントエンドへは /api/system/config 経由で公開される。
"""
from app.core.config import settings


class FeatureFlags:
    MAINTENANCE_MODE: bool = settings.ENABLE_MAINTENANCE_MODE
    NOTICE_BANNER: bool = settings.ENABLE_NOTICE_BANNER

    # 将来機能（全て False 固定 in Phase 0）
    AUTH_SYSTEM: bool = settings.ENABLE_AUTH_SYSTEM
    ADMIN_DASHBOARD: bool = settings.ENABLE_ADMIN_DASHBOARD
    COMMUNITY: bool = settings.ENABLE_COMMUNITY
    GAMIFICATION: bool = settings.ENABLE_GAMIFICATION
    INVITE_SYSTEM: bool = settings.ENABLE_INVITE_SYSTEM

    def as_dict(self) -> dict:
        """フロントエンド向けに辞書形式で返す。"""
        return {
            "maintenance": self.MAINTENANCE_MODE,
            "notice_banner": {
                "enabled": self.NOTICE_BANNER,
                "text": settings.NOTICE_BANNER_TEXT if self.NOTICE_BANNER else "",
                "link": settings.NOTICE_BANNER_LINK if self.NOTICE_BANNER else "",
            },
            "features": {
                "auth_system": self.AUTH_SYSTEM,
                "admin_dashboard": self.ADMIN_DASHBOARD,
                "community": self.COMMUNITY,
                "gamification": self.GAMIFICATION,
                "invite_system": self.INVITE_SYSTEM,
            },
        }


# グローバルシングルトン
flags = FeatureFlags()
