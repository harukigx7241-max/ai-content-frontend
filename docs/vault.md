# 保管庫 (Vault) 仕様書 — Phase A

## 概要

ログインユーザーが生成したプロンプトをサーバー DB に永続保存する機能。
再ログイン後も完全に復元される。ゲストは localStorage のみ利用可。

---

## DB モデル

### `saved_prompts`

| カラム       | 型           | 説明                                      |
|------------|------------|------------------------------------------|
| id         | INTEGER PK | 自動採番                                   |
| user_id    | INTEGER FK | users.id (インデックス付き)                   |
| title      | VARCHAR(100)| 表示タイトル                                 |
| content    | TEXT        | プロンプト本文 (最大 10,000 文字)             |
| source     | VARCHAR(20) | forge / square / template / remix / fork |
| is_favorite| BOOLEAN     | お気に入りフラグ                              |
| tags       | VARCHAR(200)| カンマ区切りタグ                              |
| folder_id  | INTEGER FK  | vault_folders.id (nullable = 未分類)      |
| summary    | TEXT        | 短いメモ (nullable)                         |
| status     | VARCHAR(20) | draft / completed / archived              |
| created_at | DATETIME    | UTC, 作成時刻                              |
| updated_at | DATETIME    | UTC, 最終編集時刻 (nullable)               |

### `vault_folders`

| カラム       | 型           | 説明                    |
|------------|------------|------------------------|
| id         | INTEGER PK | 自動採番                 |
| user_id    | INTEGER FK | users.id (インデックス付き)|
| name       | VARCHAR(50) | フォルダ名               |
| created_at | DATETIME    | UTC                     |

---

## API エンドポイント

全エンドポイントは `require_member` (認証必須)。  
ゲストは 401 → localStorage のみ使用。

### アイテム系

| メソッド | パス                        | 説明                                    |
|---------|---------------------------|----------------------------------------|
| GET     | /api/vault                 | 一覧 (クエリパラメータでフィルタ・検索)      |
| POST    | /api/vault                 | 保存 (最大 200 件)                       |
| GET     | /api/vault/{id}            | 詳細取得                                 |
| PATCH   | /api/vault/{id}            | 更新 (title/tags/folder/status/summary) |
| DELETE  | /api/vault/{id}            | 削除                                    |
| PATCH   | /api/vault/{id}/fav        | お気に入り切替 (後方互換)                  |

**GET /api/vault クエリパラメータ:**

| パラメータ  | 型      | 説明                  |
|----------|--------|----------------------|
| folder_id | int    | フォルダ絞り込み          |
| fav      | bool   | お気に入りのみ            |
| source   | str    | ソース絞り込み            |
| status   | str    | ステータス絞り込み         |
| q        | str    | タイトル・本文・タグ全文検索 |
| tag      | str    | タグ部分一致検索          |

### フォルダ系

| メソッド | パス                            | 説明                              |
|---------|-------------------------------|----------------------------------|
| GET     | /api/vault/folders             | フォルダ一覧 (件数付き)            |
| POST    | /api/vault/folders             | 作成 (最大 20 個)                 |
| PATCH   | /api/vault/folders/{folder_id} | 名前変更                           |
| DELETE  | /api/vault/folders/{folder_id} | 削除 (中身は未分類に移動)           |

---

## 上限定数 (プラン差分の起点)

```python
# app/routers/vault.py
MAX_ITEMS   = 200  # アイテム上限 (将来: paid → 500, master → unlimited)
MAX_FOLDERS = 20   # フォルダ上限 (将来: paid → 50)
```

将来の有料プラン拡張はここを参照して分岐を追加する。

---

## 保存元との連携

| 保存元               | source 値  | 実装状況           |
|--------------------|-----------|--------------------|
| 工房・鍛冶場          | forge     | ✅ forge.js         |
| 広場投稿詳細          | square    | ✅ square_detail.html|
| テンプレートライブラリ  | template  | 🔜 (将来実装)       |
| Remix / Fork 結果   | remix/fork| 🔜 (将来実装)       |

**forge.js の二重保存フロー:**
1. localStorage に即時保存 (ゲスト含む全員・モーダル表示用)
2. ログイン済みなら `/api/vault` に POST し、`serverId` をローカルに記録
3. forge モーダルで削除すると `serverId` があれば DELETE も実行

**square_detail.html のフロー:**
1. localStorage に保存 (ゲスト含む全員)
2. `{% if user %}` ブロックで `/api/vault` POST も実行 (source=square)

---

## 権限設計

| ロール             | アクセス可否          | 備考                          |
|------------------|---------------------|-------------------------------|
| guest (0)        | ❌ (401)             | localStorage のみ              |
| member_free (1)  | ✅                   | 200 件 / 20 フォルダ           |
| member_paid (2)  | ✅ (将来: 上限緩和)   | MAX_ITEMS/MAX_FOLDERS を参照   |
| member_master (3)| ✅ (将来: 無制限)     | 同上                           |
| admin (4)        | 自分のデータのみ      | 他ユーザーのデータは参照しない   |
| headquarters (5) | 監査 API (将来実装)   | 一般ユーザーの中身は不用意に見ない|

---

## UI 機能 (mypage.html)

- フォルダチップによるフォルダフィルター
- テキスト検索 (タイトル・本文・タグ)
- ソース別フィルター (すべて / お気に入り / 鍛冶場 / 広場 / テンプレ)
- 並び替え (新着 / 更新 / お気に入り優先 / タイトル順)
- アイテムカード: タイトル・プレビュー・タグ・フォルダ名・ステータス・日付
- 編集モーダル: タイトル / タグ / フォルダ / ステータス / メモ
- フォルダ管理: 作成 / 名前変更 / 削除
- エクスポート (JSON) / インポート (JSON)
- 空状態 UI

---

## 将来の拡張余地

- **保存件数上限**: `MAX_ITEMS` を role ベースで可変に
- **フォルダ上限**: `MAX_FOLDERS` を role ベースで可変に
- **チーム共有保管庫**: vault_folders に `team_id` 追加
- **公開/非公開切替**: SavedPrompt に `visibility` カラム追加
- **バージョン履歴**: `vault_item_versions` テーブルで履歴管理
- **リミックス系統図**: `source_id` + `source` で親子関係を可視化
