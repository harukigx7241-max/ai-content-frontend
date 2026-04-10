"""
app/invite/admin_router.py — 管理者向け招待コード API (薄いルーター)

エンドポイント:
  POST  /api/admin/invite/codes            — 招待コード発行 (管理者)
  GET   /api/admin/invite/codes            — 全コード一覧
  PATCH /api/admin/invite/codes/{code_id} — コード無効化

将来拡張:
  TODO: Phase N+ GET /api/admin/invite/codes/{id}/uses — 使用ログ一覧
  TODO: Phase N+ GET /api/admin/invite/stats           — 招待統計ダッシュボード
  TODO: Phase N+ PATCH /api/admin/invite/codes/{id}/reactivate — 再有効化
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.db.models.user import User
from app.db.session import get_db
from app.invite import service as invite_service
from app.invite.schemas import AdminInviteCodeCreateRequest, AdminInviteCodeListItem, InviteCodeResponse

router = APIRouter(prefix="/api/admin/invite", tags=["admin-invite"])


@router.post("/codes", response_model=InviteCodeResponse, status_code=201)
def create_admin_code(
    data: AdminInviteCodeCreateRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """管理者が招待コードを発行する。レベル制限なし。コード手動指定可能。"""
    result = invite_service.generate_admin_code(db, admin.id, data)
    return JSONResponse(
        InviteCodeResponse.model_validate(result).model_dump(mode="json"),
        status_code=201,
    )


@router.get("/codes", response_model=list[AdminInviteCodeListItem])
def list_all_codes(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """全招待コード一覧を返す。発行者の表示名を含む。"""
    return invite_service.get_all_codes_admin(db)


@router.patch("/codes/{code_id}/deactivate", response_model=InviteCodeResponse)
def deactivate(
    code_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """招待コードを無効化する。一度無効化したコードは使用不可になる。"""
    result = invite_service.deactivate_code(db, code_id)
    return InviteCodeResponse.model_validate(result)
