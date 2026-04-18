"""
app/admin/hq_router.py — /api/hq/* エンドポイント (Phase 18)
全エンドポイントは require_hq (headquarters ロールのみ) で保護。
admin ロールはアクセス不可。
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import require_hq
from app.db.models.user import User
from app.db.session import get_db

router = APIRouter(prefix="/api/hq", tags=["hq"])


# ── 1. KPI サマリー ───────────────────────────────────────────────────

@router.get("/kpi")
def get_kpi(
    hq: User = Depends(require_hq),
    db: Session = Depends(get_db),
):
    """管理本部向けプラットフォーム KPI サマリー。"""
    from app.services.hq_dashboard_service import hq_dashboard_service
    result = hq_dashboard_service.get_kpi_summary(db=db)
    return JSONResponse(result.content or {})


# ── 2. Trend Room ─────────────────────────────────────────────────────

@router.get("/trends")
def get_trend_analysis(hq: User = Depends(require_hq)):
    """全ワークショップのクロストレンド分析。"""
    from app.services.hq_dashboard_service import hq_dashboard_service
    result = hq_dashboard_service.get_trend_analysis()
    return JSONResponse(result.content or {})


# ── 3. Incident Room ──────────────────────────────────────────────────

class IncidentCreateRequest(BaseModel):
    title: str
    severity: str = "info"   # info | warning | critical
    description: str = ""


class IncidentStatusRequest(BaseModel):
    status: str               # open | monitoring | resolved
    resolution: str = ""


@router.get("/incidents")
def list_incidents(
    status: Optional[str] = Query(None, description="open|monitoring|resolved"),
    hq: User = Depends(require_hq),
):
    """インシデント一覧を返す。"""
    from app.services.hq_dashboard_service import hq_dashboard_service
    result = hq_dashboard_service.get_incidents(status=status)
    return JSONResponse(result.content or {})


@router.post("/incidents")
def create_incident(
    body: IncidentCreateRequest,
    hq: User = Depends(require_hq),
):
    """新規インシデントを作成する。"""
    from app.services.hq_dashboard_service import hq_dashboard_service
    result = hq_dashboard_service.create_incident(
        title=body.title,
        severity=body.severity,
        description=body.description,
        created_by=hq.display_name or hq.email or "hq",
    )
    if "error" in (result.content or {}):
        raise HTTPException(status_code=400, detail=result.content["error"])
    return JSONResponse(result.content or {})


@router.put("/incidents/{incident_id}")
def update_incident(
    incident_id: str,
    body: IncidentStatusRequest,
    hq: User = Depends(require_hq),
):
    """インシデントのステータスを更新する。"""
    from app.services.hq_dashboard_service import hq_dashboard_service
    result = hq_dashboard_service.update_incident_status(
        incident_id=incident_id,
        new_status=body.status,
        resolution=body.resolution,
        updated_by=hq.display_name or "hq",
    )
    if "error" in (result.content or {}):
        raise HTTPException(status_code=400, detail=result.content["error"])
    return JSONResponse(result.content or {})


# ── 4. Feature Flag Console ───────────────────────────────────────────

class FlagToggleRequest(BaseModel):
    key: str
    enabled: bool
    reason: str = ""


class FlagClearRequest(BaseModel):
    key: str


@router.get("/flags")
def get_flags(hq: User = Depends(require_hq)):
    """全フラグの詳細 (デフォルト値・現在値・オーバーライド・ポリシー情報) を返す。"""
    from app.services.hq_dashboard_service import hq_dashboard_service
    result = hq_dashboard_service.get_flag_details()
    return JSONResponse(result.content or {})


@router.post("/flags/toggle")
def toggle_flag(
    body: FlagToggleRequest,
    hq: User = Depends(require_hq),
):
    """フラグのランタイムオーバーライドを設定する。"""
    from app.services.hq_dashboard_service import hq_dashboard_service
    result = hq_dashboard_service.set_flag_override(
        flag_key=body.key,
        enabled=body.enabled,
        reason=body.reason,
    )
    return JSONResponse(result.content or {})


@router.post("/flags/clear")
def clear_flag_override(
    body: FlagClearRequest,
    hq: User = Depends(require_hq),
):
    """フラグのオーバーライドを解除してデフォルト値に戻す。"""
    from app.services.hq_dashboard_service import hq_dashboard_service
    result = hq_dashboard_service.clear_flag_override(flag_key=body.key)
    return JSONResponse(result.content or {})


# ── 5. Admin ユーザー管理 (HQ 専用) ──────────────────────────────────

class AdminRoleChangeRequest(BaseModel):
    user_id: int
    new_role: str


@router.get("/admins")
def list_admin_users(
    hq: User = Depends(require_hq),
    db: Session = Depends(get_db),
):
    """admin / headquarters ロールのユーザー一覧を返す (HQ 専用)。"""
    from app.services.hq_dashboard_service import hq_dashboard_service
    result = hq_dashboard_service.get_admin_users(db=db)
    return JSONResponse(result.content or {})


@router.post("/admins/role")
def change_admin_role(
    body: AdminRoleChangeRequest,
    hq: User = Depends(require_hq),
    db: Session = Depends(get_db),
):
    """admin ユーザーのロールを変更する (HQ 専用)。"""
    from app.services.hq_dashboard_service import hq_dashboard_service
    result = hq_dashboard_service.change_admin_role(
        target_user_id=body.user_id,
        new_role=body.new_role,
        db=db,
    )
    if "error" in (result.content or {}):
        raise HTTPException(status_code=400, detail=result.content["error"])
    return JSONResponse(result.content or {})
