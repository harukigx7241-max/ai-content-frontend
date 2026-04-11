"""
app/services/article_draft_service.py
記事下書き自動生成サービス。note記事の下書きをLLMで自動生成する。

Tiers:
  FREE     — 対応なし (API専用機能)。骨組みプロンプトを返すのみ。
  API      — LLM記事下書き生成 (未実装)
  DISABLED — ENABLE_ARTICLE_DRAFT_AI=false 時 (デフォルト)

デフォルト false のため、APIキーがあっても明示的に有効化が必要。
Phase 20+ で本実装予定。
"""
from __future__ import annotations

from app.services.base import BaseService, ServiceMode, ServiceResult


class ArticleDraftService(BaseService):
    FLAG_KEY = "ARTICLE_DRAFT_AI"

    def generate_draft(
        self,
        theme: str,
        target: str = "",
        tone: str = "です・ます調",
        free_chars: int = 2000,
        paid_chars: int = 5000,
    ) -> ServiceResult:
        """note記事の下書きを生成する。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled(
                hint="記事下書きAIは現在準備中です。"
                     "プロンプト鍛冶場で生成したプロンプトをご利用ください。"
            )
        if mode == ServiceMode.API:
            try:
                return self._run_api(
                    theme=theme,
                    target=target,
                    tone=tone,
                    free_chars=free_chars,
                    paid_chars=paid_chars,
                )
            except Exception:
                return self._run_fallback(theme=theme)
        # FREE: 骨組みプロンプトのみ返す
        return self._run_free(theme=theme, target=target)

    # ── FREE: 骨組みプロンプト ─────────────────────────────────

    def _run_free(
        self, theme: str = "", target: str = "", **_: object
    ) -> ServiceResult:
        skeleton = f"""# {theme} — 記事下書き骨組み

## 導入 (600文字目安)
- 読者の悩みから始める
- 3つの具体的な悩みを列挙
- 「でも大丈夫です」で希望を示す

## 問題の本質 (800文字目安)
- なぜその悩みが生まれるか
- 多くの人が気づいていない原因
- 放置するとどうなるか

## 解決策の全体像 (600文字目安)
- この記事で得られる3つのこと
- 期待できる結果

━━━━ ここから有料エリア ━━━━

## 具体的な手順 (2000文字目安)
- ステップ1〜5
- よくある失敗と対処法

## 実践例 (800文字目安)
- 数字付き架空事例
- ビフォーアフター

## よくある質問 (600文字目安)
- Q&A形式5問

## 今すぐできること (400文字目安)
- 3つのアクションプラン (難易度順)
"""
        return ServiceResult.free(
            content={"draft": skeleton, "theme": theme},
            hint="APIキー設定後にAI自動生成が利用できます",
        )

    # ── API: LLM記事下書き生成 (未実装) ───────────────────────

    def _run_api(
        self,
        theme: str = "",
        target: str = "",
        tone: str = "です・ます調",
        free_chars: int = 2000,
        paid_chars: int = 5000,
        **_: object,
    ) -> ServiceResult:
        """
        TODO: LLM を使って完全な記事下書きを生成。
        - knowledge/workshops/note/ のナレッジを活用
        - 無料/有料エリアの境界を明確に指示
        - Web検索で最新データを引用
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_fallback(self, **kwargs: object) -> ServiceResult:
        theme = str(kwargs.get("theme", ""))
        return self._run_free(theme=theme)


# グローバルシングルトン
article_draft_service = ArticleDraftService()
