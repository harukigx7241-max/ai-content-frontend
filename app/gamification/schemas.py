"""
app/gamification/schemas.py — ゲーミフィケーション Pydantic スキーマ

将来拡張:
  TODO: Phase N+ RankingEntryResponse (週次/月次ランキング)
  TODO: Phase N+ MissionResponse (ミッション進捗)
  TODO: Phase N+ XP 獲得履歴レスポンス
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BadgeResponse(BaseModel):
    """獲得済みバッジ 1件分のレスポンス。"""
    key: str
    name: str
    icon: str
    description: str
    earned_at: datetime

    model_config = {"from_attributes": True}


class BadgeDefinitionResponse(BaseModel):
    """バッジ定義一覧用 (未取得も含む)。"""
    key: str
    name: str
    icon: str
    description: str
    earned: bool = False
    earned_at: Optional[datetime] = None


class LevelDefinitionResponse(BaseModel):
    """レベル定義一覧用。"""
    level: int
    min_xp: int
    title: str


class LevelBenefitsResponse(BaseModel):
    """レベル特典。GamificationStatusResponse に含まれる。"""
    daily_gen_limit: int  # 日次生成上限 (-1 = 無制限)
    post_limit: int       # 投稿上限 (-1 = 無制限)
    invite_codes: int     # 招待コード発行可能数


class GamificationStatusResponse(BaseModel):
    """
    自分のゲーミフィケーション状況サマリー。
    GET /api/gamification/status が返す。
    """
    user_id: int
    xp: int
    level: int
    title: str

    # レベルバー表示用
    xp_at_current_level: int         # 現在レベルの下限 XP
    xp_at_next_level: Optional[int]  # 次レベルの下限 XP (最大レベルなら None)
    xp_to_next: Optional[int]        # 次レベルまでの残り XP (最大レベルなら None)
    progress_pct: int                # 現レベル内での進捗 % (0-100)

    badges: list[BadgeResponse]
    level_benefits: LevelBenefitsResponse

    # TODO: Phase N+
    # active_missions: list[MissionResponse]


class XpActivityItem(BaseModel):
    """XP イベント履歴 1件分。"""
    id: int
    event_type: str
    event_label: str
    xp_delta: int
    created_at: datetime


class XpActivityResponse(BaseModel):
    """最近の XP 活動履歴リスト。"""
    items: list[XpActivityItem]
    total_xp: int
