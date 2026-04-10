"""app/routers/sns.py — Tab4: SNS特化系エンドポイント"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.sns import (
    SnsTweetRequest,
    SnsThreadsRequest,
    SnsInstagramRequest,
    SnsBioRequest,
)
from app.prompts.builders.sns import (
    build_sns_tweet_prompt,
    build_sns_threads_prompt,
    build_sns_instagram_prompt,
    build_sns_bio_prompt,
)
from app.services.generate_service import dispatch

router = APIRouter(prefix="/api/sns", tags=["sns"])


@router.post("/twitter")
def sns_twitter(p: SnsTweetRequest):
    prompt, meta = dispatch(p, build_sns_tweet_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})


@router.post("/threads")
def sns_threads(p: SnsThreadsRequest):
    prompt, meta = dispatch(p, build_sns_threads_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})


@router.post("/instagram")
def sns_instagram(p: SnsInstagramRequest):
    prompt, meta = dispatch(p, build_sns_instagram_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})


@router.post("/bio")
def sns_bio(p: SnsBioRequest):
    prompt, meta = dispatch(p, build_sns_bio_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})
