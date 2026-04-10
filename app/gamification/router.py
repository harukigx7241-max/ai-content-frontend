"""
app/gamification/router.py — ゲーミフィケーション API ルーター (薄く保つ)

エンドポイント:
  GET /api/gamification/status   — 自分の XP / レベル / バッジ (要認証)
  GET /api/gamification/levels   — レベル定義一覧 (未認証可、参照用)
  GET /api/gamification/badges   — バッジ定義一覧 (未認証可、参照用)

将来拡張:
  TODO: Phase N+ GET /api/gamification/ranking (週次/月次ランキング)
  TODO: Phase N+ GET /api/gamification/missions (ミッション進捗)
  TODO: Phase N+ GET /api/gamification/history  (XP獲得履歴)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.gamification import service as gami_service, xp_service
from app.gamification.constants import BADGE_DEFINITIONS
from app.gamification.schemas import (
    BadgeDefinitionResponse,
    GamificationStatusResponse,
    LevelDefinitionResponse,
)

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


@router.get("/status", response_model=GamificationStatusResponse)
def get_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """自分の現在の XP / レベル / 称号 / 獲得バッジを返す。認証必須。"""
    return gami_service.get_status(db, current_user.id)


@router.get("/levels", response_model=list[LevelDefinitionResponse])
def get_levels():
    """レベル定義一覧 (Lv1〜30) を返す。未認証でも閲覧可能。"""
    return [
        LevelDefinitionResponse(
            level=lv,
            min_xp=xp_service.xp_for_level(lv),
            title=xp_service.get_title(lv),
        )
        for lv in range(1, 31)
    ]


@router.get("/badges", response_model=list[BadgeDefinitionResponse])
def get_badges():
    """バッジ定義一覧を返す。未認証でも閲覧可能。"""
    return [
        BadgeDefinitionResponse(
            key=key,
            name=defn["name"],
            icon=defn["icon"],
            description=defn["description"],
        )
        for key, defn in BADGE_DEFINITIONS.items()
    ]
