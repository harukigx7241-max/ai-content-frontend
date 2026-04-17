# API 接続手順 (API Connection Guide)

> 対象バージョン: Phase 12+  
> 最終更新: 2026-04-17

---

## 概要

プロンプトギルドの AI 機能は **APIキー不要の FREE tier** でも動作します。  
APIキーを設定すると対応サービスが自動的に **AI 版** にアップグレードされます。

| 状態 | 動作 |
|------|------|
| APIキー未設定 | 全サービスが FREE tier (ルールベース/テンプレート) で動作 |
| APIキー設定済み | 対応サービスが AI 版 (LLM) で動作 |

---

## 対応 LLM プロバイダー

| プロバイダー | 環境変数 | 推奨モデル |
|------------|---------|-----------|
| Anthropic (Claude) | `ANTHROPIC_API_KEY` | `claude-haiku-4-5-20251001` |
| OpenAI (GPT) | `OPENAI_API_KEY` | `gpt-4o-mini` |
| Google (Gemini) | `GEMINI_API_KEY` | `gemini-1.5-flash` |

複数設定した場合は **Anthropic → OpenAI → Gemini** の優先度で自動選択されます。  
`LLM_PROVIDER=openai` のように明示的に指定することも可能です。

---

## 設定手順

### 1. 環境変数ファイルの作成

```bash
cp .env.example .env
```

`.env.example` が存在しない場合はプロジェクトルートに `.env` を新規作成してください。

### 2. APIキーを設定する

```env
# いずれか1つ以上を設定 (複数設定可)

# Anthropic Claude (推奨)
ANTHROPIC_API_KEY=sk-ant-api03-...
ANTHROPIC_MODEL=claude-haiku-4-5-20251001

# OpenAI GPT
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini

# Google Gemini
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash

# 優先プロバイダーを明示する場合 (auto = 自動選択)
LLM_PROVIDER=auto
```

### 3. サーバーを再起動する

```bash
uvicorn main:app --reload
```

### 4. 動作確認

管理ダッシュボード → **「⚙ サービス状態」タブ** を開くと、各サービスの動作モードが確認できます。  
APIキーが正しく設定されている場合、「APIキー設定済み」と表示されます。

---

## サービス別 API 対応状況

| サービス | FREE 実装 | API 実装 | 状態 |
|---------|----------|---------|------|
| プロンプト鍛冶場 | テンプレート生成 | LLM強化プロンプト最適化 | 準備中 |
| プロンプト診断 | ルールベーススコアリング | LLM詳細診断 | 準備中 |
| ギルドガイドAI | スクリプトヒント | LLM文脈対応ガイド | 準備中 |
| ワークショップマスターAI | なし (API専用) | LLM工房アシスタント | 準備中 |
| トレンドリフレッシュ | JSONファイル読み込み | Webスクレイピング自動更新 | 準備中 |
| 日本語品質チェック | ルールベースチェック | LLM日本語添削 | 準備中 |
| ギルド書記AI | テンプレート投稿文生成 | LLM文脈対応投稿文生成 | 準備中 |
| キャンペーン工房 | テンプレートベース | LLMキャンペーン戦略生成 | 準備中 |
| 記事下書きAI | なし (API専用) | LLM記事下書き生成 | 準備中 |
| 画像生成連携 | プロンプト文字列生成のみ | DALL-E / Stable Diffusion | 準備中 |
| 混雑状況表示 | xp_eventsプロキシ | リアルタイムキュー確認 | 準備中 |

> **「準備中」** = API tier の実装は将来のフェーズで行います。  
> 現在は API キーを設定しても FREE tier で動作します。

---

## 画像生成 API の設定 (Phase 20+)

```env
ENABLE_IMAGE_API_CALL=true
IMAGE_API_PROVIDER=dalle   # dalle | sd | none

# DALL-E を使う場合 (OpenAI キーが必要)
OPENAI_API_KEY=sk-proj-...

# Stable Diffusion を使う場合
SD_API_URL=http://localhost:7860
```

---

## 月次予算上限の設定

API コストを制御するために月次上限を設定できます。

```env
# 月次トークン上限 (0 = 無制限)
API_MONTHLY_TOKEN_LIMIT=1000000

# 月次コスト上限 (USD, 0 = 無制限)
API_MONTHLY_COST_LIMIT_USD=10.0

# 上限超過時の動作: disable | fallback | notify_only
API_OVER_LIMIT_ACTION=fallback

# 管理者通知メール (空白 = 通知なし)
ADMIN_ALERT_EMAIL=admin@example.com
```

> 予算管理の詳細実装は **Phase 16** で予定しています。

---

## サービス別フラグで機能を個別 ON/OFF する

各サービスは個別の環境変数で有効/無効を制御できます。

```env
# デフォルト true (無効にする場合は false を設定)
ENABLE_PROMPT_FORGE=true
ENABLE_PROMPT_DOCTOR=true
ENABLE_GUILD_GUIDE_AI=true
ENABLE_TREND_REFRESH=true
ENABLE_LANGUAGE_QUALITY_AI=true
ENABLE_CAMPAIGN_FORGE=true
ENABLE_IMAGE_GENERATION=true
ENABLE_API_USAGE_DASHBOARD=true
ENABLE_CONGESTION_DISPLAY=true
ENABLE_PROMOTION_PLANNER=true
ENABLE_GUILD_SCRIBE_AI=true

# デフォルト false (API専用・未完成機能)
ENABLE_WORKSHOP_MASTER_AI=false
ENABLE_ARTICLE_DRAFT_AI=false
ENABLE_IMAGE_API_CALL=false
```

---

## トラブルシューティング

### APIキーを設定したのに AI 版にならない

→ サーバーを再起動してください (`uvicorn main:app --reload`)。  
→ 環境変数が正しく読み込まれているか確認してください: `python -c "import os; print(os.getenv('OPENAI_API_KEY'))"`

### サービス状態パネルで「無効」と表示される

→ `ENABLE_xxx=false` に設定されていないか確認してください。  
→ デフォルト `false` のサービス (WORKSHOP_MASTER_AI など) は明示的に `true` に設定が必要です。

### API 呼び出しに失敗する

→ APIキーの有効期限・残高を各プロバイダーのダッシュボードで確認してください。  
→ フォールバックモードに自動降格します (FREE tier で継続動作)。

---

## 関連ドキュメント

- `docs/roadmap_phases.md` — フェーズロードマップ
- `docs/fixed_requirements.md` — システム要件・方針
- `docs/service_tiers.md` — サービス tier 詳細
- `app/core/config.py` — 全設定項目の定義
- `app/services/registry.py` — サービスレジストリ
