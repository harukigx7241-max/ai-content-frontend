"""
app/core/maintenance.py
メンテナンスモードミドルウェア。
ENABLE_MAINTENANCE_MODE=true の場合、API エンドポイントに 503 を返す。
フロントエンドのページ自体は通すので、UI 側でも告知可能。
"""
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import settings


async def maintenance_middleware(request: Request, call_next):
    if settings.ENABLE_MAINTENANCE_MODE:
        # API リクエストのみブロック（静的ファイルとページは通す）
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=503,
                content={
                    "error": "maintenance",
                    "message": settings.MAINTENANCE_MESSAGE,
                },
            )
    return await call_next(request)
