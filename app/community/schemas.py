"""
app/community/schemas.py — 公開広場 Pydantic スキーマ

スキーマ一覧:
  PostCreateRequest  — 投稿作成バリデーション
  PostUpdateRequest  — PATCH セマンティクス (None フィールドはスキップ)
  PostSummaryResponse — 一覧用 (prompt_body 省略)
  PostResponse       — 詳細用 (prompt_body 含む)
  PostListResponse   — ページネーション付き一覧

将来拡張:
  TODO: Phase N+ LikeResponse / SaveResponse / CommentResponse
  TODO: Phase N+ RankingResponse (view_count / like_count 降順)
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# ── 許容値定数 ────────────────────────────────────────────────────
CATEGORIES = {"note", "sns", "cw", "fortune", "image", "other"}
PURPOSES = {"article", "sales", "proposal", "profile", "post", "research", "image"}
TARGET_PLATFORMS = {"note", "x", "threads", "instagram", "brain", "tips", "blog", "generic"}
VISIBILITIES = {"public", "private"}


def _clean_tags(v: Optional[str]) -> Optional[str]:
    """タグを正規化: 前後空白除去・空タグ除去・最大10タグ・200文字上限。"""
    if not v or not v.strip():
        return None
    tags = [t.strip() for t in v.split(",") if t.strip()]
    return ",".join(tags[:10])[:200] or None


# ── リクエスト ────────────────────────────────────────────────────

class PostCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    prompt_body: str = Field(..., min_length=1, max_length=10000)
    category: str = Field(default="other", max_length=50)
    purpose: Optional[str] = Field(None, max_length=50)
    target_platform: Optional[str] = Field(None, max_length=50)
    tags: Optional[str] = Field(None, max_length=200)
    visibility: str = Field(default="public")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        return v if v in CATEGORIES else "other"

    @field_validator("purpose")
    @classmethod
    def validate_purpose(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return v if v in PURPOSES else None

    @field_validator("target_platform")
    @classmethod
    def validate_platform(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return v if v in TARGET_PLATFORMS else None

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v: str) -> str:
        if v not in VISIBILITIES:
            raise ValueError("visibility は public または private のみ有効です")
        return v

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, v: Optional[str]) -> Optional[str]:
        return _clean_tags(v)


class PostUpdateRequest(BaseModel):
    """PATCH セマンティクス: None フィールドはスキップ。"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    prompt_body: Optional[str] = Field(None, min_length=1, max_length=10000)
    category: Optional[str] = Field(None, max_length=50)
    purpose: Optional[str] = Field(None, max_length=50)
    target_platform: Optional[str] = Field(None, max_length=50)
    tags: Optional[str] = Field(None, max_length=200)
    visibility: Optional[str] = None

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if v not in VISIBILITIES:
            raise ValueError("visibility は public または private のみ有効です")
        return v

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None  # None = 変更しない
        return _clean_tags(v)  # 空文字列は None に変換 (削除)


# ── レスポンス ────────────────────────────────────────────────────

class PostSummaryResponse(BaseModel):
    """一覧用レスポンス: prompt_body は省略し軽量に。"""
    id: int
    user_id: int
    author_name: str
    title: str
    description: Optional[str] = None
    category: str
    purpose: Optional[str] = None
    target_platform: Optional[str] = None
    tags: Optional[str] = None
    visibility: str
    view_count: int = 0
    created_at: datetime
    is_own: bool = False
    # TODO: Phase N+ like_count: int = 0
    # TODO: Phase N+ save_count: int = 0

    model_config = {"from_attributes": True}


class PostResponse(PostSummaryResponse):
    """詳細用レスポンス: prompt_body と updated_at を追加。"""
    prompt_body: str
    updated_at: Optional[datetime] = None
    # TODO: Phase N+ comments: list[CommentResponse] = []


class PostListResponse(BaseModel):
    posts: list[PostSummaryResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
