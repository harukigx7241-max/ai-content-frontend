"""app/schemas/common.py — 複数タブ横断のリクエストモデル"""
from pydantic import BaseModel, Field


class ProjectBundleRequest(BaseModel):
    theme: str = Field(..., min_length=1, max_length=200)
    target: str = Field(..., min_length=1, max_length=200)
    ai_mode: str = Field(default="ChatGPT", max_length=20)


class RemixRequest(BaseModel):
    original_prompt: str = Field(..., min_length=10, max_length=8000)
    variant: str = Field(default="emotional", max_length=30)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
