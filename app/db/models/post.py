"""
app/db/models/post.py — CommunityPost (公開広場 投稿) + PostReaction SQLAlchemy モデル

設計方針:
  - user_id で User と紐づく (外部キー制約は intentionally 省略 — SQLite migration 容易性)
  - visibility: "public" | "private" (モデル default="private" で安全側に)
  - PostReaction: post_id + user_id + reaction_type の UNIQUE 制約でトグル実装
  - tags はカンマ区切り文字列 (将来は別テーブルへ正規化可能)
  - category / purpose / target_platform は文字列カラム (Enum 化は Phase N+)
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint

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

    # ── カウンター ───────────────────────────────────────────────────
    view_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)
    save_count = Column(Integer, nullable=False, default=0)
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


class PostReaction(Base):
    """
    いいね / 保存 リアクションテーブル。

    制約: (post_id, user_id, reaction_type) の組み合わせは UNIQUE。
    これにより 1ユーザー × 1投稿 × 1種別 で 1 レコードのみ保持される。
    削除でトグル OFF を表現する。
    """
    __tablename__ = "post_reactions"
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", "reaction_type", name="uq_post_user_reaction"),
    )

    id            = Column(Integer, primary_key=True, autoincrement=True)
    post_id       = Column(Integer, nullable=False, index=True)
    user_id       = Column(Integer, nullable=False, index=True)
    reaction_type = Column(String(20), nullable=False)  # "like" | "save"
    created_at    = Column(DateTime(timezone=True), nullable=False, default=_now)

    def __repr__(self) -> str:
        return (
            f"<PostReaction post_id={self.post_id} user_id={self.user_id} "
            f"type={self.reaction_type!r}>"
        )
