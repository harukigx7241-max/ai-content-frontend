"""
app/services/trend_service.py
トレンド注入サービス。

Tiers:
  FREE  — knowledge/workshops/*/trend_signals.json からファイルベースで読み込む (既存実装)
  API   — Web スクレイピングによる自動トレンド更新 (未実装)
  DISABLED — ENABLE_TREND_REFRESH=false 時

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

from app.services.knowledge_service import get_trend_signals, get_trend_insights
from app.services.base import BaseService, ServiceMode, ServiceResult

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


def _signals_from_insights(insights: dict) -> dict:
    """
    trend_insights.json (Phase 15拡張形式) を trend_signals.json 互換の辞書に変換する。
    既存の get_trend_hint() がそのまま使えるようにブリッジする。
    """
    result: dict = {}

    hot_cats = insights.get("hot_categories")
    if hot_cats:
        result["hot_categories"] = hot_cats

    title_patterns = insights.get("title_patterns")
    if title_patterns:
        result["title_patterns"] = [
            p.get("pattern", "") for p in title_patterns if p.get("pattern")
        ]

    result["price_sweet_spots"] = insights.get("price_sweet_spots", [])
    result["conversion_boosters"] = insights.get("conversion_boosters", [])

    # selling_angles から強いものをキーワードとして補足
    angles = insights.get("selling_angles", [])
    strong_kws: list[str] = []
    for a in angles:
        if a.get("strength", 0) >= 0.8:
            strong_kws.extend(a.get("keywords", [])[:2])
    if strong_kws:
        result.setdefault("conversion_boosters", [])
        result["conversion_boosters"] = list(dict.fromkeys(
            result["conversion_boosters"] + strong_kws
        ))

    return result


def get_trend_hint(workshop: str) -> str:
    """
    ワークショップのトレンド情報をプロンプト挿入用文字列で返す。
    trend_insights.json (Phase 15拡張形式) を優先し、なければ trend_signals.json を使う。
    データがない場合は空文字を返す。
    """
    insights = get_trend_insights(workshop)
    if insights:
        signals = _signals_from_insights(insights)
    else:
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
        if isinstance(patterns[0], dict):
            pat_strs = [p.get("pattern", "") for p in patterns[:3] if p.get("pattern")]
        else:
            pat_strs = patterns[:3]
        pats = " / ".join(pat_strs)
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


# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: TrendService — BaseService 準拠クラス
# ─────────────────────────────────────────────────────────────────────────────

class TrendService(BaseService):
    """
    トレンドリフレッシュサービス (BaseService準拠)。
    既存のモジュール関数との後方互換を保ちつつ ServiceResult を返す。
    """
    FLAG_KEY = "TREND_REFRESH"
    PREFER_API = False  # 現時点では Web スクレイピング未実装のため FREE 固定

    def get_hint(self, workshop: str) -> ServiceResult:
        """指定工房のトレンドヒント文字列を ServiceResult で返す。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        hint = get_trend_hint(workshop)
        return ServiceResult.free(content={"hint": hint, "workshop": workshop})

    def get_all(self) -> ServiceResult:
        """全工房のトレンドシグナルを ServiceResult で返す。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        return ServiceResult.free(content=get_all_trend_signals())

    def _run_api(self, workshop: str = "", **_: object) -> ServiceResult:
        """
        TODO: Web スクレイピングで最新トレンドを取得して trend_signals.json を更新。
        """
        return ServiceResult.not_implemented(ServiceMode.API)


# グローバルシングルトン
trend_service = TrendService()
