"""
app/services/guild_scribe_service.py
ギルド書記AIサービス。ギルド広場への投稿文・説明文・キャプション生成を支援する。

Tiers:
  FREE  — テンプレートベースの投稿文生成 (カテゴリ別雛形 + 入力埋め込み)
  API   — LLMによる文脈対応・高品質投稿文生成 (未実装)
  DISABLED — ENABLE_GUILD_SCRIBE_AI=false 時

連携:
  - ギルド広場 (square.html) の投稿フォーム
  - /api/guild/scribe エンドポイント (将来実装)
"""
from __future__ import annotations

from app.services.base import BaseService, ServiceMode, ServiceResult

# ─────────────────────────────────────────────────────────────────────────────
# テンプレートベース雛形 (FREE tier)
# ─────────────────────────────────────────────────────────────────────────────

_TEMPLATES: dict[str, str] = {
    "note": (
        "【{title}】\n\n"
        "{theme}について、実体験を交えながらまとめました。\n\n"
        "▼ この投稿でわかること\n"
        "・{point1}\n"
        "・{point2}\n"
        "・{point3}\n\n"
        "詳しくはプロフィールのリンクから。\n"
        "スキ・フォローで応援よろしくお願いします！"
    ),
    "cw": (
        "【{title}】\n\n"
        "{theme}の案件で培ったノウハウをシェアします。\n\n"
        "▼ ポイント\n"
        "・{point1}\n"
        "・{point2}\n\n"
        "同じ悩みを持つ方の参考になれば幸いです。\n"
        "コメントでご意見もお待ちしています！"
    ),
    "fortune": (
        "【{title}】\n\n"
        "{theme}について鑑定を通じて気づいたことを投稿します。\n\n"
        "✨ {point1}\n"
        "✨ {point2}\n\n"
        "あなたのエネルギーが今日も輝きますように。\n"
        "気になる方はDMまたはプロフィールへ✉"
    ),
    "sns": (
        "【{title}】\n\n"
        "{theme}の発信で意識していることをまとめました。\n\n"
        "→ {point1}\n"
        "→ {point2}\n"
        "→ {point3}\n\n"
        "フォロワーさんと一緒に成長していきたいです。\n"
        "参考になったらいいね👍をお願いします！"
    ),
    "default": (
        "【{title}】\n\n"
        "{theme}について投稿します。\n\n"
        "・{point1}\n"
        "・{point2}\n\n"
        "ご感想・ご質問はコメントまで。よろしくお願いします！"
    ),
}

_CAPTION_TEMPLATES: dict[str, str] = {
    "note": "📝 {theme} | 詳細はリンクから｜#note副業 #コンテンツ販売",
    "cw": "💼 {theme} | クラウドワークス実践記｜#在宅ワーク #フリーランス",
    "fortune": "🔮 {theme} | スピリチュアルな気づき｜#占い #タロット #開運",
    "sns": "✨ {theme} | SNS運用のコツ｜#SNSマーケティング #副業",
    "default": "📌 {theme}｜#副業 #プロンプトギルド",
}


class GuildScribeService(BaseService):
    FLAG_KEY = "GUILD_SCRIBE_AI"

    def generate_post(
        self,
        title: str,
        theme: str,
        category: str = "default",
        points: list[str] | None = None,
    ) -> ServiceResult:
        """投稿文を生成する。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        if mode == ServiceMode.API:
            try:
                return self._run_api(
                    title=title, theme=theme, category=category, points=points
                )
            except Exception:
                return self._run_fallback(
                    title=title, theme=theme, category=category, points=points
                )
        return self._run_free(
            title=title, theme=theme, category=category, points=points
        )

    def generate_caption(
        self, theme: str, category: str = "default"
    ) -> ServiceResult:
        """SNS・広場向け短いキャプションを生成する。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        tpl = _CAPTION_TEMPLATES.get(category, _CAPTION_TEMPLATES["default"])
        caption = tpl.format(theme=theme)
        return ServiceResult.free(content={"caption": caption, "category": category})

    # ── FREE: テンプレートベース ────────────────────────────────────

    def _run_free(
        self,
        title: str = "",
        theme: str = "",
        category: str = "default",
        points: list[str] | None = None,
        **_: object,
    ) -> ServiceResult:
        tpl = _TEMPLATES.get(category, _TEMPLATES["default"])
        pts = points or ["ポイント1", "ポイント2", "ポイント3"]
        # テンプレートに埋め込む (不足分は空文字)
        text = tpl.format(
            title=title or theme,
            theme=theme,
            point1=pts[0] if len(pts) > 0 else "",
            point2=pts[1] if len(pts) > 1 else "",
            point3=pts[2] if len(pts) > 2 else "",
        )
        return ServiceResult.free(
            content={"text": text, "category": category},
            hint="テンプレートをベースに編集してご利用ください。",
        )

    # ── API: LLM高品質生成 (未実装) ────────────────────────────────

    def _run_api(
        self,
        title: str = "",
        theme: str = "",
        category: str = "default",
        points: list[str] | None = None,
        **_: object,
    ) -> ServiceResult:
        """
        TODO: ユーザーの過去投稿・カテゴリ・トレンドを踏まえたLLM投稿文生成。
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_fallback(self, **kwargs: object) -> ServiceResult:
        return self._run_free(**kwargs)


# グローバルシングルトン
guild_scribe_service = GuildScribeService()
