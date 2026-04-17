# 傾向収集基盤 (Trend Ingestion)

> 対象バージョン: Phase 15+  
> 最終更新: 2026-04-17

---

## 概要

各工房 (note / tips / brain / cw / fortune / sns / sales) のトレンドインサイトを定期収集し、
`knowledge/workshops/<workshop>/trend_insights.json` に保存する基盤です。

収集したデータはプロンプト生成時に自動注入され、「今売れているタイトルパターン」「注目カテゴリ」
などをリアルタイムに反映したプロンプトを生成できます。

---

## ディレクトリ構成

```
knowledge/
├── trend_schema.json         # インサイトのスキーマ定義
├── trend_sources.json        # 収集ソース定義 (URL・CSS selector)
├── trend_history.json        # 収集実行ログ
└── workshops/
    ├── note/
    │   ├── trend_insights.json   # Phase 15拡張形式 (本ドキュメントのメイン)
    │   └── trend_signals.json    # Phase 11以前の旧形式 (後方互換)
    ├── tips/
    ├── brain/
    ├── cw/
    ├── fortune/
    ├── sns/
    └── sales/
```

---

## インサイトフォーマット (trend_insights.json)

```json
{
  "workshop": "note",
  "schema_version": "1.1",
  "extracted_at": "2026-04-17T09:00:00Z",
  "expires_at": "2026-04-20T09:00:00Z",
  "source": "admin_trigger",
  "confidence": 1.0,
  "title_patterns": [
    {
      "pattern": "【保存版】〇〇",
      "momentum": "hot",
      "example": "【保存版】月5万円副業の全手順",
      "source_count": 1
    }
  ],
  "cta_patterns": [...],
  "selling_angles": [
    {
      "angle": "money",
      "label": "収益化・稼ぎたい",
      "strength": 0.95,
      "keywords": ["月収", "副業収入"]
    }
  ],
  "theme_signals": [
    {
      "theme": "AI副業",
      "momentum": "hot",
      "volume": "very_high",
      "related_keywords": ["ChatGPT", "プロンプト"],
      "peak_forecast": "2026-09"
    }
  ],
  "category_momentum": {
    "AI・自動化": "hot",
    "投資": "warm"
  },
  "hot_categories": ["AI・自動化", "SNS運用"],
  "price_sweet_spots": ["500円", "980円", "1,980円"],
  "conversion_boosters": ["見出しに数字", "無料エリアの最後にフック"]
}
```

`hot_categories` / `price_sweet_spots` / `conversion_boosters` は旧形式 (`trend_signals.json`) との後方互換フィールドです。

---

## 鮮度ポリシー

| 工房 | 更新頻度 | 有効期限 |
|------|---------|---------|
| note | 毎日 | 3日 |
| sns  | 毎日 | 3日 |
| tips / brain / cw / fortune | 週次 | 10日 |
| sales | 月次 | 45日 |

`expires_at` を過ぎると管理画面で「古い (stale)」として警告表示されます。

---

## 収集方式

### Phase 15: 手動データ + タイムスタンプ更新

現フェーズでは、インサイトデータは手動でキュレーションされたものです。
「収集」操作は `extracted_at` / `expires_at` を現在日時に更新し、
次回の鮮度チェックをリセットします。

### Phase 16+: 自動スクレイピング

`trend_sources.json` に定義された URL から自動収集する予定です。
`TrendIngestionService._run_api()` に実装してください。

---

## 管理画面からの手動トリガー

1. `/admin` → **🔥 トレンド管理** タブ
2. 「傾向収集」パネルの **▶ 全工房を収集** ボタンをクリック
3. 成功メッセージと各工房の鮮度状態が更新される

---

## CLI からの実行

```bash
# 全ワークショップ
python scripts/ingest_trends.py

# 特定ワークショップのみ
python scripts/ingest_trends.py --workshop note

# トリガー識別子を指定
python scripts/ingest_trends.py --triggered-by "cron"

# シェルラッパー
./scripts/ingest_trends.sh
./scripts/ingest_trends.sh note
```

---

## systemd タイマー設定

```bash
# ファイルをコピー
sudo cp scripts/systemd/pguild-trend-ingest.service /etc/systemd/system/
sudo cp scripts/systemd/pguild-trend-ingest.timer   /etc/systemd/system/

# パスを本番環境に合わせて編集
sudo nano /etc/systemd/system/pguild-trend-ingest.service

# 有効化
sudo systemctl daemon-reload
sudo systemctl enable --now pguild-trend-ingest.timer

# 状態確認
sudo systemctl status pguild-trend-ingest.timer
sudo journalctl -u pguild-trend-ingest.service -n 50
```

デフォルトスケジュール: **毎日 03:00 JST** (UTC 18:00)

---

## cron 設定例 (systemd の代替)

```cron
# /etc/cron.d/pguild-trends
# 毎日 03:00 JST に実行
0 18 * * * www-data cd /var/www/ai-content-frontend && ./scripts/ingest_trends.sh >> /var/log/pguild-trends.log 2>&1
```

---

## API エンドポイント

| エンドポイント | 権限 | 説明 |
|--------------|------|------|
| `POST /api/admin/trends/ingest` | admin | 手動収集トリガー。`workshop` 省略で全工房 |
| `GET /api/admin/trends/history` | admin | 収集実行履歴 (最新 N 件) |
| `GET /api/admin/trends/status` | admin | 全工房の鮮度状態 |
| `GET /api/admin/trends` | admin | 全工房の trend_signals.json (旧 API、後方互換) |
| `PUT /api/admin/trends/{workshop}` | admin | 個別工房のデータを直接更新 |

### POST /api/admin/trends/ingest リクエスト例

```json
{ "workshop": "note" }          // note のみ
{}                               // 全工房 (workshop 省略)
{ "triggered_by": "manual" }    // 識別子付き
```

---

## テンプレート注入ルール

`TrendService.get_trend_hint(workshop)` が呼ばれると:

1. `trend_insights.json` (Phase 15形式) を優先して読み込む
2. なければ `trend_signals.json` (旧形式) にフォールバック
3. `title_patterns[0..2]` → **【売れるタイトルパターン】**
4. `hot_categories[0..5]` → **【今注目のカテゴリ】**
5. `price_sweet_spots[0..4]` → **【価格の目安】** (note/tips/brain/sales のみ)
6. `conversion_boosters[0..3]` → **【コンバージョン向上ポイント】**

これらがプロンプトの末尾参考情報セクションに追加されます。

`template_injection_rules` (trend_schema.json) による将来の高度な注入:

| ルール | 動作 |
|--------|------|
| `title_boost` | title_patterns[0..2] をプロンプトの【タイトル例】に挿入 |
| `cta_inject` | placement=無料エリア末尾 の CTA をセクション末尾指示に追加 |
| `theme_inject` | momentum=hot/rising のテーマをカテゴリ候補として提示 |
| `angle_inject` | strength≥0.7 の selling_angles を訴求角度選択肢に追加 |
| `momentum_gate` | category_momentum=declining のテーマはデフォルトから除外 |

---

## 関連ファイル

- `knowledge/trend_schema.json` — スキーマ定義
- `knowledge/trend_sources.json` — スクレイピングソース定義 (Phase 16+)
- `knowledge/trend_history.json` — 実行ログ
- `app/services/trend_ingestion_service.py` — 収集サービス
- `app/services/trend_service.py` — ヒント文字列生成 (テンプレ注入)
- `app/services/knowledge_service.py` — ファイルローダー (`get_trend_insights`)
- `scripts/ingest_trends.py` — CLI スクリプト
- `scripts/ingest_trends.sh` — シェルラッパー
- `scripts/systemd/` — systemd unit ファイル
