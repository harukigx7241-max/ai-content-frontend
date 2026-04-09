"""app/routers/fortune.py — Tab3: 占い副業系エンドポイント"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.fortune import (
    FortuneReadingRequest,
    FortuneCoconalaRequest,
    FortuneProfileRequest,
)
from app.prompts.builders.fortune import (
    build_fortune_reading_prompt,
    build_fortune_coconala_prompt,
    build_fortune_profile_prompt,
)

router = APIRouter(prefix="/api/fortune", tags=["fortune"])


@router.post("/reading")
def fortune_reading(p: FortuneReadingRequest):
    return JSONResponse({"prompt": build_fortune_reading_prompt(p)})


@router.post("/coconala")
def fortune_coconala(p: FortuneCoconalaRequest):
    return JSONResponse({"prompt": build_fortune_coconala_prompt(p)})


@router.post("/profile")
def fortune_profile(p: FortuneProfileRequest):
    return JSONResponse({"prompt": build_fortune_profile_prompt(p)})
