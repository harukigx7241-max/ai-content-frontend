"""app/db/models/saved_prompt.py — プロンプト保管庫 DB モデル (Phase A 拡張)"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SavedPrompt(Base):
    __tablename__ = "saved_prompts"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title       = Column(String(100), nullable=False, default="保管庫アイテム")
    content     = Column(Text, nullable=False)
    source      = Column(String(20), nullable=False, default="forge")  # forge|square|template|remix|fork
    is_favorite = Column(Boolean, nullable=False, default=False)
    tags        = Column(String(200), nullable=True, default="")  # カンマ区切り
    # Phase A 追加フィールド
    folder_id   = Column(Integer, ForeignKey("vault_folders.id"), nullable=True, index=True)
    summary     = Column(Text, nullable=True)                           # 短いメモ
    status      = Column(String(20), nullable=False, default="draft")  # draft|completed|archived
    created_at  = Column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at  = Column(DateTime(timezone=True), nullable=True)       # 編集時に更新
