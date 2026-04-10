"""
app/db/models/post.py — CommunityPost (公開広場 投稿) SQLAlchemy モデル

設計方針:
  - user_id で User と紐づく (外部キー制約は intentionally 省略 — SQLite migration 容易性)
  - visibility: "public" | "private" (モデル default="private" で安全側に)
  - view_count のみ Phase 5 で実装済み。以下は将来拡張用 (TODO: Phase N+):
      like_count, save_count, use_count, comment_count, moderation_status
  - tags はカンマ区切り文字列 (将来は別テーブルへ正規化可能)
  - category / purpose / target_platform は文字列カラム (Enum 化は Phase N+)
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CommunityPost(Base):
    __tablename__ = "community_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)  # User.id (FK制約省略)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    prompt_body = Column(Text, nullable=False)

    # ── 分類 ──────────────────────────────────────────────────────────
    # category: "note" | "sns" | "cw" | "fortune" | "image" | "other"
    category = Column(String(50), nullable=False, default="other")
    # purpose: "article" | "sales" | "proposal" | "profile" | "post" | "research" | "image"
    purpose = Column(String(50), nullable=True)
    # target_platform: "note" | "x" | "threads" | "instagram" | "brain" | "tips" | "blog" | "generic"
    target_platform = Column(String(50), nullable=True)
    # tags: カンマ区切り文字列 (最大200文字, 最大10タグ)
    tags = Column(String(200), nullable=True)

    # ── 公開設定 ──────────────────────────────────────────────────────
    visibility = Column(String(20), nullable=False, default="private")
    # "public" | "private"

    # ── カウンター (Phase 5 実装済み) ────────────────────────────────
    view_count = Column(Integer, nullable=False, default=0)

    # TODO: Phase N+ like_count = Column(Integer, nullable=False, default=0)
    # TODO: Phase N+ save_count = Column(Integer, nullable=False, default=0)
    # TODO: Phase N+ use_count = Column(Integer, nullable=False, default=0)
    # TODO: Phase N+ comment_count = Column(Integer, nullable=False, default=0)

    # ── モデレーション (TODO: Phase N+) ─────────────────────────────
    # moderation_status: None="未審査", "ok", "flagged"(通報あり), "hidden"(非表示)
    # moderation_status = Column(String(20), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<CommunityPost id={self.id} user_id={self.user_id} "
            f"visibility={self.visibility!r}>"
        )
