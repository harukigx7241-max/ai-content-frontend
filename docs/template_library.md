# テンプレートライブラリ ドキュメント

> Phase 5 導入  
> 最終更新: 2026-04-16

---

## 概要

`templates_library/` はカテゴリ別・媒体別・用途別に細分化された **プロンプトテンプレート** の格納場所。  
各テンプレートは **フォームのデフォルト値** を持ち、UI 上の「テンプレートギャラリー」から呼び出される。

---

## ディレクトリ構造

```
templates_library/
├── _index.json          # 全テンプレートの索引 (21件)
├── _schema.json         # メタデータスキーマ定義 (v2.0)
├── _parts/              # 共通部品ファイル
│   ├── hooks.json           # フック（掴み）パターン 6種
│   ├── title_templates.json # タイトル生成パターン
│   ├── intro_templates.json # 導入文パターン (PAS/権威/ストーリー)
│   ├── body_patterns.json   # 本文構成パターン 5種
│   ├── cta_templates.json   # CTA（行動喚起）パターン 5種
│   ├── closings.json        # 締め文パターン 5種
│   ├── anti_patterns.md     # アンチパターン集
│   └── examples.md          # カテゴリ別出力サンプル集
├── common/              # 媒体横断共通テンプレート
│   ├── authority.json       # 権威プロフィール
│   └── story.json           # ストーリー型自己開示
├── note/                # note 有料記事
│   ├── beginner_income.json # AI副業入門
│   ├── sns_growth.json      # SNS運用術
│   ├── educational.json     # 教育型ハウツー
│   └── seasonal.json        # 年末年始特集
├── tips/                # tips デジタル販売
│   ├── beginner.json        # tips 入門
│   └── premium.json         # バンドル・高単価
├── brain/               # Brain 情報商材
│   ├── authority.json       # 権威者ページ
│   └── conversion.json      # コンバージョン設計
├── sns/                 # SNS 投稿・プロフィール
│   ├── side_hustle_announce.json  # 副業告知
│   ├── campaign.json              # 商品発売告知シリーズ
│   └── announcement.json          # プロフィール最適化
├── sales/               # セールスライティング
│   └── landing_page.json    # デジタル商品 LP
├── fortune/             # 占い副業
│   ├── tarot_love.json      # タロット恋愛鑑定
│   └── authority.json       # 占い師権威ページ
├── cw/                  # クラウドワークス
│   ├── writer_proposal.json # ライター提案文
│   └── conversion.json      # 高単価案件獲得プロフィール
├── blog/                # ブログ記事
│   └── beginner.json        # SEO記事入門
├── email/               # メルマガ・LINE
│   └── newsletter.json      # 週刊メルマガ
└── prompt_forge/        # プロンプト設計ツール
    └── role_definition.json # 役割定義マスター
```

---

## メタデータスキーマ (v2.0)

各テンプレート JSON の `_meta` に以下 16 フィールドが必須：

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | string | ユニーク ID (スネークケース) |
| `title` | string | 表示名 |
| `category` | string | カテゴリ名 (下表参照) |
| `subcategory` | string | サブカテゴリ名 (下表参照) |
| `platform` | string[] | 対応プラットフォーム |
| `target_audience` | string | ターゲット読者像 |
| `goal` | string | このテンプレートで達成できること |
| `tone` | string | 文体・トーン |
| `difficulty` | string | `beginner` / `intermediate` / `advanced` |
| `tags` | string[] | 検索・フィルタ用タグ |
| `seasonality` | string | `all_year` / `year_end` / `spring` 等 |
| `last_updated` | string | 最終更新日 (YYYY-MM-DD) |
| `requires_ai` | boolean | AI (ChatGPT等) が必要か |
| `free_available` | boolean | 無料プランで使用可能か |
| `rarity` | string | `common` / `uncommon` / `rare` / `epic` / `legendary` |
| `knowledge_ref` | string \| null | 対応する knowledge/ ファイルのパス |

---

## カテゴリ・サブカテゴリ一覧

### カテゴリ

| カテゴリ ID | 説明 |
|---|---|
| `note` | note 有料記事 |
| `tips` | tips デジタルコンテンツ販売 |
| `brain` | Brain 情報商材 |
| `sns` | SNS 投稿・プロフィール |
| `sales` | セールスライティング / LP |
| `fortune` | 占い副業 |
| `cw` | クラウドワークス |
| `blog` | ブログ記事 |
| `email` | メルマガ・LINE 公式 |
| `common` | 媒体横断共通 |
| `prompt_forge` | プロンプト設計ツール |

### サブカテゴリ

| サブカテゴリ ID | 説明 |
|---|---|
| `beginner` | 初心者向け基本テンプレート |
| `educational` | 教育・解説型コンテンツ |
| `authority` | 権威・実績訴求 |
| `story` | ストーリー・体験談型 |
| `review` | レビュー・比較型 |
| `conversion` | 購買・CV 率最大化 |
| `seasonal` | 季節限定・期間特化 |
| `premium` | 上級者・高単価向け |
| `campaign` | キャンペーン・告知シリーズ |
| `announcement` | プロフィール・アナウンス |

---

## レアリティ (Rarity) システム

ゲーム UI のランクバッジと連動：

| レアリティ | 色 | 用途 |
|---|---|---|
| `common` | ブロンズ | 汎用・基本テンプレート |
| `uncommon` | シルバー | 中級・用途特化テンプレート |
| `rare` | ゴールド | 上級・高成果が期待できるテンプレート |
| `epic` | プラチナ | 専門性の高い特化テンプレート |
| `legendary` | 紫グロー | 最高レベルの希少テンプレート |

---

## ナレッジ ↔ テンプレート 対応表

`_meta.knowledge_ref` フィールドで `knowledge/` ファイルと紐付ける。

| テンプレート ID | knowledge_ref |
|---|---|
| `note_beginner_income` | `workshops/note/overview.md` |
| `note_sns_growth` | `workshops/note/trend_signals.json` |
| `note_educational_howto` | `workshops/note/overview.md` |
| その他 | `null` (紐付けなし) |

---

## Python サービス API

### TemplateService (app/services/template_service.py)

```python
from app.services.template_service import template_service

# カテゴリ一覧
result = template_service.categories()        # ServiceResult

# テンプレート一覧 (フィルタ付き)
result = template_service.list(
    category="note",
    difficulty="beginner",
)

# テンプレート詳細
result = template_service.get("note_beginner_income")

# フォームデフォルト値のみ
result = template_service.form_defaults("note_beginner_income")

# _parts/ 部品取得
result = template_service.part("hooks.json")
result = template_service.part("examples.md")
```

### モジュール関数 (TemplateService を使わない場合)

```python
from app.services.template_service import (
    list_templates, get_template, get_form_defaults,
    get_meta, get_categories, get_part, invalidate_cache
)

templates = list_templates(category="sns", tag="副業")
tmpl = get_template("fortune_tarot_love")
```

### KnowledgeService との連携

```python
from app.services.knowledge_service import knowledge_service

# ナレッジサービス経由でテンプレート部品を取得
result = knowledge_service.template_parts("hooks.json")
```

---

## _parts/ 部品ファイル使用ガイド

| ファイル | 内容 | 用途 |
|---|---|---|
| `hooks.json` | 6種のフック（掴み）パターン | 冒頭の注意引き文 |
| `title_templates.json` | タイトル生成パターン | 記事・商品タイトル |
| `intro_templates.json` | 導入文パターン | PAS/権威/ストーリー型 |
| `body_patterns.json` | 本文構成パターン | ステップ/柱/Q&A等 |
| `cta_templates.json` | CTA パターン | 有料壁/SNS/購入誘導 |
| `closings.json` | 締め文パターン | 行動促進/感謝/次ステップ |
| `anti_patterns.md` | アンチパターン集 | プロンプト設計時の注意点 |
| `examples.md` | 出力サンプル集 | ユーザー参考・UI 表示用 |

---

## 今後の拡張予定

- `_index.json` の `/api/templates` エンドポイント公開 (Phase 19 予定)
- ベクトル類似検索対応 (`template_service._run_api()`)
- ユーザー別お気に入りテンプレート (localStorage 連携)
- テンプレートギャラリー UI (Tab 上部クイックスタートパネル)
