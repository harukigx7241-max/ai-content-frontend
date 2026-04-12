"""
app/services/feature_access_service.py
機能アクセス制御サービス。

【Phase 2 更新】
  Phase 1 の inline ロール定義を app.core.roles に移動。
  app.core.access_policy の FeaturePolicy / FEATURE_POLICIES を使用。

ロール定義 : app/core/roles.py
ポリシー定義: app/core/access_policy.py
依存性      : app/auth/dependencies.py
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.core.access_policy import (
    FEATURE_POLICIES,
    FeaturePolicy,
    FeatureStatus,
    get_policies_by_category,
    get_policies_for_role,
    get_policy,
)
from app.core.feature_flags import flags
from app.core.roles import RoleRank, RoleValue, get_upgrade_hint


# ─────────────────────────────────────────────────────────────────────────────
# AccessResult
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AccessResult:
    allowed: bool
    reason: str = ""
    required_role: str = ""
    upgrade_hint: str = ""
    feature_status: str = ""

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "required_role": self.required_role,
            "upgrade_hint": self.upgrade_hint,
            "feature_status": self.feature_status,
        }


# ─────────────────────────────────────────────────────────────────────────────
# FeatureAccessService
# ─────────────────────────────────────────────────────────────────────────────

class FeatureAccessService:
    """
    機能アクセス制御サービス。

    判定順序:
      1. FEATURE_POLICIES に登録されているか
      2. FeatureStatus が HIDDEN / MAINTENANCE → 全員拒否
      3. 機能フラグ (feature_flags) が OFF → 拒否
      4. ロールチェック (RoleRank.gte)
    """

    def check(
        self,
        feature: str,
        user_role: Optional[str] = None,
    ) -> AccessResult:
        """
        指定機能にアクセス可能かどうかを返す。

        Args:
            feature:   機能 ID (FEATURE_POLICIES のキー)
            user_role: ユーザーの role 文字列 (None = ゲスト扱い)
        """
        policy = get_policy(feature)

        # ── ポリシー未登録の機能は一般会員以上で許可 ─────────────────
        if policy is None:
            role = user_role or RoleValue.GUEST
            allowed = RoleRank.gte(role, RoleValue.MEMBER_FREE)
            return AccessResult(
                allowed=allowed,
                reason="" if allowed else "会員登録が必要です",
                required_role=RoleValue.MEMBER_FREE,
                upgrade_hint="" if allowed else get_upgrade_hint(role, RoleValue.MEMBER_FREE),
            )

        # ── HIDDEN / MAINTENANCE は全員拒否 ─────────────────────────
        if policy.status in (FeatureStatus.HIDDEN, FeatureStatus.MAINTENANCE):
            return AccessResult(
                allowed=False,
                reason="この機能は現在利用できません",
                feature_status=policy.status.value,
            )

        # ── 機能フラグチェック ────────────────────────────────────────
        if policy.flag_key and not flags.is_enabled(policy.flag_key):
            return AccessResult(
                allowed=False,
                reason=f"機能 '{feature}' は現在無効です",
                feature_status="disabled",
            )

        # ── ロールチェック ────────────────────────────────────────────
        role = user_role or RoleValue.GUEST
        if RoleRank.gte(role, policy.required_role):
            return AccessResult(
                allowed=True,
                feature_status=policy.status.value,
            )

        return AccessResult(
            allowed=False,
            reason=f"この機能は {_role_label(policy.required_role)} 以上のメンバーが利用できます",
            required_role=policy.required_role,
            upgrade_hint=policy.upgrade_hint,
            feature_status=policy.status.value,
        )

    def check_many(
        self,
        features: list[str],
        user_role: Optional[str] = None,
    ) -> dict[str, AccessResult]:
        """複数機能を一括チェックする。"""
        return {f: self.check(f, user_role) for f in features}

    def get_accessible_features(self, user_role: Optional[str]) -> list[str]:
        """指定ロールがアクセスできる機能 ID の一覧を返す。"""
        return [
            p.feature_id
            for p in get_policies_for_role(user_role)
            if not p.flag_key or flags.is_enabled(p.flag_key)
        ]

    def get_feature_map(self, user_role: Optional[str]) -> dict[str, dict]:
        """
        全機能の accessible / status をまとめた dict を返す。
        フロントエンドの /api/system/features で利用。
        """
        role = user_role or RoleValue.GUEST
        result: dict[str, dict] = {}
        for fid, policy in FEATURE_POLICIES.items():
            r = self.check(fid, role)
            result[fid] = {
                "allowed": r.allowed,
                "status": policy.status.value,
                "status_badge": policy.status.ui_badge,
                "required_role": policy.required_role,
                "upgrade_hint": r.upgrade_hint,
            }
        return result

    def is_admin(self, user_role: Optional[str]) -> bool:
        from app.core.roles import ADMIN_ROLES
        return user_role in ADMIN_ROLES

    def is_hq(self, user_role: Optional[str]) -> bool:
        from app.core.roles import HQ_ROLES
        return user_role in HQ_ROLES


# ─────────────────────────────────────────────────────────────────────────────
# ヘルパー
# ─────────────────────────────────────────────────────────────────────────────

def _role_label(role: str) -> str:
    from app.core.roles import get_role_meta
    return get_role_meta(role).label


# グローバルシングルトン
feature_access_service = FeatureAccessService()
