"""app/schemas/cw.py — Tab2: クラウドワークス系リクエストモデル"""
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.options import GenerateOptions


class CwProposalRequest(BaseModel):
    job_title: str = Field(..., min_length=1, max_length=200)
    skills: str = Field(..., min_length=1, max_length=400)
    appeal: str = Field(..., min_length=1, max_length=300)
    desired_rate: str = Field(..., max_length=50)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
    options: Optional[GenerateOptions] = None


class CwProfileRequest(BaseModel):
    job_type: str = Field(..., max_length=50)
    experience_years: str = Field(..., max_length=20)
    specialty: str = Field(..., min_length=1, max_length=300)
    achievements: str = Field(..., min_length=1, max_length=400)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
    options: Optional[GenerateOptions] = None


class CwPricingRequest(BaseModel):
    current_rate: str = Field(..., max_length=50)
    desired_rate: str = Field(..., max_length=50)
    evidence: str = Field(..., min_length=1, max_length=400)
    tone: str = Field(default="丁寧", max_length=20)
    ai_mode: str = Field(default="ChatGPT", max_length=20)
    options: Optional[GenerateOptions] = None
