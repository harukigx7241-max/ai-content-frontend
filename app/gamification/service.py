"""
app/gamification/service.py — ゲーミフィケーション オーケストレーター

責務:
  - try_award()  : XP を安全に付与する (日次制限・バッジ判定を含む)
  - get_status() : ユーザーの現在の XP / レベル / バッジ状況を返す

設計原則:
  - try_award は必ず try/except で囲み、失敗しても呼び出し元 (router) に例外を伝播しない
    → ゲーミフィケーションの不具合でログインや投稿が壊れないようにする
  - 重いロジックは xp_service / badge_service に委譲し、このファイルは薄く保つ
  - 全ての XP 付与は xp_events テーブルに記録 (監査ログ)

将来拡張:
  TODO: Phase N+ ランキング集計 (xp_events を期間で sum)
  TODO: Phase N+ ミッション進捗チェック
  TODO: Phase N+ 連続ログイン streak 追跡
"""
import logging
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.xp_event import XpEvent
from app.gamification import badge_service, xp_service
from app.gamification.constants import (
    BADGE_DEFINITIONS,
    DAILY_CAP_EVENTS,
    ENTITY_TYPE_BY_EVENT,
    XP_VALUES,
)
from app.gamification.schemas import (
    BadgeResponse,
    GamificationStatusResponse,
    LevelBenefitsResponse,
    XpActivityItem,
    XpActivityResponse,
)

logger = logging.getLogger(__name__)

# ── XP イベントの日本語ラベル ─────────────────────────────────────────
_EVENT_LABELS: dict[str, str] = {
    "login":            "デイリーログイン",
    "post_public":      "公開投稿",
    "post_private":     "非公開投稿",
    "copy_received":    "コピーされた",
    "generate":         "プロンプト生成",
    "post_liked":       "いいね獲得",
    "post_saved":       "保存獲得",
    "post_used":        "使用獲得",
    "comment_received": "コメント獲得",
    "invite_registered":"招待登録",
    "invite_approved":  "招待承認",
}


# ── XP 付与 ───────────────────────────────────────────────────────

def try_award(
    db: Session,
    user_id: int,
    event_type: str,
    ref_id: Optional[int] = None,
) -> tuple[int, list[str]]:
    """
    XP を安全に付与する。エラーが発生しても (0, []) を返し例外を伝播しない。

    Returns:
        (xp_gained, list_of_new_badge_keys)
    """
    try:
        return _do_award(db, user_id, event_type, ref_id)
    except Exception as e:
        logger.warning("gamification.try_award failed (user=%s event=%s): %s", user_id, event_type, e)
        try:
            db.rollback()
        except Exception:
            pass
        return 0, []


def _do_award(
    db: Session,
    user_id: int,
    event_type: str,
    ref_id: Optional[int],
) -> tuple[int, list[str]]:
    xp_amount = XP_VALUES.get(event_type, 0)
    if xp_amount <= 0:
        return 0, []

    # ── 日次制限チェック ──────────────────────────────────────────
    if event_type in DAILY_CAP_EVENTS:
        today_start = datetime(
            *date.today().timetuple()[:3], tzinfo=timezone.utc
        )
        exists = db.execute(
            select(XpEvent.id).where(
                XpEvent.user_id == user_id,
                XpEvent.event_type == event_type,
                XpEvent.created_at >= today_start,
            ).limit(1)
        ).first()
        if exists:
            return 0, []  # 今日はすでに付与済み

    # ── XP ログを追記 ──────────────────────────────────────────────
    log = XpEvent(
        user_id=user_id,
        event_type=event_type,
        xp_delta=xp_amount,
        ref_id=ref_id,                                       # 後方互換
        related_entity_type=ENTITY_TYPE_BY_EVENT.get(event_type),
        related_entity_id=ref_id,
    )
    db.add(log)

    # ── User の xp / level を更新 ─────────────────────────────────
    user = db.get(User, user_id)
    if not user:
        db.rollback()
        return 0, []

    old_level  = user.level or 1
    user.xp    = (user.xp or 0) + xp_amount
    user.level = xp_service.calc_level(user.xp)
    db.commit()

    # ── バッジ判定 (コミット後) ───────────────────────────────────
    new_badges = badge_service.check_and_award_badges(db, user, old_level, event_type)
    return xp_amount, new_badges


# ── アクティビティ履歴 ────────────────────────────────────────────

def get_recent_activity(db: Session, user_id: int, limit: int = 20) -> XpActivityResponse:
    """最近の XP イベント履歴を返す。"""
    events = db.execute(
        select(XpEvent)
        .where(XpEvent.user_id == user_id)
        .order_by(XpEvent.created_at.desc())
        .limit(limit)
    ).scalars().all()
    items = [
        XpActivityItem(
            id=e.id,
            event_type=e.event_type,
            event_label=_EVENT_LABELS.get(e.event_type, e.event_type),
            xp_delta=e.xp_delta,
            created_at=e.created_at,
        )
        for e in events
    ]
    total_xp = sum(i.xp_delta for i in items)
    return XpActivityResponse(items=items, total_xp=total_xp)


# ── ステータス取得 ────────────────────────────────────────────────

def get_status(db: Session, user_id: int) -> GamificationStatusResponse:
    """ユーザーの現在の XP / レベル / バッジ状況を返す。"""
    user  = db.get(User, user_id)
    xp    = user.xp    if user and user.xp    is not None else 0
    level = user.level if user and user.level is not None else 1

    current_min, next_min, title, _ = xp_service.get_level_info(level)

    if next_min is not None:
        xp_to_next   = max(0, next_min - xp)
        range_width  = next_min - current_min or 1
        progress_pct = min(100, int((xp - current_min) / range_width * 100))
    else:
        xp_to_next   = None
        progress_pct = 100  # 最大レベル

    # 獲得バッジ一覧
    badges = [
        BadgeResponse(
            key=b.badge_key,
            name=BADGE_DEFINITIONS[b.badge_key]["name"],
            icon=BADGE_DEFINITIONS[b.badge_key]["icon"],
            description=BADGE_DEFINITIONS[b.badge_key]["description"],
            earned_at=b.earned_at,
        )
        for b in badge_service.get_user_badges(db, user_id)
        if b.badge_key in BADGE_DEFINITIONS
    ]

    # レベル特典
    raw_benefits = xp_service.get_benefits(level)
    benefits = LevelBenefitsResponse(**raw_benefits)

    return GamificationStatusResponse(
        user_id=user_id,
        xp=xp,
        level=level,
        title=title,
        xp_at_current_level=current_min,
        xp_at_next_level=next_min,
        xp_to_next=xp_to_next,
        progress_pct=progress_pct,
        badges=badges,
        level_benefits=benefits,
    )
