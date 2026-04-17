"""
app/analytics/router.py — /api/analytics/* + /api/feedback (Phase 9)

ルーターは薄く保ち、ロジックは analytics/service.py に委譲する。
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.analytics import service as analytics_service
from app.analytics.schemas import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackStatusUpdate,
    KpiResponse,
)
from app.auth.dependencies import get_current_user_soft, require_admin
from app.db.models.user import User
from app.db.session import get_db

router = APIRouter(tags=["analytics"])


# ── KPI / 分析 (管理者のみ) ──────────────────────────────────────────

@router.get("/api/admin/congestion")
def admin_congestion(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    管理者向け混雑詳細指標。
    一般ステータス + admin 詳細 (active_5m / events / posts_1h / error_rate) を返す。
    """
    from app.services.congestion_service import congestion_service
    from app.services.priority_lane import lane_summary
    data = congestion_service.get_admin_metrics(db=db)
    data["priority_lanes"] = lane_summary()
    return data


@router.get("/api/analytics/kpi", response_model=KpiResponse)
def kpi(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """総合 KPI を返す。"""
    return analytics_service.get_kpi(db)


@router.get("/api/analytics/activity")
def activity(
    days: int = Query(30, ge=1, le=90),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """xp_events の日別件数でアクティビティ推移を返す。"""
    data = analytics_service.get_daily_activity(db, days)
    return {"days": days, "data": data}


@router.get("/api/analytics/popular-posts")
def popular_posts(
    limit: int = Query(10, ge=1, le=50),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """view_count 上位の公開投稿一覧。"""
    return analytics_service.get_popular_posts(db, limit)


@router.get("/api/analytics/categories")
def categories(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """公開投稿のカテゴリ別件数。"""
    return analytics_service.get_category_stats(db)


@router.get("/api/analytics/xp-events")
def xp_events(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """XP イベントタイプ別件数。"""
    return analytics_service.get_xp_event_stats(db)


@router.get("/api/analytics/recent-users")
def recent_users(
    limit: int = Query(10, ge=1, le=50),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """直近ログインユーザー上位。"""
    return analytics_service.get_recently_active_users(db, limit)


@router.get("/api/analytics/invite-stats")
def invite_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """招待コード別利用状況。"""
    return analytics_service.get_invite_code_stats(db)


@router.get("/api/analytics/improvement-candidates")
def improvement_candidates(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """改善候補の簡易集計（離脱ユーザー予備軍など）。"""
    return analytics_service.get_improvement_candidates(db)


# ── フィードバック ────────────────────────────────────────────────────

@router.post("/api/feedback", response_model=FeedbackResponse, status_code=201)
def submit_feedback(
    body: FeedbackCreate,
    current_user: Optional[User] = Depends(get_current_user_soft),
    db: Session = Depends(get_db),
):
    """要望・フィードバックを送信する。ログイン任意（未ログインでも user_id=None で保存）。"""
    user_id = current_user.id if current_user else None
    return analytics_service.create_feedback(db, user_id, body.model_dump())


@router.get("/api/admin/feedback")
def list_feedback(
    status: Optional[str] = Query(None, description="open / acknowledged / closed"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """フィードバック一覧（管理者のみ）。"""
    return analytics_service.list_feedback(db, status)


@router.patch("/api/admin/feedback/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    feedback_id: int,
    body: FeedbackStatusUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """フィードバックのステータス・優先度・管理者メモを更新する。"""
    return analytics_service.update_feedback_status(
        db, feedback_id, body.status, body.admin_note, body.priority
    )
