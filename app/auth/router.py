"""
app/auth/router.py — /api/auth/* エンドポイント (薄いルーター)
重いロジックは auth/service.py に委譲。
"""
from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.auth import service as auth_service
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

_COOKIE_NAME = "pguild_token"
_COOKIE_MAX_AGE = settings.JWT_EXPIRE_DAYS * 86400


@router.post("/register", status_code=201)
def register(p: RegisterRequest, db: Session = Depends(get_db)):
    """
    SNS アカウント名ベースの新規登録。
    登録直後は status=pending。管理者アカウントは status=approved で自動承認。
    """
    user = auth_service.register_user(db, p)
    auto_approved = user.status == "approved"
    msg = "登録が完了しました。ログインできます" if auto_approved else \
          "登録が完了しました。管理者の承認をお待ちください"
    return JSONResponse({"message": msg, "user_id": user.id, "auto_approved": auto_approved},
                        status_code=201)


@router.post("/login")
def login(p: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    承認済みユーザーのログイン。JWT を httpOnly Cookie にセットして返す。
    pending / rejected / suspended は 403 + ステータス別メッセージ。
    """
    user, token = auth_service.login_user(db, p)
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=_COOKIE_MAX_AGE,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
    )
    return JSONResponse({
        "message": "ログインしました",
        "display_name": user.display_name,
        "role": user.role,
    })


@router.post("/logout")
def logout(response: Response):
    """Cookie を削除してログアウト。"""
    response.delete_cookie(_COOKIE_NAME, samesite="lax")
    return JSONResponse({"message": "ログアウトしました"})


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """現在のログインユーザー情報を返す。フロントの認証状態確認に使用。"""
    return current_user


@router.post("/change_password")
def change_password(
    p: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """パスワード変更。現在のパスワード照合必須。"""
    auth_service.change_password(db, current_user, p)
    return JSONResponse({"message": "パスワードを変更しました"})
