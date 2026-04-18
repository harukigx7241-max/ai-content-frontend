"""
app/routers/pages.py — 会員向け HTML ページルーター
認証が必要なページはサーバーサイドでチェックし、未ログイン時は /login にリダイレクト。
既存の / (index) は system.py が担当し、このルーターは会員ページのみ扱う。
Phase 16: /plans ページ追加
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


@router.get("/plans")
def plans_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_soft),
):
    """プラン比較・アップグレードページ。未ログインでも閲覧可能。"""
    from app.services.subscription_service import subscription_service, get_plan_for_role
    from app.core.roles import RoleValue
    from app.core.config import settings

    user_plan_id = "free"
    if current_user:
        user_plan_id = get_plan_for_role(current_user.role)

    plans_result = subscription_service.get_plans()
    return templates.TemplateResponse(
        request=request,
        name="plans.html",
        context={
            "user": current_user,
            "plans": plans_result.content.get("plans", []),
            "billing_enabled": settings.ENABLE_BILLING,
            "trial_days": settings.BILLING_TRIAL_DAYS,
            "user_plan_id": user_plan_id,
        },
    )


@router.get("/hq")
def hq_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_soft),
):
    """管理本部司令室。未ログインは /login へ。headquarters 以外は /admin へ。"""
    if not current_user:
        return RedirectResponse("/login?next=/hq", status_code=302)
    from app.core.roles import HQ_ROLES
    if current_user.role not in HQ_ROLES:
        return RedirectResponse("/admin", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="hq/dashboard.html",
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
