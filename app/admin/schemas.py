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


class AdminStatsResponse(BaseModel):
    """管理ダッシュボード向け基本統計"""
    total: int
    pending: int
    approved: int
    rejected: int
    suspended: int
    signups_last_7days: int


class SystemSettingsResponse(BaseModel):
    """システム設定の現在値"""
    maintenance_enabled: bool
    maintenance_message: str
    notice_banner_enabled: bool
    notice_banner_text: str
    notice_banner_link: str


class SystemSettingsUpdate(BaseModel):
    """システム設定の更新リクエスト。None のフィールドは変更しない。"""
    maintenance_enabled: Optional[bool] = None
    maintenance_message: Optional[str] = None
    notice_banner_enabled: Optional[bool] = None
    notice_banner_text: Optional[str] = None
    notice_banner_link: Optional[str] = None
