"""
app/services/language_quality_service.py
日本語品質チェックサービス。生成されたプロンプトの日本語品質を評価する。

Tiers:
  FREE  — ルールベースチェック (句読点・文体・語尾一貫性・敬語チェック)
  API   — LLM日本語添削・文体統一 (未実装)
  DISABLED — ENABLE_LANGUAGE_QUALITY_AI=false 時
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.services.base import BaseService, ServiceMode, ServiceResult


@dataclass
class LanguageCheckResult:
    score: int                       # 0-100
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    tone: str = "unknown"            # "desu_masu" | "da_dearu" | "mixed" | "unknown"
    mode: str = "free"

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "tone": self.tone,
            "mode": self.mode,
        }


class LanguageQualityService(BaseService):
    FLAG_KEY = "LANGUAGE_QUALITY_AI"

    def check(self, text: str) -> ServiceResult:
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        if mode == ServiceMode.API:
            try:
                return self._run_api(text=text)
            except Exception:
                return self._run_fallback(text=text)
        return self._run_free(text=text)

    # ── FREE: ルールベースチェック ─────────────────────────────────

    def _run_free(self, text: str = "", **_: object) -> ServiceResult:
        result = self._rule_check(text)
        return ServiceResult.free(content=result.to_dict())

    def _rule_check(self, text: str) -> LanguageCheckResult:
        score = 100
        issues: list[str] = []
        suggestions: list[str] = []

        # ── 文体判定 ──────────────────────────────────────────────
        desu_masu = len(re.findall(r"(です|ます|でしょう|ましょう)[。、\s]", text))
        da_dearu = len(re.findall(r"(だ|である|だろう)[。、\s]", text))

        if desu_masu > 0 and da_dearu > 0:
            tone = "mixed"
            score -= 20
            issues.append("文体が混在しています (です・ます調 と だ・である調)")
            suggestions.append("どちらかの文体に統一してください")
        elif desu_masu > da_dearu:
            tone = "desu_masu"
        elif da_dearu > desu_masu:
            tone = "da_dearu"
        else:
            tone = "unknown"

        # ── 句読点チェック ─────────────────────────────────────────
        if "、、" in text or "。。" in text:
            score -= 10
            issues.append("重複する句読点があります")

        # ── 長い文チェック (80文字超) ─────────────────────────────
        sentences = re.split(r"[。！？]", text)
        long_sentences = [s for s in sentences if len(s) > 80]
        if len(long_sentences) > 2:
            score -= 15
            issues.append(f"{len(long_sentences)}個の文が80文字を超えています")
            suggestions.append("長い文を分割して読みやすくしましょう")

        # ── 半角カタカナチェック ─────────────────────────────────
        if re.search(r"[\uff65-\uff9f]", text):
            score -= 10
            issues.append("半角カタカナが含まれています")
            suggestions.append("全角カタカナに統一してください")

        # ── 全角数字チェック ──────────────────────────────────────
        if re.search(r"[０-９]", text):
            score -= 5
            suggestions.append("全角数字は半角数字に統一するとスッキリします")

        return LanguageCheckResult(
            score=max(0, score),
            issues=issues,
            suggestions=suggestions,
            tone=tone,
            mode="free",
        )

    # ── API: LLM日本語添削 (未実装) ───────────────────────────────

    def _run_api(self, text: str = "", **_: object) -> ServiceResult:
        """
        TODO: LLM を使って自然な日本語に添削。
        - 文体統一
        - より自然な言い回しへの置換
        - ニュアンスの改善
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_fallback(self, **kwargs: object) -> ServiceResult:
        return self._run_free(**kwargs)


# グローバルシングルトン
language_quality_service = LanguageQualityService()
