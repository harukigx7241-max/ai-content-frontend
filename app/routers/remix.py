"""app/routers/remix.py — リミックス（バリアント再生成）エンドポイント"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.common import RemixRequest
from app.prompts.builders.remix import build_remix_prompt

router = APIRouter(prefix="/api", tags=["remix"])


@router.post("/remix")
def remix_prompt(p: RemixRequest):
    return JSONResponse({"prompt": build_remix_prompt(p)})
