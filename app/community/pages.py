"""
app/community/pages.py — 公開広場 HTML ページルーター

ルート:
  GET /square          — 一覧ページ (未ログインでも閲覧可)
  GET /square/new      — 投稿作成ページ (要ログイン)
  GET /square/{post_id} — 詳細ページ (公開投稿は未ログインでも閲覧可)

NOTE: /square/new を /square/{post_id} より先に定義すること (FastAPI ルート解決順)
"""
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user_soft
from app.community import service as community_service
from app.core.templates import templates
from app.db.models.user import User
from app.db.session import get_db

router = APIRouter(tags=["community-pages"])


@router.get("/square")
def square_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_soft),
):
    """公開広場 一覧ページ。未ログインでも閲覧可能。"""
    return templates.TemplateResponse(
        request=request,
        name="square.html",
        context={"user": current_user},
    )


@router.get("/square/new")
def square_new_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_soft),
):
    """投稿作成ページ。未ログインは /login にリダイレクト。"""
    if not current_user:
        return RedirectResponse("/login?next=/square/new", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="square_new.html",
        context={"user": current_user},
    )


@router.get("/square/{post_id}")
def square_detail_page(
    post_id: int,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_soft),
    db: Session = Depends(get_db),
):
    """投稿詳細ページ。公開投稿は未ログインでも閲覧可能。"""
    post = community_service.get_post(db, post_id, current_user.id if current_user else None)
    community_service.increment_view(db, post_id)
    return templates.TemplateResponse(
        request=request,
        name="square_detail.html",
        context={"user": current_user, "post": post},
    )
