"""
app/services/feature_access_service.py
機能アクセス制御サービス。ロールと機能フラグに基づいてアクセス可否を判定する。

このサービスはフィーチャーフラグ + ロール + サブスク状態を組み合わせて
「このユーザーはこの機能を使えるか」を一元管理する。

Phase 15 のロール体系拡張後に本格稼働。
現時点は "user" | "admin" の 2 ロールのみ対応。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.core.feature_flags import flags


# ─────────────────────────────────────────────────────────────────────────────
# ロール定義 (Phase 15 で DB の role カラム値と同期)
# ─────────────────────────────────────────────────────────────────────────────

class Role:
    GUEST          = "guest"
    MEMBER_FREE    = "user"         # DB 現在値 (Phase 15 で member_free に変更予定)
    MEMBER_PAID    = "member_paid"
    MEMBER_MASTER  = "member_master"
    ADMIN          = "admin"
    HEADQUARTERS   = "headquarters"


# ロール階層 (数値が高いほど上位)
_ROLE_RANK: dict[str, int] = {
    Role.GUEST:         0,
    Role.MEMBER_FREE:   1,
    Role.MEMBER_PAID:   2,
    Role.MEMBER_MASTER: 3,
    Role.ADMIN:         4,
    Role.HEADQUARTERS:  5,
}


@dataclass
class AccessResult:
    allowed: bool
    reason: str = ""       # 拒否理由 (allowed=False の場合)
    required_role: str = ""  # 必要なロール

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "required_role": self.required_role,
        }


# ─────────────────────────────────────────────────────────────────────────────
# 機能ごとの最低必要ロール定義
# ─────────────────────────────────────────────────────────────────────────────

_FEATURE_REQUIREMENTS: dict[str, str] = {
    # 誰でも使える機能
    "prompt_forge":       Role.GUEST,
    "guild_guide":        Role.GUEST,
    "congestion_display": Role.GUEST,

    # 無料会員以上
    "guild_square":       Role.MEMBER_FREE,
    "save_prompt":        Role.MEMBER_FREE,
    "prompt_history":     Role.MEMBER_FREE,
    "prompt_doctor":      Role.MEMBER_FREE,
    "language_quality":   Role.MEMBER_FREE,

    # 有料会員以上
    "campaign_forge":     Role.MEMBER_PAID,
    "promotion_planner":  Role.MEMBER_PAID,
    "article_draft":      Role.MEMBER_PAID,
    "workshop_master":    Role.MEMBER_PAID,
    "image_generation":   Role.MEMBER_PAID,

    # マスター会員以上
    "priority_queue":     Role.MEMBER_MASTER,
    "bulk_generate":      Role.MEMBER_MASTER,

    # 管理者以上
    "admin_dashboard":    Role.ADMIN,
    "user_management":    Role.ADMIN,
    "trend_management":   Role.ADMIN,
    "api_budget_view":    Role.ADMIN,

    # 本部のみ
    "hq_analytics":       Role.HEADQUARTERS,
    "hq_campaign":        Role.HEADQUARTERS,
}


class FeatureAccessService:
    """機能アクセス制御サービス。フィーチャーフラグ不要 (常に使用可能)。"""

    def check(self, feature: str, user_role: Optional[str] = None) -> AccessResult:
        """
        指定機能にアクセス可能かどうかを返す。

        Args:
            feature:   機能キー (_FEATURE_REQUIREMENTS のキー)
            user_role: ユーザーのロール文字列 (None = ゲスト扱い)
        """
        # 機能フラグチェック
        flag_key = feature.upper()
        if not flags.is_enabled(flag_key):
            return AccessResult(
                allowed=False,
                reason=f"機能 '{feature}' は現在無効です",
                required_role="",
            )

        role = user_role or Role.GUEST
        required = _FEATURE_REQUIREMENTS.get(feature, Role.MEMBER_FREE)

        user_rank = _ROLE_RANK.get(role, 0)
        required_rank = _ROLE_RANK.get(required, 1)

        if user_rank >= required_rank:
            return AccessResult(allowed=True)

        return AccessResult(
            allowed=False,
            reason=f"この機能は {required} 以上のメンバーが利用できます",
            required_role=required,
        )

    def is_admin(self, user_role: Optional[str]) -> bool:
        return user_role in (Role.ADMIN, Role.HEADQUARTERS)

    def is_hq(self, user_role: Optional[str]) -> bool:
        return user_role == Role.HEADQUARTERS

    def get_accessible_features(self, user_role: Optional[str]) -> list[str]:
        """指定ロールがアクセスできる全機能のリストを返す。"""
        role = user_role or Role.GUEST
        rank = _ROLE_RANK.get(role, 0)
        return [
            feat for feat, req in _FEATURE_REQUIREMENTS.items()
            if _ROLE_RANK.get(req, 1) <= rank
        ]


# グローバルシングルトン
feature_access_service = FeatureAccessService()
