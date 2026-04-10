"""
app/schemas/auth.py — 認証系 Pydantic リクエスト/レスポンスモデル
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

SNS_PLATFORMS = ["X", "Threads", "Instagram", "note", "TikTok", "YouTube", "ブログ", "その他"]


class RegisterRequest(BaseModel):
    sns_platform: str = Field(..., max_length=50)
    sns_handle: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    profile_url: Optional[str] = Field(None, max_length=500)
    # TODO: Phase 3+ email: Optional[str] = Field(None, max_length=200)

    @field_validator("sns_platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        if v not in SNS_PLATFORMS:
            raise ValueError(f"sns_platform は {SNS_PLATFORMS} のいずれかである必要があります")
        return v

    @field_validator("sns_handle")
    @classmethod
    def clean_handle(cls, v: str) -> str:
        """先頭の @ は任意。前後の空白を除去。"""
        return v.strip().lstrip("@")


class LoginRequest(BaseModel):
    sns_platform: str = Field(..., max_length=50)
    sns_handle: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("sns_handle")
    @classmethod
    def clean_handle(cls, v: str) -> str:
        return v.strip().lstrip("@")


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)
    new_password_confirm: str = Field(..., min_length=1, max_length=128)
    # TODO: Phase 3+ reset_token: Optional[str] = None (パスワードリセット用)


class UserResponse(BaseModel):
    id: int
    sns_platform: str
    sns_handle: str
    display_name: str
    profile_url: Optional[str]
    bio: Optional[str] = None  # Phase 4: 自己紹介文
    status: str
    role: str
    created_at: datetime
    last_login_at: Optional[datetime]

    model_config = {"from_attributes": True}
