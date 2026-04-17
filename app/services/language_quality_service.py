"""
app/services/language_quality_service.py
日本語品質チェックサービス。

Tiers:
  FREE  — ルールベースチェック (Phase 8 強化版)
  LITE  — 将来: 軽量モデルによる添削 (未実装)
  API   — LLM日本語添削・文体統一 (未実装)
  DISABLED — ENABLE_LANGUAGE_QUALITY_AI=false 時

FREE チェック項目 (Phase 8):
  1. 文体一貫性 (です・ます / だ・である 混在)
  2. 語尾連発 (同じ語尾が3回以上連続)
  3. 冗長な文 (80字超)
  4. 英語混入過多 (ASCII比率)
  5. 直訳っぽさ (「〜という」連発・「的な」多用)
  6. AIっぽい定型文
  7. 記号過多
  8. 半角カタカナ
  9. 全角数字
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.services.base import BaseService, ServiceMode, ServiceResult


# ─────────────────────────────────────────────────────────────────────────────
# 品質チェック結果型
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LanguageCheckResult:
    score: int                          # 0-100
    grade: str = "C"                    # S/A/B/C/D
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    tone: str = "unknown"               # "desu_masu" | "da_dearu" | "mixed" | "unknown"
    mode: str = "free"
    upgrade_hint: str = ""

    def __post_init__(self) -> None:
        if self.score >= 90:
            self.grade = "S"
        elif self.score >= 75:
            self.grade = "A"
        elif self.score >= 55:
            self.grade = "B"
        elif self.score >= 35:
            self.grade = "C"
        else:
            self.grade = "D"

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "grade": self.grade,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "tone": self.tone,
            "mode": self.mode,
            "upgrade_hint": self.upgrade_hint,
        }


# ─────────────────────────────────────────────────────────────────────────────
# LanguageQualityService
# ─────────────────────────────────────────────────────────────────────────────

class LanguageQualityService(BaseService):
    FLAG_KEY = "LANGUAGE_QUALITY_AI"

    # AIっぽい定型文
    _AI_BOILERPLATE = [
        "もちろん", "もちろんです", "もちろんございます",
        "おっしゃる通り", "おっしゃる通りです",
        "素晴らしい", "素晴らしいですね",
        "なるほど", "なるほどですね",
        "確かに", "確かにそうですね",
        "承知しました", "かしこまりました",
        "ご指摘の通り",
        "ありがとうございます。以下に",
        "以下にご提案します",
        "以下の通りです",
    ]

    # 直訳パターン
    _LITERAL_TRANSLATION_PATTERNS = [
        (r"(という|といった|というような|というものの|というわけ){3,}", "「〜という」の連発（直訳っぽさ）"),
        (r"(的な|的に|的){4,}", "「〜的」の多用"),
        (r"(することができ|することが可能){2,}", "「することができ」の繰り返し（→「できる」に簡略化可）"),
        (r"(において|に関して|に対して|に際して){3,}", "「において」等の連発"),
        (r"(いる|います|いました)(。|\n).*?(いる|います|いました)(。|\n)", "文末「いる/います」の繰り返し"),
    ]

    # 記号過多しきい値
    _SYMBOL_RE = re.compile(r"[！!？?…★☆◆◇■□▶▷→←↓↑※〇●◎]")

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

    def _rule_check(self, text: str) -> LanguageCheckResult:  # noqa: C901
        score = 100
        issues: list[str] = []
        suggestions: list[str] = []

        if not text.strip():
            return LanguageCheckResult(
                score=0, issues=["テキストが空です"], suggestions=["診断するテキストを入力してください"],
                tone="unknown", mode="free",
            )

        # ── チェック 1: 文体一貫性 ──────────────────────────────
        desu_masu = len(re.findall(r"(です|ます|でしょう|ましょう)[。、\s！？]", text))
        da_dearu  = len(re.findall(r"(?<![でし])(だ|である|だろう)[。、\s！？]", text))

        if desu_masu > 0 and da_dearu > 0:
            tone = "mixed"
            penalty = min(25, (min(desu_masu, da_dearu)) * 5)
            score -= penalty
            issues.append(f"文体が混在しています（です・ます調: {desu_masu}回 / だ・である調: {da_dearu}回）")
            suggestions.append("どちらかの文体に統一してください")
        elif desu_masu >= da_dearu:
            tone = "desu_masu"
        elif da_dearu > desu_masu:
            tone = "da_dearu"
        else:
            tone = "unknown"

        # ── チェック 2: 語尾連発 ────────────────────────────────
        sentences = [s.strip() for s in re.split(r"[。！？\n]", text) if s.strip()]
        if len(sentences) >= 3:
            endings = [s[-3:] if len(s) >= 3 else s for s in sentences]
            # 3連続で同じ語尾
            for i in range(len(endings) - 2):
                if endings[i] == endings[i+1] == endings[i+2] and len(endings[i]) > 1:
                    score -= 12
                    issues.append(f"語尾「…{endings[i]}」が3回以上連続しています")
                    suggestions.append("語尾のパターンをバリエーション豊かにしてください")
                    break

        # ── チェック 3: 冗長な文 (80字超) ───────────────────────
        long_sentences = [s for s in sentences if len(s) > 80]
        if len(long_sentences) >= 3:
            score -= 15
            issues.append(f"長すぎる文が {len(long_sentences)} 個あります（80字超）")
            suggestions.append("1文は50〜70字を目安に分割してください")
        elif len(long_sentences) >= 1:
            score -= 5
            suggestions.append(f"長い文が {len(long_sentences)} 個あります。可能なら分割しましょう")

        # ── チェック 4: 英語混入過多 ─────────────────────────────
        total = max(len(text), 1)
        ascii_count = sum(1 for c in text if ord(c) < 128 and c not in ' \t\n\r\u3000')
        ascii_ratio = ascii_count / total
        if ascii_ratio > 0.45:
            score -= 20
            issues.append(f"英語・ASCII 文字が多すぎます（比率: {ascii_ratio:.0%}）")
            suggestions.append("日本語読者向けのコンテンツは日本語で書いてください。専門用語は括弧内に英語を補足する程度にとどめましょう")
        elif ascii_ratio > 0.25:
            score -= 8
            suggestions.append(f"英語が若干多めです（比率: {ascii_ratio:.0%}）。不要なカタカナ英語は日本語に置き換えましょう")

        # ── チェック 5: 直訳っぽさ ────────────────────────────────
        for pattern, desc in self._LITERAL_TRANSLATION_PATTERNS:
            if re.search(pattern, text):
                score -= 8
                issues.append(desc)
                suggestions.append(f"「{desc}」は自然な日本語に書き換えると読みやすくなります")
                break  # 1件だけ報告

        # ── チェック 6: AIっぽい定型文 ──────────────────────────
        ai_found = [phrase for phrase in self._AI_BOILERPLATE if phrase in text]
        if len(ai_found) >= 3:
            score -= 18
            issues.append(f"AI 生成っぽい定型文が多い（例: {', '.join(ai_found[:3])}）")
            suggestions.append("「もちろん」「おっしゃる通り」などの定型表現を削除し、自然な文章にしてください")
        elif len(ai_found) >= 1:
            score -= 6
            suggestions.append(f"AI らしい定型文が含まれています（{', '.join(ai_found[:2])}）。書き直しを検討してください")

        # ── チェック 7: 記号過多 ─────────────────────────────────
        symbol_count = len(self._SYMBOL_RE.findall(text))
        char_count = max(len(text), 1)
        symbol_ratio = symbol_count / char_count
        if symbol_ratio > 0.08:
            score -= 12
            issues.append(f"記号・装飾文字が多すぎます（{symbol_count} 個）")
            suggestions.append("「！！」「★☆」などの過剰な記号を減らしてください。読みやすさが上がります")
        elif symbol_ratio > 0.04:
            score -= 4
            suggestions.append("記号が若干多めです。適度に抑えましょう")

        # ── チェック 8: 半角カタカナ ─────────────────────────────
        if re.search(r"[\uff65-\uff9f]", text):
            score -= 8
            issues.append("半角カタカナが含まれています")
            suggestions.append("全角カタカナに統一してください（例: ｱｲｳ → アイウ）")

        # ── チェック 9: 全角数字 ──────────────────────────────────
        fullwidth_digits = re.findall(r"[０-９]+", text)
        if fullwidth_digits:
            score -= 5
            suggestions.append(f"全角数字（{', '.join(fullwidth_digits[:3])}）は半角に統一するとスッキリします")

        # ── チェック 10: 句読点重複 ──────────────────────────────
        if re.search(r"[、，][、，]|[。．][。．]", text):
            score -= 5
            issues.append("重複する句読点があります（例: ,,  ..）")
            suggestions.append("句読点の重複を取り除いてください")

        upgrade_hint = (
            "AI版（準備中）では、LLM が文体を統一し、"
            "より自然な日本語への書き換え案を提示します。"
        )

        return LanguageCheckResult(
            score=max(0, score),
            issues=issues,
            suggestions=suggestions,
            tone=tone,
            mode="free",
            upgrade_hint=upgrade_hint,
        )

    # ── LITE / API: 将来実装 ──────────────────────────────────────

    def _run_api(self, text: str = "", **_: object) -> ServiceResult:
        """
        TODO Phase 20+: LLM で文体統一・自然な書き換え案生成。
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_fallback(self, **kwargs: object) -> ServiceResult:
        return self._run_free(**kwargs)


# グローバルシングルトン
language_quality_service = LanguageQualityService()
