# Phase 0 — コードベース再監査レポート

> 最終更新: 2026-04-11  
> 目的: 実装済み / 仮実装 / 骨組みのみ / 未実装 を再確認し、以後のフェーズで認識ズレを防ぐ

---

## 1. 主要画面

| 画面 | URL | 状態 | 備考 |
|------|-----|------|------|
| トップ工房 | `/` | ✅ 完全実装済み | hero・4工房タブ・収益シミュレーター・ゲスト制限 |
| ログイン | `/login` | ✅ 完全実装済み | SNS プラットフォーム + パスワード認証 |
| 新規登録 | `/register` | ✅ 完全実装済み | SNS ハンドル・表示名・規約同意 |
| マイページ | `/mypage` | ✅ 完全実装済み | プロフィール / 活動 / 設定タブ、XP バー |
| ギルド広場 | `/square` | ✅ 完全実装済み | 検索・フィルタ・注目ログ・ページネーション |
| 広場詳細 | `/square/{id}` | ✅ 完全実装済み | いいね / 保存・閲覧数・著者情報 |
| 管理ダッシュボード | `/admin` | ✅ 完全実装済み | 統計・ユーザー管理・分析・トレンド管理 |

---

## 2. 機能状態一覧

### ✅ 完全実装済み

| 機能 | 主要ファイル |
|------|------------|
| スマホ基本対応 (768/520/480px) | `static/css/style.css` |
| ロゴ / 見出し演出 | `templates/index.html` |
| ギルド世界観 UI (琥珀色テーマ) | `static/css/style.css` |
| 工房カード 4 種 | `templates/index.html` |
| ギルド依頼板 (広場) | `templates/square.html` + `app/community/` |
| XP / ランク / 称号 (Lv1-99・5称号) | `app/gamification/` |
| like / save / 人気 / 新着ソート | `app/community/router.py` |
| ゲスト制限 (1日3回) | `static/js/core/guest.js` |
| API 機能フラグ基盤 | `app/core/feature_flags.py` |
| Prompt Forge (4工房) | `app/prompts/builders/` |
| Guild Guide AI (スクリプト版) | `static/js/core/guild_guide.js` |
| Trend refresh シグナル | `knowledge/workshops/*/trend_signals.json` |
| 日本語固定サフィックス | `app/prompts/suffixes/japanese.py` |
| 管理本部 (承認・停止・設定) | `app/admin/` |
| 画像プロンプト生成 | `app/services/image_prompt_service.py` |
| 認証基盤 (JWT・ステータス管理) | `app/auth/` |
| ナレッジベースローダー | `app/services/knowledge_service.py` |
| トレンド注入 | `app/services/trend_service.py` |

### 🔶 一部実装済み

| 機能 | 状態 | 不足部分 |
|------|------|---------|
| テンプレ市場 | 広場が代替機能として動作 | 専用ページ・評価システムなし |
| Guild Guide AI | スクリプトヒントのみ | LLM API 未接続 |
| 画像生成連携 | プロンプト生成のみ | 実際の画像 API 未接続 |

### 🟡 UI のみ

| 機能 | 不足部分 |
|------|---------|
| テンプレ診断 Lite | 入力充実度スコアのみ・AI 診断なし |
| 保管庫 (saved prompts) | UI 言及あり・専用 API なし |

### 🟠 骨組みのみ

| 機能 | 不足部分 |
|------|---------|
| クエスト / 実績 / デイリー任務 | バッジ定数のみ・進捗・リセット・達成判定なし |

### ❌ 未実装

| 機能 | 優先度 |
|------|--------|
| スマホ完全最適化 (ハンバーガー・ボトムナビ) | 🔴 最高 |
| ロール体系拡張 (6ロール) | 🔴 最高 |
| admin / HQ 権限分離 | 🔴 最高 |
| API 利用量 / コスト可視化 | 🟠 高 |
| テンプレライブラリ | 🟠 高 |
| 混雑表示 | 🟡 中 |
| Prompt Doctor | 🟡 中 |
| Workshop Master AI | 🟡 中 |
| 管理者集客工房 | 🟡 中 |
| 自動記事下書き | 🟡 中 |
| Launch Pack / Campaign Forge | 🟡 中 |
| Note Promotion Builder | 🟡 中 |

---

## 3. ロールシステム現状

```python
# app/db/models/user.py
role = Column(String(20), nullable=False, default="user")
# 現状: "user" | "admin" の 2 種のみ
# 必要: guest | member_free | member_paid | member_master | admin | headquarters
```

---

## 4. サービス一覧

| ファイル | 目的 | 状態 |
|---------|------|------|
| `generate_service.py` | プロンプト生成オーケストレーター | ✅ |
| `knowledge_service.py` | ナレッジ JSON/MD ローダー | ✅ |
| `trend_service.py` | トレンドシグナル注入 | ✅ |
| `image_prompt_service.py` | 画像プロンプト構築 | ✅ |
| `note_format_service.py` | note.com 形式整形 | ✅ |
| `input_mode_service.py` | 入力モード補足文 | ✅ |
| `community_service.py` | 広場 CRUD + reactions | ✅ |
| `gamification_service.py` | XP 付与・レベル計算 | ✅ |
| 生成ログサービス | API 利用量追跡 | ❌ 未実装 |

---

## 5. 以降のフェーズ優先順位

→ `docs/roadmap_phases.md` 参照
