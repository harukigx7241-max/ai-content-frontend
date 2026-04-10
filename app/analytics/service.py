"""
app/analytics/service.py — 分析・KPI 集計ロジック (Phase 9)

責務: DB からの集計クエリのみ。ルーターから直接呼ばれる。

──── イベントソースマッピング ─────────────────────────────────────────────────
行動カテゴリ      収集先                              備考
─────────────────────────────────────────────────────────────────────────────
auth / login    │ xp_events (event_type=login)      │ auth/router.py で try_award 呼び出し
generate        │ ※ generation_log 未実装            │ TODO Phase N+: generation_log 追加後に集計
post create     │ xp_events (post_public/private)   │ community/router.py で try_award 呼び出し
like / save     │ xp_events (post_liked/post_saved) │ community/router.py で try_award 呼び出し
post_used       │ xp_events (post_used)             │ community/router.py でコピー時に発火
invite          │ invite_uses テーブル               │ invite/service.py で record_code_use
xp / level      │ xp_events + users (xp/level)      │ gamification/service.py で管理
badge           │ user_badges テーブル               │ gamification/badge_service.py で管理
audit           │ audit_logs テーブル                │ 本ファイルの log_audit() で書き込み
─────────────────────────────────────────────────────────────────────────────

将来拡張ポイント (Phase N+):
  ランキング強化   → popular_posts / category_stats が基盤
  通知最適化       → xp_events の event_type 分布が閾値通知の判断材料
  A/B テスト       → audit_log.action に "ab_test_assign" を追加するだけで記録可能な構造
  招待品質評価     → invite_code_stats に承認率・離脱率を追加しやすい構造
  不正検知         → audit_log + generation_log(未実装) の組み合わせで異常検知
  おすすめ機能     → category_stats + popular_posts が行動ベースレコメンドの入力になる

設計方針:
  - 各セクションは try/except で囲み、機能フラグ無効でも安全に動作する
  - 将来 generation_log / like_count が追加されたら stub を差し替えるだけ
  - 重い集計が必要になったら daily_stats キャッシュテーブルへ移行を検討する
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.xp_event import XpEvent


# ── KPI 集計 ─────────────────────────────────────────────────────────

def get_kpi(db: Session) -> dict:
    """
    管理ダッシュボード向け総合 KPI。
    現在値 / 日次ベース で集計する。
    将来は daily_stats テーブルへのキャッシュで高速化できる構造を維持する。
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    d7  = now - timedelta(days=7)
    d30 = now - timedelta(days=30)

    # ── ユーザー ────────────────────────────────────────────────────
    users_total    = db.query(User).count()
    users_pending  = db.query(User).filter(User.status == "pending").count()
    users_approved = db.query(User).filter(User.status == "approved").count()
    users_suspended = db.query(User).filter(User.status == "suspended").count()
    users_7d       = db.query(User).filter(User.created_at >= d7).count()
    users_30d      = db.query(User).filter(User.created_at >= d30).count()
    # 承認済みだが直近30日間未ログイン（離脱ユーザー予備軍）
    dormant_30d = db.query(User).filter(
        User.status == "approved",
        (User.last_login_at < d30) | (User.last_login_at.is_(None)),
    ).count()

    # ── 今日のアクティビティ ─────────────────────────────────────────
    logins_today = 0
    posts_today  = 0
    try:
        logins_today = db.query(XpEvent).filter(
            XpEvent.event_type == "login",
            XpEvent.created_at >= today_start,
        ).count()
    except Exception:
        pass
    # TODO: Phase N+ generation_log 実装後に今日の生成数・目的別生成数を集計
    generations_today = 0  # stub: generation_log 未実装

    # ── コミュニティ ────────────────────────────────────────────────
    posts_total = posts_public = 0
    # TODO: Phase N+ CommunityPost に like_count / save_count / comment_count 追加後に集計
    likes_total = saves_total = comments_total = 0  # stub
    try:
        from app.db.models.post import CommunityPost
        posts_total  = db.query(CommunityPost).count()
        posts_public = db.query(CommunityPost).filter(CommunityPost.visibility == "public").count()
        posts_today  = db.query(CommunityPost).filter(CommunityPost.created_at >= today_start).count()
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
        "users_suspended":      users_suspended,
        "users_signups_7d":     users_7d,
        "users_signups_30d":    users_30d,
        "dormant_users_30d":    dormant_30d,
        "logins_today":         logins_today,
        "posts_today":          posts_today,
        "generations_today":    generations_today,   # stub
        "likes_total":          likes_total,         # stub
        "saves_total":          saves_total,         # stub
        "comments_total":       comments_total,      # stub
        "posts_total":          posts_total,
        "posts_public":         posts_public,
        "xp_events_total":      xp_total,
        "xp_events_7d":         xp_7d,
        "invites_total":        invites_total,
        "invites_approved":     invites_approved,
        "invite_conversion_rate": conversion,
    }


# ── AuditLog 書き込み ─────────────────────────────────────────────────

def log_audit(
    db: Session,
    admin_id: Optional[int],
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    detail: Optional[str] = None,
) -> None:
    """
    管理操作を audit_log に記録する。
    失敗は無視する（呼び出し元の処理に影響させない）。

    呼び出し側のパターン (admin/service.py など):
        try:
            from app.analytics.service import log_audit
            log_audit(db, admin_id, "approve_user", "user", user_id)
        except Exception:
            pass

    将来の action 一覧例:
        approve_user / reject_user / suspend_user / restore_user
        create_invite_code / deactivate_invite_code
        update_settings
        feature_flag_change (Phase N+)
        ab_test_assign (Phase N+)
    """
    try:
        from app.db.models.feedback import AuditLog
        db.add(AuditLog(
            admin_user_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
        ))
        db.commit()
    except Exception:
        pass


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


# ── 最近アクティブなユーザー ─────────────────────────────────────────

def get_recently_active_users(db: Session, limit: int = 10) -> list[dict]:
    """直近ログインユーザー上位。承認済みかつ last_login_at がある順。"""
    try:
        users = (
            db.query(User)
            .filter(User.status == "approved", User.last_login_at.isnot(None))
            .order_by(User.last_login_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id":            u.id,
                "display_name":  u.display_name,
                "sns_platform":  u.sns_platform,
                "last_login_at": u.last_login_at,
                "xp":            getattr(u, "xp", 0),
                "level":         getattr(u, "level", 1),
            }
            for u in users
        ]
    except Exception:
        return []


# ── 人気投稿 ─────────────────────────────────────────────────────────

def get_popular_posts(db: Session, limit: int = 10) -> list[dict]:
    """view_count 上位の公開投稿一覧。コミュニティ無効時は空リスト。"""
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
                "purpose":     post.purpose,
                "view_count":  post.view_count,
                "created_at":  post.created_at,
            }
            for post, name in rows
        ]
    except Exception:
        return []


# ── カテゴリ別統計 ───────────────────────────────────────────────────

def get_category_stats(db: Session) -> list[dict]:
    """
    公開投稿のカテゴリ別件数。
    TODO: Phase N+ like_count / use_count 追加後に人気カテゴリ判断指標を強化する
    """
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
    """
    XP イベントタイプ別件数。
    イベント種別はgamification/constants.py の XPEvent クラスで管理している。
    TODO: 将来 "generate" 系イベント (generation_log) が追加されたらここに統合する
    """
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


# ── 招待コード利用状況 ────────────────────────────────────────────────

def get_invite_code_stats(db: Session) -> list[dict]:
    """
    招待コード別利用状況。管理者・ユーザー発行問わず最新50件。
    将来: used_count / max_uses から承認率・離脱率を計算する拡張ポイント。
    """
    try:
        from app.db.models.invite import InviteCode
        codes = (
            db.query(InviteCode, User.display_name)
            .join(User, InviteCode.created_by_user_id == User.id, isouter=True)
            .order_by(InviteCode.created_at.desc())
            .limit(50)
            .all()
        )
        return [
            {
                "id":           c.id,
                "code":         c.code,
                "label":        c.label,
                "created_by":   name or ("管理者" if c.is_admin_code else "—"),
                "used_count":   c.used_count,
                "max_uses":     c.max_uses,
                "auto_approve": c.auto_approve,
                "status":       c.status,
                "expires_at":   c.expires_at,
                "created_at":   c.created_at,
            }
            for c, name in codes
        ]
    except Exception:
        return []


# ── 改善候補 ─────────────────────────────────────────────────────────

def get_improvement_candidates(db: Session) -> dict:
    """
    運営改善に役立つ簡易集計。現在取れる指標のみ。

    現在提供できる指標:
      dormant_users         : 承認済みだが30日間未ログイン (last_login_at が古い上位10件)
      never_logged_in_count : 承認済みで一度もログインしていないユーザー数

    TODO: Phase N+ で追加する指標:
      high_view_low_save    : view_count は多いが save/use が少ない投稿 (like_count 実装後)
      low_engagement_cats   : 投稿数は多いが使用数が少ないカテゴリ (use_count 実装後)
      invite_churn          : 招待経由で登録したが早期離脱したユーザーパターン
      low_conversion_funnel : 登録数は多いが承認後の初回ログインまでの日数が長い導線
    """
    d30 = datetime.now(timezone.utc) - timedelta(days=30)
    dormant = []
    never_logged_in_count = 0
    try:
        dormant_users = (
            db.query(User)
            .filter(
                User.status == "approved",
                User.last_login_at < d30,
                User.last_login_at.isnot(None),
            )
            .order_by(User.last_login_at.asc())
            .limit(10)
            .all()
        )
        dormant = [
            {
                "id":            u.id,
                "display_name":  u.display_name,
                "last_login_at": u.last_login_at,
                "created_at":    u.created_at,
            }
            for u in dormant_users
        ]
        never_logged_in_count = db.query(User).filter(
            User.status == "approved",
            User.last_login_at.is_(None),
        ).count()
    except Exception:
        pass
    return {
        "dormant_users":         dormant,
        "never_logged_in_count": never_logged_in_count,
    }


# ── フィードバック ────────────────────────────────────────────────────

def create_feedback(db: Session, user_id: Optional[int], data: dict):
    from app.db.models.feedback import Feedback
    fb = Feedback(
        user_id=user_id,
        category=data.get("category", "general"),
        title=data["title"],
        body=data.get("body"),
        priority=data.get("priority", "medium"),
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
    items = []
    for fb, display_name in q.all():
        d = {c.name: getattr(fb, c.name) for c in fb.__table__.columns}
        d["display_name"] = display_name
        items.append(d)
    return items


def update_feedback_status(
    db: Session,
    feedback_id: int,
    status: str,
    admin_note: Optional[str] = None,
    priority: Optional[str] = None,
):
    from fastapi import HTTPException
    from app.db.models.feedback import Feedback
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(404, f"フィードバック ID={feedback_id} が見つかりません")
    fb.status = status
    if admin_note is not None:
        fb.admin_note = admin_note
    if priority is not None:
        fb.priority = priority
    fb.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(fb)
    return fb
