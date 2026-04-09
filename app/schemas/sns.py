"""app/schemas/sns.py — Tab4: SNS特化系リクエストモデル"""
from pydantic import BaseModel, Field


class SnsTweetRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    genre: str = Field(..., max_length=50)
    style: str = Field(default="問いかけ", max_length=30)
    length: str = Field(default="140字", max_length=20)
    ai_mode: str = Field(default="ChatGPT", max_length=20)


class SnsThreadsRequest(BaseModel):
    theme: str = Field(..., min_length=1, max_length=200)
    mood: str = Field(default="カジュアル", max_length=30)
    audience: str = Field(..., min_length=1, max_length=200)
    ai_mode: str = Field(default="ChatGPT", max_length=20)


class SnsInstagramRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=300)
    genre: str = Field(..., max_length=50)
    goal: str = Field(default="エンゲージメント", max_length=50)
    ai_mode: str = Field(default="ChatGPT", max_length=20)


class SnsBioRequest(BaseModel):
    platform: str = Field(..., max_length=30)
    niche: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    target: str = Field(..., min_length=1, max_length=200)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
