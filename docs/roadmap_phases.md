# フェーズロードマップ (Roadmap Phases)

> 最終更新: 2026-04-11  
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
| 0 (再) | コードベース再監査・docs 整備 | phase13-mobile-game-ui | (本 PR) |

---

## 進行中フェーズ

### Phase 13 — スマホ完全最適化 🔴 最高優先

**目的:** 全画面でモバイル体験を最優先にする  
**ブランチ:** `claude/phase13-mobile-game-ui`

実装内容:
- [ ] CSS: ハンバーガーボタン・モバイルドロワー・ボトムナビ
- [ ] `index.html`: ハンバーガー + ボトムナビ HTML
- [ ] `square.html` / `mypage.html` / `admin`: モバイルヘッダー統一
- [ ] 375px / 480px ブレークポイント強化
- [ ] タッチターゲット 44px 保証

---

## 予定フェーズ

### Phase 14 — ゲーム UI 強化 🟠 高

**目的:** ロゴ・見出し・バッジ・ボタンにゲーム感を追加

実装内容:
- [ ] ロゴをゲーム風エンブレムデザインに
- [ ] 見出しに装飾フレーム (レリーフ風)
- [ ] ランクバッジのビジュアル強化
- [ ] 主要ボタンに光沢・立体感
- [ ] 称号テキストに装飾エフェクト

---

### Phase 15 — ロール体系拡張 + HQ 権限分離 🔴 最高

**目的:** 6ロール定義・admin / headquarters の権限分離

実装内容:
- [ ] DB: `role` カラムを 6 値に拡張 (migration)
- [ ] `member_free` / `member_paid` / `member_master` / `headquarters` 追加
- [ ] `ADMIN_ROLES` / `HQ_ROLES` / `MEMBER_ROLES` 分離
- [ ] `require_hq` 依存性追加
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

**目的:** `templates_library/` ディレクトリ + テンプレ一覧 UI

実装内容:
- [ ] `knowledge/templates/` にプリセット JSON 定義
- [ ] `GET /api/templates` エンドポイント
- [ ] トップページ: テンプレギャラリー (クイックスタート)
- [ ] フォーム自動入力連携

---

### Phase 20 — Prompt Doctor (AI 未接続でも動く版) 🟡 中

**目的:** プロンプト改善診断ツール

実装内容:
- [ ] ルールベース診断 (API なし): 文字数・役割定義・具体性チェック
- [ ] スコア + 改善提案 UI
- [ ] API 接続時: LLM による詳細診断

---

### Phase 21 — 管理者集客工房 🟡 中

**目的:** 管理者向け集客・告知 PR ツール

実装内容:
- [ ] プロンプトを使った SNS 告知文生成
- [ ] 招待コード発行自動化
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
