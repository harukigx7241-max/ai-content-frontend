"""
app/community/service.py — 公開広場 サービス層

責務:
  - 投稿の CRUD (create / read / update / delete)
  - 一覧取得 (公開のみ, ページネーション + キーワード/カテゴリ絞り込み)
  - 自分の投稿一覧取得 (public + private)
  - 詳細取得 (公開 or 本人の非公開)
  - 閲覧数インクリメント (view_count)
  - コピーアクション受け皿 (将来 use_count++)
  - いいね / 保存 トグル (toggle_reaction)
  - フォーク (fork_post) — Phase 9

sort 対応 (Phase 9):
  new      — 新着順 (created_at DESC)
  popular  — いいね数降順 (like_count DESC)
  saves    — 保存数降順 (save_count DESC)
  trending — 注目順 (like×2 + save×1.5 + view×0.1 複合スコア)

popularity_tier (Phase 9):
  common / uncommon / rare / epic / legendary
  総合スコア = like×2 + save×1.5 + view×0.1 を元に 5 段階

将来拡張:
  TODO: Phase N+ use_count のインクリメント + CopyLog テーブル
  TODO: Phase N+ moderation_status によるフィルタリング
  TODO: Phase N+ 管理者おすすめラベルによるフィルタリング
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from app.community.schemas import PostCreateRequest, PostUpdateRequest
from app.db.models.post import CommunityPost, PostReaction
from app.db.models.user import User


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _popularity_tier(like: int, save: int, view: int) -> str:
    """総合スコアから 5 段階のレア度ティアを返す。"""
    score = like * 2 + save * 1.5 + view * 0.1
    if score >= 50:
        return "legendary"
    if score >= 20:
        return "epic"
    if score >= 8:
        return "rare"
    if score >= 3:
        return "uncommon"
    return "common"


def _to_summary_dict(
    post: CommunityPost,
    author_name: str,
    is_own: bool,
    user_liked: bool = False,
    user_saved: bool = False,
) -> dict:
    like  = post.like_count  or 0
    save  = post.save_count  or 0
    view  = post.view_count  or 0
    remix = getattr(post, "remix_count", 0) or 0
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
        "view_count":      view,
        "like_count":      like,
        "save_count":      save,
        "remix_count":     remix,
        "forked_from_id":  getattr(post, "forked_from_id", None),
        "popularity_tier": _popularity_tier(like, save, view),
        "user_liked":      user_liked,
        "user_saved":      user_saved,
        "created_at":      post.created_at,
        "is_own":          is_own,
    }


def _to_detail_dict(
    post: CommunityPost,
    author_name: str,
    is_own: bool,
    user_liked: bool = False,
    user_saved: bool = False,
) -> dict:
    d = _to_summary_dict(post, author_name, is_own, user_liked, user_saved)
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
        forked_from_id=getattr(data, "forked_from_id", None),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    author = db.get(User, user_id)
    return _to_detail_dict(post, author.display_name if author else "不明", is_own=True)


# ── フォーク ──────────────────────────────────────────────────────

def fork_post(db: Session, post_id: int, user_id: int) -> dict:
    """
    投稿をフォークする (自分用コピーとして新規作成)。
    元投稿の remix_count を +1 する。
    返り値: 新規作成した投稿の detail_dict。
    """
    original = db.get(CommunityPost, post_id)
    if not original:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    if original.visibility == "private" and original.user_id != user_id:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")

    forked = CommunityPost(
        user_id=user_id,
        title=f"【Fork】{original.title}"[:200],
        description=original.description,
        prompt_body=original.prompt_body,
        category=original.category,
        purpose=original.purpose,
        target_platform=original.target_platform,
        tags=original.tags,
        visibility="private",   # フォーク直後は非公開 (本人が公開設定する)
        forked_from_id=post_id,
    )
    db.add(forked)

    # 元投稿の remix_count +1
    try:
        original.remix_count = (getattr(original, "remix_count", 0) or 0) + 1
    except Exception:
        pass

    db.commit()
    db.refresh(forked)
    author = db.get(User, user_id)
    return _to_detail_dict(forked, author.display_name if author else "不明", is_own=True)


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
    sort: str = "new",
) -> dict:
    """
    公開投稿一覧を返す。

    sort:
      "new"      — 新着順 (created_at DESC)
      "popular"  — いいね数降順 (like_count DESC)
      "saves"    — 保存数降順 (save_count DESC)
      "trending" — 注目順 (like×2 + save×1.5 + view×0.1 複合)

    将来: full-text search エンジンへの置き換えポイント (TODO: Phase N+)
    将来: moderation_status == "hidden" のフィルタリング (TODO: Phase N+)
    """
    if sort == "popular":
        order_col = CommunityPost.like_count.desc()
    elif sort == "saves":
        order_col = CommunityPost.save_count.desc()
    elif sort == "trending":
        order_col = text(
            "(community_posts.like_count * 2 + community_posts.save_count * 1 "
            "+ community_posts.view_count / 10) DESC"
        )
    else:
        order_col = CommunityPost.created_at.desc()

    stmt = (
        select(CommunityPost, User.display_name.label("author_name"))
        .join(User, CommunityPost.user_id == User.id)
        .where(CommunityPost.visibility == "public")
        .order_by(order_col)
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

    # Batch-fetch current user's reactions for this page (1 extra query)
    liked_set: set[int] = set()
    saved_set: set[int] = set()
    if current_user_id and rows:
        post_ids = [post.id for post, _ in rows]
        reactions = db.execute(
            select(PostReaction.post_id, PostReaction.reaction_type)
            .where(PostReaction.post_id.in_(post_ids))
            .where(PostReaction.user_id == current_user_id)
        ).all()
        liked_set = {r.post_id for r in reactions if r.reaction_type == "like"}
        saved_set = {r.post_id for r in reactions if r.reaction_type == "save"}

    posts = [
        _to_summary_dict(
            post, author_name,
            is_own=(post.user_id == current_user_id),
            user_liked=post.id in liked_set,
            user_saved=post.id in saved_set,
        )
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
    ログイン済みの場合は user_liked / user_saved も返す。
    """
    post = db.get(CommunityPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    if post.visibility == "private" and post.user_id != current_user_id:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    author = db.get(User, post.user_id)

    user_liked = user_saved = False
    if current_user_id:
        reactions = db.execute(
            select(PostReaction.reaction_type)
            .where(PostReaction.post_id == post_id)
            .where(PostReaction.user_id == current_user_id)
        ).scalars().all()
        user_liked = "like" in reactions
        user_saved = "save" in reactions

    return _to_detail_dict(
        post,
        author.display_name if author else "不明",
        is_own=(post.user_id == current_user_id),
        user_liked=user_liked,
        user_saved=user_saved,
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
    """閲覧数を +1 する。存在しない / 非公開の場合は静かに無視。"""
    post = db.get(CommunityPost, post_id)
    if post and post.visibility == "public":
        post.view_count = (post.view_count or 0) + 1
        db.commit()


# ── コピーアクション受け皿 ────────────────────────────────────────

def record_copy(db: Session, post_id: int) -> Optional[int]:
    """
    コピーアクションの受け皿。投稿作者の user_id を返す。
    TODO: Phase N+ use_count インクリメント + CopyLog テーブル
    """
    post = db.get(CommunityPost, post_id)
    if post and post.visibility == "public":
        return post.user_id
    return None


# ── いいね / 保存 トグル ──────────────────────────────────────────

def toggle_reaction(
    db: Session,
    post_id: int,
    user_id: int,
    reaction_type: str,
) -> dict:
    """
    いいね / 保存 をトグルする。
    Returns: {"active": bool, "count": int, "author_id": int}
    """
    post = db.get(CommunityPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    if post.visibility == "private" and post.user_id != user_id:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")

    existing = db.execute(
        select(PostReaction)
        .where(PostReaction.post_id == post_id)
        .where(PostReaction.user_id == user_id)
        .where(PostReaction.reaction_type == reaction_type)
    ).scalar_one_or_none()

    if existing:
        db.delete(existing)
        if reaction_type == "like":
            post.like_count = max(0, (post.like_count or 0) - 1)
            count = post.like_count
        else:
            post.save_count = max(0, (post.save_count or 0) - 1)
            count = post.save_count
        db.commit()
        return {"active": False, "count": count, "author_id": post.user_id}
    else:
        reaction = PostReaction(
            post_id=post_id,
            user_id=user_id,
            reaction_type=reaction_type,
            created_at=_now(),
        )
        db.add(reaction)
        if reaction_type == "like":
            post.like_count = (post.like_count or 0) + 1
            count = post.like_count
        else:
            post.save_count = (post.save_count or 0) + 1
            count = post.save_count
        db.commit()
        return {"active": True, "count": count, "author_id": post.user_id}
