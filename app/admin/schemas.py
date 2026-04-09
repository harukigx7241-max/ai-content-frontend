"""app/admin/schemas.py — 管理者向け Pydantic レスポンスモデル"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserAdminResponse(BaseModel):
    """管理者向けユーザー詳細レスポンス (UserResponse より多くの情報を含む)"""
    id: int
    sns_platform: str
    sns_handle: str
    display_name: str
    profile_url: Optional[str]
    status: str
    role: str
    created_at: datetime
    last_login_at: Optional[datetime]
    approved_at: Optional[datetime]
    approved_by: Optional[int]

    model_config = {"from_attributes": True}
