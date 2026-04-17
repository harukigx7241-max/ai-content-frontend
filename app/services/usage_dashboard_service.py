"""
app/services/usage_dashboard_service.py — Phase 14
管理者・管理本部向け API トークン使用量・コストダッシュボード。

Tiers:
  FREE  — モック/スタブデータ (リアルな形式・UIは完全動作)
  API   — OpenAI /v1/usage 等のコスト API から実データ取得 (Phase 16 本実装)
  DISABLED — ENABLE_API_USAGE_DASHBOARD=false 時

設計方針:
  - 全データ構造を Phase 16 の本実装に合わせて設計
  - FREE tier でも UI が完全動作するよう mock データを提供
  - HQ ロールには拡張データ (budget率・危険機能・自動停止履歴) を付与
  - _run_api() は OpenAI usage API 向けの scaffold (インターフェースのみ定義)
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional

from app.core.config import settings
from app.services.base import BaseService, ServiceMode, ServiceResult


# ─────────────────────────────────────────────────────────────────────────────
# データクラス
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict:
        return {
            "input": self.input_tokens,
            "output": self.output_tokens,
            "total": self.total,
        }


@dataclass
class PeriodUsage:
    label: str          # "今日" | "今月"
    tokens: TokenUsage = field(default_factory=TokenUsage)
    cost_usd: float = 0.0
    web_searches: int = 0
    api_calls: int = 0

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "tokens": self.tokens.to_dict(),
            "cost_usd": round(self.cost_usd, 6),
            "web_searches": self.web_searches,
            "api_calls": self.api_calls,
        }


@dataclass
class FeatureUsageRecord:
    feature: str           # service name (英語)
    label: str             # 日本語表示名
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    calls: int = 0
    is_high_cost: bool = False

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict:
        return {
            "feature": self.feature,
            "label": self.label,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "calls": self.calls,
            "is_high_cost": self.is_high_cost,
        }


@dataclass
class ModelUsageRecord:
    model: str
    provider: str          # "anthropic" | "openai" | "gemini" | "none"
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    calls: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "provider": self.provider,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "calls": self.calls,
        }


@dataclass
class AutoStopEvent:
    timestamp: str     # ISO 8601
    reason: str        # "daily_limit" | "monthly_limit" | "manual_preset" | "budget_guard"
    reason_label: str
    action: str        # "fallback" | "disable"
    services_affected: list[str] = field(default_factory=list)
    triggered_by: str = "system"

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "reason": self.reason,
            "reason_label": self.reason_label,
            "action": self.action,
            "services_affected": self.services_affected,
            "triggered_by": self.triggered_by,
        }


@dataclass
class HqExtendedData:
    """管理本部 (HQ) のみ表示される拡張分析データ。"""
    budget_daily_pct: float = 0.0
    budget_monthly_pct: float = 0.0
    projected_monthly_cost_usd: float = 0.0   # 月末予測コスト
    threshold_alerts: list[str] = field(default_factory=list)
    danger_features: list[str] = field(default_factory=list)
    auto_stop_history: list[AutoStopEvent] = field(default_factory=list)
    cost_trend_7d: list[float] = field(default_factory=list)  # 直近7日のコスト (USD)

    def to_dict(self) -> dict:
        return {
            "budget_daily_pct": round(self.budget_daily_pct, 1),
            "budget_monthly_pct": round(self.budget_monthly_pct, 1),
            "projected_monthly_cost_usd": round(self.projected_monthly_cost_usd, 4),
            "threshold_alerts": self.threshold_alerts,
            "danger_features": self.danger_features,
            "auto_stop_history": [e.to_dict() for e in self.auto_stop_history],
            "cost_trend_7d": [round(v, 6) for v in self.cost_trend_7d],
        }


@dataclass
class UsageDashboardData:
    """ダッシュボード全データ。"""
    today: PeriodUsage = field(default_factory=lambda: PeriodUsage(label="今日"))
    monthly: PeriodUsage = field(default_factory=lambda: PeriodUsage(label="今月"))
    feature_breakdown: list[FeatureUsageRecord] = field(default_factory=list)
    model_breakdown: list[ModelUsageRecord] = field(default_factory=list)
    top_cost_features: list[FeatureUsageRecord] = field(default_factory=list)
    mode: str = "mock"       # "mock" | "live"
    snapshot_at: str = ""    # ISO 8601
    hq: Optional[HqExtendedData] = None

    def to_dict(self, include_hq: bool = False) -> dict:
        result = {
            "today": self.today.to_dict(),
            "monthly": self.monthly.to_dict(),
            "feature_breakdown": [f.to_dict() for f in self.feature_breakdown],
            "model_breakdown": [m.to_dict() for m in self.model_breakdown],
            "top_cost_features": [f.to_dict() for f in self.top_cost_features],
            "mode": self.mode,
            "snapshot_at": self.snapshot_at,
        }
        if include_hq and self.hq:
            result["hq"] = self.hq.to_dict()
        return result


# ─────────────────────────────────────────────────────────────────────────────
# モック費用レート (OpenAI / Anthropic 参考値 — Phase 16 で実実績に差し替え)
# ─────────────────────────────────────────────────────────────────────────────

_COST_PER_1K_INPUT = {
    "claude-haiku-4-5-20251001": 0.00025,
    "claude-sonnet-4-6":         0.003,
    "gpt-4o-mini":               0.00015,
    "gpt-4o":                    0.005,
    "gemini-1.5-flash":          0.000075,
    "gemini-1.5-pro":            0.00125,
}
_COST_PER_1K_OUTPUT = {
    "claude-haiku-4-5-20251001": 0.00125,
    "claude-sonnet-4-6":         0.015,
    "gpt-4o-mini":               0.0006,
    "gpt-4o":                    0.015,
    "gemini-1.5-flash":          0.0003,
    "gemini-1.5-pro":            0.005,
}


def _cost(model: str, inp: int, out: int) -> float:
    ri = _COST_PER_1K_INPUT.get(model, 0.00025)
    ro = _COST_PER_1K_OUTPUT.get(model, 0.00125)
    return inp / 1000 * ri + out / 1000 * ro


# ─────────────────────────────────────────────────────────────────────────────
# モックデータビルダー
# ─────────────────────────────────────────────────────────────────────────────

def _build_mock(is_hq: bool = False) -> UsageDashboardData:
    """
    APIキー未設定時に表示するリアルなモックデータを生成する。
    シード固定で「毎回同じ」表示にする。
    """
    day_of_month = date.today().day  # 当月経過日数

    # ── モデル選択 (設定済みキーを優先) ─────────────────────────────
    primary_model = settings.ANTHROPIC_MODEL if settings.ANTHROPIC_API_KEY else \
                    settings.OPENAI_MODEL    if settings.OPENAI_API_KEY    else \
                    settings.GEMINI_MODEL    if settings.GEMINI_API_KEY    else \
                    "claude-haiku-4-5-20251001"
    provider_map = {
        "claude": "anthropic",
        "gpt":    "openai",
        "gemini": "gemini",
    }
    primary_provider = next(
        (v for k, v in provider_map.items() if primary_model.startswith(k)),
        "anthropic",
    )

    # ── 今日の使用量 ─────────────────────────────────────────────────
    today_input  = 1_240
    today_output = 870
    today_cost   = _cost(primary_model, today_input, today_output)
    today_searches = 8
    today_calls    = 23

    today_usage = PeriodUsage(
        label="今日",
        tokens=TokenUsage(input_tokens=today_input, output_tokens=today_output),
        cost_usd=today_cost,
        web_searches=today_searches,
        api_calls=today_calls,
    )

    # ── 今月の使用量 ─────────────────────────────────────────────────
    month_input  = today_input  * day_of_month + 8_300
    month_output = today_output * day_of_month + 5_100
    month_cost   = _cost(primary_model, month_input, month_output)
    month_searches = today_searches * day_of_month + 44
    month_calls    = today_calls    * day_of_month + 180

    monthly_usage = PeriodUsage(
        label="今月",
        tokens=TokenUsage(input_tokens=month_input, output_tokens=month_output),
        cost_usd=month_cost,
        web_searches=month_searches,
        api_calls=month_calls,
    )

    # ── 機能別内訳 ────────────────────────────────────────────────────
    feature_ratios = [
        ("prompt_forge",       "プロンプト鍛冶場",     0.38, False),
        ("prompt_doctor",      "プロンプト診断",       0.22, False),
        ("guild_guide_ai",     "ギルドガイドAI",       0.14, False),
        ("guild_scribe_ai",    "ギルド書記AI",         0.10, False),
        ("campaign_forge",     "キャンペーン工房",      0.07, False),
        ("language_quality_ai","日本語品質チェック",    0.05, False),
        ("workshop_master_ai", "ワークショップマスター", 0.03, True),
        ("article_draft_ai",   "記事下書きAI",         0.01, True),
    ]
    feature_records: list[FeatureUsageRecord] = []
    for fname, flabel, ratio, is_hc in feature_ratios:
        fi = int(month_input  * ratio)
        fo = int(month_output * ratio)
        fc = _cost(primary_model, fi, fo)
        feature_records.append(FeatureUsageRecord(
            feature=fname, label=flabel,
            input_tokens=fi, output_tokens=fo,
            cost_usd=fc,
            calls=int(month_calls * ratio),
            is_high_cost=is_hc,
        ))

    top_cost = sorted(feature_records, key=lambda r: r.cost_usd, reverse=True)[:5]

    # ── モデル別内訳 ──────────────────────────────────────────────────
    model_records = [
        ModelUsageRecord(
            model=primary_model,
            provider=primary_provider,
            input_tokens=int(month_input  * 0.85),
            output_tokens=int(month_output * 0.85),
            cost_usd=_cost(primary_model, int(month_input * 0.85), int(month_output * 0.85)),
            calls=int(month_calls * 0.85),
        ),
        ModelUsageRecord(
            model="gemini-1.5-flash",
            provider="gemini",
            input_tokens=int(month_input  * 0.15),
            output_tokens=int(month_output * 0.15),
            cost_usd=_cost("gemini-1.5-flash", int(month_input * 0.15), int(month_output * 0.15)),
            calls=int(month_calls * 0.15),
        ),
    ]

    # ── HQ 拡張データ ─────────────────────────────────────────────────
    hq_data: Optional[HqExtendedData] = None
    if is_hq:
        daily_limit  = settings.API_DAILY_TOKEN_LIMIT
        monthly_limit = settings.API_MONTHLY_TOKEN_LIMIT

        daily_pct   = (today_input + today_output) / daily_limit   * 100 if daily_limit   else 0.0
        monthly_pct = (month_input + month_output) / monthly_limit * 100 if monthly_limit else 0.0

        # 月末予測コスト (経過日数で線形外挿)
        days_in_month  = 30
        projected_cost = month_cost / day_of_month * days_in_month if day_of_month > 0 else month_cost

        # 警告
        alerts: list[str] = []
        warn_pct = settings.API_WARN_THRESHOLD_PCT
        if daily_pct   >= warn_pct: alerts.append(f"日次トークン使用量が {warn_pct}% に達しました")
        if monthly_pct >= warn_pct: alerts.append(f"月次トークン使用量が {warn_pct}% に達しました")
        monthly_cost_limit = settings.API_MONTHLY_COST_LIMIT_USD
        if monthly_cost_limit and month_cost / monthly_cost_limit * 100 >= warn_pct:
            alerts.append(f"月次コストが警告しきい値を超えました (${month_cost:.4f} / ${monthly_cost_limit})")

        # 危険機能 (高コスト + 使用率高い)
        danger = [r.label for r in feature_records if r.is_high_cost and r.calls > 5]

        # 直近7日コスト推移 (疑似データ)
        base_daily = today_cost
        trend = [round(base_daily * (0.7 + 0.1 * i), 6) for i in range(7)]

        # 自動停止履歴 — api_control_service のメモリから取得
        from app.services.api_control_service import api_control_service
        stop_history = api_control_service.get_stop_history()

        hq_data = HqExtendedData(
            budget_daily_pct=daily_pct,
            budget_monthly_pct=monthly_pct,
            projected_monthly_cost_usd=projected_cost,
            threshold_alerts=alerts,
            danger_features=danger,
            auto_stop_history=stop_history,
            cost_trend_7d=trend,
        )

    return UsageDashboardData(
        today=today_usage,
        monthly=monthly_usage,
        feature_breakdown=feature_records,
        model_breakdown=model_records,
        top_cost_features=top_cost,
        mode="mock",
        snapshot_at=datetime.utcnow().isoformat() + "Z",
        hq=hq_data,
    )


# ─────────────────────────────────────────────────────────────────────────────
# UsageDashboardService
# ─────────────────────────────────────────────────────────────────────────────

class UsageDashboardService(BaseService):
    FLAG_KEY = "API_USAGE_DASHBOARD"

    def get_report(self, is_hq: bool = False) -> ServiceResult:
        """
        使用量ダッシュボードデータを返す。
        is_hq=True の場合は HQ 拡張データも含む。
        """
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        if mode == ServiceMode.API:
            try:
                return self._run_api(is_hq=is_hq)
            except Exception:
                return self._run_fallback(is_hq=is_hq)
        return self._run_free(is_hq=is_hq)

    # ── FREE: モック ─────────────────────────────────────────────

    def _run_free(self, is_hq: bool = False, **_: object) -> ServiceResult:
        data = _build_mock(is_hq=is_hq)
        return ServiceResult.free(
            content=data.to_dict(include_hq=is_hq),
            hint="モックデータを表示しています。APIキーを接続すると実データが取得できます。",
        )

    # ── API: OpenAI usage API scaffold (未実装) ──────────────────

    def _run_api(self, is_hq: bool = False, **_: object) -> ServiceResult:
        """
        TODO Phase 16: OpenAI /v1/usage エンドポイントから実データを取得する。

        実装予定:
          GET https://api.openai.com/v1/usage
          Authorization: Bearer {OPENAI_API_KEY}
          Parameters: date (YYYY-MM-DD), group_by=model

        Anthropic / Gemini は各プロバイダーの usage API を利用予定。
        複数プロバイダーのデータを UsageDashboardData に統合する。
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_fallback(self, **kwargs: object) -> ServiceResult:
        return self._run_free(**kwargs)


# グローバルシングルトン
usage_dashboard_service = UsageDashboardService()
