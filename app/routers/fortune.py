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
from app.services.generate_service import dispatch

router = APIRouter(prefix="/api/fortune", tags=["fortune"])


@router.post("/reading")
def fortune_reading(p: FortuneReadingRequest):
    prompt, meta = dispatch(p, build_fortune_reading_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})


@router.post("/coconala")
def fortune_coconala(p: FortuneCoconalaRequest):
    prompt, meta = dispatch(p, build_fortune_coconala_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})


@router.post("/profile")
def fortune_profile(p: FortuneProfileRequest):
    prompt, meta = dispatch(p, build_fortune_profile_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})
