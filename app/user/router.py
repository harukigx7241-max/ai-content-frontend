"""
app/user/router.py — /api/user/* エンドポイント (薄いルーター)

一般ユーザーの自己操作 API。認証必須。重いロジックは user/service.py に委譲。
TODO: Phase N+ 通知設定 / SNS変更 / アカウント削除エンドポイントを追加
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import UserResponse
from app.schemas.user import ProfileUpdateRequest, UserStatsResponse
from app.user import service as user_service

router = APIRouter(prefix="/api/user", tags=["user"])


@router.patch("/profile", response_model=UserResponse)
def update_profile(
    p: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    プロフィール更新。display_name / profile_url のみ変更可能。
    None フィールドはスキップ (PATCH セマンティクス)。
    """
    updated = user_service.update_profile(db, current_user, p)
    return JSONResponse(UserResponse.model_validate(updated).model_dump(mode="json"))


@router.get("/stats", response_model=UserStatsResponse)
def get_stats(current_user: User = Depends(get_current_user)):
    """
    自分の利用状況サマリー (DB 取得分のみ)。
    生成回数・お気に入り数はフロントの localStorage から取得する。
    """
    return user_service.get_stats(current_user)
