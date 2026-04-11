"""
app/services/trend_service.py
トレンド注入サービス。

knowledge/workshops/<workshop>/trend_signals.json から読み込んだ
トレンドデータをプロンプトに付加するためのユーティリティ。

設計:
  - get_trend_hint(workshop) で差し込み用の日本語ヒント文字列を返す
  - プロンプトビルダーが呼び出す (オプショナル)
  - trend_signals.json が存在しない/空の場合は空文字を返す
  - 将来: admin API から trend_signals.json を更新 → invalidate_cache() で反映

trend_signals.json 形式 (例):
{
  "hot_categories": ["AI・自動化", "投資"],
  "title_patterns": ["【保存版】〇〇", "〇〇日で達成"],
  "price_sweet_spots": ["500円", "980円"],
  "conversion_boosters": ["見出しに数字", "無料エリアの最後にフック"]
}
"""

from app.services.knowledge_service import get_trend_signals

# ワークショップごとのラベル (UI表示用)
WORKSHOP_LABELS: dict[str, str] = {
    "note":    "有料note記事",
    "tips":    "tips",
    "brain":   "Brain",
    "cw":      "クラウドワークス",
    "fortune": "占い鑑定",
    "sns":     "SNS",
    "sales":   "販売ページ",
}


def get_trend_hint(workshop: str) -> str:
    """
    ワークショップのトレンド情報をプロンプト挿入用文字列で返す。
    データがない場合は空文字を返す。
    """
    signals = get_trend_signals(workshop)
    if not signals:
        return ""

    parts: list[str] = []

    hot = signals.get("hot_categories")
    if hot:
        cats = "・".join(hot[:5])
        parts.append(f"【今注目のカテゴリ】{cats}")

    patterns = signals.get("title_patterns")
    if patterns:
        pats = " / ".join(patterns[:3])
        parts.append(f"【売れるタイトルパターン】{pats}")

    prices = signals.get("price_sweet_spots")
    if prices and workshop in ("note", "tips", "brain", "sales"):
        ps = "・".join(prices[:4])
        parts.append(f"【価格の目安】{ps}")

    boosters = signals.get("conversion_boosters")
    if boosters:
        bs = " / ".join(boosters[:3])
        parts.append(f"【コンバージョン向上ポイント】{bs}")

    if not parts:
        return ""

    label = WORKSHOP_LABELS.get(workshop, workshop)
    header = f"\n\n【{label}のトレンドデータ (参考情報)】\n"
    return header + "\n".join(parts)


def get_all_trend_signals() -> dict[str, dict | None]:
    """全ワークショップのトレンドシグナルを辞書で返す (admin API用)。"""
    return {ws: get_trend_signals(ws) for ws in WORKSHOP_LABELS}
