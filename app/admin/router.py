"""
app/admin/router.py — /api/admin/* エンドポイント (薄いルーター)
重いロジックは admin/service.py に委譲。
TODO: Phase 4+ メール通知 / 一括操作 / 監査ログ
"""
import json
import pathlib
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.admin import service as admin_service
from app.admin.schemas import (
    AdminStatsResponse,
    SystemSettingsResponse,
    SystemSettingsUpdate,
    UserAdminDetailResponse,
    UserAdminResponse,
    UserUsageResponse,
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


@router.get("/users/{user_id}", response_model=UserAdminDetailResponse)
def get_user_detail(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """個別ユーザーの詳細情報。将来 admin_notes / audit_log を追加しやすい受け皿。"""
    return admin_service.get_user_detail(db, user_id)


@router.get("/users/{user_id}/usage", response_model=UserUsageResponse)
def get_user_usage(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    ユーザー利用状況。現時点はスタブ（生成ログ未実装）。
    TODO: Phase N+ generation_log 実装後に実データを返す
    """
    return admin_service.get_user_usage(db, user_id)


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


# ── トレンド管理 ──────────────────────────────────────────────────

_KNOWLEDGE_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent / "knowledge" / "workshops"
_VALID_WORKSHOPS = {"note", "tips", "brain", "cw", "fortune", "sns", "sales"}


@router.get("/trends")
def get_all_trends(admin: User = Depends(require_admin)):
    """全ワークショップの trend_signals.json を返す。"""
    from app.services.trend_service import get_all_trend_signals
    return JSONResponse(get_all_trend_signals())


@router.put("/trends/{workshop}")
def update_trend(
    workshop: str,
    body: dict,
    admin: User = Depends(require_admin),
):
    """指定ワークショップの trend_signals.json を更新する。"""
    if workshop not in _VALID_WORKSHOPS:
        raise HTTPException(status_code=404, detail=f"Unknown workshop: {workshop}")

    target = _KNOWLEDGE_ROOT / workshop / "trend_signals.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")

    # ナレッジキャッシュを無効化して次回アクセス時に再ロードさせる
    from app.services.knowledge_service import invalidate_cache
    invalidate_cache(f"workshops/{workshop}/trend_signals.json")

    return JSONResponse({"message": f"{workshop} のトレンドデータを更新しました"})
