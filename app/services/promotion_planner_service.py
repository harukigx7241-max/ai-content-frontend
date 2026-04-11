"""
app/services/promotion_planner_service.py
プロモーションプランナーサービス。コンテンツ販売の集客プランを生成する。

Tiers:
  FREE  — テンプレートベースの集客プランプロンプト生成
  API   — LLMによるカスタム集客戦略生成 (未実装)
  DISABLED — ENABLE_PROMOTION_PLANNER=false 時

Phase 21 で本実装予定。
"""
from __future__ import annotations

from app.services.base import BaseService, ServiceMode, ServiceResult

# ─────────────────────────────────────────────────────────────────────────────
# テンプレート (FREE tier)
# ─────────────────────────────────────────────────────────────────────────────

_PROMO_TEMPLATE = """\
あなたはデジタルコンテンツ販売で月収200万円を達成したマーケターです。
以下の商品・サービスの集客プランを作成してください。

【商品・サービス名】{product_name}
【プラットフォーム】{platform}
【価格】{price}円
【ターゲット読者】{target}
【強み・差別化ポイント】{strengths}

以下を含む集客プランを作成してください:
1. SNS告知スケジュール (1週間分)
2. X(Twitter)投稿文3パターン
3. 無料公開コンテンツ案 (集客用ティザー)
4. フォロワーへのDMテンプレート
5. 販売ページのキャッチコピー3案

数字・具体例を豊富に使い、すぐに実行できる内容にしてください。
"""


class PromotionPlannerService(BaseService):
    FLAG_KEY = "PROMOTION_PLANNER"

    def build_plan(
        self,
        product_name: str,
        platform: str = "note",
        price: int = 0,
        target: str = "",
        strengths: str = "",
    ) -> ServiceResult:
        """プロモーションプランのプロンプトを生成する。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        if mode == ServiceMode.API:
            try:
                return self._run_api(
                    product_name=product_name,
                    platform=platform,
                    price=price,
                    target=target,
                    strengths=strengths,
                )
            except Exception:
                return self._run_fallback(
                    product_name=product_name,
                    platform=platform,
                    price=price,
                    target=target,
                    strengths=strengths,
                )
        return self._run_free(
            product_name=product_name,
            platform=platform,
            price=price,
            target=target,
            strengths=strengths,
        )

    # ── FREE: テンプレートベース ─────────────────────────────────

    def _run_free(
        self,
        product_name: str = "",
        platform: str = "note",
        price: int = 0,
        target: str = "",
        strengths: str = "",
        **_: object,
    ) -> ServiceResult:
        prompt = _PROMO_TEMPLATE.format(
            product_name=product_name or "商品名未入力",
            platform=platform,
            price=price,
            target=target or "副業・収入アップに興味がある方",
            strengths=strengths or "独自の視点と実体験に基づく内容",
        )
        return ServiceResult.free(content={"prompt": prompt})

    # ── API: LLMカスタム集客戦略 (未実装) ───────────────────────

    def _run_api(self, **kwargs: object) -> ServiceResult:
        """
        TODO: LLM を使って市場分析・競合分析を含むカスタム集客戦略を生成。
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_fallback(self, **kwargs: object) -> ServiceResult:
        return self._run_free(**{k: v for k, v in kwargs.items()})


# グローバルシングルトン
promotion_planner_service = PromotionPlannerService()
