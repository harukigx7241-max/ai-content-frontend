"""
app/community/router.py — 公開広場 API ルーター (薄く保つ)

エンドポイント:
  POST   /api/community/posts            — 投稿作成 (要認証)
  GET    /api/community/posts            — 公開投稿一覧 (未認証可)
  GET    /api/community/posts/mine       — 自分の投稿一覧 (要認証)
  GET    /api/community/posts/{id}       — 詳細 (公開 or 本人の非公開)
  PATCH  /api/community/posts/{id}       — 更新 (本人のみ)
  DELETE /api/community/posts/{id}       — 削除 (本人のみ, 204)
  POST   /api/community/posts/{id}/copy  — コピー記録 (受け皿, 将来 use_count++)

重複ルート対応:
  /posts/mine は /posts/{id} より先に定義することで FastAPI が正しく解決する。
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_current_user_soft
from app.community import service as community_service
from app.community.schemas import (
    PostCreateRequest,
    PostListResponse,
    PostResponse,
    PostUpdateRequest,
)
from app.db.models.user import User
from app.db.session import get_db

router = APIRouter(prefix="/api/community", tags=["community"])


@router.post("/posts", response_model=PostResponse, status_code=201)
def create_post(
    data: PostCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """投稿を作成する。認証必須。承認済みユーザーのみ。"""
    post = community_service.create_post(db, current_user.id, data)
    return JSONResponse(
        PostResponse.model_validate(post).model_dump(mode="json"),
        status_code=201,
    )


@router.get("/posts", response_model=PostListResponse)
def list_posts(
    q: Optional[str] = Query(None, max_length=100, description="キーワード検索 (title / description / tags)"),
    category: Optional[str] = Query(None),
    purpose: Optional[str] = Query(None),
    target_platform: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    current_user: Optional[User] = Depends(get_current_user_soft),
    db: Session = Depends(get_db),
):
    """公開投稿一覧。未ログインでも閲覧可能。"""
    return community_service.list_posts(
        db, q, category, purpose, target_platform, page, per_page,
        current_user_id=current_user.id if current_user else None,
    )


# NOTE: /posts/mine は /posts/{post_id} より先に定義すること (FastAPI ルート解決順)
@router.get("/posts/mine", response_model=PostListResponse)
def list_my_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """自分の投稿一覧 (public + private)。認証必須。"""
    return community_service.list_my_posts(db, current_user.id, page, per_page)


@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    current_user: Optional[User] = Depends(get_current_user_soft),
    db: Session = Depends(get_db),
):
    """投稿詳細。public は誰でも可。private は本人のみ (他人には 404)。"""
    post = community_service.get_post(db, post_id, current_user.id if current_user else None)
    community_service.increment_view(db, post_id)
    return post


@router.patch("/posts/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    data: PostUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """投稿を更新する。本人のみ。PATCH セマンティクス。"""
    post = community_service.update_post(db, post_id, current_user.id, data)
    return JSONResponse(PostResponse.model_validate(post).model_dump(mode="json"))


@router.delete("/posts/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """投稿を削除する。本人のみ。204 No Content を返す。"""
    community_service.delete_post(db, post_id, current_user.id)
    return Response(status_code=204)


@router.post("/posts/{post_id}/copy", status_code=200)
def copy_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    """
    コピーアクションの受け皿。現在は OK を返すのみ。
    TODO: Phase N+ use_count インクリメント + ログ記録
    """
    community_service.record_copy(db, post_id)
    return {"ok": True}
