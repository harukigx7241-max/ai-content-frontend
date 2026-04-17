"""
app/routers/subscription.py — プラン・サブスクリプション公開 API (Phase 16)
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.auth.dependencies import get_current_user_soft, get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/api/plans", tags=["subscription"])


@router.get("")
def get_plans():
    """全プラン定義を返す (認証不要・公開 API)。"""
    from app.services.subscription_service import subscription_service
    result = subscription_service.get_plans()
    return JSONResponse(result.content or {})


@router.get("/me")
def get_my_plan(
    current_user: Optional[User] = Depends(get_current_user_soft),
):
    """ログイン中ユーザーのプラン情報を返す。未ログインはゲスト扱い。"""
    from app.services.subscription_service import subscription_service
    result = subscription_service.get_user_plan_info(current_user)
    return JSONResponse(result.content or {})


class CheckoutRequest(BaseModel):
    plan_id: str
    billing_cycle: str = "monthly"
    success_url: str = ""
    cancel_url: str = ""


@router.post("/checkout")
def create_checkout(
    body: CheckoutRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Stripe Checkout セッションを作成してリダイレクト URL を返す。
    ENABLE_BILLING=false の間は「準備中」メッセージを返す。
    """
    from app.services.subscription_service import subscription_service, PLANS
    if body.plan_id not in PLANS:
        raise HTTPException(status_code=400, detail=f"Unknown plan: {body.plan_id}")

    result = subscription_service.create_checkout_session(
        user_id=current_user.id,
        plan_id=body.plan_id,
        billing_cycle=body.billing_cycle,
        success_url=body.success_url,
        cancel_url=body.cancel_url,
    )
    return JSONResponse(result.content or {})
