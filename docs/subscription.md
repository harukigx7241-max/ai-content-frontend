# サブスクリプション設計 (Subscription)

> 対象バージョン: Phase 16+  
> 最終更新: 2026-04-17  
> 関連ファイル: `app/services/subscription_service.py`

---

## 概要

**無料先行・後から課金解放** を基本方針とします。

- 現フェーズ: 全ユーザーがフリープランの全機能を無料で利用可能
- Phase 17+: Stripe 接続後に有料プランを順次解放
- 課金システムが未接続でも UI・API・データ構造は完成済み

---

## プラン定義

| プラン | ID | ロール | 月額 | 年額 | アイコン |
|--------|-----|--------|------|------|---------|
| フリープラン   | `free`   | `user` (member_free) | 無料 | 無料 | ⚗ |
| プロプラン     | `paid`   | `member_paid`        | ¥980 | ¥9,800 | ⚔ |
| マスタープラン | `master` | `member_master`      | ¥2,480 | ¥24,800 | ✦ |

年払いは約17%オフ。

---

## 機能解放マップ

### フリープラン (全員)

| 機能 | ステータス |
|------|---------|
| プロンプト鍛冶場 (全7工房) | ✅ LIVE |
| テンプレートライブラリ閲覧 | ✅ LIVE |
| テンプレート保存・リミックス | ✅ LIVE |
| プロンプト診断 (基本10項目) | ✅ LIVE |
| 日本語品質チェック | ✅ LIVE |
| ギルド広場 閲覧・投稿 | ✅ LIVE |
| XP・ランク・称号システム | ✅ LIVE |
| プロンプト履歴 (ブラウザ保存) | ✅ LIVE |

### プロプランで解放 (近日)

| 機能 | ステータス |
|------|---------|
| キャンペーン鍛冶場 | 🔒 PREMIUM_READY |
| note販促ビルダー | 🔒 PREMIUM_READY |
| リサーチ下書き自動生成 | 🔒 PREMIUM_READY |
| 画像プロンプト生成 | 🔒 PREMIUM_READY |
| 優先処理レーン | 🔒 PREMIUM_READY |
| プロンプト診断 詳細モード | 🔒 PREMIUM_READY |

### マスタープランで解放 (近日)

| 機能 | ステータス |
|------|---------|
| Workshop Master AI | 🔒 PREMIUM_READY |
| 一括生成 | 🔒 PREMIUM_READY |
| 最優先レーン | 🔒 PREMIUM_READY |
| マスターバッジ | 🔒 PREMIUM_READY |

### 管理者専用 (課金なし)

| 機能 | 対象ロール |
|------|---------|
| ユーザー管理・承認 | admin + headquarters |
| API 利用量ダッシュボード | admin + headquarters |
| トレンド収集管理 | admin + headquarters |
| KPI・コスト分析 | headquarters のみ |

---

## データ設計

### DB カラム (users テーブル)

| カラム | 型 | デフォルト | 説明 |
|--------|-----|---------|------|
| `subscription_plan` | VARCHAR(20) | `"free"` | `"free"` / `"paid"` / `"master"` |
| `subscription_status` | VARCHAR(20) | `"active"` | `"active"` / `"inactive"` / `"cancelled"` / `"trial"` / `"past_due"` |
| `subscription_expires_at` | DATETIME | NULL | 有料プランの有効期限 (free は NULL) |
| `stripe_customer_id` | VARCHAR(100) | NULL | Stripe 顧客 ID (課金接続後に設定) |

### ロールと subscription_plan の関係

- `subscription_plan` は課金状態の追跡用
- `role` はアクセス制御の実施主体
- 課金確認後 → `subscription_plan` を更新 → `role` を昇格 (admin が手動 or Webhook 経由)
- admin / headquarters は `subscription_plan = "master"` 相当として扱う (課金不要)

---

## API

| エンドポイント | 認証 | 説明 |
|--------------|------|------|
| `GET /api/plans` | 不要 | 全プラン定義を返す |
| `GET /api/plans/me` | 任意 | 現在ユーザーのプラン情報 |
| `POST /api/plans/checkout` | 必要 | Stripe Checkout セッション作成 |

### GET /api/plans レスポンス例

```json
{
  "plans": [
    {
      "plan_id": "free",
      "label": "フリープラン",
      "icon": "⚗",
      "price_monthly_jpy": 0,
      "features_free": ["プロンプト鍛冶場 (全工房・無制限)", ...],
      "billing_enabled": false
    },
    {
      "plan_id": "paid",
      "label": "プロプラン",
      "price_monthly_jpy": 980,
      "price_yearly_jpy": 9800,
      "yearly_discount_pct": 17,
      ...
    }
  ],
  "billing_enabled": false,
  "trial_days": 0
}
```

---

## UI

| ページ | URL | 説明 |
|--------|-----|------|
| プラン比較ページ | `/plans` | 3プランのカード・機能比較テーブル・FAQ |
| マイページ | `/mypage` | 現在のプランバッジ + アップグレード CTA |
| トップページ | `/` | 工房タブ末尾にプレミアム機能ティーザー |

---

## Stripe 接続手順 (Phase 17+)

1. Stripe ダッシュボードで Product を作成し Price ID を取得
2. `.env` に設定:
   ```
   STRIPE_SECRET_KEY=sk_live_xxx
   STRIPE_PUBLISHABLE_KEY=pk_live_xxx
   STRIPE_WEBHOOK_SECRET=whsec_xxx
   STRIPE_PRICE_PAID_MONTHLY=price_xxx
   STRIPE_PRICE_PAID_YEARLY=price_xxx
   STRIPE_PRICE_MASTER_MONTHLY=price_xxx
   STRIPE_PRICE_MASTER_YEARLY=price_xxx
   ENABLE_BILLING=true
   ```
3. `app/services/subscription_service.py` の `create_checkout_session()` に実装
4. Webhook エンドポイント `POST /api/plans/webhook` を追加
5. `checkout.session.completed` イベントで `user.subscription_plan` と `user.role` を更新
6. `customer.subscription.deleted` イベントで降格処理

---

## FeatureStatus との連携

```python
# access_policy.py の機能を課金解放するには:
# 1. status を PREMIUM_READY → LIVE に変更
# 2. required_role を RoleValue.MEMBER_PAID に設定済みであること確認
# 3. feature_flags の ENABLE_CAMPAIGN_FORGE 等を True に設定

"campaign_forge": FeaturePolicy(
    feature_id="campaign_forge",
    required_role=RoleValue.MEMBER_PAID,
    status=FeatureStatus.PREMIUM_READY,  # ← LIVE に変更すると解放
    ...
)
```

---

## 関連ファイル

- `app/services/subscription_service.py` — プラン定義・課金 scaffold
- `app/routers/subscription.py` — `/api/plans/*` エンドポイント
- `app/routers/pages.py` — `/plans` ページルート
- `app/db/models/user.py` — subscription_plan/status/expires_at/stripe_customer_id
- `app/db/migrations.py` — Phase 16 カラムマイグレーション
- `app/core/config.py` — STRIPE_* / ENABLE_BILLING 設定
- `app/core/access_policy.py` — FEATURE_POLICIES・FeatureStatus
- `app/core/roles.py` — RoleValue・PLAN_TO_ROLE マッピング
- `templates/plans.html` — プラン比較ページ
- `docs/permission_matrix.md` — 権限マトリクス全体図
