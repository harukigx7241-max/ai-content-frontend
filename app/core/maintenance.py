"""
app/core/maintenance.py
メンテナンスモードミドルウェア。

優先順位: runtime_config (管理者ダッシュボードで変更可能) > 環境変数
  - /api/admin/* は常に通す (管理者がメンテナンスを解除できるようにするため)
  - 静的ファイルとページは常に通す
"""
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core import runtime_config as rc
from app.core.config import settings


async def maintenance_middleware(request: Request, call_next):
    # runtime_config の値を優先し、未設定時は env var にフォールバック
    is_maintenance = rc.get_bool(rc.KEY_MAINTENANCE_ENABLED, settings.ENABLE_MAINTENANCE_MODE)

    if is_maintenance:
        path = request.url.path
        # /api/admin/* は管理者がメンテナンスを解除できるよう除外
        if path.startswith("/api/") and not path.startswith("/api/admin/"):
            message = rc.get(rc.KEY_MAINTENANCE_MESSAGE, settings.MAINTENANCE_MESSAGE)
            return JSONResponse(
                status_code=503,
                content={"error": "maintenance", "message": message},
            )

    return await call_next(request)
