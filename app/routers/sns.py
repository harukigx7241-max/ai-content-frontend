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

router = APIRouter(prefix="/api/sns", tags=["sns"])


@router.post("/twitter")
def sns_twitter(p: SnsTweetRequest):
    return JSONResponse({"prompt": build_sns_tweet_prompt(p)})


@router.post("/threads")
def sns_threads(p: SnsThreadsRequest):
    return JSONResponse({"prompt": build_sns_threads_prompt(p)})


@router.post("/instagram")
def sns_instagram(p: SnsInstagramRequest):
    return JSONResponse({"prompt": build_sns_instagram_prompt(p)})


@router.post("/bio")
def sns_bio(p: SnsBioRequest):
    return JSONResponse({"prompt": build_sns_bio_prompt(p)})
