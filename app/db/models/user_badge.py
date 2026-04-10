"""
app/db/models/user_badge.py — ユーザーが獲得したバッジ

設計方針:
  - badge_key は gamification/constants.py の BADGE_DEFINITIONS と対応
  - (user_id, badge_key) に UNIQUE 制約で同じバッジの重複取得を防止
  - 将来バッジの「表示/非表示」設定や順序を追加しやすい構造 (TODO: Phase N+)
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)   # User.id (FK 制約省略)
    badge_key = Column(String(50), nullable=False)           # "first_post", "level_5", ...
    earned_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    # TODO: Phase N+ display_order = Column(Integer, nullable=True)
    # TODO: Phase N+ is_pinned = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("user_id", "badge_key", name="uq_user_badge"),
    )

    def __repr__(self) -> str:
        return f"<UserBadge user_id={self.user_id} badge={self.badge_key!r}>"
