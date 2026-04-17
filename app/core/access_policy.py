"""
app/core/access_policy.py
機能アクセスポリシーの一元管理。

各機能に以下を紐づける:
  - required_role : 最低必要ロール (RoleValue.*)
  - status        : 機能のライフサイクル状態 (FeatureStatus)
  - flag_key      : 機能フラグ名 (feature_flags の属性名、空文字は常時有効)
  - upgrade_hint  : アクセス拒否時のアップグレード促進メッセージ

【FeatureStatus 一覧】
  LIVE          — 本番稼働中
  BETA          — ベータ版 (FREE実装はあるがまだ洗練中)
  PREMIUM_READY — 課金接続待ち (骨組みあり・有料会員向け機能として予告)
  ADMIN_ONLY    — 管理者専用 (ユーザーには非表示)
  HQ_ONLY       — 管理本部専用
  HIDDEN        — 非表示 (開発中・完全非公開)
  MAINTENANCE   — メンテナンス中 (一時的に無効)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from app.core.roles import RoleValue, get_upgrade_hint


# ─────────────────────────────────────────────────────────────────────────────
# FeatureStatus
# ─────────────────────────────────────────────────────────────────────────────

class FeatureStatus(str, Enum):
    LIVE          = "live"           # 本番稼働
    BETA          = "beta"           # ベータ版
    PREMIUM_READY = "premium_ready"  # 課金接続待ち
    ADMIN_ONLY    = "admin_only"     # 管理者専用
    HQ_ONLY       = "hq_only"        # 管理本部専用
    HIDDEN        = "hidden"         # 非表示
    MAINTENANCE   = "maintenance"    # メンテナンス中

    @property
    def is_visible_to_users(self) -> bool:
        """一般ユーザーに表示すべきステータスか。"""
        return self in (
            FeatureStatus.LIVE,
            FeatureStatus.BETA,
            FeatureStatus.PREMIUM_READY,
        )

    @property
    def ui_badge(self) -> str:
        """フロントエンド表示用バッジラベル。"""
        return {
            "live": "",
            "beta": "BETA",
            "premium_ready": "有料版",
            "admin_only": "管理者",
            "hq_only": "本部",
            "hidden": "",
            "maintenance": "メンテ中",
        }.get(self.value, "")


# ─────────────────────────────────────────────────────────────────────────────
# FeaturePolicy
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class FeaturePolicy:
    """
    1つの機能に対するアクセスポリシー定義。

    feature_id   : 機能の一意 ID (snake_case)
    label        : 日本語表示名
    required_role: 最低必要ロール (RoleValue.*)
    status       : 機能のライフサイクル状態
    flag_key     : feature_flags 属性名 (空文字 = 常時有効)
    description  : 機能説明
    upgrade_hint : 拒否時のアップグレードメッセージ (空文字 = 自動生成)
    category     : 分類 (ui表示用)
    """
    feature_id:    str
    label:         str
    required_role: str
    status:        FeatureStatus
    flag_key:      str = ""
    description:   str = ""
    _upgrade_hint: str = field(default="", repr=False)
    category:      str = "general"

    @property
    def upgrade_hint(self) -> str:
        if self._upgrade_hint:
            return self._upgrade_hint
        return get_upgrade_hint(RoleValue.GUEST, self.required_role)

    def is_accessible(self, user_role: str | None) -> bool:
        """ロールのみでアクセス可能かを確認 (フラグチェックは別途)。"""
        from app.core.roles import RoleRank
        return RoleRank.gte(user_role, self.required_role)

    def to_dict(self) -> dict:
        return {
            "feature_id": self.feature_id,
            "label": self.label,
            "required_role": self.required_role,
            "status": self.status.value,
            "status_badge": self.status.ui_badge,
            "flag_key": self.flag_key,
            "description": self.description,
            "upgrade_hint": self.upgrade_hint,
            "category": self.category,
        }


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE_POLICIES — 全機能ポリシーテーブル
# ─────────────────────────────────────────────────────────────────────────────

FEATURE_POLICIES: dict[str, FeaturePolicy] = {

    # ── 誰でも使える (ゲスト含む) ─────────────────────────────────────
    "template_view": FeaturePolicy(
        feature_id="template_view",
        label="テンプレ閲覧",
        required_role=RoleValue.GUEST,
        status=FeatureStatus.LIVE,
        description="テンプレートライブラリの閲覧",
        category="prompt",
    ),
    "prompt_forge": FeaturePolicy(
        feature_id="prompt_forge",
        label="テンプレ鍛冶場 / Prompt Forge",
        required_role=RoleValue.GUEST,
        status=FeatureStatus.LIVE,
        flag_key="PROMPT_FORGE",
        description="4工房のプロンプト生成 (1日3回制限: ゲスト)",
        category="prompt",
    ),
    "square_view": FeaturePolicy(
        feature_id="square_view",
        label="ギルド広場 閲覧",
        required_role=RoleValue.GUEST,
        status=FeatureStatus.LIVE,
        flag_key="COMMUNITY",
        description="ギルド広場の投稿閲覧・検索",
        category="community",
    ),
    "congestion_display": FeaturePolicy(
        feature_id="congestion_display",
        label="混雑状況表示",
        required_role=RoleValue.GUEST,
        status=FeatureStatus.BETA,
        flag_key="CONGESTION_DISPLAY",
        description="サービス利用状況の表示",
        category="ui",
    ),
    "guild_guide": FeaturePolicy(
        feature_id="guild_guide",
        label="ギルドガイドAI",
        required_role=RoleValue.GUEST,
        status=FeatureStatus.LIVE,
        flag_key="GUILD_GUIDE_AI",
        description="操作ガイドウィジェット",
        category="ui",
    ),

    # ── 無料会員以上 ─────────────────────────────────────────────────
    "template_save": FeaturePolicy(
        feature_id="template_save",
        label="テンプレ保存",
        required_role=RoleValue.MEMBER_FREE,
        status=FeatureStatus.BETA,
        description="生成したプロンプトの保存 (ローカルストレージ)",
        category="prompt",
    ),
    "template_remix": FeaturePolicy(
        feature_id="template_remix",
        label="テンプレ リミックス / フォーク",
        required_role=RoleValue.MEMBER_FREE,
        status=FeatureStatus.BETA,
        description="公開テンプレートを元に自分用に編集",
        category="prompt",
    ),
    "prompt_doctor": FeaturePolicy(
        feature_id="prompt_doctor",
        label="テンプレ診断Lite / Prompt Doctor",
        required_role=RoleValue.MEMBER_FREE,
        status=FeatureStatus.BETA,
        flag_key="PROMPT_DOCTOR",
        description="生成プロンプトの品質診断・改善提案 (ルールベース)",
        category="prompt",
    ),
    "prompt_history": FeaturePolicy(
        feature_id="prompt_history",
        label="プロンプト履歴",
        required_role=RoleValue.MEMBER_FREE,
        status=FeatureStatus.BETA,
        description="過去に生成したプロンプトの履歴閲覧",
        category="prompt",
    ),
    "square_post": FeaturePolicy(
        feature_id="square_post",
        label="ギルド広場 投稿",
        required_role=RoleValue.MEMBER_FREE,
        status=FeatureStatus.LIVE,
        flag_key="COMMUNITY",
        description="ギルド広場へのプロンプトログ投稿",
        category="community",
    ),
    "square_reaction": FeaturePolicy(
        feature_id="square_reaction",
        label="ギルド広場 リアクション (いいね・保存)",
        required_role=RoleValue.MEMBER_FREE,
        status=FeatureStatus.LIVE,
        flag_key="COMMUNITY",
        description="投稿へのいいね・保存",
        category="community",
    ),
    "xp_ranking": FeaturePolicy(
        feature_id="xp_ranking",
        label="XP / ランク / 称号",
        required_role=RoleValue.MEMBER_FREE,
        status=FeatureStatus.LIVE,
        flag_key="GAMIFICATION",
        description="経験値・レベル・称号システム",
        category="gamification",
    ),
    "language_quality": FeaturePolicy(
        feature_id="language_quality",
        label="日本語品質チェック",
        required_role=RoleValue.MEMBER_FREE,
        status=FeatureStatus.BETA,
        flag_key="LANGUAGE_QUALITY_AI",
        description="日本語文体・句読点・一貫性のルールベースチェック",
        category="prompt",
    ),

    # ── 有料会員以上 ─────────────────────────────────────────────────
    "campaign_forge": FeaturePolicy(
        feature_id="campaign_forge",
        label="Campaign Forge (キャンペーン工房)",
        required_role=RoleValue.MEMBER_PAID,
        status=FeatureStatus.PREMIUM_READY,
        flag_key="CAMPAIGN_FORGE",
        description="SNS告知・キャンペーン文のプロンプト生成",
        category="marketing",
    ),
    "promotion_planner": FeaturePolicy(
        feature_id="promotion_planner",
        label="Note Promotion Builder (プロモーションプランナー)",
        required_role=RoleValue.MEMBER_PAID,
        status=FeatureStatus.PREMIUM_READY,
        flag_key="PROMOTION_PLANNER",
        description="コンテンツ販売の集客プラン生成",
        category="marketing",
    ),
    "article_draft": FeaturePolicy(
        feature_id="article_draft",
        label="Auto Research Draft (記事下書きAI)",
        required_role=RoleValue.MEMBER_PAID,
        status=FeatureStatus.PREMIUM_READY,
        flag_key="ARTICLE_DRAFT_AI",
        description="note記事の下書き自動生成 (APIキー必須)",
        category="content",
    ),
    "image_generation": FeaturePolicy(
        feature_id="image_generation",
        label="Image Generation (画像生成連携)",
        required_role=RoleValue.MEMBER_PAID,
        status=FeatureStatus.PREMIUM_READY,
        flag_key="IMAGE_GENERATION",
        description="AI画像生成プロンプト構築・実行",
        category="content",
    ),
    "workshop_master": FeaturePolicy(
        feature_id="workshop_master",
        label="Workshop Master AI",
        required_role=RoleValue.MEMBER_PAID,
        status=FeatureStatus.HIDDEN,
        flag_key="WORKSHOP_MASTER_AI",
        description="工房専門AIアシスタント・質問応答 (未実装)",
        category="prompt",
    ),

    # ── マスター会員以上 ──────────────────────────────────────────────
    "priority_queue": FeaturePolicy(
        feature_id="priority_queue",
        label="混雑優先レーン",
        required_role=RoleValue.MEMBER_MASTER,
        status=FeatureStatus.PREMIUM_READY,
        description="混雑時の優先処理レーン",
        category="premium",
    ),
    "bulk_generate": FeaturePolicy(
        feature_id="bulk_generate",
        label="一括生成",
        required_role=RoleValue.MEMBER_MASTER,
        status=FeatureStatus.HIDDEN,
        description="複数プロンプトの一括生成 (未実装)",
        category="premium",
    ),

    # ── 管理者以上 (ADMIN + HQ) ───────────────────────────────────────
    "admin_dashboard": FeaturePolicy(
        feature_id="admin_dashboard",
        label="管理画面",
        required_role=RoleValue.ADMIN,
        status=FeatureStatus.ADMIN_ONLY,
        flag_key="ADMIN_DASHBOARD",
        description="管理ダッシュボード (統計・ユーザー管理・設定)",
        category="admin",
    ),
    "user_management": FeaturePolicy(
        feature_id="user_management",
        label="ユーザー管理",
        required_role=RoleValue.ADMIN,
        status=FeatureStatus.ADMIN_ONLY,
        flag_key="ADMIN_DASHBOARD",
        description="ユーザー承認・停止・ロール変更",
        category="admin",
    ),
    "trend_management": FeaturePolicy(
        feature_id="trend_management",
        label="トレンドシグナル管理",
        required_role=RoleValue.ADMIN,
        status=FeatureStatus.ADMIN_ONLY,
        flag_key="TREND_REFRESH",
        description="工房トレンドシグナルの編集・更新",
        category="admin",
    ),
    "api_budget_view": FeaturePolicy(
        feature_id="api_budget_view",
        label="API利用量 / コスト可視化",
        required_role=RoleValue.ADMIN,
        status=FeatureStatus.ADMIN_ONLY,
        flag_key="API_USAGE_DASHBOARD",
        description="API使用量・概算コストの確認 (管理者専用)",
        category="admin",
    ),
    "content_moderation": FeaturePolicy(
        feature_id="content_moderation",
        label="コンテンツモデレーション",
        required_role=RoleValue.ADMIN,
        status=FeatureStatus.ADMIN_ONLY,
        description="広場投稿の削除・非表示操作",
        category="admin",
    ),

    # ── Phase 17: 管理者専用集客工房 (将来 member_paid/master へ解放) ──
    "admin_growth_multi_channel": FeaturePolicy(
        feature_id="admin_growth_multi_channel",
        label="マルチチャンネル記事パック",
        required_role=RoleValue.ADMIN,
        status=FeatureStatus.ADMIN_ONLY,
        flag_key="ADMIN_GROWTH_MULTI_CHANNEL",
        description="1記事を5チャンネル向けにアレンジするプロンプト生成",
        category="admin_growth",
    ),
    "admin_growth_launch_pack": FeaturePolicy(
        feature_id="admin_growth_launch_pack",
        label="ローンチパックビルダー",
        required_role=RoleValue.ADMIN,
        status=FeatureStatus.ADMIN_ONLY,
        flag_key="ADMIN_GROWTH_LAUNCH_PACK",
        description="商品ローンチに必要な7素材のプロンプトを一括生成",
        category="admin_growth",
    ),
    "admin_growth_promo_calendar": FeaturePolicy(
        feature_id="admin_growth_promo_calendar",
        label="販促カレンダー生成",
        required_role=RoleValue.ADMIN,
        status=FeatureStatus.ADMIN_ONLY,
        flag_key="ADMIN_GROWTH_PROMO_CALENDAR",
        description="30日間の販促スケジュールプロンプトを自動生成",
        category="admin_growth",
    ),
    "admin_growth_hook_library": FeaturePolicy(
        feature_id="admin_growth_hook_library",
        label="フック文ライブラリ",
        required_role=RoleValue.ADMIN,
        status=FeatureStatus.ADMIN_ONLY,
        flag_key="ADMIN_GROWTH_HOOK_LIBRARY",
        description="読者を引き込む冒頭フック文を10スタイルで生成",
        category="admin_growth",
    ),
    "admin_growth_variation": FeaturePolicy(
        feature_id="admin_growth_variation",
        label="バリエーション生成",
        required_role=RoleValue.ADMIN,
        status=FeatureStatus.ADMIN_ONLY,
        flag_key="ADMIN_GROWTH_VARIATION",
        description="既存コンテンツを3トーンでリライト",
        category="admin_growth",
    ),
    "admin_growth_promo_score": FeaturePolicy(
        feature_id="admin_growth_promo_score",
        label="販促スコアリング",
        required_role=RoleValue.ADMIN,
        status=FeatureStatus.ADMIN_ONLY,
        flag_key="ADMIN_GROWTH_PROMO_SCORE",
        description="販促プランを5軸で採点・改善提案を生成",
        category="admin_growth",
    ),

    # ── 管理本部のみ (HQ) ─────────────────────────────────────────────
    "hq_dashboard": FeaturePolicy(
        feature_id="hq_dashboard",
        label="管理本部画面",
        required_role=RoleValue.HEADQUARTERS,
        status=FeatureStatus.HQ_ONLY,
        description="管理本部専用ダッシュボード",
        category="hq",
    ),
    "hq_analytics": FeaturePolicy(
        feature_id="hq_analytics",
        label="詳細分析 / KPIダッシュボード",
        required_role=RoleValue.HEADQUARTERS,
        status=FeatureStatus.HQ_ONLY,
        description="全ユーザー活動・収益・コスト分析",
        category="hq",
    ),
    "hq_campaign": FeaturePolicy(
        feature_id="hq_campaign",
        label="キャンペーン / プロモーション管理",
        required_role=RoleValue.HEADQUARTERS,
        status=FeatureStatus.HQ_ONLY,
        description="SNS告知・招待コード一括発行・A/Bテスト設定",
        category="hq",
    ),
    "hq_admin_management": FeaturePolicy(
        feature_id="hq_admin_management",
        label="管理者ユーザー管理",
        required_role=RoleValue.HEADQUARTERS,
        status=FeatureStatus.HQ_ONLY,
        description="adminロールユーザーの管理 (HQのみ可能)",
        category="hq",
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# ヘルパー関数
# ─────────────────────────────────────────────────────────────────────────────

def get_policy(feature_id: str) -> Optional[FeaturePolicy]:
    """機能 ID からポリシーを返す。存在しない場合は None。"""
    return FEATURE_POLICIES.get(feature_id)


def get_policies_for_role(role: str | None) -> list[FeaturePolicy]:
    """指定ロールがアクセスできる機能ポリシー一覧を返す。"""
    from app.core.roles import RoleRank
    return [
        p for p in FEATURE_POLICIES.values()
        if RoleRank.gte(role, p.required_role)
        and p.status.is_visible_to_users
    ]


def get_policies_by_category(category: str) -> list[FeaturePolicy]:
    """カテゴリで絞り込んだポリシー一覧を返す。"""
    return [p for p in FEATURE_POLICIES.values() if p.category == category]


def get_all_categories() -> list[str]:
    """全カテゴリの重複なし一覧を返す。"""
    seen: set[str] = set()
    result: list[str] = []
    for p in FEATURE_POLICIES.values():
        if p.category not in seen:
            seen.add(p.category)
            result.append(p.category)
    return result
