"""
app/services/priority_lane.py
優先レーン設定 (Phase 11 スキャフォールド)

優先レーンは将来の生成キュー管理・レート制限・優先処理に使用する。
現時点では設定定義のみで、実際のキュー制御は Phase 16+ で実装予定。

優先度スコア: 数値が高いほど優先 (同スコアは FIFO)
  headquarters: 100  — 最優先 (管理本部)
  admin:         90  — 管理者
  member_master: 70  — マスター会員 (優先レーン)
  member_paid:   50  — 有料会員 (標準レーン)
  member_free:   30  — 無料会員 (標準レーン)
  guest:         10  — ゲスト (制限レーン)

レーン区分:
  FAST  — headquarters / admin / member_master
  STD   — member_paid / member_free
  SLOW  — guest (混雑時に制限対象)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ── レーン定義 ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LaneConfig:
    role: str
    priority: int       # 高いほど優先 (0-100)
    lane: str           # "fast" | "std" | "slow"
    label: str          # 日本語表示名
    max_concurrent: int  # 同時処理上限 (-1 = 無制限) — Phase 16+ で使用
    rate_limit_rpm: int  # 分あたりリクエスト上限 (-1 = 無制限) — Phase 16+ で使用
    description: str


LANE_CONFIGS: dict[str, LaneConfig] = {
    "guest": LaneConfig(
        role="guest",
        priority=10,
        lane="slow",
        label="ゲスト",
        max_concurrent=2,
        rate_limit_rpm=3,
        description="未ログイン訪問者。混雑時に処理が遅延する場合があります。",
    ),
    "user": LaneConfig(  # RoleValue.MEMBER_FREE = "user" (後方互換)
        role="user",
        priority=30,
        lane="std",
        label="無料会員",
        max_concurrent=5,
        rate_limit_rpm=20,
        description="無料会員。標準レーンで処理されます。",
    ),
    "member_free": LaneConfig(
        role="member_free",
        priority=30,
        lane="std",
        label="無料会員",
        max_concurrent=5,
        rate_limit_rpm=20,
        description="無料会員 (Phase 15+)。標準レーンで処理されます。",
    ),
    "member_paid": LaneConfig(
        role="member_paid",
        priority=50,
        lane="std",
        label="有料会員",
        max_concurrent=10,
        rate_limit_rpm=60,
        description="有料会員。標準レーンで優先的に処理されます。",
    ),
    "member_master": LaneConfig(
        role="member_master",
        priority=70,
        lane="fast",
        label="マスター会員",
        max_concurrent=20,
        rate_limit_rpm=120,
        description="マスター会員。高速レーンで処理されます。",
    ),
    "admin": LaneConfig(
        role="admin",
        priority=90,
        lane="fast",
        label="管理者",
        max_concurrent=-1,
        rate_limit_rpm=-1,
        description="管理者。高速レーンで無制限に処理されます。",
    ),
    "headquarters": LaneConfig(
        role="headquarters",
        priority=100,
        lane="fast",
        label="管理本部",
        max_concurrent=-1,
        rate_limit_rpm=-1,
        description="管理本部。最優先レーンで無制限に処理されます。",
    ),
}

# デフォルト設定 (未知ロール → guest 扱い)
_DEFAULT_LANE = LANE_CONFIGS["guest"]


def get_lane(role: Optional[str]) -> LaneConfig:
    """ロール文字列から LaneConfig を返す。未知ロールは guest 扱い。"""
    return LANE_CONFIGS.get(role or "guest", _DEFAULT_LANE)


def get_priority(role: Optional[str]) -> int:
    """ロールの優先度スコアを返す。"""
    return get_lane(role).priority


def is_fast_lane(role: Optional[str]) -> bool:
    """高速レーン (fast) かどうかを返す。"""
    return get_lane(role).lane == "fast"


def lane_summary() -> list[dict]:
    """全レーン設定のサマリーを返す (API レスポンス用)。"""
    return [
        {
            "role":           cfg.role,
            "label":          cfg.label,
            "priority":       cfg.priority,
            "lane":           cfg.lane,
            "max_concurrent": cfg.max_concurrent,
            "rate_limit_rpm": cfg.rate_limit_rpm,
            "description":    cfg.description,
        }
        for cfg in sorted(LANE_CONFIGS.values(), key=lambda c: -c.priority)
    ]
