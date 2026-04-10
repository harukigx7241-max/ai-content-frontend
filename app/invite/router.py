"""
app/invite/router.py — 一般ユーザー向け招待 API (薄いルーター)

エンドポイント:
  POST /api/invite/codes     — 自分の招待コードを発行 (Lv5以上)
  GET  /api/invite/codes     — 自分の招待コード一覧
  GET  /api/invite/summary   — マイページ向けサマリー (招待数・承認数・XP)

将来拡張:
  TODO: Phase N+ DELETE /api/invite/codes/{id} — 自分のコードを無効化
  TODO: Phase N+ GET /api/invite/tree — 招待ツリー表示
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.invite import service as invite_service
from app.invite.schemas import InviteCodeResponse, InviteSummaryResponse

router = APIRouter(prefix="/api/invite", tags=["invite"])


@router.post("/codes", response_model=InviteCodeResponse, status_code=201)
def create_my_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    自分の招待コードを発行する。認証必須。
    発行可能数はレベルに応じて解放される (Lv5 以上で 1 個〜)。
    """
    result = invite_service.generate_user_code(db, current_user)
    return InviteCodeResponse.model_validate(result)


@router.get("/codes", response_model=list[InviteCodeResponse])
def list_my_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """自分が発行した招待コード一覧を返す。認証必須。"""
    return [InviteCodeResponse.model_validate(c) for c in invite_service.get_my_codes(db, current_user.id)]


@router.get("/summary", response_model=InviteSummaryResponse)
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    マイページ向け招待サマリーを返す。認証必須。
    招待数・承認済み数・XP・自分のコード一覧を含む。
    """
    return invite_service.get_my_summary(db, current_user)
