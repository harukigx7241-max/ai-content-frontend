"""app/schemas/fortune.py — Tab3: 占い副業系リクエストモデル"""
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.options import GenerateOptions


class FortuneReadingRequest(BaseModel):
    divination_type: str = Field(..., max_length=50)
    category: str = Field(..., max_length=50)
    direction: str = Field(..., max_length=50)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
    options: Optional[GenerateOptions] = None


class FortuneCoconalaRequest(BaseModel):
    divination_type: str = Field(..., max_length=50)
    specialty: str = Field(..., min_length=1, max_length=300)
    style: str = Field(..., max_length=50)
    price_range: str = Field(..., max_length=50)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
    options: Optional[GenerateOptions] = None


class FortuneProfileRequest(BaseModel):
    experience: str = Field(..., min_length=1, max_length=300)
    motivation: str = Field(..., min_length=1, max_length=300)
    strengths: str = Field(..., min_length=1, max_length=300)
    target: str = Field(..., min_length=1, max_length=200)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
    options: Optional[GenerateOptions] = None
