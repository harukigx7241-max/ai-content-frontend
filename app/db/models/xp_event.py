"""
app/db/models/xp_event.py — XP イベントログテーブル

設計方針:
  - XP の付与履歴を全てログとして残す (監査・デバッグ・二重付与防止に使用)
  - event_type は gamification/constants.py の XPEvent 定数と対応
  - ref_id は投稿 ID など関連エンティティの ID (nullable)
  - 将来のランキング・期間集計もこのテーブルを使う想定 (TODO: Phase N+)
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class XpEvent(Base):
    __tablename__ = "xp_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)   # User.id (FK 制約省略)
    event_type = Column(String(50), nullable=False, index=True)  # "login", "post_public", ...
    xp_delta = Column(Integer, nullable=False)               # 付与した XP (正値)
    ref_id = Column(Integer, nullable=True)                  # 関連エンティティ ID (任意)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now, index=True)

    def __repr__(self) -> str:
        return (
            f"<XpEvent id={self.id} user_id={self.user_id} "
            f"event={self.event_type!r} xp={self.xp_delta}>"
        )
