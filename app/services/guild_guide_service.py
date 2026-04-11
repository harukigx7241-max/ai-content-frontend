"""
app/services/guild_guide_service.py
ギルドガイドAIサービス。ユーザーの操作を助けるガイドコンテンツを生成する。

Tiers:
  FREE  — スクリプトベースのヒント (静的テキスト + コンテキスト判定)
  API   — LLM文脈対応ガイド・パーソナライズドヒント (未実装)
  DISABLED — ENABLE_GUILD_GUIDE_AI=false 時

フロントエンドの static/js/core/guild_guide.js と連携。
バックエンドAPIは現時点では未実装 (全てJSで完結)。
"""
from __future__ import annotations

from app.services.base import BaseService, ServiceMode, ServiceResult

# ─────────────────────────────────────────────────────────────────────────────
# 静的ヒントテーブル (FREE tier)
# ─────────────────────────────────────────────────────────────────────────────

_HINTS: dict[str, list[str]] = {
    "note": [
        "「ターゲットの悩み」に具体的な状況を書くほど、読者に刺さるプロンプトになります。",
        "無料エリアは「解決策の全体像」まで。有料エリアで「具体的な手順」を出しましょう。",
        "文字数は「無料エリア2000字 + 有料エリア5000字」が実績のある比率です。",
    ],
    "cw": [
        "提案文は「クライアントの課題解決」に焦点を当てると採用率が上がります。",
        "自分のスキルではなく「クライアントが得られる価値」で書きましょう。",
        "初期単価は低めに設定し、実績を積んでから交渉するのが定石です。",
    ],
    "fortune": [
        "鑑定書は「問題 → 原因 → 解決策 → アドバイス」の流れが基本です。",
        "ターゲットの相談内容に合わせた言葉選びが信頼感を高めます。",
        "ポジティブな表現と具体的なアドバイスを組み合わせましょう。",
    ],
    "sns": [
        "X(Twitter)では最初の1行で読者を引き込むことが最重要です。",
        "Instagramはハッシュタグより画像の説明文の質が大切です。",
        "Threadsは連投形式で「起承転結」を作るとエンゲージメントが上がります。",
    ],
    "default": [
        "フォームの入力が具体的なほど、高品質なプロンプトが生成されます。",
        "生成されたプロンプトは ChatGPT・Gemini・Claude のどれでも使えます。",
        "プロンプトをコピーして AI に貼り付けると、すぐに使えます。",
    ],
}


class GuildGuideService(BaseService):
    FLAG_KEY = "GUILD_GUIDE_AI"

    def get_hints(self, workshop: str = "default", count: int = 3) -> ServiceResult:
        """指定した工房のガイドヒントを返す。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        if mode == ServiceMode.API:
            try:
                return self._run_api(workshop=workshop, count=count)
            except Exception:
                return self._run_fallback(workshop=workshop, count=count)
        return self._run_free(workshop=workshop, count=count)

    # ── FREE: 静的ヒント ────────────────────────────────────────────

    def _run_free(
        self, workshop: str = "default", count: int = 3, **_: object
    ) -> ServiceResult:
        hints = _HINTS.get(workshop, _HINTS["default"])
        return ServiceResult.free(content={"hints": hints[:count], "workshop": workshop})

    # ── API: LLMガイド (未実装) ─────────────────────────────────────

    def _run_api(
        self, workshop: str = "default", count: int = 3, **_: object
    ) -> ServiceResult:
        """
        TODO: ユーザーの操作履歴・入力内容に基づいてパーソナライズドヒントを生成。
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_fallback(self, **kwargs: object) -> ServiceResult:
        return self._run_free(**kwargs)


# グローバルシングルトン
guild_guide_service = GuildGuideService()
