"""
app/routers/system.py — システム系エンドポイント
・/ (ページ描画)
・/health (ヘルスチェック)
・/api/system/config (フロントエンド向け設定 & 機能フラグ)
・/api/system/congestion (混雑状況 — 一般向け, 認証不要)
"""
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.feature_flags import flags
from app.core.templates import templates

router = APIRouter(tags=["system"])


@router.get("/")
def root(request: Request):
    """メインページ。機能フラグ・告知バー情報をテンプレートコンテキストで渡す。"""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME,
            "maintenance_mode": flags.MAINTENANCE_MODE,
            "maintenance_message": settings.MAINTENANCE_MESSAGE,
            "notice_banner_enabled": flags.NOTICE_BANNER,
            "notice_banner_text": settings.NOTICE_BANNER_TEXT,
            "notice_banner_link": settings.NOTICE_BANNER_LINK,
            "auth_system_enabled": flags.AUTH_SYSTEM,
        },
    )


@router.get("/health")
def health():
    """ヘルスチェック。デプロイ・監視ツールから使用。"""
    return {"status": "ok", "version": settings.APP_VERSION}


@router.get("/api/system/config")
def system_config():
    """
    フロントエンド向けの公開設定を返す。
    機能フラグ・告知バー情報を含む。
    """
    return JSONResponse(flags.as_dict())


@router.get("/api/system/congestion")
def congestion_status():
    """
    一般ユーザー向け混雑状況。認証不要。
    ENABLE_AUTH_SYSTEM=false の環境でも DB なしで静的ステータスを返す。
    DB が利用可能な場合は xp_events から算出する。
    """
    from app.services.congestion_service import congestion_service
    # DB セッション: ENABLE_AUTH_SYSTEM=true の場合のみ利用可能
    db: Optional[Session] = None
    if settings.ENABLE_AUTH_SYSTEM:
        try:
            from app.db.session import SessionLocal
            with SessionLocal() as _db:
                result = congestion_service.get_status(db=_db)
                return JSONResponse(result.content or result.to_dict())
        except Exception:
            pass
    result = congestion_service.get_status()
    return JSONResponse(result.content or {})
