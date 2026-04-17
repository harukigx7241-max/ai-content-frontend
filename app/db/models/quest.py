"""
app/db/models/quest.py — クエスト / デイリータスク スキャフォールド

Phase 10: テーブル定義のみ。サービスロジックは Phase 18+ で実装予定。

テーブル構成:
  daily_tasks   — 1日ごとのミッション進捗 (ログイン/生成/投稿/いいね)
  quest_progresses — 長期クエストの進捗 (スキャフォールド)
"""
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DailyTask(Base):
    """デイリーミッション進捗テーブル。"""
    __tablename__ = "daily_tasks"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False, index=True)
    task_type  = Column(String(50), nullable=False)  # "login"|"generate"|"post"|"like_received"
    task_date  = Column(Date, nullable=False, index=True)
    completed  = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    def __repr__(self) -> str:
        return (
            f"<DailyTask id={self.id} user={self.user_id} "
            f"type={self.task_type!r} date={self.task_date} done={self.completed}>"
        )


class QuestProgress(Base):
    """長期クエスト進捗テーブル (スキャフォールド)。"""
    __tablename__ = "quest_progresses"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False, index=True)
    quest_key  = Column(String(100), nullable=False)  # quest identifier
    progress   = Column(Integer, nullable=False, default=0)
    target     = Column(Integer, nullable=False, default=1)
    completed  = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    def __repr__(self) -> str:
        return (
            f"<QuestProgress id={self.id} user={self.user_id} "
            f"quest={self.quest_key!r} {self.progress}/{self.target}>"
        )
