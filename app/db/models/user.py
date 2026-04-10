"""
app/db/models/user.py — User SQLAlchemy モデル

カラム設計方針:
  - sns_platform + sns_handle の複合ユニーク制約で SNS アカウント一意性を保証
  - email は NULL 許可 — TODO: Phase 3+ メール認証追加時に使用
  - role は "user" / "admin" で管理者判定。TODO: Phase 3+ モデレーター等に拡張
  - status は "pending" / "approved" / "rejected" / "suspended" の4値
  - approved_by は承認した管理者の user.id (監査ログ用。外部キー制約は意図的に省略)
  - TODO: Phase 5+ invite_code_id カラム追加
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sns_platform = Column(String(50), nullable=False)
    sns_handle = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    profile_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)  # Phase 4: 自己紹介文（500字以内）
    email = Column(String(200), nullable=True, unique=True)  # TODO: Phase 3+ メール認証

    password_hash = Column(String(256), nullable=False)

    # ステータス: pending → approved (or rejected) → suspended
    status = Column(String(20), nullable=False, default="pending")
    # ロール: user / admin (TODO: Phase 3+ moderator等)
    role = Column(String(20), nullable=False, default="user")

    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Integer, nullable=True)  # 承認した管理者の user.id

    # Phase 7: ゲーミフィケーション (既存 DB には ALTER TABLE で追加)
    xp    = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)

    # Phase 8: 招待元ユーザー追跡 (既存 DB には ALTER TABLE で追加)
    invited_by_user_id = Column(Integer, nullable=True)  # 招待した User.id

    __table_args__ = (
        UniqueConstraint("sns_platform", "sns_handle", name="uq_sns_platform_handle"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} {self.sns_platform}:{self.sns_handle} status={self.status}>"
