"""
app/core/exceptions.py
共通例外ハンドラの受け皿。
app/main.py で app.add_exception_handler() に登録する。
TODO: Phase 1+ でユーザー向けエラーメッセージの国際化対応
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Pydantic バリデーションエラーを統一フォーマットで返す。"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "detail": exc.errors(),
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """想定外の例外をキャッチして 500 を返す。"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "予期しないエラーが発生しました。しばらくしてから再度お試しください。",
        },
    )
