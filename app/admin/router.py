"""
app/admin/router.py — /api/admin/* エンドポイント (薄いルーター)
重いロジックは admin/service.py に委譲。
TODO: Phase 4+ メール通知 / 一括操作 / 監査ログ
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.admin import service as admin_service
from app.admin.schemas import (
    AdminStatsResponse,
    SystemSettingsResponse,
    SystemSettingsUpdate,
    UserAdminResponse,
)
from app.auth.dependencies import require_admin
from app.db.models.user import User
from app.db.session import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[UserAdminResponse])
def list_users(
    status: Optional[str] = Query(None, description="pending / approved / rejected / suspended"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """全ユーザー一覧。status クエリでフィルタリング可能。"""
    return admin_service.list_users(db, status)


@router.post("/users/{user_id}/approve")
def approve(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = admin_service.approve_user(db, user_id, admin.id)
    return JSONResponse({"message": f"{user.display_name} を承認しました", "user_id": user.id})


@router.post("/users/{user_id}/reject")
def reject(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = admin_service.reject_user(db, user_id, admin.id)
    return JSONResponse({"message": f"{user.display_name} の登録を却下しました", "user_id": user.id})


@router.post("/users/{user_id}/suspend")
def suspend(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = admin_service.suspend_user(db, user_id, admin.id)
    return JSONResponse({"message": f"{user.display_name} を停止しました", "user_id": user.id})


@router.post("/users/{user_id}/restore")
def restore(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = admin_service.restore_user(db, user_id, admin.id)
    return JSONResponse({"message": f"{user.display_name} を復元しました", "user_id": user.id})


# ── 統計 ─────────────────────────────────────────────────────────

@router.get("/stats", response_model=AdminStatsResponse)
def stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """管理ダッシュボード向け基本統計。"""
    return admin_service.get_stats(db)


# ── システム設定 ──────────────────────────────────────────────────

@router.get("/settings", response_model=SystemSettingsResponse)
def get_settings(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """現在のシステム設定を返す。"""
    return admin_service.get_settings(db)


@router.post("/settings", response_model=SystemSettingsResponse)
def update_settings(
    body: SystemSettingsUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """システム設定を更新する。None フィールドはスキップ。"""
    return admin_service.update_settings(db, body.model_dump(), admin.id)
