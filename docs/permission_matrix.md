# 権限マトリクス (Permission Matrix)

> 最終更新: 2026-04-11 (Phase 2)  
> ロール定義: `app/core/roles.py`  
> ポリシー定義: `app/core/access_policy.py`  
> 依存性: `app/auth/dependencies.py`

---

## 1. ロール一覧

| ロール | DB値 | 階層 | アイコン | 説明 |
|--------|------|------|--------|------|
| `guest` | *(DBなし)* | 0 | 👤 | 未ログイン訪問者。1日3回制限。 |
| `member_free` | `"user"` | 1 | ⚗ | 無料会員。広場・プロンプト生成が使える。 |
| `member_paid` | `"member_paid"` | 2 | ⚔ | 有料会員。上位ツール・画像生成が使える。 |
| `member_master` | `"member_master"` | 3 | ✦ | マスター会員。全機能 + 優先レーン。 |
| `admin` | `"admin"` | 4 | ⚒ | 管理者。現場運営担当。 |
| `headquarters` | `"headquarters"` | 5 | 🏛 | 管理本部。司令室・最上位制御。 |

> **DB 注意:** 現在 DB に存在するロールは `"user"` と `"admin"` が主。  
> `member_paid` / `member_master` は Phase 16 で DB カラム追加済み (subscription_plan で追跡)。  
> `headquarters` ロールは手動で DB に設定可能。

---

## 2. 機能 × ロール 権限マトリクス

凡例: ✅ 利用可 / 🔒 要アップグレード / ❌ 利用不可 / 🔧 管理者専用

### プロンプト生成系

| 機能 | ゲスト | 無料会員 | 有料会員 | マスター | 管理者 | 管理本部 | ステータス |
|------|:------:|:-------:|:-------:|:-------:|:------:|:-------:|---------|
| テンプレ閲覧 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | LIVE |
| Prompt Forge (生成) | ✅¹ | ✅ | ✅ | ✅ | ✅ | ✅ | LIVE |
| テンプレ保存 | 🔒 | ✅ | ✅ | ✅ | ✅ | ✅ | BETA |
| テンプレ リミックス/フォーク | 🔒 | ✅ | ✅ | ✅ | ✅ | ✅ | BETA |
| Prompt Doctor (診断) | 🔒 | ✅ | ✅ | ✅ | ✅ | ✅ | BETA |
| 日本語品質チェック | 🔒 | ✅ | ✅ | ✅ | ✅ | ✅ | BETA |
| プロンプト履歴 | 🔒 | ✅ | ✅ | ✅ | ✅ | ✅ | BETA |
| Campaign Forge | 🔒 | 🔒 | ✅ | ✅ | ✅ | ✅ | PREMIUM_READY |
| Note Promotion Builder | 🔒 | 🔒 | ✅ | ✅ | ✅ | ✅ | PREMIUM_READY |
| Auto Research Draft | 🔒 | 🔒 | ✅ | ✅ | ✅ | ✅ | PREMIUM_READY |
| Image Generation | 🔒 | 🔒 | ✅ | ✅ | ✅ | ✅ | PREMIUM_READY |
| Workshop Master AI | 🔒 | 🔒 | ✅ | ✅ | ✅ | ✅ | HIDDEN² |

### コミュニティ系

| 機能 | ゲスト | 無料会員 | 有料会員 | マスター | 管理者 | 管理本部 | ステータス |
|------|:------:|:-------:|:-------:|:-------:|:------:|:-------:|---------|
| ギルド広場 閲覧 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | LIVE |
| ギルド広場 投稿 | 🔒 | ✅ | ✅ | ✅ | ✅ | ✅ | LIVE |
| ギルド広場 リアクション | 🔒 | ✅ | ✅ | ✅ | ✅ | ✅ | LIVE |

### ゲーミフィケーション系

| 機能 | ゲスト | 無料会員 | 有料会員 | マスター | 管理者 | 管理本部 | ステータス |
|------|:------:|:-------:|:-------:|:-------:|:------:|:-------:|---------|
| XP / ランク / 称号 | 🔒 | ✅ | ✅ | ✅ | ✅ | ✅ | LIVE |

### プレミアム系

| 機能 | ゲスト | 無料会員 | 有料会員 | マスター | 管理者 | 管理本部 | ステータス |
|------|:------:|:-------:|:-------:|:-------:|:------:|:-------:|---------|
| 混雑優先レーン | 🔒 | 🔒 | 🔒 | ✅ | ✅ | ✅ | PREMIUM_READY |
| 一括生成 | 🔒 | 🔒 | 🔒 | ✅ | ✅ | ✅ | HIDDEN² |

### 管理系

| 機能 | ゲスト | 無料会員 | 有料会員 | マスター | 管理者 | 管理本部 | ステータス |
|------|:------:|:-------:|:-------:|:-------:|:------:|:-------:|---------|
| 管理画面 | ❌ | ❌ | ❌ | ❌ | 🔧 | 🔧 | ADMIN_ONLY |
| ユーザー管理 | ❌ | ❌ | ❌ | ❌ | 🔧 | 🔧 | ADMIN_ONLY |
| トレンドシグナル管理 | ❌ | ❌ | ❌ | ❌ | 🔧 | 🔧 | ADMIN_ONLY |
| API利用量/コスト可視化 | ❌ | ❌ | ❌ | ❌ | 🔧 | 🔧 | ADMIN_ONLY |
| コンテンツモデレーション | ❌ | ❌ | ❌ | ❌ | 🔧 | 🔧 | ADMIN_ONLY |
| 管理本部画面 | ❌ | ❌ | ❌ | ❌ | ❌ | 🔧 | HQ_ONLY |
| 詳細分析/KPIダッシュボード | ❌ | ❌ | ❌ | ❌ | ❌ | 🔧 | HQ_ONLY |
| キャンペーン管理 | ❌ | ❌ | ❌ | ❌ | ❌ | 🔧 | HQ_ONLY |
| 管理者ユーザー管理 | ❌ | ❌ | ❌ | ❌ | ❌ | 🔧 | HQ_ONLY |

> ¹ ゲストは1日3回制限 (`static/js/core/guest.js`)  
> ² HIDDEN = フロントエンドに非表示。開発中または未実装。

---

## 3. admin と headquarters の違い

### admin (管理者) — 現場運営担当

```
担当範囲: 日常的なサイト運営
  ✅ ユーザー承認・停止・ロール変更
  ✅ 広場投稿の削除・モデレーション
  ✅ サーバー設定 (メンテナンスモード・告知バー)
  ✅ トレンドシグナル編集
  ✅ API利用量確認
  ❌ 戦略分析・KPI閲覧 → HQ専用
  ❌ キャンペーン管理   → HQ専用
  ❌ 他のadminユーザー管理 → HQ専用
```

### headquarters (管理本部) — 司令室・最上位制御

```
担当範囲: 戦略・統制・最上位管理
  ✅ adminの全権限に加えて
  ✅ 全ユーザー活動の詳細分析
  ✅ KPI・収益・コスト分析
  ✅ キャンペーン / プロモーション戦略管理
  ✅ 招待コード一括発行・管理
  ✅ adminユーザーのロール変更 (adminは他adminを管理できない)
  ✅ A/Bテスト設定 (将来実装)
```

---

## 4. FeatureStatus 定義

| ステータス | 値 | 意味 | フロント表示 |
|-----------|-----|------|-------------|
| `LIVE` | `"live"` | 本番稼働中 | ラベルなし |
| `BETA` | `"beta"` | ベータ版 (FREE実装済み・改善中) | `BETA` バッジ |
| `PREMIUM_READY` | `"premium_ready"` | 有料接続待ち (骨組みあり) | `有料版` バッジ |
| `ADMIN_ONLY` | `"admin_only"` | 管理者専用 | 管理者には表示 |
| `HQ_ONLY` | `"hq_only"` | 管理本部専用 | HQには表示 |
| `HIDDEN` | `"hidden"` | 非表示 (開発中) | 表示なし |
| `MAINTENANCE` | `"maintenance"` | メンテナンス中 | `メンテ中` バッジ |

---

## 5. FastAPI 依存性 クイックリファレンス

```python
from app.auth.dependencies import (
    get_current_user,       # 認証必須 (全ロール)
    get_current_user_soft,  # 認証任意 (None許容)
    require_member,         # ログイン済み全員
    require_paid,           # 有料会員以上
    require_master,         # マスター以上
    require_admin,          # admin + headquarters
    require_hq,             # headquarters のみ
    role_guard,             # 任意ロード指定ファクトリ
    has_role,               # ロールチェック (例外なし)
    is_admin_user,          # bool チェック
    is_hq_user,             # bool チェック
)
from app.core.roles import RoleValue  # ロール定数

# エンドポイント例
@router.post("/api/campaign")
async def campaign(user = Depends(require_paid)):
    ...

@router.get("/api/hq/analytics")
async def hq_analytics(user = Depends(require_hq)):
    ...

@router.get("/api/foo")
async def foo(user = Depends(role_guard(RoleValue.MEMBER_MASTER))):
    ...
```

---

## 6. 実装状態

| 層 | ファイル | 状態 |
|----|---------|------|
| ロール定義 | `app/core/roles.py` | ✅ Phase 2 実装済み |
| ポリシーテーブル | `app/core/access_policy.py` | ✅ Phase 18 時点で 30+ ポリシー定義済み |
| 依存性 | `app/auth/dependencies.py` | ✅ Phase 2 実装済み |
| アクセスサービス | `app/services/feature_access_service.py` | ✅ Phase 2 更新済み |
| DB ロールカラム | `app/db/models/user.py` | ✅ role カラムあり (subscription_plan も Phase 16 で追加) |
| JWT ロールクレーム | `app/core/security.py` | ✅ role フィールドあり |
| HQ 司令室 | `/hq` + `/api/hq/*` | ✅ Phase 18 実装済み |
| 管理本部サービス | `app/services/hq_dashboard_service.py` | ✅ Phase 18 実装済み |
| フロントへの公開 | `/api/system/features` | ✅ 実装済み |

---

## 7. Phase 15 以降の移行計画

```sql
-- Phase 15: DB migration
ALTER TABLE users MODIFY role VARCHAR(20);
-- 既存 "user" は member_free に相当するが後方互換として "user" を維持
-- 新規登録者は "member_free" を使用

-- 将来の role 値一覧:
-- "user"          (既存・後方互換)
-- "member_free"   (新規・Phase 15 以降)
-- "member_paid"
-- "member_master"
-- "admin"
-- "headquarters"
```

> `app/core/roles.py` の `RoleValue.MEMBER_FREE = "user"` は Phase 15 で  
> `"member_free"` に変更し、DB マイグレーション + JWT 更新を同時に行う。
