"""
app/services/api_control_service.py — Phase 13
API利用の機能単位制御・一括制御・予算ガード。

責務:
  - 各 AI サービスの ON/OFF を runtime で切り替える
  - 一括プリセット (全ON/全OFF/高コスト停止/管理者限定/無料会員向けOFF)
  - 日次・月次予算ガード (Phase 16 で実データ連携予定)
  - 管理ダッシュボードへの状態公開

アーキテクチャ:
  - flags._runtime_overrides に書き込んで既存の is_enabled() を拡張
  - 永続化なし (サーバー再起動でリセット)。Phase 16 で DB 化予定。
  - 予算トラッキングはスタブ。Phase 16 で generation_log 連携。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.core.config import settings
from app.core.feature_flags import flags


# ─────────────────────────────────────────────────────────────────────────────
# AI サービス定義テーブル
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AiServiceDef:
    name: str         # registry と一致するサービス名
    label: str        # 日本語表示名
    flag_key: str     # FeatureFlags の属性名
    is_high_cost: bool = False   # 高コストサービス (デフォルト false で無効)
    api_only: bool = False       # FREE fallback なし (API 専用)
    admin_only: bool = False     # 管理者専用機能
    free_member_uses: bool = True  # 無料会員が使う機能か


_AI_SERVICES: list[AiServiceDef] = [
    AiServiceDef("prompt_forge",       "プロンプト鍛冶場",     "PROMPT_FORGE",        free_member_uses=True),
    AiServiceDef("prompt_doctor",      "プロンプト診断",       "PROMPT_DOCTOR",       free_member_uses=True),
    AiServiceDef("guild_guide_ai",     "ギルドガイドAI",       "GUILD_GUIDE_AI",      free_member_uses=True),
    AiServiceDef("workshop_master_ai", "ワークショップマスター", "WORKSHOP_MASTER_AI",  is_high_cost=True, api_only=True, admin_only=True, free_member_uses=False),
    AiServiceDef("trend_refresh",      "トレンドリフレッシュ",  "TREND_REFRESH",       free_member_uses=True),
    AiServiceDef("language_quality_ai","日本語品質チェック",    "LANGUAGE_QUALITY_AI", free_member_uses=True),
    AiServiceDef("campaign_forge",     "キャンペーン工房",      "CAMPAIGN_FORGE",      free_member_uses=True),
    AiServiceDef("article_draft_ai",   "記事下書きAI",         "ARTICLE_DRAFT_AI",    is_high_cost=True, api_only=True, admin_only=True, free_member_uses=False),
    AiServiceDef("image_generation",   "画像生成連携",         "IMAGE_GENERATION",    is_high_cost=True, free_member_uses=False),
    AiServiceDef("guild_scribe_ai",    "ギルド書記AI",         "GUILD_SCRIBE_AI",     free_member_uses=True),
    AiServiceDef("promotion_planner",  "プロモーションプランナー","PROMOTION_PLANNER",  free_member_uses=True),
]

# 名前引きの高速化
_SVC_BY_NAME: dict[str, AiServiceDef] = {s.name: s for s in _AI_SERVICES}

# 高コストサービス一覧 (config で上書き可能)
_HIGH_COST_NAMES: frozenset[str] = frozenset(
    n.strip() for n in settings.API_HIGH_COST_SERVICES.split(",") if n.strip()
)


# ─────────────────────────────────────────────────────────────────────────────
# 予算ガード
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class BudgetGuard:
    """日次・月次の予算状態スナップショット。"""
    # 日次
    daily_tokens_used: int = 0
    daily_tokens_limit: int = 0       # 0 = 無制限
    daily_cost_usd: float = 0.0
    daily_cost_limit_usd: float = 0.0 # 0 = 無制限
    # 月次
    monthly_tokens_used: int = 0
    monthly_tokens_limit: int = 0
    monthly_cost_usd: float = 0.0
    monthly_cost_limit_usd: float = 0.0
    # 状態
    warn_threshold_pct: int = 80
    over_limit_action: str = "fallback"
    mode: str = "stub"  # stub → Phase 16 で "live" に

    # ── 計算プロパティ ────────────────────────────────────────────

    @property
    def daily_token_pct(self) -> float:
        if self.daily_tokens_limit == 0:
            return 0.0
        return min(100.0, self.daily_tokens_used / self.daily_tokens_limit * 100)

    @property
    def monthly_token_pct(self) -> float:
        if self.monthly_tokens_limit == 0:
            return 0.0
        return min(100.0, self.monthly_tokens_used / self.monthly_tokens_limit * 100)

    @property
    def daily_cost_pct(self) -> float:
        if self.daily_cost_limit_usd == 0:
            return 0.0
        return min(100.0, self.daily_cost_usd / self.daily_cost_limit_usd * 100)

    @property
    def monthly_cost_pct(self) -> float:
        if self.monthly_cost_limit_usd == 0:
            return 0.0
        return min(100.0, self.monthly_cost_usd / self.monthly_cost_limit_usd * 100)

    @property
    def is_daily_over(self) -> bool:
        if self.daily_tokens_limit and self.daily_tokens_used >= self.daily_tokens_limit:
            return True
        if self.daily_cost_limit_usd and self.daily_cost_usd >= self.daily_cost_limit_usd:
            return True
        return False

    @property
    def is_monthly_over(self) -> bool:
        if self.monthly_tokens_limit and self.monthly_tokens_used >= self.monthly_tokens_limit:
            return True
        if self.monthly_cost_limit_usd and self.monthly_cost_usd >= self.monthly_cost_limit_usd:
            return True
        return False

    @property
    def is_over_limit(self) -> bool:
        return self.is_daily_over or self.is_monthly_over

    @property
    def warn_level(self) -> str:
        """none / warn / critical"""
        max_pct = max(
            self.daily_token_pct, self.monthly_token_pct,
            self.daily_cost_pct,  self.monthly_cost_pct,
        )
        if self.is_over_limit:
            return "critical"
        if max_pct >= self.warn_threshold_pct:
            return "warn"
        return "none"

    def to_dict(self) -> dict:
        return {
            "daily": {
                "tokens_used": self.daily_tokens_used,
                "tokens_limit": self.daily_tokens_limit,
                "token_pct": round(self.daily_token_pct, 1),
                "cost_usd": round(self.daily_cost_usd, 4),
                "cost_limit_usd": self.daily_cost_limit_usd,
                "cost_pct": round(self.daily_cost_pct, 1),
                "is_over": self.is_daily_over,
            },
            "monthly": {
                "tokens_used": self.monthly_tokens_used,
                "tokens_limit": self.monthly_tokens_limit,
                "token_pct": round(self.monthly_token_pct, 1),
                "cost_usd": round(self.monthly_cost_usd, 4),
                "cost_limit_usd": self.monthly_cost_limit_usd,
                "cost_pct": round(self.monthly_cost_pct, 1),
                "is_over": self.is_monthly_over,
            },
            "warn_level": self.warn_level,
            "warn_threshold_pct": self.warn_threshold_pct,
            "over_limit_action": self.over_limit_action,
            "is_over_limit": self.is_over_limit,
            "mode": self.mode,
        }


# ─────────────────────────────────────────────────────────────────────────────
# バッチプリセット定義
# ─────────────────────────────────────────────────────────────────────────────

BATCH_PRESETS: dict[str, dict] = {
    "all_on": {
        "label": "全AI機能ON",
        "description": "すべての AI サービスを有効化する",
        "icon": "🟢",
        "danger": False,
    },
    "all_off": {
        "label": "全AI機能OFF",
        "description": "すべての AI サービスを無効化する (FREE tier に降格)",
        "icon": "⚫",
        "danger": True,
    },
    "high_cost_off": {
        "label": "高コスト停止",
        "description": "高コストサービス (画像生成・記事下書き・WSマスター) を停止",
        "icon": "🟠",
        "danger": False,
    },
    "admin_only": {
        "label": "管理者限定AIのみ",
        "description": "管理者専用 AI のみ有効化し、一般向け AI を停止",
        "icon": "🔴",
        "danger": True,
    },
    "free_tier_off": {
        "label": "無料会員向けAI停止",
        "description": "無料会員が使う AI 機能を停止 (有料会員・管理者は継続)",
        "icon": "🟡",
        "danger": False,
    },
    "reset": {
        "label": "設定リセット",
        "description": "実行時オーバーライドをすべてクリアし、環境変数設定に戻す",
        "icon": "🔄",
        "danger": False,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# ApiControlService
# ─────────────────────────────────────────────────────────────────────────────

class ApiControlService:
    """
    API利用の機能単位制御・一括制御・予算ガードを提供するサービス。

    flags._runtime_overrides を通じて FeatureFlags と連携する。
    """

    # 自動停止履歴 (in-memory, Phase 16 で DB 永続化予定)
    _stop_history: list = []

    # ── 個別トグル ────────────────────────────────────────────────

    def toggle_service(self, service_name: str, enabled: bool) -> dict:
        """
        指定サービスの ON/OFF を実行時に切り替える。
        Returns: {"service": ..., "enabled": ..., "flag_key": ...}
        Raises: KeyError if service_name is unknown.
        """
        svc = _SVC_BY_NAME.get(service_name)
        if svc is None:
            raise KeyError(f"Unknown service: {service_name}")
        flags.set_override(svc.flag_key, enabled)
        return {
            "service": service_name,
            "label": svc.label,
            "flag_key": svc.flag_key,
            "enabled": enabled,
        }

    # ── バッチプリセット ─────────────────────────────────────────

    def apply_preset(self, preset: str) -> dict:
        """
        一括プリセットを適用する。
        Returns: {"preset": ..., "applied": [...changed services...]}
        Raises: ValueError if preset is unknown.
        """
        if preset not in BATCH_PRESETS:
            raise ValueError(f"Unknown preset: {preset}")

        applied: list[dict] = []

        if preset == "reset":
            for svc in _AI_SERVICES:
                flags.clear_override(svc.flag_key)
            return {"preset": preset, "applied": [], "message": "全オーバーライドをクリアしました"}

        for svc in _AI_SERVICES:
            target: Optional[bool] = None

            if preset == "all_on":
                target = True
            elif preset == "all_off":
                target = False
            elif preset == "high_cost_off":
                is_high = svc.name in _HIGH_COST_NAMES or svc.is_high_cost
                if is_high:
                    target = False
            elif preset == "admin_only":
                target = True if svc.admin_only else False
            elif preset == "free_tier_off":
                if svc.free_member_uses:
                    target = False

            if target is not None:
                flags.set_override(svc.flag_key, target)
                applied.append({
                    "service": svc.name,
                    "label": svc.label,
                    "enabled": target,
                })

        # 停止イベントを記録
        stopped = [a["service"] for a in applied if not a["enabled"]]
        if stopped:
            self._record_stop_event(
                reason="manual_preset",
                reason_label=f'バッチプリセット「{BATCH_PRESETS[preset]["label"]}」',
                action="disable",
                services_affected=stopped,
                triggered_by="admin",
            )

        return {
            "preset": preset,
            "preset_label": BATCH_PRESETS[preset]["label"],
            "applied": applied,
        }

    # ── 状態取得 ─────────────────────────────────────────────────

    def get_control_state(self) -> dict:
        """管理ダッシュボード向けに全サービスの現在状態を返す。"""
        overrides = flags.get_overrides()
        services = []
        for svc in _AI_SERVICES:
            current_enabled = flags.is_enabled(svc.flag_key)
            base_enabled = bool(getattr(flags, svc.flag_key, True))
            is_high = svc.name in _HIGH_COST_NAMES or svc.is_high_cost
            services.append({
                "name": svc.name,
                "label": svc.label,
                "flag_key": svc.flag_key,
                "enabled": current_enabled,
                "base_enabled": base_enabled,
                "overridden": svc.flag_key in overrides,
                "is_high_cost": is_high,
                "api_only": svc.api_only,
                "admin_only": svc.admin_only,
                "free_member_uses": svc.free_member_uses,
            })

        return {
            "services": services,
            "presets": BATCH_PRESETS,
            "overrides": overrides,
            "has_overrides": bool(overrides),
        }

    # ── 予算ガード ────────────────────────────────────────────────

    def get_budget(self) -> BudgetGuard:
        """
        現在の予算状態を返す。
        Phase 16 以降は generation_log テーブルから実データを集計する。
        現時点はスタブ (設定値のみ、実使用量ゼロ)。
        """
        return BudgetGuard(
            daily_tokens_limit=settings.API_DAILY_TOKEN_LIMIT,
            daily_cost_limit_usd=settings.API_DAILY_COST_LIMIT_USD,
            monthly_tokens_limit=settings.API_MONTHLY_TOKEN_LIMIT,
            monthly_cost_limit_usd=settings.API_MONTHLY_COST_LIMIT_USD,
            warn_threshold_pct=settings.API_WARN_THRESHOLD_PCT,
            over_limit_action=settings.API_OVER_LIMIT_ACTION,
            mode="stub",
        )

    def is_within_budget(self) -> bool:
        """
        API 呼び出し前に予算内かどうかを確認する。
        over_limit_action="disable" かつ上限超過なら False を返す。
        Phase 16 で実データ連携後に実効化。
        """
        budget = self.get_budget()
        if budget.is_over_limit and budget.over_limit_action == "disable":
            return False
        return True

    def get_stop_history(self) -> list:
        """自動停止・手動停止の履歴を返す (UsageDashboardService 用)。"""
        from app.services.usage_dashboard_service import AutoStopEvent
        return [AutoStopEvent(**e) for e in self._stop_history]

    def _record_stop_event(
        self,
        reason: str,
        reason_label: str,
        action: str,
        services_affected: list[str],
        triggered_by: str = "system",
    ) -> None:
        """停止イベントを記録する (Phase 16 で DB 永続化予定)。"""
        from datetime import datetime
        self._stop_history.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "reason": reason,
            "reason_label": reason_label,
            "action": action,
            "services_affected": services_affected,
            "triggered_by": triggered_by,
        })
        # 最新 50 件のみ保持
        if len(self._stop_history) > 50:
            self._stop_history = self._stop_history[-50:]

    def check_budget_for_service(self, service_name: str) -> dict:
        """
        指定サービスに対して予算チェック結果を返す。
        {"allowed": bool, "warn_level": str, "message": str}
        """
        budget = self.get_budget()
        if budget.is_over_limit and budget.over_limit_action == "disable":
            return {
                "allowed": False,
                "warn_level": "critical",
                "message": "API予算上限に達しました。管理者に連絡してください。",
            }
        if budget.warn_level == "warn":
            return {
                "allowed": True,
                "warn_level": "warn",
                "message": f"API予算が警告しきい値 ({budget.warn_threshold_pct}%) に近づいています。",
            }
        return {"allowed": True, "warn_level": "none", "message": ""}


# グローバルシングルトン
api_control_service = ApiControlService()
