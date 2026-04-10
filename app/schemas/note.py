"""app/schemas/note.py — Tab1: 有料コンテンツ系リクエストモデル"""
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.options import GenerateOptions


class NoteArticleRequest(BaseModel):
    theme: str = Field(..., min_length=1, max_length=200)
    age_range: str = Field(default="25〜35歳", max_length=50)
    situation: str = Field(..., min_length=1, max_length=300)
    concern: str = Field(..., min_length=1, max_length=300)
    tone: str = Field(default="です・ます調", max_length=50)
    free_chars: str = Field(default="2000字", max_length=20)
    paid_chars: str = Field(default="5000字", max_length=20)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
    options: Optional[GenerateOptions] = None


class NoteTitlesRequest(BaseModel):
    genre: str = Field(..., min_length=1, max_length=100)
    keyword: str = Field(..., min_length=1, max_length=200)
    target: str = Field(..., min_length=1, max_length=200)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
    options: Optional[GenerateOptions] = None


class NoteSalesCopyRequest(BaseModel):
    platform: str = Field(..., max_length=50)
    content: str = Field(..., min_length=1, max_length=300)
    target: str = Field(..., min_length=1, max_length=200)
    price: str = Field(..., max_length=50)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
    options: Optional[GenerateOptions] = None


class NoteGiftRequest(BaseModel):
    theme: str = Field(..., min_length=1, max_length=200)
    gift_type: str = Field(..., max_length=50)
    volume: str = Field(default="標準版（A4 3枚相当）", max_length=50)
    buyer_situation: str = Field(..., min_length=1, max_length=300)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
    options: Optional[GenerateOptions] = None
