"""app/analytics/schemas.py — 分析 API レスポンスモデル (Phase 9)"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class KpiResponse(BaseModel):
    # ── ユーザー ─────────────────────────────────────────────────────
    users_total: int
    users_pending: int
    users_approved: int
    users_suspended: int
    users_signups_7d: int
    users_signups_30d: int
    dormant_users_30d: int          # 承認済みだが30日間未ログイン
    # ── 今日のアクティビティ ──────────────────────────────────────────
    logins_today: int               # xp_events event_type=login 今日分
    posts_today: int                # 今日新規作成された投稿
    generations_today: int          # stub: generation_log 未実装
    # ── コミュニティ ──────────────────────────────────────────────────
    posts_total: int
    posts_public: int
    likes_total: int                # stub: CommunityPost.like_count 未実装
    saves_total: int                # stub: CommunityPost.save_count 未実装
    comments_total: int             # stub: CommunityPost.comment_count 未実装
    # ── XP / アクティビティ ───────────────────────────────────────────
    xp_events_total: int
    xp_events_7d: int
    # ── 招待 ──────────────────────────────────────────────────────────
    invites_total: int
    invites_approved: int
    invite_conversion_rate: float   # invites_approved / invites_total * 100


class DailyActivityItem(BaseModel):
    date: str   # "YYYY-MM-DD"
    count: int


class PopularPostItem(BaseModel):
    id: int
    title: str
    author_name: str
    category: Optional[str] = None
    purpose: Optional[str] = None
    view_count: int
    created_at: datetime


class CategoryStatItem(BaseModel):
    category: str
    post_count: int


class XpEventStatItem(BaseModel):
    event_type: str
    count: int


class RecentUserItem(BaseModel):
    id: int
    display_name: str
    sns_platform: str
    last_login_at: datetime
    xp: int = 0
    level: int = 1


class InviteCodeStatItem(BaseModel):
    id: int
    code: str
    label: Optional[str] = None
    created_by: str
    used_count: int
    max_uses: int
    auto_approve: bool
    status: str
    expires_at: Optional[datetime] = None
    created_at: datetime


class ImprovementDormantUserItem(BaseModel):
    id: int
    display_name: str
    last_login_at: Optional[datetime] = None
    created_at: datetime


class ImprovementCandidatesResponse(BaseModel):
    dormant_users: list[ImprovementDormantUserItem]
    never_logged_in_count: int


# ── フィードバック ────────────────────────────────────────────────────

class FeedbackCreate(BaseModel):
    category: str = "general"      # "feature" | "bug" | "other" | "general"
    title: str
    body: Optional[str] = None
    priority: str = "medium"       # "low" | "medium" | "high"


class FeedbackStatusUpdate(BaseModel):
    status: str                    # "open" | "acknowledged" | "closed"
    admin_note: Optional[str] = None
    priority: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    category: str
    title: str
    body: Optional[str] = None
    status: str
    priority: str = "medium"
    admin_note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    display_name: Optional[str] = None

    model_config = {"from_attributes": True}
