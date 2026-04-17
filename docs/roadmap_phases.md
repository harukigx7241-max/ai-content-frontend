# フェーズロードマップ (Roadmap Phases)

> 最終更新: 2026-04-11 (Phase 2 完了)  
> ブランチ: `claude/phase13-mobile-game-ui`  
> 方針詳細: `docs/fixed_requirements.md`

---

## 完了済みフェーズ

| Phase | タイトル | ブランチ | コミット |
|-------|----------|---------|---------|
| 0 | 現状監査 (初回) | side-hustle-web-app-195e3 | 8b6e59e |
| 1 | 明るいロッジ CSS テーマ全面刷新 | side-hustle-web-app-195e3 | 8b6e59e |
| 2 | ブランドワーディング統一 (副業→工房) | side-hustle-web-app-195e3 | abfa0eb |
| 3 | トップページ hero + 工房ガイド再設計 | side-hustle-web-app-195e3 | f53591d |
| 4 | ゲスト体験改善 (⚗ 見習い冒険者) | side-hustle-web-app-195e3 | e83d420 |
| 5 | ギルド広場・注目ログ強化 | side-hustle-web-app-195e3 | e83d420 |
| 6 | マイページ XP アニメーション | side-hustle-web-app-195e3 | e83d420 |
| 7 | 効果音・アニメーション拡張 | side-hustle-web-app-195e3 | e83d420 |
| 8 | ガイドウィジェット設定トグル | side-hustle-web-app-195e3 | e83d420 |
| 9 | 日本語ファースト出力レイヤー | side-hustle-web-app-195e3 | cd60e28 |
| 10 | ナレッジベース Python ローダー | side-hustle-web-app-195e3 | cd60e28 |
| 11 | トレンド注入スキャフォールド | side-hustle-web-app-195e3 | cd60e28 |
| 12 | 管理トレンド収集室 | side-hustle-web-app-195e3 | cd60e28 |
| 0 (再・Phase 13 前) | コードベース再監査・docs 整備 | phase13-mobile-game-ui | bb46f6d |
| **13** | **スマホ完全最適化** (ハンバーガー・ドロワー・ボトムナビ) | phase13-mobile-game-ui | **14e9bd8** |
| 0 (再・Phase 13 後) | コードベース再監査・docs 更新 | phase13-mobile-game-ui | 1203f17 |
| **1** | **サービス層整理 (FREE-first API-ready)** | phase13-mobile-game-ui | 8ec368f |
| **2** | **ロール体系 + アクセスポリシー整備** | phase13-mobile-game-ui | abfa0eb |
| **3** | **レスポンシブ全面見直し** (4 段階ティア・モーダル・ボトムナビ拡充) | phase13-mobile-game-ui | b813eee |
| **4** | **ゲーム UI 強化** (SVG ロゴ・Cinzel フォント・レアリティバッジ・カード台帳風) | phase13-mobile-game-ui | c1130b6 |
| **5** | **テンプレートライブラリ拡張** (21件・11カテゴリ・_parts 8ファイル・template_service.py) | phase13-mobile-game-ui | 22198ca |
| **6** | **無料テンプレート武器庫** (46件・6パック・武器庫UI・/api/templates) | phase13-mobile-game-ui | 89b1b4f |
| **7** | **テンプレ鍛冶場** (Mixer・Path・Compare・Vault・forge.js・/api/templates/parts) | phase13-mobile-game-ui | 420348a |
| **8** | **診断 Lite** (プロンプト診断10項目・日本語品質10項目・diagnose.js・/api/diagnose) | phase13-mobile-game-ui | ee5b0f4 |
| **9** | **ギルド掲示板 + テンプレ市場** (sort×4・Fork・Remix・保管庫連携・popularity_tier) | phase13-mobile-game-ui | (本コミット) |

---

## 予定フェーズ

### Phase 15 — ロール体系拡張 + HQ 権限分離 🔴 最高

**目的:** 6ロール定義・admin / headquarters の権限分離

実装内容:
- [ ] DB: `role` カラムを 6 値に拡張 (Alembic migration)
- [ ] `member_free` / `member_paid` / `member_master` / `headquarters` 追加
- [ ] `ADMIN_ROLES` / `HQ_ROLES` / `MEMBER_ROLES` 定数分離
- [ ] `require_hq` FastAPI 依存性追加
- [ ] HQ 専用エンドポイント `/api/hq/*`
- [ ] 管理画面に HQ タブ追加

---

### Phase 16 — API ON/OFF インフラ基盤 🟠 高

**目的:** 機能単位の API 制御・予算上限・フォールバックモード

実装内容:
- [ ] `feature_flags.py` に API フィーチャー enum 追加
- [ ] DB: `api_budget` テーブル (機能・上限・使用量・リセット日)
- [ ] 生成ログ (`generation_log`) テーブル
- [ ] 月次予算超過で自動停止 + 管理者通知
- [ ] 無料代替モード (API 未接続時の fallback)
- [ ] 管理画面: API 利用量・コスト可視化ウィジェット

---

### Phase 17 — 保管庫バックエンド実装 🟠 高

**目的:** saved prompts の永続化 API

実装内容:
- [ ] DB: `saved_prompt` テーブル
- [ ] `GET/POST/DELETE /api/prompts/saved`
- [ ] マイページ保管庫タブ完全実装
- [ ] ローカルストレージ → DB 移行パス

---

### Phase 18 — クエスト / デイリー任務 🟡 中

**目的:** ゲーミフィケーション強化

実装内容:
- [ ] DB: `quest` / `daily_task` / `user_quest_progress` テーブル
- [ ] デイリーミッション (毎日リセット)
- [ ] 達成判定 + XP 付与
- [ ] マイページ: クエストパネル

---

### Phase 19 — テンプレライブラリ 🟠 高

**目的:** `knowledge/templates/` + テンプレ一覧 UI

実装内容:
- [ ] `knowledge/templates/` にプリセット JSON 定義
- [ ] `GET /api/templates` エンドポイント
- [ ] トップページ: テンプレギャラリー (クイックスタート)
- [ ] フォーム自動入力連携

---

### Phase 20 — Prompt Doctor (ルールベース版) 🟡 中

**目的:** プロンプト改善診断ツール (API 未接続でも動く)

実装内容:
- [ ] ルールベース診断: 文字数・役割定義・具体性チェック
- [ ] スコア + 改善提案 UI
- [ ] API 接続時: LLM による詳細診断

---

### Phase 21 — 管理者集客工房 🟡 中

**目的:** 管理者向け集客・告知 PR ツール

実装内容:
- [ ] プロンプトを使った SNS 告知文生成
- [ ] 招待コード発行自動化 (`ENABLE_INVITE_SYSTEM` ON)
- [ ] HQ 専用パネル

---

## 技術的負債 / 継続監視

| 項目 | 対応フェーズ |
|------|------------|
| `templates_library/` ディレクトリなし | Phase 19 |
| 保管庫 API なし | Phase 17 |
| 生成ログなし | Phase 16 |
| クエスト未実装 | Phase 18 |
| `role` カラムが 2 値のみ | Phase 15 |
| HQ ロール未定義 | Phase 15 |
| 広場ページネーション UI なし | Phase 19 以前に軽量修正推奨 |
| コメント機能なし | Phase 18 以降 |
