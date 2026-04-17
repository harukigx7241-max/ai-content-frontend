"""
app/services/prompt_doctor_service.py
プロンプト診断サービス。生成されたプロンプトの品質を評価し改善提案を返す。

Tiers:
  FREE  — ルールベーススコアリング (Phase 8 強化版)
  LITE  — 将来: 軽量モデルによる診断 (未実装)
  API   — LLM詳細診断・改善後プロンプト生成 (未実装)
  DISABLED — ENABLE_PROMPT_DOCTOR=false 時

FREE チェック項目 (Phase 8):
  1. 文字数
  2. 役割定義
  3. 読者指定
  4. ベネフィット
  5. 具体性
  6. CTA
  7. 出力形式指定
  8. タイトル強度
  9. 導入の長さ
  10. 冗長性
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
    score: int                       # 0-100
    stars: int = 0                   # 1-5 (スコアから自動計算)
    issues: list[str] = field(default_factory=list)    # 問題点
    hints: list[str] = field(default_factory=list)     # 改善ヒント
    strengths: list[str] = field(default_factory=list) # 良い点
    mode: str = "free"
    upgrade_hint: str = ""           # 将来 AI 版で改善できる点の案内

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
            "upgrade_hint": self.upgrade_hint,
        }


# ─────────────────────────────────────────────────────────────────────────────
# PromptDoctorService
# ─────────────────────────────────────────────────────────────────────────────

class PromptDoctorService(BaseService):
    FLAG_KEY = "PROMPT_DOCTOR"

    # 役割定義パターン
    _ROLE_PATTERNS = [
        r"あなたは.{2,40}(です|である|として)",
        r"(専門家|プロ|エキスパート|マスター|スペシャリスト)",
        r"として振る舞",
        r"(役割|ロール).*?:",
    ]

    # 読者指定パターン
    _READER_PATTERNS = [
        r"(ターゲット|読者|対象者|向け)",
        r"(初心者|中級者|上級者|ビギナー)",
        r"[2-7]0代",
        r"(副業|フリーランス|会社員|主婦|学生).*?(向け|の人|の方)",
        r"【ターゲット|【読者|【対象",
    ]

    # ベネフィットパターン
    _BENEFIT_PATTERNS = [
        r"(できます|なれます|身につきます|実現できます)",
        r"(メリット|効果|結果|成果|得られる|変わります)",
        r"(〜を手に入れ|〜が叶い|〜を達成)",
        r"(月収|収入|稼げ|節約|時間短縮)",
        r"(改善|解決|克服|突破)",
    ]

    # CTA パターン
    _CTA_PATTERNS = [
        r"(今すぐ|さっそく|まずは|ぜひ)",
        r"(してください|お試し|ご確認|チェック)",
        r"(行動|実践|取り組ん|始め).*?(ください|みて)",
        r"(登録|申込|購入|フォロー).*?(こちら|から|お願い)",
        r"(アクション|次のステップ|まず.*?から)",
    ]

    # タイトル強化パワーワード
    _POWER_WORDS = [
        "方法", "秘密", "完全", "初心者", "月収", "稼", "無料", "限定", "最速",
        "ゼロから", "達成", "暴露", "真実", "最強", "徹底", "保存版", "革命",
        "爆速", "必見", "決定版", "失敗しない", "〜だけで",
    ]

    # 冗長な表現
    _REDUNDANT_PATTERNS = [
        r"(非常に|とても|かなり|すごく|大変){2,}",   # 強調の連発
        r"(〜という|〜といった|〜のような){3,}",      # 「という」連発
        r"(もちろん|確かに|なるほど|おっしゃる通り)", # AI定型文
        r"(それ|これ|あれ)(は|が|を|に)(それ|これ|あれ)", # 代名詞連発
    ]

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

    def _rule_based_diagnosis(self, text: str) -> DiagnosisResult:  # noqa: C901
        score = 0
        issues: list[str] = []
        hints: list[str] = []
        strengths: list[str] = []

        # ── チェック 1: 文字数 (25点満点) ─────────────────────────
        length = len(text.strip())
        if length >= 400:
            score += 25
            strengths.append("十分な文字数があります（400字以上）")
        elif length >= 150:
            score += 15
            hints.append("さらに詳細を追加するとより良いプロンプトになります（目安: 400字以上）")
        elif length >= 50:
            score += 5
            issues.append("プロンプトが短すぎます（150字以上を推奨）")
            hints.append("背景・目的・条件・制約を追加してください")
        else:
            issues.append("プロンプトが極端に短いです（50字未満）")
            hints.append("内容をもっと具体的に書いてください")

        # ── チェック 2: 役割定義 (20点) ──────────────────────────
        has_role = any(re.search(p, text) for p in self._ROLE_PATTERNS)
        if has_role:
            score += 20
            strengths.append("役割定義が含まれています")
        else:
            issues.append("役割定義がありません")
            hints.append("「あなたは〇〇の専門家です」のような役割定義を冒頭に追加してください")

        # ── チェック 3: 読者指定 (10点) ──────────────────────────
        has_reader = any(re.search(p, text) for p in self._READER_PATTERNS)
        if has_reader:
            score += 10
            strengths.append("読者・ターゲットが指定されています")
        else:
            issues.append("読者指定がありません")
            hints.append("「ターゲット: 〇〇な人」のように対象読者を明記してください")

        # ── チェック 4: ベネフィット (10点) ─────────────────────
        has_benefit = any(re.search(p, text) for p in self._BENEFIT_PATTERNS)
        if has_benefit:
            score += 10
            strengths.append("ベネフィット（読者が得られること）が示されています")
        else:
            issues.append("ベネフィットの記述がありません")
            hints.append("読者が「これで何を得られるか」を明示してください（例: 月5万円稼げる方法）")

        # ── チェック 5: 具体性 (10点) ────────────────────────────
        concrete_count = sum(1 for p in [
            r"\d+",                          # 数字
            r"例えば|たとえば|具体的に",
            r"ステップ|手順|Step",
            r"【|】|\[|\]|《|》",           # 構造化マーカー
            r"(第[一二三四五1-5]|1\.|2\.|3\.)",  # 番号
        ] if re.search(p, text))
        if concrete_count >= 3:
            score += 10
            strengths.append("具体的な指示・構造が含まれています")
        elif concrete_count >= 1:
            score += 5
            hints.append("数字・例・ステップ番号を追加するとより効果的です")
        else:
            issues.append("具体性が不足しています")
            hints.append("数字・例・ステップ形式で指示を具体化してください")

        # ── チェック 6: CTA (10点) ───────────────────────────────
        has_cta = any(re.search(p, text) for p in self._CTA_PATTERNS)
        if has_cta:
            score += 10
            strengths.append("行動を促す CTA が含まれています")
        else:
            issues.append("CTA（行動促進フレーズ）が不足しています")
            hints.append("「今すぐ〇〇してください」のような行動促進フレーズを加えてください")

        # ── チェック 7: 出力形式指定 (10点) ─────────────────────
        has_format = any(re.search(p, text) for p in [
            r"箇条書き|リスト形式|番号付き",
            r"文字(程度|以内|以上)",
            r"セクション|章|項目",
            r"マークダウン|Markdown",
            r"表形式|テーブル",
        ])
        if has_format:
            score += 10
            strengths.append("出力形式が指定されています")
        else:
            hints.append("出力形式（箇条書き・文字数・セクション数）を指定すると使いやすくなります")

        # ── チェック 8: タイトル強度 (5点) ──────────────────────
        # 最初の行や【】内のテキストをタイトル候補と見なす
        first_line = text.split("\n")[0][:80]
        title_candidates = re.findall(r"【(.{2,40})】", text[:200]) + [first_line]
        title_text = " ".join(title_candidates)
        power_found = [w for w in self._POWER_WORDS if w in title_text]
        if power_found:
            score += 5
            strengths.append(f"タイトル・見出しにパワーワードがあります（{', '.join(power_found[:3])}）")
        else:
            issues.append("タイトルや見出しが弱いです")
            hints.append(f"パワーワード（例: {', '.join(self._POWER_WORDS[:5])}）をタイトルに使うとクリック率が上がります")

        # ── チェック 9: 導入の長さ ────────────────────────────────
        # 最初の段落が長すぎる場合
        paragraphs = [p for p in re.split(r"\n\n+", text) if p.strip()]
        if paragraphs and len(paragraphs[0]) > 350:
            issues.append("導入部分が長すぎます（最初の段落が350字超）")
            hints.append("導入は読者を引き込む1〜2文に凝縮し、早めに本題へ移りましょう")
        elif paragraphs and len(paragraphs[0]) <= 100 and length > 300:
            strengths.append("導入が簡潔です")

        # ── チェック 10: 冗長性 ──────────────────────────────────
        redundant_hits = sum(1 for p in self._REDUNDANT_PATTERNS if re.search(p, text))
        if redundant_hits >= 2:
            issues.append("冗長な表現が複数見られます")
            hints.append("「非常に非常に」「〜という〜という」などの繰り返し表現を整理してください")
        elif redundant_hits == 1:
            hints.append("一部に冗長な表現があります。簡潔にまとめましょう")

        upgrade_hint = (
            "AI版（準備中）では、プロンプト全体を LLM が読み、"
            "改善後の完全なプロンプト案を自動生成します。"
        )

        return DiagnosisResult(
            score=min(score, 100),
            issues=issues,
            hints=hints,
            strengths=strengths,
            mode="free",
            upgrade_hint=upgrade_hint,
        )

    # ── LITE / API: 将来実装 ──────────────────────────────────────

    def _run_api(self, prompt_text: str = "", **_: object) -> ServiceResult:
        """
        TODO Phase 20+: LLM を使って詳細診断 + 改善後プロンプト案生成。
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_fallback(self, **kwargs: object) -> ServiceResult:
        return self._run_free(**kwargs)


# グローバルシングルトン
prompt_doctor_service = PromptDoctorService()
