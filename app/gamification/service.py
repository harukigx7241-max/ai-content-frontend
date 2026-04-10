"""
app/gamification/service.py — XP付与・レベル計算・バッジ判定

責務:
  - try_award()  : XP を安全に付与する (日次制限・バッジ判定を含む)
  - get_status() : ユーザーの現在の XP / レベル / バッジ状況を返す

設計原則:
  - try_award は必ず try/except で囲み、失敗しても呼び出し元 (router) に例外を伝播しない
    → ゲーミフィケーションの不具合でログインや投稿が壊れないようにする
  - 全ての XP 付与は xp_events テーブルに記録 (監査ログ)
  - レベルは XP から計算し User.level にキャッシュする
  - バッジは user_badges テーブルで管理し重複取得を防ぐ

将来拡張:
  TODO: Phase N+ ランキング集計 (xp_events を期間で sum)
  TODO: Phase N+ ミッション進捗チェック
  TODO: Phase N+ 連続ログイン streak 追跡
  TODO: Phase N+ use_count に基づく shared_10 バッジ
"""
import logging
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.user_badge import UserBadge
from app.db.models.xp_event import XpEvent
from app.gamification.constants import (
    BADGE_DEFINITIONS,
    DAILY_CAP_EVENTS,
    LEVEL_BADGE_MAP,
    LEVEL_THRESHOLDS,
    MAX_LEVEL,
    XP_VALUES,
)
from app.gamification.schemas import (
    BadgeResponse,
    GamificationStatusResponse,
)

logger = logging.getLogger(__name__)


# ── レベル計算 ────────────────────────────────────────────────────

def calc_level(xp: int) -> int:
    """XP からレベルを計算する。LEVEL_THRESHOLDS の変更だけで調整可能。"""
    level = 1
    for lv, min_xp, _ in LEVEL_THRESHOLDS:
        if xp >= min_xp:
            level = lv
        else:
            break
    return level


def get_level_info(level: int) -> tuple[int, int, str, Optional[int]]:
    """
    Returns: (min_xp_current, min_xp_next_or_none, title, next_level_or_none)
    """
    current_min = 0
    current_title = "見習い副業家"
    next_min: Optional[int] = None

    for i, (lv, min_xp, title) in enumerate(LEVEL_THRESHOLDS):
        if lv == level:
            current_min = min_xp
            current_title = title
            if i + 1 < len(LEVEL_THRESHOLDS):
                next_min = LEVEL_THRESHOLDS[i + 1][1]
            break
    return current_min, next_min, current_title, (None if next_min is None else level + 1)


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
        ref_id=ref_id,
    )
    db.add(log)

    # ── User の xp / level を更新 ─────────────────────────────────
    user = db.get(User, user_id)
    if not user:
        db.rollback()
        return 0, []

    old_level = user.level or 1
    user.xp = (user.xp or 0) + xp_amount
    user.level = calc_level(user.xp)
    db.commit()

    # ── バッジ判定 (コミット後) ───────────────────────────────────
    new_badges = _check_and_award_badges(db, user, old_level, event_type)
    return xp_amount, new_badges


# ── バッジ判定 ────────────────────────────────────────────────────

def _check_and_award_badges(
    db: Session,
    user: User,
    old_level: int,
    event_type: str,
) -> list[str]:
    earned: list[str] = []

    # 初公開投稿バッジ
    if event_type == "post_public":
        if _try_award_badge(db, user.id, "first_post"):
            earned.append("first_post")

    # レベル到達バッジ (Phase 7 実装: level 2, 5, 10)
    current_level = user.level or 1
    for target_level, badge_key in LEVEL_BADGE_MAP.items():
        if current_level >= target_level > old_level:
            if _try_award_badge(db, user.id, badge_key):
                earned.append(badge_key)

    return earned


def _try_award_badge(db: Session, user_id: int, badge_key: str) -> bool:
    """バッジを付与する。既に持っていれば False を返す。"""
    if badge_key not in BADGE_DEFINITIONS:
        return False
    # 重複チェック (UNIQUE 制約でも防ぐが事前チェックで例外を避ける)
    exists = db.execute(
        select(UserBadge.id).where(
            UserBadge.user_id == user_id,
            UserBadge.badge_key == badge_key,
        ).limit(1)
    ).first()
    if exists:
        return False
    db.add(UserBadge(user_id=user_id, badge_key=badge_key))
    db.commit()
    return True


# ── ステータス取得 ────────────────────────────────────────────────

def get_status(db: Session, user_id: int) -> GamificationStatusResponse:
    """ユーザーの現在の XP / レベル / バッジ状況を返す。"""
    user = db.get(User, user_id)
    xp    = user.xp    if user and user.xp    is not None else 0
    level = user.level if user and user.level is not None else 1

    current_min, next_min, title, _ = get_level_info(level)

    if next_min is not None:
        xp_to_next   = max(0, next_min - xp)
        range_width  = next_min - current_min or 1
        progress_pct = min(100, int((xp - current_min) / range_width * 100))
    else:
        xp_to_next   = None
        progress_pct = 100  # 最大レベル

    # 獲得バッジ一覧
    rows = db.execute(
        select(UserBadge).where(UserBadge.user_id == user_id)
        .order_by(UserBadge.earned_at)
    ).scalars().all()

    badges = [
        BadgeResponse(
            key=b.badge_key,
            name=BADGE_DEFINITIONS[b.badge_key]["name"],
            icon=BADGE_DEFINITIONS[b.badge_key]["icon"],
            description=BADGE_DEFINITIONS[b.badge_key]["description"],
            earned_at=b.earned_at,
        )
        for b in rows
        if b.badge_key in BADGE_DEFINITIONS
    ]

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
    )
