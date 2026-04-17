"""
app/admin/router.py — /api/admin/* エンドポイント (薄いルーター)
重いロジックは admin/service.py に委譲。
Phase 13: API制御センター (/api/admin/api-control, /api/admin/budget) 追加
"""
import json
import pathlib
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
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
from app.auth.dependencies import require_admin, require_hq
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


# ── Phase 13: API 制御センター ─────────────────────────────────────


class ToggleRequest(BaseModel):
    service: str
    enabled: bool


class BatchRequest(BaseModel):
    preset: str


@router.get("/api-control")
def get_api_control(admin: User = Depends(require_admin)):
    """全 AI サービスの現在の制御状態を返す。"""
    from app.services.api_control_service import api_control_service
    return JSONResponse(api_control_service.get_control_state())


@router.post("/api-control/toggle")
def toggle_api_service(
    body: ToggleRequest,
    admin: User = Depends(require_admin),
):
    """個別サービスの ON/OFF を切り替える。"""
    from app.services.api_control_service import api_control_service
    try:
        result = api_control_service.toggle_service(body.service, body.enabled)
        return JSONResponse(result)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api-control/batch")
def batch_api_control(
    body: BatchRequest,
    admin: User = Depends(require_admin),
):
    """一括プリセットを適用する。"""
    from app.services.api_control_service import api_control_service
    try:
        result = api_control_service.apply_preset(body.preset)
        return JSONResponse(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/budget")
def get_budget(admin: User = Depends(require_admin)):
    """日次・月次の予算状態を返す。"""
    from app.services.api_control_service import api_control_service
    budget = api_control_service.get_budget()
    return JSONResponse(budget.to_dict())


# ── Phase 15: 傾向収集 (Trend Ingestion) ──────────────────────────


class IngestRequest(BaseModel):
    workshop: Optional[str] = None  # None → 全ワークショップ
    triggered_by: str = "admin"


@router.post("/trends/ingest")
def trigger_trend_ingest(
    body: IngestRequest,
    admin: User = Depends(require_admin),
):
    """
    傾向収集を手動トリガーする。
    workshop=None → 全ワークショップ。workshop 指定 → 1件のみ。
    """
    from app.services.trend_ingestion_service import trend_ingestion_service
    triggered_by = f"{admin.display_name or admin.email} (admin)"
    if body.workshop:
        result = trend_ingestion_service.run_for_workshop(body.workshop, triggered_by)
    else:
        result = trend_ingestion_service.run_all(triggered_by)
    if not result.available:
        raise HTTPException(status_code=400, detail=result.hint or "収集に失敗しました")
    return JSONResponse(result.content or {})


@router.get("/trends/history")
def get_trend_history(
    limit: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin),
):
    """傾向収集の実行履歴を返す (最新N件)。"""
    from app.services.trend_ingestion_service import trend_ingestion_service
    result = trend_ingestion_service.get_history(limit=limit)
    return JSONResponse(result.content or {})


@router.get("/trends/status")
def get_trend_status(admin: User = Depends(require_admin)):
    """全ワークショップの傾向データ鮮度状態を返す。"""
    from app.services.trend_ingestion_service import trend_ingestion_service
    result = trend_ingestion_service.get_status()
    return JSONResponse(result.content or {})


# ── Phase 14: 使用量ダッシュボード ───────────────────────────────


@router.get("/usage")
def get_usage_report(admin: User = Depends(require_admin)):
    """
    API使用量・コストレポート (管理者向け)。
    管理者には今日+今月の概要・機能別・モデル別内訳を返す。
    管理本部 (HQ) には拡張データ (予算消化率・危険機能・自動停止履歴) も付与する。
    """
    from app.core.roles import HQ_ROLES
    from app.services.usage_dashboard_service import usage_dashboard_service
    is_hq = admin.role in HQ_ROLES
    result = usage_dashboard_service.get_report(is_hq=is_hq)
    return JSONResponse(result.to_dict() if hasattr(result, "to_dict") else result.content or {})


@router.get("/usage/summary")
def get_usage_summary(admin: User = Depends(require_admin)):
    """今日・今月のサマリのみを返す (軽量エンドポイント)。"""
    from app.services.usage_dashboard_service import usage_dashboard_service
    result = usage_dashboard_service.get_report(is_hq=False)
    data = result.content or {}
    return JSONResponse({
        "today":   data.get("today", {}),
        "monthly": data.get("monthly", {}),
        "mode":    data.get("mode", "mock"),
    })


@router.get("/usage/hq")
def get_usage_hq(hq: User = Depends(require_hq)):
    """
    管理本部専用の拡張分析データ。
    予算消化率・閾値警告・危険機能・自動停止履歴を含む。
    require_hq により headquarters ロール以外はアクセス不可。
    """
    from app.services.usage_dashboard_service import usage_dashboard_service
    result = usage_dashboard_service.get_report(is_hq=True)
    data = result.content or {}
    return JSONResponse(data.get("hq", {}))
