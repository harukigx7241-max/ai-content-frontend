"""
app/services/ — ビジネスロジックサービス層

Phase 1 で整理されたサービス一覧:

【既存・更新済み】
  generate_service      — プロンプト生成オーケストレーター (PromptForgeService のコア)
  knowledge_service     — ナレッジ JSON/MD ローダー (+ KnowledgeService クラス)
  trend_service         — トレンドシグナル注入 (+ TrendService クラス)
  image_prompt_service  — 画像プロンプト構築 (+ BaseService 継承)
  note_format_service   — note.com 形式整形
  input_mode_service    — 入力モード補足文

【Phase 1 新規 (骨組み)】
  base                  — ServiceMode, ServiceResult, BaseService
  registry              — ServiceRegistry (全サービス状態一覧)
  prompt_forge_service  — PromptForgeService (generate_service ラッパー)
  prompt_doctor_service — PromptDoctorService (プロンプト品質診断)
  guild_guide_service   — GuildGuideService (ガイドウィジェット)
  workshop_master_service — WorkshopMasterService (工房マスターAI)
  language_quality_service — LanguageQualityService (日本語品質チェック)
  congestion_service    — CongestionService (混雑状況表示)
  api_budget_service    — ApiBudgetService (API予算管理)
  feature_access_service — FeatureAccessService (ロール別アクセス制御)
  campaign_forge_service — CampaignForgeService (キャンペーン工房)
  article_draft_service  — ArticleDraftService (記事下書きAI)
  promotion_planner_service — PromotionPlannerService (プロモーションプランナー)

各サービスの動作モード判定: app/services/base.py 参照
フィーチャーフラグ: app/core/feature_flags.py 参照
サービス状態一覧: app/services/registry.py 参照
"""
