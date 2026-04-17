# 管理者専用集客工房 (Admin Growth Tools)

> 対象バージョン: Phase 17+  
> 最終更新: 2026-04-17  
> 関連ファイル: `app/services/admin_growth_service.py`

---

## 概要

**管理者専用の集客支援ツール群**。11種のプロンプト生成ツールを一元管理する。

- **現フェーズ (Phase 17)**: admin / headquarters のみ利用可能
- **将来の解放**: 各ツールは `future_unlock` フィールドで解放予定ロールを示す
- **API未接続でも動作**: FREE tier のテンプレートベース実装が常に動く
- **生成物**: プロンプト文字列のみを返す。ユーザーが ChatGPT / Gemini / Claude に貼り付けて使用

---

## ツール一覧

| ツール ID | ラベル | カテゴリ | 将来解放予定ロール |
|-----------|--------|----------|----------------|
| `campaign_forge` | キャンペーン工房 | 販促・告知 | member_paid |
| `note_promotion` | note販促ビルダー | 販促・告知 | member_paid |
| `auto_research` | リサーチ下書き生成 | コンテンツ生成 | member_paid |
| `image_campaign` | 画像キャンペーンビルダー | 画像プロンプト | member_paid |
| `multi_channel_pack` | マルチチャンネル記事パック | コンテンツ生成 | member_paid |
| `launch_pack` | ローンチパックビルダー | 販促・告知 | member_paid |
| `promo_calendar` | 販促カレンダー生成 | スケジュール | member_paid |
| `hook_library` | フック文ライブラリ | コンテンツ生成 | member_paid |
| `variation_generator` | バリエーション生成 | コンテンツ生成 | member_paid |
| `promo_score` | 販促スコアリング | 分析・スコアリング | member_master |
| `scribe_campaign` | ギルド書記キャンペーンモード | 販促・告知 | member_paid |

---

## 機能詳細

### 既存サービス委譲ツール (5種)

| ツール | 委譲先サービス | 主な入力 |
|--------|--------------|---------|
| `campaign_forge` | `campaign_forge_service.build_prompt()` | title, target, value, price |
| `note_promotion` | `promotion_planner_service.build_plan()` | product_name, platform, price, target, strengths |
| `auto_research` | `article_draft_service.generate_draft()` | theme, target, tone |
| `image_campaign` | `ImagePromptService.build_as_result()` | theme, image_type, style |
| `scribe_campaign` | `guild_scribe_service.generate_post()` | campaign_theme, platform, point1, point2 |

### 新ツール (6種)

#### multi_channel_pack — マルチチャンネル記事パック
1記事を5チャンネル (X / Instagram / note / メルマガ / YouTube) 向けに展開するプロンプトを生成。
- 入力: `article_title`, `key_points`, `target_audience`

#### launch_pack — ローンチパックビルダー
商品ローンチに必要な7素材 (LP キャッチ・先行告知・メール・FAQ・レビュー依頼・アフィリエイター案内・フォローメール) のプロンプトを一括生成。
- 入力: `product_name`, `price`, `launch_date`, `target`, `unique_value`

#### promo_calendar — 販促カレンダー生成
5フェーズ30日間 (認知拡大→興味喚起→欲求促進→販売促進→クロージング) の販促スケジュールを生成。
- 入力: `product_name`, `start_date`, `platform`

#### hook_library — フック文ライブラリ
10スタイル (衝撃の事実型/共感型/数字型/問いかけ型/逆説型/ストーリー型/緊急性型/権威型/好奇心型/ビフォーアフター型) のフック文 + 解説を生成。
- 入力: `theme`, `audience`, `tone`

#### variation_generator — バリエーション生成
既存コンテンツを3トーン (エモーショナル / ロジカル / ストーリー) でリライトするプロンプトを生成。
- 入力: `original_content`, `variation_style`

#### promo_score — 販促スコアリング
販促プランを5軸 (ターゲット明確度・差別化・CTA設計・コンテンツ品質・継続性拡散性) で採点・改善提案するプロンプトを生成。
- 入力: `promotion_plan`, `target_platform`

---

## アーキテクチャ

```
app/services/admin_growth_service.py
  └─ AdminGrowthService(BaseService)
       ├─ list_tools()           → GrowthToolDef 一覧
       ├─ run_tool(tool_id, params)  → ServiceResult
       │    ├─ _campaign_forge()     → campaign_forge_service
       │    ├─ _note_promotion()     → promotion_planner_service
       │    ├─ _auto_research()      → article_draft_service
       │    ├─ _image_campaign()     → ImagePromptService
       │    ├─ _scribe_campaign()    → guild_scribe_service
       │    ├─ _multi_channel_pack() → テンプレートベース (新)
       │    ├─ _launch_pack()        → テンプレートベース (新)
       │    ├─ _promo_calendar()     → テンプレートベース (新)
       │    ├─ _hook_library()       → テンプレートベース (新)
       │    ├─ _variation_generator()→ テンプレートベース (新)
       │    └─ _promo_score()        → テンプレートベース (新)
       └─ GROWTH_TOOLS: dict[str, GrowthToolDef]
```

---

## API エンドポイント

| エンドポイント | 認証 | 説明 |
|--------------|------|------|
| `GET /api/admin/growth/tools` | admin | 全ツール定義と入力フィールド一覧を返す |
| `POST /api/admin/growth/run` | admin | 指定ツールを実行してプロンプトを返す |

### GET /api/admin/growth/tools レスポンス例

```json
{
  "tools": [
    {
      "tool_id": "campaign_forge",
      "label": "キャンペーン工房",
      "icon": "⚔",
      "description": "SNS告知文・キャンペーン文のプロンプト生成",
      "category": "promotion",
      "future_unlock": "member_paid",
      "inputs": ["title", "target", "value", "price"],
      "sort_order": 1
    },
    ...
  ],
  "total": 11,
  "categories": {
    "promotion": "販促・告知",
    "content": "コンテンツ生成",
    "image": "画像プロンプト",
    "calendar": "スケジュール",
    "analysis": "分析・スコアリング"
  }
}
```

### POST /api/admin/growth/run リクエスト例

```json
{
  "tool_id": "launch_pack",
  "params": {
    "product_name": "副業スタートガイド",
    "price": "1980",
    "launch_date": "2026-05-01",
    "target": "副業を始めたい30代会社員",
    "unique_value": "実体験に基づく7日間プログラム"
  }
}
```

### POST /api/admin/growth/run レスポンス例

```json
{
  "prompt": "あなたはデジタルコンテンツ販売で累計1億円以上を...",
  "tool_id": "launch_pack",
  "hint": "ローンチに必要な7素材のプロンプトです"
}
```

---

## UI: 集客工房パネル

管理ダッシュボードの「🚀 集客工房」タブ:

1. **ツールグリッド**: 11ツールをカード形式で表示
   - アイコン・名前・説明・カテゴリバッジ・将来解放ロールバッジ
   - カードクリックでモーダルを開く

2. **ツール実行モーダル**:
   - ツールごとに動的フォームフィールドを生成
   - 「▶ プロンプト生成」ボタンで API 呼び出し
   - 生成結果を表示 + ワンクリックコピー
   - ChatGPT / Gemini / Claude へのリンクを表示

---

## 有料会員への解放手順 (Phase 18+)

各ツールを有料会員に解放するには:

1. `access_policy.py` の対応する `FeaturePolicy` を変更:
   ```python
   # 変更前
   "admin_growth_multi_channel": FeaturePolicy(
       required_role=RoleValue.ADMIN,
       status=FeatureStatus.ADMIN_ONLY,
       ...
   ),
   # 変更後
   "admin_growth_multi_channel": FeaturePolicy(
       required_role=RoleValue.MEMBER_PAID,
       status=FeatureStatus.LIVE,
       ...
   ),
   ```

2. ユーザー向けルーター (`app/routers/`) に対応エンドポイントを追加

3. `templates/index.html` の Premium Teaser セクションに対応カードを追加

---

## 関連ファイル

- `app/services/admin_growth_service.py` — メインオーケストレーター
- `app/services/campaign_forge_service.py` — campaign_forge 委譲先
- `app/services/promotion_planner_service.py` — note_promotion 委譲先
- `app/services/article_draft_service.py` — auto_research 委譲先
- `app/services/image_prompt_service.py` — image_campaign 委譲先
- `app/services/guild_scribe_service.py` — scribe_campaign 委譲先
- `app/admin/router.py` — `/api/admin/growth/*` エンドポイント
- `app/core/access_policy.py` — `admin_growth_*` FeaturePolicy 定義
- `app/core/config.py` — `ENABLE_ADMIN_GROWTH_*` フラグ
- `templates/admin/dashboard.html` — 集客工房パネル UI
- `docs/subscription.md` — 有料プラン解放マップ
