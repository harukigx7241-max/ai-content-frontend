# API 使用量ダッシュボード (Usage Dashboard)

> 対象バージョン: Phase 14+  
> 最終更新: 2026-04-17  
> アクセス: 管理者・管理本部のみ

---

## 概要

管理ダッシュボード → **「📊 使用量」タブ** で確認できます。

| 閲覧権限 | 表示内容 |
|---------|---------|
| 管理者 (admin) | 今日・今月の概要・機能別・モデル別内訳・コストランキング |
| 管理本部 (headquarters) | 管理者の全内容 + 予算消化率・閾値アラート・危険機能・自動停止履歴・推移グラフ |

---

## 表示内容

### 共通 (管理者・管理本部)

| 項目 | 説明 |
|------|------|
| 入力トークン | 今日 / 今月の LLM 入力トークン数 |
| 出力トークン | 今日 / 今月の LLM 出力トークン数 |
| 概算コスト (USD) | 参考価格レートに基づく概算コスト |
| API呼び出し / Web検索 | 実行回数 |
| 高コスト機能ランキング | コスト順の機能ランキング (Top 5) |
| 機能別使用量 | 横棒グラフで機能別トークン使用量を可視化 |
| モデル別使用量 | 使用モデル・プロバイダー別の内訳 |

### 管理本部専用 (HQ ONLY)

| 項目 | 説明 |
|------|------|
| 日次消化率 | 日次トークン上限に対する使用割合 |
| 月次消化率 | 月次トークン上限に対する使用割合 |
| 月末予測コスト | 経過日数から月末コストを線形外挿 |
| 直近7日推移 | コストのスパークライン |
| 閾値アラート | 設定しきい値 (API_WARN_THRESHOLD_PCT) に近づいた際の警告 |
| 危険機能 | 高コスト + 高頻度で使われている機能 |
| 自動停止履歴 | 管理者が適用したバッチプリセット等の停止イベント |

---

## データモード

| モード | 説明 |
|--------|------|
| 📋 モックデータ | APIキー未設定時に表示。リアルな形式のサンプルデータ。 |
| ✅ ライブデータ | Phase 16 実装後にリアルタイムデータを表示。 |

---

## 概算コストについて

以下の参考レートに基づいて計算しています (USD / 1K tokens):

| モデル | 入力 | 出力 |
|--------|------|------|
| claude-haiku-4-5 | $0.00025 | $0.00125 |
| claude-sonnet-4-6 | $0.003 | $0.015 |
| gpt-4o-mini | $0.00015 | $0.0006 |
| gpt-4o | $0.005 | $0.015 |
| gemini-1.5-flash | $0.000075 | $0.0003 |

> **注意:** これらは参考値です。実際のコストは各プロバイダーの最新価格を確認してください。

---

## API エンドポイント (開発者向け)

| エンドポイント | 権限 | 説明 |
|--------------|------|------|
| `GET /api/admin/usage` | admin + HQ | 全使用量レポート (HQには拡張データ付き) |
| `GET /api/admin/usage/summary` | admin + HQ | 今日・今月のサマリのみ |
| `GET /api/admin/usage/hq` | HQ のみ | 管理本部専用拡張データ |

### レスポンス例 (`/api/admin/usage`)

```json
{
  "today": {
    "label": "今日",
    "tokens": { "input": 1240, "output": 870, "total": 2110 },
    "cost_usd": 0.000309,
    "web_searches": 8,
    "api_calls": 23
  },
  "monthly": { ... },
  "feature_breakdown": [
    {
      "feature": "prompt_forge",
      "label": "プロンプト鍛冶場",
      "input_tokens": 18240,
      "output_tokens": 12480,
      "total_tokens": 30720,
      "cost_usd": 0.0202,
      "calls": 187,
      "is_high_cost": false
    },
    ...
  ],
  "model_breakdown": [ ... ],
  "top_cost_features": [ ... ],
  "mode": "mock",
  "snapshot_at": "2026-04-17T12:00:00Z",
  "hq": {  // HQ ロールのみ
    "budget_daily_pct": 0.0,
    "budget_monthly_pct": 0.0,
    "projected_monthly_cost_usd": 0.0093,
    "threshold_alerts": [],
    "danger_features": [],
    "auto_stop_history": [],
    "cost_trend_7d": [0.0002, 0.0003, ...]
  }
}
```

---

## Phase 別実装状況

| Phase | 内容 |
|-------|------|
| Phase 13 | 自動停止履歴の土台 (ApiControlService._stop_history) |
| **Phase 14** | **使用量ダッシュボード UI・サービス・API エンドポイント・HQ 拡張データ** |
| Phase 16 | generation_log テーブル・実トークン追跡・実コスト計算 |
| Phase 17 以降 | OpenAI /v1/usage API 接続・複数プロバイダー統合・CSV エクスポート |

---

## OpenAI usage API 接続 (Phase 16 予定)

将来的に以下のエンドポイントに接続する予定です:

```
GET https://api.openai.com/v1/usage
Authorization: Bearer {OPENAI_API_KEY}
Query: date=2026-04-17&group_by=model

GET https://api.openai.com/v1/costs  (新 API)
Authorization: Bearer {OPENAI_API_KEY}
```

Anthropic / Gemini のコスト API にも対応予定です。  
`usage_dashboard_service.py` の `_run_api()` メソッドに実装してください。

---

## 関連ドキュメント

- `docs/api_budget.md` — 予算管理・制御ガイド
- `docs/api_connection.md` — APIキー設定手順
- `app/services/usage_dashboard_service.py` — ダッシュボードサービス実装
- `app/services/api_control_service.py` — 制御サービス (自動停止履歴含む)
