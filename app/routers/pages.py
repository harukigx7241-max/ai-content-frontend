"""
app/routers/pages.py — 会員向け HTML ページルーター
認証が必要なページはサーバーサイドでチェックし、未ログイン時は /login にリダイレクト。
既存の / (index) は system.py が担当し、このルーターは会員ページのみ扱う。

TODO: Phase 4+ mypage にプロンプト履歴・お気に入りを追加
TODO: Phase 5+ mypage に XP / レベル を追加
"""
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.auth.dependencies import get_current_user_soft
from app.core.templates import templates
from app.db.models.user import User

router = APIRouter(tags=["pages"])


@router.get("/login")
def login_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_soft),
):
    """ログインページ。ログイン済みなら /mypage にリダイレクト。"""
    if current_user:
        return RedirectResponse("/mypage", status_code=302)
    return templates.TemplateResponse(request=request, name="auth/login.html", context={})


@router.get("/register")
def register_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_soft),
):
    """新規登録ページ。ログイン済みなら /mypage にリダイレクト。"""
    if current_user:
        return RedirectResponse("/mypage", status_code=302)
    return templates.TemplateResponse(request=request, name="auth/register.html", context={})


@router.get("/mypage")
def mypage(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_soft),
):
    """マイページ。未ログインなら /login にリダイレクト。"""
    if not current_user:
        return RedirectResponse("/login?next=/mypage", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="mypage.html",
        context={"user": current_user},
    )


@router.get("/admin")
def admin_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_soft),
):
    """管理者ダッシュボード。未ログインは /login へ。管理者以外は / へ。"""
    if not current_user:
        return RedirectResponse("/login?next=/admin", status_code=302)
    from app.core.roles import ADMIN_ROLES, HQ_ROLES
    if current_user.role not in ADMIN_ROLES:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "user": current_user,
            "is_hq": current_user.role in HQ_ROLES,
        },
    )
