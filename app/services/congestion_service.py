"""
app/services/congestion_service.py
混雑状況サービス (Phase 11 全面刷新)

4段階レベル:
  low      — 空いています  (アクティブユーザー < 5 / 30min)
  medium   — やや混雑      (5-15)
  high     — 混雑中        (15-30)
  critical — 非常に混雑    (30+)

算出方法:
  xp_events テーブルの直近30分の distinct user_id 数をアクティブユーザーの代理指標として使用。
  (Phase 16 の generation_log 実装後はそちらに切り替える予定)

管理者向け追加指標:
  active_5m   — 直近5分のアクティブユーザー数 (同時利用の近似値)
  active_30m  — 直近30分のアクティブユーザー数
  events_5m   — 直近5分のイベント件数 (生成待ちの代理)
  posts_1h    — 直近1時間の投稿数
  error_rate  — エラー率 (Phase 16 まで常に 0.0)

優先レーン:
  app/services/priority_lane.py を参照。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.services.base import BaseService, ServiceMode, ServiceResult


# ── 4段階レベル定義 ──────────────────────────────────────────────────────────

@dataclass
class CongestionLevel:
    key: str    # "low" | "medium" | "high" | "critical"
    label: str  # ユーザー向け日本語ラベル
    color: str  # "green" | "yellow" | "orange" | "red"
    icon: str
    threshold: int  # active_30m がこの値以上でこのレベル (昇順に評価)


_LEVELS: list[CongestionLevel] = [
    CongestionLevel("low",      "空いています",   "green",  "🟢", 0),
    CongestionLevel("medium",   "やや混雑",       "yellow", "🟡", 5),
    CongestionLevel("high",     "混雑中",         "orange", "🟠", 15),
    CongestionLevel("critical", "非常に混雑",     "red",    "🔴", 30),
]


def _calc_level(active_30m: int) -> CongestionLevel:
    """アクティブユーザー数からレベルを判定する。"""
    result = _LEVELS[0]
    for lvl in _LEVELS:
        if active_30m >= lvl.threshold:
            result = lvl
    return result


def _wait_estimate(level: CongestionLevel) -> Optional[str]:
    """推定待ち時間の文字列を返す (low は None)。"""
    mapping = {
        "low":      None,
        "medium":   "通常より少し遅くなる場合があります",
        "high":     "応答が遅くなる場合があります (推定 +5〜15秒)",
        "critical": "大幅に遅くなる場合があります (推定 +30秒以上)",
    }
    return mapping.get(level.key)


def _light_mode_hint(level: CongestionLevel) -> Optional[str]:
    """軽量モード案内を返す (high 以上のみ)。"""
    if level.key in ("high", "critical"):
        return "混雑時は「軽量モード」のご利用をおすすめします。"
    return None


# ── メイン混雑ステータス ─────────────────────────────────────────────────────

@dataclass
class CongestionStatus:
    """一般ユーザー向け混雑状況レスポンス。"""
    level: str             # "low" | "medium" | "high" | "critical"
    label: str             # "空いています" etc.
    color: str             # "green" | "yellow" | "orange" | "red"
    icon: str
    active_approx: int     # 直近30分のアクティブユーザー概算 (プライバシーのため丸め)
    wait_estimate: Optional[str]
    light_mode_hint: Optional[str]
    mode: str = "free"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "level":            self.level,
            "label":            self.label,
            "color":            self.color,
            "icon":             self.icon,
            "active_approx":    self.active_approx,
            "wait_estimate":    self.wait_estimate,
            "light_mode_hint":  self.light_mode_hint,
            "mode":             self.mode,
            "timestamp":        self.timestamp,
        }


# ── 管理者向け追加指標 ────────────────────────────────────────────────────────

@dataclass
class CongestionAdminMetrics:
    """管理者専用の詳細混雑指標。"""
    active_5m: int    # 直近5分の distinct ユーザー数 (同時利用の近似)
    active_30m: int   # 直近30分の distinct ユーザー数
    events_5m: int    # 直近5分のイベント総数 (生成中の代理指標)
    events_30m: int   # 直近30分のイベント総数
    posts_1h: int     # 直近1時間の新規投稿数
    events_per_min: float   # 直近5分の平均イベント/分 (スループット指標)
    error_rate: float = 0.0  # エラー率 (Phase 16 まで 0.0)
    note: str = "error_rate は Phase 16 (generation_log) 実装後に実値に置き換えます"

    def to_dict(self) -> dict:
        return {
            "active_5m":       self.active_5m,
            "active_30m":      self.active_30m,
            "events_5m":       self.events_5m,
            "events_30m":      self.events_30m,
            "posts_1h":        self.posts_1h,
            "events_per_min":  round(self.events_per_min, 2),
            "error_rate":      self.error_rate,
            "note":            self.note,
        }


# ── DB なし・静的フォールバック ───────────────────────────────────────────────

_STATIC_STATUS = CongestionStatus(
    level="low", label="空いています", color="green", icon="🟢",
    active_approx=0, wait_estimate=None, light_mode_hint=None, mode="free",
)

_STATIC_ADMIN = CongestionAdminMetrics(
    active_5m=0, active_30m=0, events_5m=0, events_30m=0,
    posts_1h=0, events_per_min=0.0,
)


# ── CongestionService ─────────────────────────────────────────────────────────

class CongestionService(BaseService):
    FLAG_KEY = "CONGESTION_DISPLAY"

    def get_status(self, db=None) -> ServiceResult:
        """
        一般ユーザー向け混雑状況を返す。
        db が渡された場合は DB から算出、なければ静的ステータスを返す。
        """
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        if db is not None:
            try:
                status = self._calc_from_db(db)
                return ServiceResult.free(content=status.to_dict())
            except Exception:
                pass
        return ServiceResult.free(content=_STATIC_STATUS.to_dict())

    def get_admin_metrics(self, db=None) -> dict:
        """
        管理者向け詳細指標を返す。
        一般ステータスと詳細指標を合わせた dict を返す。
        """
        if db is not None:
            try:
                status  = self._calc_from_db(db)
                metrics = self._calc_admin_from_db(db)
                return {**status.to_dict(), "admin": metrics.to_dict()}
            except Exception:
                pass
        return {
            **_STATIC_STATUS.to_dict(),
            "admin": _STATIC_ADMIN.to_dict(),
        }

    # ── DB 算出 ─────────────────────────────────────────────────────────────

    def _calc_from_db(self, db) -> CongestionStatus:
        from datetime import datetime, timedelta, timezone
        from sqlalchemy import func, select, distinct
        from app.db.models.xp_event import XpEvent

        now   = datetime.now(timezone.utc)
        t30   = now - timedelta(minutes=30)

        active_30m = db.execute(
            select(func.count(distinct(XpEvent.user_id)))
            .where(XpEvent.created_at >= t30)
        ).scalar() or 0

        lvl  = _calc_level(active_30m)
        # プライバシー配慮: 5刻みで丸める
        approx = (active_30m // 5) * 5 if active_30m >= 5 else active_30m

        return CongestionStatus(
            level=lvl.key, label=lvl.label, color=lvl.color, icon=lvl.icon,
            active_approx=approx,
            wait_estimate=_wait_estimate(lvl),
            light_mode_hint=_light_mode_hint(lvl),
            mode="free",
        )

    def _calc_admin_from_db(self, db) -> CongestionAdminMetrics:
        from datetime import datetime, timedelta, timezone
        from sqlalchemy import func, select, distinct
        from app.db.models.xp_event import XpEvent
        from app.db.models.post import CommunityPost

        now   = datetime.now(timezone.utc)
        t5    = now - timedelta(minutes=5)
        t30   = now - timedelta(minutes=30)
        t1h   = now - timedelta(hours=1)

        active_5m  = db.execute(
            select(func.count(distinct(XpEvent.user_id))).where(XpEvent.created_at >= t5)
        ).scalar() or 0
        active_30m = db.execute(
            select(func.count(distinct(XpEvent.user_id))).where(XpEvent.created_at >= t30)
        ).scalar() or 0
        events_5m  = db.execute(
            select(func.count(XpEvent.id)).where(XpEvent.created_at >= t5)
        ).scalar() or 0
        events_30m = db.execute(
            select(func.count(XpEvent.id)).where(XpEvent.created_at >= t30)
        ).scalar() or 0
        posts_1h   = db.execute(
            select(func.count(CommunityPost.id))
            .where(CommunityPost.created_at >= t1h)
        ).scalar() or 0

        events_per_min = events_5m / 5.0 if events_5m else 0.0

        return CongestionAdminMetrics(
            active_5m=active_5m,
            active_30m=active_30m,
            events_5m=events_5m,
            events_30m=events_30m,
            posts_1h=posts_1h,
            events_per_min=events_per_min,
        )

    # ── 後方互換フォールバック ───────────────────────────────────────────────

    def _run_free(self, **_) -> ServiceResult:
        return ServiceResult.free(content=_STATIC_STATUS.to_dict())

    def _run_fallback(self, **_) -> ServiceResult:
        return self._run_free()


# グローバルシングルトン
congestion_service = CongestionService()
