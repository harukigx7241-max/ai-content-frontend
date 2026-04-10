"""app/analytics/schemas.py — 分析 API レスポンスモデル (Phase 9)"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class KpiResponse(BaseModel):
    # ユーザー
    users_total: int
    users_pending: int
    users_approved: int
    users_signups_7d: int
    users_signups_30d: int
    # コミュニティ
    posts_total: int
    posts_public: int
    posts_7d: int
    # XP / アクティビティ
    xp_events_total: int
    xp_events_7d: int
    # 招待
    invites_total: int
    invites_approved: int
    invite_conversion_rate: float  # invites_approved / invites_total * 100


class DailyActivityItem(BaseModel):
    date: str   # "YYYY-MM-DD"
    count: int


class PopularPostItem(BaseModel):
    id: int
    title: str
    author_name: str
    category: Optional[str] = None
    view_count: int
    created_at: datetime


class CategoryStatItem(BaseModel):
    category: str
    post_count: int


class XpEventStatItem(BaseModel):
    event_type: str
    count: int


class FeedbackCreate(BaseModel):
    category: str = "general"   # "feature" | "bug" | "other" | "general"
    title: str
    body: Optional[str] = None


class FeedbackStatusUpdate(BaseModel):
    status: str                          # "open" | "acknowledged" | "closed"
    admin_note: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    category: str
    title: str
    body: Optional[str] = None
    status: str
    admin_note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    display_name: Optional[str] = None  # JOIN から取得

    model_config = {"from_attributes": True}
