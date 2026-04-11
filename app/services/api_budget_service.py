"""
app/services/api_budget_service.py
API予算・利用量管理サービス。API利用量のトラッキングと予算制限を担う。

Tiers:
  FREE  — スタブ (データなし、常にゼロ表示)
  API   — 生成ログDBからの集計・コスト計算 (Phase 16で本実装)
  DISABLED — ENABLE_API_USAGE_DASHBOARD=false 時

Phase 16 で generation_log テーブルとともに本実装予定。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.core.config import settings
from app.services.base import BaseService, ServiceMode, ServiceResult


@dataclass
class BudgetStatus:
    monthly_tokens_used: int = 0
    monthly_tokens_limit: int = 0         # 0 = 無制限
    monthly_cost_usd: float = 0.0
    monthly_cost_limit_usd: float = 0.0   # 0 = 無制限
    is_over_limit: bool = False
    over_limit_action: str = "fallback"
    mode: str = "free"

    @property
    def usage_pct(self) -> float:
        if self.monthly_tokens_limit == 0:
            return 0.0
        return min(100.0, self.monthly_tokens_used / self.monthly_tokens_limit * 100)

    @property
    def cost_pct(self) -> float:
        if self.monthly_cost_limit_usd == 0:
            return 0.0
        return min(100.0, self.monthly_cost_usd / self.monthly_cost_limit_usd * 100)

    def to_dict(self) -> dict:
        return {
            "monthly_tokens_used": self.monthly_tokens_used,
            "monthly_tokens_limit": self.monthly_tokens_limit,
            "monthly_cost_usd": round(self.monthly_cost_usd, 4),
            "monthly_cost_limit_usd": self.monthly_cost_limit_usd,
            "usage_pct": round(self.usage_pct, 1),
            "cost_pct": round(self.cost_pct, 1),
            "is_over_limit": self.is_over_limit,
            "over_limit_action": self.over_limit_action,
            "mode": self.mode,
        }


class ApiBudgetService(BaseService):
    FLAG_KEY = "API_USAGE_DASHBOARD"

    def get_status(self) -> ServiceResult:
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        # FREE でも stub データを返す (管理画面 UI のため)
        return self._run_free()

    def is_within_budget(self) -> bool:
        """
        API 呼び出し前に予算内かどうかを確認する。
        Phase 16 以降は実際のDBデータで判定。現時点は常に True。
        """
        return True

    def record_usage(self, tokens: int, cost_usd: float = 0.0, service: str = "") -> None:
        """
        API 使用量を記録する。
        Phase 16 で generation_log テーブルへの書き込みに差し替える。
        """
        # TODO: Phase 16 — generation_log テーブルに書き込む
        pass

    # ── FREE: スタブ ────────────────────────────────────────────

    def _run_free(self, **_: object) -> ServiceResult:
        stub = BudgetStatus(
            monthly_tokens_limit=settings.API_MONTHLY_TOKEN_LIMIT,
            monthly_cost_limit_usd=settings.API_MONTHLY_COST_LIMIT_USD,
            over_limit_action=settings.API_OVER_LIMIT_ACTION,
            mode="free",
        )
        return ServiceResult.free(
            content=stub.to_dict(),
            hint="利用量データは Phase 16 実装後に表示されます",
        )

    # ── API: 生成ログ集計 (未実装) ─────────────────────────────

    def _run_api(self, **_: object) -> ServiceResult:
        """
        TODO: generation_log テーブルから当月のトークン使用量・コストを集計。
        """
        return ServiceResult.not_implemented(ServiceMode.API)


# グローバルシングルトン
api_budget_service = ApiBudgetService()
