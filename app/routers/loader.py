"""
app/routers/loader.py — 機能フラグ制御による認証系ルーター一括登録

main.py からは include_feature_routers(app) を呼ぶだけでよい。
新しいルーターを追加する場合はこのファイルだけ変更すればよい。

設計方針:
  - ENABLE_AUTH_SYSTEM=true の前提で呼ぶ (main.py 側で保証)
  - フラグが False のルーターはスキップし INFO ログを残す
  - ルーターの URL は変更しない (既存 API の後方互換維持)
  - _reg() ヘルパーでログを統一し、抜けが起きにくくする

TODO: フラグの種類が増えてきたら、各フラグを個別関数に分離することを検討する。
"""
import logging

from fastapi import FastAPI

from app.core.config import settings

logger = logging.getLogger(__name__)


def _reg(app: FastAPI, router, label: str) -> None:
    """ルーターを登録しログを残す小さなヘルパー。"""
    app.include_router(router)
    logger.info("router registered: %s", label)


def include_feature_routers(app: FastAPI) -> None:
    """
    認証系・機能フラグ依存のルーターをすべて登録する。
    ENABLE_AUTH_SYSTEM=true の場合のみ main.py から呼ばれる。
    """
    # ── 認証コア (常時有効) ────────────────────────────────────────────
    from app.auth.router import router as auth_router
    from app.admin.router import router as admin_router
    from app.user.router import router as user_router
    from app.routers.pages import router as pages_router

    _reg(app, auth_router,   "/api/auth/*")
    _reg(app, admin_router,  "/api/admin/*")
    _reg(app, user_router,   "/api/user/*")
    _reg(app, pages_router,  "/login /register /mypage /admin")

    # ── Phase 5: コミュニティ (ENABLE_COMMUNITY) ──────────────────────
    if settings.ENABLE_COMMUNITY:
        from app.community.router import router as community_router
        from app.community.pages import router as community_pages_router
        _reg(app, community_router,       "/api/community/*")
        _reg(app, community_pages_router, "/square/*")
    else:
        logger.info("router skipped: community (ENABLE_COMMUNITY=false)")

    # ── Phase 7: ゲーミフィケーション (ENABLE_GAMIFICATION) ──────────
    if settings.ENABLE_GAMIFICATION:
        from app.gamification.router import router as gami_router
        _reg(app, gami_router, "/api/gamification/*")
    else:
        logger.info("router skipped: gamification (ENABLE_GAMIFICATION=false)")

    # ── Phase 8: 招待システム (常時有効) ──────────────────────────────
    from app.invite.router import router as invite_router
    from app.invite.admin_router import router as invite_admin_router
    _reg(app, invite_router,       "/api/invite/*")
    _reg(app, invite_admin_router, "/api/admin/invite/*")

    # ── Phase 9: 分析 + フィードバック (常時有効) ─────────────────────
    from app.analytics.router import router as analytics_router
    _reg(app, analytics_router, "/api/analytics/* /api/feedback /api/admin/feedback")
