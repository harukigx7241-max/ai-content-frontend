"""
app/routers/system.py — システム系エンドポイント
・/ (ページ描画)
・/health (ヘルスチェック)
・/api/system/config (フロントエンド向け設定 & 機能フラグ)
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

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
    TODO: Phase 1+ で認証済みユーザー向けの拡張設定を追加。
    """
    return JSONResponse(flags.as_dict())
