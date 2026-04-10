"""app/db/models/feedback.py — 要望・フィードバック + 監査ログ (Phase 9)"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Feedback(Base):
    """ユーザーからの要望・バグ報告・その他フィードバック。未ログインでも送信可。"""
    __tablename__ = "feedback"

    id         = Column(Integer,     primary_key=True, autoincrement=True)
    user_id    = Column(Integer,     nullable=True, index=True)  # nullable: 未ログインユーザー対応
    category   = Column(String(50),  nullable=False, default="general")  # "feature"|"bug"|"other"|"general"
    title      = Column(String(200), nullable=False)
    body       = Column(Text,        nullable=True)
    status     = Column(String(20),  nullable=False, default="open")  # "open"|"acknowledged"|"closed"
    admin_note = Column(Text,        nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at = Column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    """
    Phase 9: 監査ログ受け皿 — 管理者操作の履歴を記録する。
    現時点では receptacle のみ。検索・一覧 API は Phase N+ で追加する。
    """
    __tablename__ = "audit_logs"

    id            = Column(Integer,      primary_key=True, autoincrement=True)
    admin_user_id = Column(Integer,      nullable=True, index=True)
    action        = Column(String(100),  nullable=False)   # "approve_user", "reject_user" など
    target_type   = Column(String(50),   nullable=True)    # "user", "feedback", "settings"
    target_id     = Column(Integer,      nullable=True)
    detail        = Column(Text,         nullable=True)    # JSON 文字列: 追加コンテキスト
    created_at    = Column(DateTime(timezone=True), nullable=False, default=_now, index=True)
