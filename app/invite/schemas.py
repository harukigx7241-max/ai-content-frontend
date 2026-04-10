"""
app/invite/schemas.py — 招待コード Pydantic スキーマ

将来拡張:
  TODO: Phase N+ InviteTreeResponse (招待ツリー可視化)
  TODO: Phase N+ InviteRankingResponse (招待ランキング)
  TODO: Phase N+ InviteQualityResponse (招待品質スコア)
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InviteCodeResponse(BaseModel):
    """招待コード 1件分のレスポンス。"""
    id:                 int
    code:               str
    created_by_user_id: Optional[int]
    created_by_role:    str
    is_admin_code:      bool
    max_uses:           int
    used_count:         int
    auto_approve:       bool
    status:             str
    expires_at:         Optional[datetime]
    label:              Optional[str]
    notes:              Optional[str]
    created_at:         datetime

    model_config = {"from_attributes": True}


class AdminInviteCodeCreateRequest(BaseModel):
    """管理者が招待コードを発行するリクエスト。"""
    code:         Optional[str]      = Field(None, max_length=20,  description="空欄で自動生成")
    max_uses:     int                = Field(default=1, ge=1, le=1000)
    auto_approve: bool               = False
    expires_at:   Optional[datetime] = None
    label:        Optional[str]      = Field(None, max_length=100)
    notes:        Optional[str]      = Field(None, max_length=500)


class AdminInviteCodeListItem(InviteCodeResponse):
    """管理画面向け: コード情報 + 発行者表示名。"""
    created_by_display_name: Optional[str] = None


class InviteSummaryResponse(BaseModel):
    """
    マイページ向け招待サマリー。
    GET /api/invite/summary が返す。
    """
    can_issue:            bool             # 招待コードを発行できるか
    max_codes:            int              # 現レベルで発行できる最大数
    active_codes_count:   int              # 現在アクティブなコード数
    next_unlock_level:    Optional[int]    # 次の枠解放レベル (null = 既に最大)
    total_invited:        int              # 招待コード経由で登録したユーザー数
    total_approved:       int              # そのうち承認済みのユーザー数
    xp_earned_from_invites: int           # 招待 XP の合計
    codes:                list[InviteCodeResponse]  # 自分が発行したコード一覧
    # TODO: Phase N+ pending_count: int (招待待ち承認数)
    # TODO: Phase N+ quality_score: Optional[float] (招待品質スコア)
