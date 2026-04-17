"""
app/services/registry.py
サービスレジストリ。全サービスの現在の動作モードを一元管理する。

用途:
- 管理ダッシュボードの「サービス状態一覧」表示
- /api/system/services エンドポイントでのステータス公開
- サービス同士の依存関係確認

使い方:
    from app.services.registry import service_registry
    status = service_registry.get_all_status()
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.core.feature_flags import flags
from app.services.base import ServiceMode


@dataclass
class ServiceStatus:
    """サービスの現在の状態スナップショット。"""
    name: str             # サービス名 (英語 snake_case)
    label: str            # 表示名 (日本語)
    flag_key: str         # feature_flags の属性名
    enabled: bool         # フラグが ON かどうか
    has_api_key: bool     # API キーが設定されているか
    current_mode: str     # "disabled" | "free" | "lite" | "api"
    description: str      # 機能説明
    free_impl: str        # FREE 実装の説明
    api_impl: str         # API 実装の説明 (未実装なら "未実装")
    phase: Optional[str] = None  # 対応フェーズ番号 (例: "Phase 16")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "enabled": self.enabled,
            "has_api_key": self.has_api_key,
            "current_mode": self.current_mode,
            "description": self.description,
            "free_impl": self.free_impl,
            "api_impl": self.api_impl,
            "phase": self.phase,
        }


# ─────────────────────────────────────────────────────────────────────────────
# サービス定義テーブル
# ─────────────────────────────────────────────────────────────────────────────

_SERVICE_DEFINITIONS: list[dict] = [
    {
        "name": "prompt_forge",
        "label": "プロンプト鍛冶場",
        "flag_key": "PROMPT_FORGE",
        "description": "4工房のプロンプト生成コア",
        "free_impl": "テンプレート+ルールベース生成 (既存実装)",
        "api_impl": "LLM強化プロンプト最適化 (未実装)",
        "phase": None,
    },
    {
        "name": "prompt_doctor",
        "label": "プロンプト診断",
        "flag_key": "PROMPT_DOCTOR",
        "description": "生成プロンプトの品質診断と改善提案",
        "free_impl": "ルールベーススコアリング (文字数・役割定義・具体性チェック)",
        "api_impl": "LLM詳細診断・改善提案 (未実装)",
        "phase": "Phase 20",
    },
    {
        "name": "guild_guide_ai",
        "label": "ギルドガイドAI",
        "flag_key": "GUILD_GUIDE_AI",
        "description": "ユーザーの操作を助けるガイドウィジェット",
        "free_impl": "スクリプトベースのヒント表示 (既存実装)",
        "api_impl": "LLM文脈対応ガイド (未実装)",
        "phase": None,
    },
    {
        "name": "workshop_master_ai",
        "label": "ワークショップマスターAI",
        "flag_key": "WORKSHOP_MASTER_AI",
        "description": "工房専門のAIアシスタント (質問応答)",
        "free_impl": "対応なし (API専用機能)",
        "api_impl": "LLM工房アシスタント (未実装)",
        "phase": "Phase 20+",
    },
    {
        "name": "trend_refresh",
        "label": "トレンドリフレッシュ",
        "flag_key": "TREND_REFRESH",
        "description": "工房のトレンドシグナルをプロンプトに注入",
        "free_impl": "JSONファイルベースのシグナル読み込み (既存実装)",
        "api_impl": "Webスクレイピング自動更新 (未実装)",
        "phase": None,
    },
    {
        "name": "language_quality_ai",
        "label": "日本語品質チェック",
        "flag_key": "LANGUAGE_QUALITY_AI",
        "description": "生成プロンプトの日本語品質チェック",
        "free_impl": "ルールベースチェック (句読点・文体・語尾一貫性)",
        "api_impl": "LLM日本語添削 (未実装)",
        "phase": "Phase 20",
    },
    {
        "name": "campaign_forge",
        "label": "キャンペーン工房",
        "flag_key": "CAMPAIGN_FORGE",
        "description": "SNS告知・キャンペーン文生成",
        "free_impl": "テンプレートベース生成",
        "api_impl": "LLMキャンペーン戦略生成 (未実装)",
        "phase": "Phase 21",
    },
    {
        "name": "article_draft_ai",
        "label": "記事下書きAI",
        "flag_key": "ARTICLE_DRAFT_AI",
        "description": "note記事の下書きを自動生成",
        "free_impl": "対応なし (API専用機能)",
        "api_impl": "LLM記事下書き生成 (未実装)",
        "phase": "Phase 20+",
    },
    {
        "name": "image_generation",
        "label": "画像生成連携",
        "flag_key": "IMAGE_GENERATION",
        "description": "AI画像生成のプロンプト構築・実行",
        "free_impl": "画像プロンプト文字列生成のみ (既存実装)",
        "api_impl": "DALL-E / Stable Diffusion API呼び出し (未実装)",
        "phase": "Phase 20+",
    },
    {
        "name": "api_usage_dashboard",
        "label": "API利用量ダッシュボード",
        "flag_key": "API_USAGE_DASHBOARD",
        "description": "API利用量・コスト可視化 (管理者向け)",
        "free_impl": "静的表示 (データなし)",
        "api_impl": "生成ログ集計・コスト計算 (Phase 16で実装予定)",
        "phase": "Phase 16",
    },
    {
        "name": "congestion_display",
        "label": "混雑状況表示",
        "flag_key": "CONGESTION_DISPLAY",
        "description": "サービス利用状況・混雑度の表示",
        "free_impl": "静的ステータス (常に '利用可能')",
        "api_impl": "リアルタイムキュー確認 (未実装)",
        "phase": "Phase 20",
    },
    {
        "name": "promotion_planner",
        "label": "プロモーションプランナー",
        "flag_key": "PROMOTION_PLANNER",
        "description": "コンテンツ販売の集客プランニング",
        "free_impl": "テンプレートベース集客プラン",
        "api_impl": "LLMカスタムプロモーション戦略 (未実装)",
        "phase": "Phase 21",
    },
    {
        "name": "guild_scribe_ai",
        "label": "ギルド書記AI",
        "flag_key": "GUILD_SCRIBE_AI",
        "description": "ギルド広場への投稿文・キャプション生成を支援",
        "free_impl": "カテゴリ別テンプレートベース投稿文生成 (Phase 12実装)",
        "api_impl": "LLM文脈対応投稿文・高品質キャプション生成 (未実装)",
        "phase": "Phase 12",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# ServiceRegistry
# ─────────────────────────────────────────────────────────────────────────────

class ServiceRegistry:
    """全サービスの現在の動作モードを一元管理するレジストリ。"""

    def get_status(self, service_name: str) -> ServiceStatus | None:
        """特定サービスの状態を返す。"""
        defn = next((d for d in _SERVICE_DEFINITIONS if d["name"] == service_name), None)
        if defn is None:
            return None
        return self._build_status(defn)

    def get_all_status(self) -> list[ServiceStatus]:
        """全サービスの状態リストを返す。"""
        return [self._build_status(d) for d in _SERVICE_DEFINITIONS]

    def get_all_status_dict(self) -> list[dict]:
        """全サービスの状態を dict リストで返す (API レスポンス用)。"""
        return [s.to_dict() for s in self.get_all_status()]

    def _build_status(self, defn: dict) -> ServiceStatus:
        flag_key = defn["flag_key"]
        enabled = flags.is_enabled(flag_key)
        has_key = flags.has_api_key()

        if not enabled:
            mode = ServiceMode.DISABLED.value
        elif has_key:
            mode = ServiceMode.API.value
        else:
            mode = ServiceMode.FREE.value

        return ServiceStatus(
            name=defn["name"],
            label=defn["label"],
            flag_key=flag_key,
            enabled=enabled,
            has_api_key=has_key,
            current_mode=mode,
            description=defn["description"],
            free_impl=defn["free_impl"],
            api_impl=defn["api_impl"],
            phase=defn.get("phase"),
        )


# グローバルシングルトン
service_registry = ServiceRegistry()
