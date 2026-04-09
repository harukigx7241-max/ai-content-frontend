"""app/schemas/common.py — 複数タブ横断のリクエストモデル"""
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.options import GenerateOptions


class ProjectBundleRequest(BaseModel):
    theme: str = Field(..., min_length=1, max_length=200)
    target: str = Field(..., min_length=1, max_length=200)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
    options: Optional[GenerateOptions] = None


class RemixRequest(BaseModel):
    original_prompt: str = Field(..., min_length=10, max_length=8000)
    variant: str = Field(default="emotional", max_length=30)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
    options: Optional[GenerateOptions] = None
