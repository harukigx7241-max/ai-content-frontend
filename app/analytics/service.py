"""
app/analytics/service.py — 分析・KPI 集計ロジック (Phase 9)

責務: DB からの集計クエリのみ。ルーターから直接呼ばれる。
設計方針:
  - 各セクションは try/except で囲み、機能フラグが無効でも安全に 0 を返す
  - community / gamification / invite が無効環境でも KPI は部分的に返せる
  - 将来 generation_log テーブルが追加されたらここに集計関数を追記する
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.xp_event import XpEvent


# ── KPI 集計 ─────────────────────────────────────────────────────────

def get_kpi(db: Session) -> dict:
    now = datetime.now(timezone.utc)
    d7  = now - timedelta(days=7)
    d30 = now - timedelta(days=30)

    # ── ユーザー ────────────────────────────────────────────────────
    users_total    = db.query(User).count()
    users_pending  = db.query(User).filter(User.status == "pending").count()
    users_approved = db.query(User).filter(User.status == "approved").count()
    users_7d       = db.query(User).filter(User.created_at >= d7).count()
    users_30d      = db.query(User).filter(User.created_at >= d30).count()

    # ── コミュニティ ────────────────────────────────────────────────
    posts_total = posts_public = posts_7d = 0
    try:
        from app.db.models.post import CommunityPost
        posts_total  = db.query(CommunityPost).count()
        posts_public = db.query(CommunityPost).filter(CommunityPost.visibility == "public").count()
        posts_7d     = db.query(CommunityPost).filter(CommunityPost.created_at >= d7).count()
    except Exception:
        pass

    # ── XP イベント ─────────────────────────────────────────────────
    xp_total = xp_7d = 0
    try:
        xp_total = db.query(XpEvent).count()
        xp_7d    = db.query(XpEvent).filter(XpEvent.created_at >= d7).count()
    except Exception:
        pass

    # ── 招待 ────────────────────────────────────────────────────────
    invites_total = invites_approved = 0
    try:
        from app.db.models.invite import InviteUse
        invites_total    = db.query(InviteUse).count()
        invites_approved = db.query(User).filter(
            User.invited_by_user_id.isnot(None),
            User.status == "approved",
        ).count()
    except Exception:
        pass

    conversion = round(invites_approved / invites_total * 100, 1) if invites_total else 0.0

    return {
        "users_total":          users_total,
        "users_pending":        users_pending,
        "users_approved":       users_approved,
        "users_signups_7d":     users_7d,
        "users_signups_30d":    users_30d,
        "posts_total":          posts_total,
        "posts_public":         posts_public,
        "posts_7d":             posts_7d,
        "xp_events_total":      xp_total,
        "xp_events_7d":         xp_7d,
        "invites_total":        invites_total,
        "invites_approved":     invites_approved,
        "invite_conversion_rate": conversion,
    }


# ── アクティビティ推移 ───────────────────────────────────────────────

def get_daily_activity(db: Session, days: int = 30) -> list[dict]:
    """xp_events の日別件数でアクティビティ推移を返す。"""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    try:
        rows = db.execute(
            text(
                "SELECT date(created_at) AS day, count(*) AS cnt "
                "FROM xp_events "
                "WHERE created_at >= :since "
                "GROUP BY day "
                "ORDER BY day ASC"
            ),
            {"since": since.isoformat()},
        ).fetchall()
        return [{"date": row[0], "count": row[1]} for row in rows]
    except Exception:
        return []


# ── 人気投稿 ─────────────────────────────────────────────────────────

def get_popular_posts(db: Session, limit: int = 10) -> list[dict]:
    """view_count 上位の公開投稿一覧。コミュニティ無効時は空リストを返す。"""
    try:
        from app.db.models.post import CommunityPost
        rows = (
            db.query(CommunityPost, User.display_name)
            .join(User, CommunityPost.user_id == User.id, isouter=True)
            .filter(CommunityPost.visibility == "public")
            .order_by(CommunityPost.view_count.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id":          post.id,
                "title":       post.title,
                "author_name": name or "—",
                "category":    post.category,
                "view_count":  post.view_count,
                "created_at":  post.created_at,
            }
            for post, name in rows
        ]
    except Exception:
        return []


# ── カテゴリ別統計 ───────────────────────────────────────────────────

def get_category_stats(db: Session) -> list[dict]:
    """公開投稿のカテゴリ別件数。コミュニティ無効時は空リスト。"""
    try:
        from app.db.models.post import CommunityPost
        rows = (
            db.query(CommunityPost.category, func.count(CommunityPost.id))
            .filter(CommunityPost.visibility == "public")
            .group_by(CommunityPost.category)
            .order_by(func.count(CommunityPost.id).desc())
            .all()
        )
        return [{"category": cat or "未分類", "post_count": cnt} for cat, cnt in rows]
    except Exception:
        return []


# ── XP イベント別統計 ────────────────────────────────────────────────

def get_xp_event_stats(db: Session) -> list[dict]:
    """XP イベントタイプ別件数。"""
    try:
        rows = (
            db.query(XpEvent.event_type, func.count(XpEvent.id))
            .group_by(XpEvent.event_type)
            .order_by(func.count(XpEvent.id).desc())
            .all()
        )
        return [{"event_type": et, "count": cnt} for et, cnt in rows]
    except Exception:
        return []


# ── フィードバック ────────────────────────────────────────────────────

def create_feedback(db: Session, user_id: Optional[int], data: dict):
    from app.db.models.feedback import Feedback
    fb = Feedback(
        user_id=user_id,
        category=data.get("category", "general"),
        title=data["title"],
        body=data.get("body"),
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


def list_feedback(db: Session, status: Optional[str] = None) -> list[dict]:
    from app.db.models.feedback import Feedback
    q = (
        db.query(Feedback, User.display_name)
        .join(User, Feedback.user_id == User.id, isouter=True)
        .order_by(Feedback.created_at.desc())
    )
    if status:
        q = q.filter(Feedback.status == status)
    results = q.all()
    items = []
    for fb, display_name in results:
        d = {c.name: getattr(fb, c.name) for c in fb.__table__.columns}
        d["display_name"] = display_name
        items.append(d)
    return items


def update_feedback_status(db: Session, feedback_id: int, status: str, admin_note: Optional[str] = None):
    from fastapi import HTTPException
    from app.db.models.feedback import Feedback
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(404, f"フィードバック ID={feedback_id} が見つかりません")
    fb.status = status
    if admin_note is not None:
        fb.admin_note = admin_note
    fb.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(fb)
    return fb
