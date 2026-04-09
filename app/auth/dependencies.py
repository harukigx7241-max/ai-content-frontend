"""
app/auth/dependencies.py — FastAPI 依存性注入 (認証 DI)

get_current_user       : 認証必須。未ログイン・期限切れは 401。status != approved は 403。
get_current_user_soft  : 認証なしでもアクセス可能。未ログイン時は None を返す。
require_admin          : 管理者のみ。一般ユーザーは 403。
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models.user import User
from app.db.session import get_db

_COOKIE_NAME = "pguild_token"


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    token = request.cookies.get(_COOKIE_NAME)
    if not token:
        raise HTTPException(401, "ログインが必要です")

    payload = decode_access_token(token)  # 期限切れ・不正は HTTPException(401)
    user_id = int(payload["sub"])

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "ユーザーが見つかりません")
    if user.status != "approved":
        raise HTTPException(403, "アカウントが有効ではありません")

    return user


def get_current_user_soft(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    認証なしでもアクセス可能なルート用。未ログイン時は None を返す。
    既存生成機能のページなど、ログイン状態を表示するだけの用途に使う。
    """
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """管理者権限チェック。role != admin は 403。"""
    if current_user.role != "admin":
        raise HTTPException(403, "管理者権限が必要です")
    return current_user
