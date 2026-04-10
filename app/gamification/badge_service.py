"""
app/gamification/badge_service.py — バッジ付与・チェック

責務:
  - check_and_award_badges() : イベント発生後にバッジを判定・付与
  - try_award_badge()        : 単一バッジを安全に付与 (重複不可)
  - get_user_badges()        : ユーザーの獲得バッジ一覧を返す

設計方針:
  - バッジは一度しか獲得できない (UniqueConstraint でも保護)
  - 各バッジの判定ロジックはここに集約する
  - イベント種別で早期 return してクエリを最小限にする

将来拡張:
  TODO: Phase N+ streak_7 (7日間連続ログイン)
  TODO: Phase N+ shared_10 (投稿が10回コピーされた)
  TODO: Phase N+ invite_3 (3人招待)
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.user_badge import UserBadge
from app.db.models.xp_event import XpEvent
from app.gamification.constants import BADGE_DEFINITIONS, XPEvent as XPEventConst


def check_and_award_badges(
    db: Session,
    user: User,
    old_level: int,
    event_type: str,
) -> list[str]:
    """
    イベント発生後にバッジを判定し、新規取得バッジのキーリストを返す。
    呼び出し元は try_award 内でコミット済みの状態で呼ぶこと。
    """
    earned: list[str] = []

    # 初公開投稿バッジ
    if event_type == XPEventConst.POST_PUBLIC:
        if try_award_badge(db, user.id, "first_post"):
            earned.append("first_post")

    # 100回生成バッジ (generate イベント累計が100件以上になった瞬間に付与)
    if event_type == XPEventConst.GENERATE:
        count = db.execute(
            select(func.count()).where(
                XpEvent.user_id == user.id,
                XpEvent.event_type == XPEventConst.GENERATE,
            )
        ).scalar() or 0
        if count >= 100:
            if try_award_badge(db, user.id, "gen_100"):
                earned.append("gen_100")

    # 初いいね獲得バッジ
    if event_type == XPEventConst.POST_LIKED:
        if try_award_badge(db, user.id, "first_liked"):
            earned.append("first_liked")

    # 初保存獲得バッジ
    if event_type == XPEventConst.POST_SAVED:
        if try_award_badge(db, user.id, "first_saved"):
            earned.append("first_saved")

    # 初使用達成バッジ
    if event_type == XPEventConst.POST_USED:
        if try_award_badge(db, user.id, "first_used"):
            earned.append("first_used")

    return earned


def try_award_badge(db: Session, user_id: int, badge_key: str) -> bool:
    """
    バッジを付与する。既に持っていれば False を返す。
    UNIQUE 制約でも保護されているが、事前チェックで不要な例外を避ける。
    """
    if badge_key not in BADGE_DEFINITIONS:
        return False
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


def get_user_badges(db: Session, user_id: int) -> list[UserBadge]:
    """ユーザーの獲得バッジ一覧を取得日時昇順で返す。"""
    return db.execute(
        select(UserBadge)
        .where(UserBadge.user_id == user_id)
        .order_by(UserBadge.earned_at)
    ).scalars().all()
