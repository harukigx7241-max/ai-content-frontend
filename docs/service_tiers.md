# サービス層 — 動作モード・フォールバックルール

> 最終更新: 2026-04-11 (Phase 1)  
> 対象ファイル: `app/services/base.py`, `app/core/config.py`, `app/core/feature_flags.py`

---

## 1. 動作モード定義

すべてのサービスは以下の 5 つの動作モードのいずれかで動作する。

| モード | 値 | 説明 | UIラベル |
|--------|-----|------|---------|
| `FREE` | `"free"` | APIキー不要・ルールベース / テンプレートベース実装 | （非表示） |
| `LITE` | `"lite"` | 軽量API呼び出し・省トークン (将来用) | Lite版で動作中 |
| `API` | `"api"` | フル機能・LLM API必須 | AI連携版で動作中 |
| `FALLBACK` | `"fallback"` | API呼び出し失敗時の代替 (FREEに降格) | AI接続に失敗しました。代替版で動作しています |
| `DISABLED` | `"disabled"` | 機能フラグがOFF | この機能は現在利用できません |

---

## 2. モード決定フロー

```
サービス呼び出し
    ↓
FLAG_KEY チェック (feature_flags.is_enabled)
    ↓ OFF → DISABLED → ServiceResult.disabled() を��す
    ↓ ON
API キーチェック (_has_api_key)
    ↓ キーあり + PREFER_API=True → API tier
    ↓ キーなし または PREFER_API=False → FREE tier
実装を呼び出す
    ↓ 例外発生 → FALLBACK tier (通常 FREE に降格)
```

---

## 3. フォールバックルール

### 原則: APIキー未設定でも例外で落ちない

```python
# 全サービスでこのパターンを使う
def run(self, **kwargs) -> ServiceResult:
    mode = self.get_mode()
    if mode == ServiceMode.DISABLED:
        return ServiceResult.disabled()          # フラグ OFF
    if mode == ServiceMode.API:
        try:
            return self._run_api(**kwargs)        # API 試行
        except Exception:
            return self._run_fallback(**kwargs)   # 失敗 → FALLBACK
    return self._run_free(**kwargs)               # API なし → FREE
```

### フォールバック先の優先順位

```
API 失敗
  → FALLBACK (_run_fallback)
    → 通常は _run_free を呼ぶ (FREE実装があれば)
    → FREE実装がなければ ServiceResult.not_implemented() を返す
```

---

## 4. UI 出し分けルール

フロントエンドは `ServiceResult.available` と `ServiceResult.mode` を見て表示を切り替える。

| `available` | `mode` | フロントエンド表示 |
|-------------|--------|-----------------|
| `false` | `disabled` | グレーアウト + 「この機能は現在利用できません」 |
| `false` | `free` / `api` | 「準備中」バッジ |
| `true` | `free` | 通常表示 (ラベルなし) |
| `true` | `lite` | 「Lite版」バッジ (アンバー色) |
| `true` | `api` | 「AI連携版」バッジ (パープル色) |
| `true` | `fallback` | 「代替版」バッジ (オレンジ色) + ヒントメッセージ |

---

## 5. 各サービスの実装状況

| サービス | FLAG_KEY | FREE 実装 | API 実装 | デフォルト |
|---------|---------|-----------|---------|----------|
| PromptForgeService | `PROMPT_FORGE` | ✅ 既存 generate_service | ❌ 未実装 | ON |
| PromptDoctorService | `PROMPT_DOCTOR` | ✅ ルールベーススコア | ❌ 未実装 | ON |
| GuildGuideService | `GUILD_GUIDE_AI` | ✅ 静的ヒント | ❌ 未実装 | ON |
| WorkshopMasterService | `WORKSHOP_MASTER_AI` | ❌ なし | ❌ 未実装 | **OFF** |
| TrendService | `TREND_REFRESH` | ✅ JSONファイル | ❌ 未実装 | ON |
| KnowledgeService | なし | ✅ ファイル読み込み | ❌ 未実装 | 常時ON |
| LanguageQualityService | `LANGUAGE_QUALITY_AI` | ✅ ルールベース | ❌ 未実装 | ON |
| CongestionService | `CONGESTION_DISPLAY` | ✅ 静的ステータス | ❌ 未実装 | ON |
| ApiBudgetService | `API_USAGE_DASHBOARD` | ✅ スタブ表示 | ❌ 未実装 | ON |
| FeatureAccessService | なし | ✅ ロールチェック | — | 常時ON |
| CampaignForgeService | `CAMPAIGN_FORGE` | ✅ テンプレート | ❌ 未実装 | ON |
| ArticleDraftService | `ARTICLE_DRAFT_AI` | 🟠 骨組みのみ | ❌ 未実装 | **OFF** |
| ImagePromptService | `IMAGE_GENERATION` | ✅ プロンプト生成 | ❌ 未実装 | ON |
| PromotionPlannerService | `PROMOTION_PLANNER` | ✅ テンプレート | ❌ 未実装 | ON |

---

## 6. 環境変数の設定例

### 最小構成 (APIキーなし・全機能 FREE で動作)

```env
# APIキー未設定でも全サービスが FREE tier で動作する
# 追加設定不要
```

### API 接続あり (Anthropic 推奨)

```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-haiku-4-5-20251001

# API使用量の上限設定 (オプション)
API_MONTHLY_TOKEN_LIMIT=500000
API_MONTHLY_COST_LIMIT_USD=10.0
API_OVER_LIMIT_ACTION=fallback
```

### API 接続あり (OpenAI)

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### 特定サービスを無効化する場合

```env
# ワークショップマスターAI を無効化 (デフォルトは false)
ENABLE_WORKSHOP_MASTER_AI=false

# 記事下書きAI を有効化 (デフォルトは false・APIキー必須)
ENABLE_ARTICLE_DRAFT_AI=true
```

---

## 7. テンプレートライブラリの責務

`templates_library/` と `knowledge/` の責務分担:

| ディレクトリ | 内容 | 利用者 |
|------------|------|--------|
| `knowledge/workshops/*/` | ドメイン知識 (トレンドシグナル・パターン・ルール) | サービス層 (バックエンド) |
| `knowledge/branding/` | ブランドガイド | サービス層 |
| `templates_library/` | ユーザー向けクイックスタートテンプレート | フロントエンド (Phase 19 以降) |

`templates_library/` は Phase 19 で `/api/templates` エンドポイントから公開予定。  
現時点はファイルとして管理し、インデックスは `templates_library/_index.json` にある。

---

## 8. 今後の実装優先度

| 優先度 | 機能 | 対応フェーズ |
|--------|------|------------|
| 🔴 最高 | ApiBudgetService — 生成ログDB実装 | Phase 16 |
| 🔴 最高 | PromptDoctorService — UI連携 | Phase 20 |
| 🟠 高 | CampaignForgeService — UI + API連携 | Phase 21 |
| 🟠 高 | PromotionPlannerService — UI + API連携 | Phase 21 |
| 🟡 中 | WorkshopMasterService — LLM実装 | Phase 20+ |
| 🟡 中 | ArticleDraftService — LLM実装 | Phase 20+ |
| 🟡 中 | TrendService — Webスクレイピング | Phase 20+ |
