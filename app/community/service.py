"""
app/community/service.py — 公開広場 サービス層

責務:
  - 投稿の CRUD (create / read / update / delete)
  - 一覧取得 (公開のみ, ページネーション + キーワード/カテゴリ絞り込み)
  - 自分の投稿一覧取得 (public + private)
  - 詳細取得 (公開 or 本人の非公開)
  - 閲覧数インクリメント (view_count)
  - コピーアクション受け皿 (将来 use_count++)

将来拡張:
  TODO: Phase N+ like / save / comment のサービス関数
  TODO: Phase N+ use_count のインクリメント + CopyLog テーブル
  TODO: Phase N+ moderation_status によるフィルタリング
  TODO: Phase N+ ランキング (view_count / like_count 降順ソート)
  TODO: Phase N+ 管理者おすすめラベルによるフィルタリング
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.community.schemas import PostCreateRequest, PostUpdateRequest
from app.db.models.post import CommunityPost
from app.db.models.user import User


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _to_summary_dict(post: CommunityPost, author_name: str, is_own: bool) -> dict:
    return {
        "id":              post.id,
        "user_id":         post.user_id,
        "author_name":     author_name,
        "title":           post.title,
        "description":     post.description,
        "category":        post.category,
        "purpose":         post.purpose,
        "target_platform": post.target_platform,
        "tags":            post.tags,
        "visibility":      post.visibility,
        "view_count":      post.view_count,
        "created_at":      post.created_at,
        "is_own":          is_own,
    }


def _to_detail_dict(post: CommunityPost, author_name: str, is_own: bool) -> dict:
    d = _to_summary_dict(post, author_name, is_own)
    d["prompt_body"] = post.prompt_body
    d["updated_at"]  = post.updated_at
    return d


# ── 投稿作成 ─────────────────────────────────────────────────────

def create_post(db: Session, user_id: int, data: PostCreateRequest) -> dict:
    post = CommunityPost(
        user_id=user_id,
        title=data.title,
        description=data.description,
        prompt_body=data.prompt_body,
        category=data.category,
        purpose=data.purpose,
        target_platform=data.target_platform,
        tags=data.tags,
        visibility=data.visibility,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    author = db.get(User, user_id)
    return _to_detail_dict(post, author.display_name if author else "不明", is_own=True)


# ── 公開投稿一覧 ──────────────────────────────────────────────────

def list_posts(
    db: Session,
    q: Optional[str],
    category: Optional[str],
    purpose: Optional[str],
    target_platform: Optional[str],
    page: int,
    per_page: int,
    current_user_id: Optional[int] = None,
) -> dict:
    """
    公開投稿一覧を返す。
    キーワード検索は title / description / tags に対して LIKE 検索。
    将来: full-text search エンジンへの置き換えポイント (TODO: Phase N+)
    将来: moderation_status == "hidden" のフィルタリング (TODO: Phase N+)
    """
    stmt = (
        select(CommunityPost, User.display_name.label("author_name"))
        .join(User, CommunityPost.user_id == User.id)
        .where(CommunityPost.visibility == "public")
        .order_by(CommunityPost.created_at.desc())
    )
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(
            CommunityPost.title.ilike(like),
            CommunityPost.description.ilike(like),
            CommunityPost.tags.ilike(like),
        ))
    if category:
        stmt = stmt.where(CommunityPost.category == category)
    if purpose:
        stmt = stmt.where(CommunityPost.purpose == purpose)
    if target_platform:
        stmt = stmt.where(CommunityPost.target_platform == target_platform)

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar() or 0
    rows = db.execute(stmt.offset((page - 1) * per_page).limit(per_page)).all()

    posts = [
        _to_summary_dict(post, author_name, is_own=(post.user_id == current_user_id))
        for post, author_name in rows
    ]
    return {
        "posts":    posts,
        "total":    total,
        "page":     page,
        "per_page": per_page,
        "has_next": (page * per_page) < total,
    }


# ── 自分の投稿一覧 ────────────────────────────────────────────────

def list_my_posts(db: Session, user_id: int, page: int, per_page: int) -> dict:
    """自分の投稿一覧 (public + private 両方)。"""
    stmt = (
        select(CommunityPost, User.display_name.label("author_name"))
        .join(User, CommunityPost.user_id == User.id)
        .where(CommunityPost.user_id == user_id)
        .order_by(CommunityPost.created_at.desc())
    )
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar() or 0
    rows = db.execute(stmt.offset((page - 1) * per_page).limit(per_page)).all()
    posts = [
        _to_summary_dict(post, author_name, is_own=True)
        for post, author_name in rows
    ]
    return {
        "posts":    posts,
        "total":    total,
        "page":     page,
        "per_page": per_page,
        "has_next": (page * per_page) < total,
    }


# ── 詳細取得 ──────────────────────────────────────────────────────

def get_post(db: Session, post_id: int, current_user_id: Optional[int] = None) -> dict:
    """
    投稿詳細を返す。
    public → 誰でも閲覧可。
    private → 本人のみ閲覧可 (他人には 404 を返す — 存在自体を隠す)。
    """
    post = db.get(CommunityPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    if post.visibility == "private" and post.user_id != current_user_id:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    author = db.get(User, post.user_id)
    return _to_detail_dict(
        post,
        author.display_name if author else "不明",
        is_own=(post.user_id == current_user_id),
    )


# ── 更新 ─────────────────────────────────────────────────────────

def update_post(db: Session, post_id: int, user_id: int, data: PostUpdateRequest) -> dict:
    """投稿を更新する。本人のみ可。PATCH セマンティクス。"""
    post = db.get(CommunityPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="この投稿を編集する権限がありません")

    if data.title is not None:
        post.title = data.title
    if data.description is not None:
        post.description = data.description or None
    if data.prompt_body is not None:
        post.prompt_body = data.prompt_body
    if data.category is not None:
        post.category = data.category
    if data.purpose is not None:
        post.purpose = data.purpose or None
    if data.target_platform is not None:
        post.target_platform = data.target_platform or None
    if data.tags is not None:
        post.tags = data.tags or None
    if data.visibility is not None:
        post.visibility = data.visibility

    post.updated_at = _now()
    db.commit()
    db.refresh(post)
    author = db.get(User, user_id)
    return _to_detail_dict(post, author.display_name if author else "不明", is_own=True)


# ── 削除 ─────────────────────────────────────────────────────────

def delete_post(db: Session, post_id: int, user_id: int) -> None:
    """投稿を削除する。本人のみ可。"""
    post = db.get(CommunityPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="この投稿を削除する権限がありません")
    db.delete(post)
    db.commit()


# ── 閲覧数インクリメント ──────────────────────────────────────────

def increment_view(db: Session, post_id: int) -> None:
    """
    閲覧数を +1 する。存在しない / 非公開の場合は静かに無視。
    将来: ユニーク閲覧数のカウントや Redis キャッシュへの移行ポイント (TODO: Phase N+)
    """
    post = db.get(CommunityPost, post_id)
    if post and post.visibility == "public":
        post.view_count = (post.view_count or 0) + 1
        db.commit()


# ── コピーアクション受け皿 ────────────────────────────────────────

def record_copy(db: Session, post_id: int) -> Optional[int]:
    """
    コピーアクションの受け皿。投稿作者の user_id を返す (XP 付与などに利用)。
    存在しない / 非公開の投稿は None を返す。
    TODO: Phase N+ use_count インクリメント
    TODO: Phase N+ CopyLog テーブルへのイベント記録 (ユーザー・日時)
    """
    post = db.get(CommunityPost, post_id)
    if post and post.visibility == "public":
        return post.user_id
    return None
