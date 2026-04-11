# Phase 0 — コードベース再監査レポート

> 最終更新: 2026-04-11 (Phase 13 完了後・第2回監査)  
> 目的: 実装済み / 仮実装 / 骨組みのみ / 未実装 を再確認し、以後のフェーズで認識ズレを防ぐ

---

## 1. 主要画面

| 画面 | URL | 状態 | 備考 |
|------|-----|------|------|
| トップ工房 | `/` | ✅ 完全実装済み | hero・4工房タブ・収益シミュレーター・ゲスト制限・スマホUI |
| ログイン | `/login` | ✅ 完全実装済み | SNS プラットフォーム + パスワード認証 |
| 新規登録 | `/register` | ✅ 完全実装済み | SNS ハンドル・表示名・規約同意 |
| マイページ | `/mypage` | 🔶 一部実装済み | プロフィール / 活動(stub) / 設定タブ、XP バー |
| ギルド広場 | `/square` | 🔶 一部実装済み | 検索・フィルタ・注目ログ・ソート・ページネーションデータあり(UIコントロール不足) |
| 広場詳細 | `/square/{id}` | 🔶 一部実装済み | いいね / 保存・著者情報 (コメント・閲覧数は未実装) |
| 管理ダッシュボード | `/admin` | 🔶 一部実装済み | 統計・ユーザー管理・分析・トレンド管理 (API コスト可視化は stub) |

---

## 2. 機能状態一覧

### ✅ 完全実装済み

| 機能 | 主要ファイル |
|------|------------|
| **スマホ完全最適化** (Phase 13) | `static/css/style.css`, `templates/*.html` |
| ハンバーガー + モバイルドロワー | `templates/index.html`, `templates/square.html`, `templates/mypage.html`, `templates/admin/dashboard.html` |
| モバイルボトムナビ (6ボタン) | `static/css/style.css` (`.mobile-bottom-nav`), `static/js/app.js` |
| ブレークポイント 375 / 480 / 520 / 768px | `static/css/style.css` (Phase 13 mobile block) |
| タッチターゲット 44px 保証 | `static/css/style.css` |
| ロゴ / 見出し演出 (gradient + orb) | `templates/index.html`, `static/css/style.css` |
| ギルド世界観 UI (琥珀色テーマ) | `static/css/style.css` (`:root` warm lodge variables) |
| 工房カード 4 種 + スクロール遷移 | `templates/index.html`, `static/js/app.js` |
| ギルド広場 (like / save / sort / featured) | `templates/square.html` + `app/community/` |
| XP / ランク / 称号 (Lv1-99・5称号) | `app/gamification/` |
| ゲスト制限 (1日3回) | `static/js/core/guest.js` |
| API 機能フラグ基盤 | `app/core/feature_flags.py` |
| Prompt Forge (4工房 + enhance/remix) | `app/prompts/builders/` |
| Guild Guide AI (スクリプト版) | `static/js/core/guild_guide.js` |
| ガイド ON/OFF localStorage 設定 | `static/js/core/guild_guide.js`, `templates/mypage.html` |
| Trend シグナルファイル | `knowledge/workshops/*/trend_signals.json` |
| 日本語固定サフィックス | `app/prompts/suffixes/japanese.py` |
| 管理本部 (承認・停止・設定・トレンド) | `app/admin/` |
| 画像プロンプト生成 | `app/services/image_prompt_service.py` |
| 認証基盤 (JWT・ステータス管理) | `app/auth/` |
| ナレッジベースローダー | `app/services/knowledge_service.py` |
| トレンド注入 | `app/services/trend_service.py` |

### 🔶 一部実装済み

| 機能 | 状態 | 不足部分 |
|------|------|---------|
| マイページ 活動タブ | stub HTML あり | 生成ログ API なし・表示データなし |
| ギルド広場 ページネーション | データ側は実装済み | prev/next ボタン UI なし |
| 管理ダッシュボード 分析 | KPI stub あり | API 利用量・コスト実データなし |
| Guild Guide AI | スクリプトヒントのみ | LLM API 未接続 |
| 画像生成連携 | プロンプト生成のみ | 実際の画像 API 未接続 |

### 🟡 UI のみ

| 機能 | 不足部分 |
|------|---------|
| テンプレ診断 Lite (quality badge) | 入力充実度スコアのみ・AI 診断バックエンドなし |
| 保管庫 (saved prompts) | UI 言及あり・localStorage のみ・専用 DB API なし |

### 🟠 骨組みのみ

| 機能 | 不足部分 |
|------|---------|
| テンプレライブラリ | `knowledge/workshops/` に JSON あり・ギャラリー UI なし・`/api/templates` エンドポイントなし |
| クエスト / 実績 / デイリー任務 | バッジ定数のみ・進捗・リセット・達成判定なし |
| 管理者集客工房 | Invite モデルあり・`ENABLE_INVITE_SYSTEM=False`・UI なし |

### ❌ 未実装

| 機能 | 優先度 |
|------|--------|
| ロール体系拡張 (6ロール) | 🔴 最高 |
| admin / HQ 権限分離 | 🔴 最高 |
| API 利用量 / コスト可視化 (実データ) | 🟠 高 |
| 保管庫バックエンド API | 🟠 高 |
| テンプレライブラリ UI + エンドポイント | 🟠 高 |
| 生成ログ (`generation_log`) テーブル | 🟠 高 |
| 広場 ページネーション UI コントロール | 🟡 中 |
| 混雑表示 | 🟡 中 |
| Prompt Doctor | 🟡 中 |
| Workshop Master AI | 🟡 中 |
| 自動記事下書き | 🟡 中 |
| Launch Pack / Campaign Forge | 🟡 中 |
| Note Promotion Builder | 🟡 中 |
| コメント機能 (広場詳細) | 🟡 中 |

---

## 3. ロールシステム現状

```python
# app/db/models/user.py
role = Column(String(20), nullable=False, default="user")
# 現状: "user" | "admin" の 2 種のみ
# 必要: guest | member_free | member_paid | member_master | admin | headquarters
```

テンプレートでは `user.role in ('admin', 'headquarters')` チェックを前方互換として追加済み。  
Python auth 側 (`require_admin`) はまだ `"admin"` のみ対応。

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

## 5. スマホ UI 実装詳細 (Phase 13)

| 要素 | CSS クラス | 状態 |
|------|-----------|------|
| ハンバーガーボタン | `.hamburger-btn` | ✅ (768px 以下で表示) |
| モバイルドロワー | `.mobile-drawer` | ✅ (slide-in, overlay) |
| ドロワー内ナビ | `#mobileDrawerNav` | ✅ (JS で動的に auth リンク注入) |
| ボトムナビ | `.mobile-bottom-nav` | ✅ (6ボタン: note/cw/fortune/sns/square/mypage) |
| ボトムナビ連動 | `updateBottomNav(tabId)` | ✅ (タブ切替と同期) |
| Esc / 外クリック | `initMobileMenu()` | ✅ |
| iOS zoom 防止 | `font-size: 16px` on inputs | ✅ (`@media max-width: 480px`) |
| 対象テンプレート | index / square / mypage / admin | ✅ 全4画面統一 |

---

## 6. 以降のフェーズ優先順位

→ `docs/roadmap_phases.md` 参照
