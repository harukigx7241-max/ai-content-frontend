# API 予算管理・制御ガイド (API Budget & Control Guide)

> 対象バージョン: Phase 13+  
> 最終更新: 2026-04-17

---

## 概要

Phase 13 で実装した API 制御センターにより、以下が可能になります。

| 機能 | 説明 |
|------|------|
| 機能単位 ON/OFF | 各 AI サービスを個別に有効/無効化 |
| 一括プリセット | 6 種のプリセットで素早く制御 |
| 予算ガード | 日次・月次の上限設定 (実データ連携は Phase 16) |
| 自動停止 | 上限到達時に FREE tier へ自動降格 |

---

## アクセス方法

管理ダッシュボード → **「🎛 API制御」タブ**

---

## 一括プリセット

| プリセット | 説明 | 危険度 |
|-----------|------|--------|
| 🟢 全AI機能ON | 全サービスを有効化 | 低 |
| ⚫ 全AI機能OFF | 全サービスを無効化 (FREE tier に降格) | 高 |
| 🟠 高コスト停止 | 高コストサービス (画像生成・記事下書き・WSマスター) を停止 | 低 |
| 🔴 管理者限定AIのみ | 管理者専用 AI のみ有効化、一般向け AI を停止 | 高 |
| 🟡 無料会員向けAI停止 | 無料会員が使う AI 機能を停止 | 低 |
| 🔄 設定リセット | 実行時オーバーライドをすべてクリア | 低 |

### 危険なプリセットについて

「高」評価のプリセット (`全AI機能OFF`, `管理者限定AIのみ`) は適用前に確認ダイアログが表示されます。

---

## 高コストサービス

以下のサービスがデフォルトの「高コスト」に分類されています。

| サービス | 理由 |
|---------|------|
| ワークショップマスターAI | API 専用・長文生成 |
| 記事下書きAI | API 専用・長文生成 |
| 画像生成連携 | 画像 API は通常のテキスト API より高コスト |

`API_HIGH_COST_SERVICES` 環境変数でカスタマイズできます:

```env
API_HIGH_COST_SERVICES=workshop_master_ai,article_draft_ai,image_generation
```

---

## 予算設定

### 環境変数

```env
# 日次上限
API_DAILY_TOKEN_LIMIT=100000      # 1日あたりのトークン上限 (0=無制限)
API_DAILY_COST_LIMIT_USD=1.00     # 1日あたりのコスト上限 USD (0=無制限)

# 月次上限
API_MONTHLY_TOKEN_LIMIT=1000000   # 月あたりのトークン上限 (0=無制限)
API_MONTHLY_COST_LIMIT_USD=10.00  # 月あたりのコスト上限 USD (0=無制限)

# 警告しきい値 (上限の何%で警告)
API_WARN_THRESHOLD_PCT=80         # デフォルト 80%

# 上限超過時の動作
API_OVER_LIMIT_ACTION=fallback    # disable | fallback | notify_only
```

### 上限超過時の動作

| アクション | 説明 |
|-----------|------|
| `fallback` | API 呼び出しを停止し、FREE tier に降格 (推奨) |
| `disable` | 機能全体を無効化 (ユーザーにエラーを表示) |
| `notify_only` | 上限超過を記録するが制限なし (監視目的のみ) |

---

## 実行時オーバーライドについて

管理ダッシュボードから変更したトグル設定は **実行時オーバーライド** として保持されます。

### 重要な制約

- **サーバー再起動でリセット**されます
- 永続化は **Phase 16 (DB管理)** で実装予定です
- オーバーライド中は管理ダッシュボードに「🔧 実行時オーバーライド適用中」バッジが表示されます

### オーバーライドの優先順位

```
実行時オーバーライド (admin dashboard) > 環境変数 (.env) > デフォルト値
```

---

## API エンドポイント (開発者向け)

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/api/admin/api-control` | GET | 全サービスの制御状態を返す |
| `/api/admin/api-control/toggle` | POST | 個別サービスの ON/OFF を切り替え |
| `/api/admin/api-control/batch` | POST | バッチプリセットを適用 |
| `/api/admin/budget` | GET | 日次・月次の予算状態を返す |

すべて管理者認証が必要です。

### `/api/admin/api-control/toggle` リクエスト例

```json
{
  "service": "prompt_doctor",
  "enabled": false
}
```

### `/api/admin/api-control/batch` リクエスト例

```json
{
  "preset": "high_cost_off"
}
```

---

## ロール別 API 制限 (将来対応)

Phase 16 以降で DB ベースのロール別制限が実装される予定です。

```env
# 現在は環境変数で粗粒度制御のみ
API_ALLOW_FREE_MEMBER=true   # 無料会員に API 呼び出しを許可するか
API_ALLOW_PAID_MEMBER=true   # 有料会員に API 呼び出しを許可するか
```

---

## Phase 別対応状況

| Phase | 実装内容 |
|-------|---------|
| Phase 12 | サービスレジストリ・API キー設定手順 |
| **Phase 13** | **機能単位 ON/OFF・バッチプリセット・予算ガード土台** |
| Phase 16 | generation_log テーブル・実使用量追跡・コスト計算 |
| Phase 17 以降 | ロール別予算・機能別課金・自動通知 |

---

## 関連ドキュメント

- `docs/api_connection.md` — API キー設定手順
- `docs/roadmap_phases.md` — フェーズロードマップ
- `app/services/api_control_service.py` — 制御サービス実装
- `app/core/config.py` — 全設定項目の定義
