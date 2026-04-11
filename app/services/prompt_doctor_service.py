"""
app/services/prompt_doctor_service.py
プロンプト診断サービス。生成されたプロンプトの品質を評価し改善提案を返す。

Tiers:
  FREE  — ルールベーススコアリング (文字数・役割定義・具体性・日本語チェック)
  API   — LLM詳細診断・具体的改善提案 (未実装)
  DISABLED — ENABLE_PROMPT_DOCTOR=false 時

Phase 20 で本実装予定。現時点では FREE tier の骨組みのみ。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.services.base import BaseService, ServiceMode, ServiceResult


# ─────────────────────────────────────────────────────────────────────────────
# 診断結果型
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DiagnosisResult:
    score: int                     # 0-100
    stars: int = 0                 # 1-5 (スコアから自動計算)
    issues: list[str] = field(default_factory=list)   # 問題点
    hints: list[str] = field(default_factory=list)    # 改善ヒント
    strengths: list[str] = field(default_factory=list)  # 良い点
    mode: str = "free"

    def __post_init__(self) -> None:
        self.stars = max(1, min(5, (self.score // 20) + 1))

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "stars": self.stars,
            "issues": self.issues,
            "hints": self.hints,
            "strengths": self.strengths,
            "mode": self.mode,
        }


# ─────────────────────────────────────────────────────────────────────────────
# PromptDoctorService
# ─────────────────────────────────────────────────────────────────────────────

class PromptDoctorService(BaseService):
    FLAG_KEY = "PROMPT_DOCTOR"

    def diagnose(self, prompt_text: str) -> ServiceResult:
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        if mode == ServiceMode.API:
            try:
                return self._run_api(prompt_text=prompt_text)
            except Exception:
                return self._run_fallback(prompt_text=prompt_text)
        return self._run_free(prompt_text=prompt_text)

    # ── FREE: ルールベース診断 ─────────────────────────────────────

    def _run_free(self, prompt_text: str = "", **_: object) -> ServiceResult:
        result = self._rule_based_diagnosis(prompt_text)
        return ServiceResult.free(content=result.to_dict())

    def _rule_based_diagnosis(self, text: str) -> DiagnosisResult:
        score = 0
        issues: list[str] = []
        hints: list[str] = []
        strengths: list[str] = []

        # ── チェック 1: 文字数 ─────────────────────────────────────
        length = len(text)
        if length >= 300:
            score += 25
            strengths.append("十分な文字数があります")
        elif length >= 100:
            score += 15
            hints.append("もう少し詳細を追加するとより良いプロンプトになります")
        else:
            issues.append("プロンプトが短すぎます (100文字以上を推奨)")
            hints.append("背景・目的・条件を追加してください")

        # ── チェック 2: 役割定義 ─────────────────────────────────────
        role_patterns = [
            r"あなたは.{2,30}(です|である|として)",
            r"専門家",
            r"プロ",
            r"エキスパート",
            r"として振る舞",
        ]
        has_role = any(re.search(p, text) for p in role_patterns)
        if has_role:
            score += 25
            strengths.append("役割定義が含まれています")
        else:
            issues.append("役割定義がありません")
            hints.append("「あなたは〇〇の専門家です」から始めると品質が上がります")

        # ── チェック 3: 具体性 ─────────────────────────────────────
        concrete_patterns = [
            r"\d+",         # 数字
            r"例えば|たとえば|具体的に",
            r"ステップ|手順|Step",
            r"【|】|\[|\]",  # 構造化マーカー
        ]
        concrete_count = sum(1 for p in concrete_patterns if re.search(p, text))
        if concrete_count >= 3:
            score += 25
            strengths.append("具体的な指示が含まれています")
        elif concrete_count >= 1:
            score += 10
            hints.append("具体的な数字・例・ステップを追加するとより効果的です")
        else:
            issues.append("具体性が不足しています")
            hints.append("数字・例・ステップ形式を使って指示を具体化してください")

        # ── チェック 4: 出力形式指定 ─────────────────────────────────
        format_patterns = [
            r"箇条書き|リスト形式|番号付き",
            r"文字(程度|以内|以上)",
            r"セクション|章|項目",
            r"マークダウン|Markdown",
            r"表形式|テーブル",
        ]
        has_format = any(re.search(p, text) for p in format_patterns)
        if has_format:
            score += 15
            strengths.append("出力形式の指定があります")
        else:
            hints.append("出力形式（箇条書き・文字数・セクション）を指定するとより使いやすくなります")

        # ── チェック 5: 日本語品質 ─────────────────────────────────
        ascii_ratio = sum(1 for c in text if ord(c) < 128) / max(len(text), 1)
        if ascii_ratio < 0.3:
            score += 10
            strengths.append("日本語が適切に使われています")
        elif ascii_ratio > 0.7:
            issues.append("英語が多すぎます。日本語で記述してください")

        return DiagnosisResult(
            score=min(score, 100),
            issues=issues,
            hints=hints,
            strengths=strengths,
            mode="free",
        )

    # ── API: LLM詳細診断 (未実装) ─────────────────────────────────

    def _run_api(self, prompt_text: str = "", **_: object) -> ServiceResult:
        """
        TODO: LLM を使って詳細診断。
        - プロンプトを LLM に送信
        - 構造・明確さ・実行可能性を評価
        - 改善後のプロンプト案を生成
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_fallback(self, **kwargs: object) -> ServiceResult:
        return self._run_free(**kwargs)


# グローバルシングルトン
prompt_doctor_service = PromptDoctorService()
