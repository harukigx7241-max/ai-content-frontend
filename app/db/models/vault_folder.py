"""app/db/models/vault_folder.py — 保管庫フォルダモデル (Phase A)"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class VaultFolder(Base):
    __tablename__ = "vault_folders"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name       = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
