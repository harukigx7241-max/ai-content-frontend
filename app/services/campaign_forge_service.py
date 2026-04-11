"""
app/services/campaign_forge_service.py
キャンペーン工房サービス。SNS告知・キャンペーン文のプロンプト生成。

Tiers:
  FREE  — テンプレートベースのキャンペーンプロンプト生成
  API   — LLMによるカスタムキャンペーン戦略生成 (未実装)
  DISABLED — ENABLE_CAMPAIGN_FORGE=false 時

Phase 21 で本実装予定。
"""
from __future__ import annotations

from app.services.base import BaseService, ServiceMode, ServiceResult

# ─────────────────────────────────────────────────────────────────────────────
# テンプレート (FREE tier)
# ─────────────────────────────────────────────────────────────────────────────

_CAMPAIGN_TEMPLATES: dict[str, str] = {
    "note_launch": """\
あなたはnoteで月50万円を稼ぐカリスマクリエイターです。
以下の新記事リリースに合わせたSNS告知文を3パターン作成してください。

【記事タイトル】{title}
【ターゲット読者】{target}
【記事の価値】{value}
【価格】{price}円

各パターンはX(Twitter)・Instagram・Threads向けに最適化してください。
CTA（購入ボタン）へ誘導する文言を必ず入れてください。
""",
    "cw_profile": """\
あなたはクラウドワークスで月収100万円を稼ぐトップフリーランサーです。
以下の情報を元にクライアントに刺さるプロフィール文を作成してください。

【スキル】{skills}
【経験】{experience}
【得意分野】{specialty}
【実績】{achievements}

プロフィール文は500文字以内で、クライアントの課題解決視点で書いてください。
""",
    "fortune_coconala": """\
あなたはココナラで星5評価・2000件超えのカリスマ占い師です。
以下の情報を元に購買意欲を高める商品説明文を作成してください。

【占い種類】{type}
【得意分野】{specialty}
【価格】{price}円
【所要時間】{duration}

タイトル案3つと詳細説明文を作成してください。
""",
}


class CampaignForgeService(BaseService):
    FLAG_KEY = "CAMPAIGN_FORGE"

    def build_prompt(
        self,
        campaign_type: str,
        **kwargs: str,
    ) -> ServiceResult:
        """キャンペーンプロンプトを生成する。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        if mode == ServiceMode.API:
            try:
                return self._run_api(campaign_type=campaign_type, **kwargs)
            except Exception:
                return self._run_fallback(campaign_type=campaign_type, **kwargs)
        return self._run_free(campaign_type=campaign_type, **kwargs)

    # ── FREE: テンプレートベース ─────────────────────────────────

    def _run_free(
        self, campaign_type: str = "note_launch", **kwargs: str
    ) -> ServiceResult:
        template = _CAMPAIGN_TEMPLATES.get(campaign_type)
        if template is None:
            return ServiceResult.free(
                content={"prompt": "", "error": f"不明なキャンペーン種類: {campaign_type}"},
                hint="対応していないキャンペーン種類です",
            )
        try:
            prompt = template.format(**kwargs)
        except KeyError as e:
            return ServiceResult.free(
                content={"prompt": template, "missing_key": str(e)},
                hint=f"入力が不足しています: {e}",
            )
        return ServiceResult.free(content={"prompt": prompt, "type": campaign_type})

    # ── API: LLMキャンペーン戦略 (未実装) ───────────────────────

    def _run_api(self, campaign_type: str = "", **kwargs: str) -> ServiceResult:
        """
        TODO: LLM を使って戦略的キャンペーンコンテンツを生成。
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_fallback(self, **kwargs: object) -> ServiceResult:
        return self._run_free(**{k: str(v) for k, v in kwargs.items()})

    def available_types(self) -> list[str]:
        return list(_CAMPAIGN_TEMPLATES.keys())


# グローバルシングルトン
campaign_forge_service = CampaignForgeService()
