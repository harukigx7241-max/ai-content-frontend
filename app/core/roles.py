"""
app/core/roles.py
ロール定義の一元管理。DB 値・階層・ラベル・セットを提供する。

【DB との対応】
  現在 DB の role カラムは "user" | "admin" の 2 値のみ。
  Phase 15 で "member_paid" / "member_master" / "headquarters" を追加する予定。
  それまでの間、 RoleValue.MEMBER_FREE = "user" と定義して後方互換を維持する。

【使い方】
  from app.core.roles import RoleValue, RoleRank, ADMIN_ROLES, HQ_ROLES

  # ロールチェック
  if RoleRank.gte(user.role, RoleValue.MEMBER_PAID):
      ...  # 有料会員以上のみ

  # FastAPI 依存性
  from app.auth.dependencies import require_admin, require_hq, require_paid
"""
from __future__ import annotations

from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────────────────
# RoleValue — DB に格納される role 文字列
# ─────────────────────────────────────────────────────────────────────────────

class RoleValue:
    """DB の role カラムに格納される文字列定数。"""
    GUEST         = "guest"          # DBには格納しない (未ログイン状態)
    MEMBER_FREE   = "user"           # DB現在値 (Phase 15で "member_free" に変更予定)
    MEMBER_PAID   = "member_paid"    # Phase 15 以降
    MEMBER_MASTER = "member_master"  # Phase 15 以降
    ADMIN         = "admin"          # 管理者 (現場運営・ユーザー管理・サーバー操作)
    HEADQUARTERS  = "headquarters"   # 管理本部 (司令室・最上位制御・戦略・分析)


# ─────────────────────────────────────────────────────────────────────────────
# RoleRank — ロール階層順序
# ─────────────────────────────────────────────────────────────────────────────

_RANK_TABLE: dict[str, int] = {
    RoleValue.GUEST:         0,
    RoleValue.MEMBER_FREE:   1,
    RoleValue.MEMBER_PAID:   2,
    RoleValue.MEMBER_MASTER: 3,
    RoleValue.ADMIN:         4,
    RoleValue.HEADQUARTERS:  5,
}


class RoleRank:
    """ロールの階層判定ユーティリティ。"""

    @classmethod
    def of(cls, role: str | None) -> int:
        """ロール文字列から階層順序値を返す。未知ロールは GUEST (0) 扱い。"""
        return _RANK_TABLE.get(role or RoleValue.GUEST, 0)

    @classmethod
    def gte(cls, role: str | None, required: str) -> bool:
        """role が required 以上かどうかを返す。"""
        return cls.of(role) >= cls.of(required)

    @classmethod
    def lt(cls, role: str | None, required: str) -> bool:
        return not cls.gte(role, required)


# ─────────────────────────────────────────────────────────────────────────────
# RoleMeta — ロールのメタ情報 (UI 表示用)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RoleMeta:
    value: str       # DB 値
    label: str       # 日本語表示名
    rank: int        # 階層順序
    icon: str        # アイコン (ゲーム風)
    color: str       # UI カラーヒント
    description: str # 説明文
    upgrade_hint: str = ""  # アップグレード促進メッセージ


ROLE_META: dict[str, RoleMeta] = {
    RoleValue.GUEST: RoleMeta(
        value=RoleValue.GUEST,
        label="ゲスト",
        rank=0,
        icon="👤",
        color="gray",
        description="未ログインの訪問者。1日3回まで基本機能を利用できます。",
        upgrade_hint="無料会員登録で全機能が解放されます。",
    ),
    RoleValue.MEMBER_FREE: RoleMeta(
        value=RoleValue.MEMBER_FREE,
        label="無料会員",
        rank=1,
        icon="⚗",
        color="blue",
        description="無料会員。広場の閲覧・投稿、プロンプト生成が利用できます。",
        upgrade_hint="有料プランへのアップグレードで上位機能が解放されます。",
    ),
    RoleValue.MEMBER_PAID: RoleMeta(
        value=RoleValue.MEMBER_PAID,
        label="有料会員",
        rank=2,
        icon="⚔",
        color="amber",
        description="有料会員。キャンペーン工房・画像生成・記事下書きなどが利用できます。",
        upgrade_hint="マスタープランへのアップグレードで最上位機能が解放されます。",
    ),
    RoleValue.MEMBER_MASTER: RoleMeta(
        value=RoleValue.MEMBER_MASTER,
        label="マスター会員",
        rank=3,
        icon="✦",
        color="gold",
        description="マスター会員。全機能 + 優先レーン + 一括生成が利用できます。",
        upgrade_hint="",
    ),
    RoleValue.ADMIN: RoleMeta(
        value=RoleValue.ADMIN,
        label="管理者",
        rank=4,
        icon="⚒",
        color="red",
        description="管理者。ユーザー管理・コンテンツ管理・サーバー設定を担当します。",
        upgrade_hint="",
    ),
    RoleValue.HEADQUARTERS: RoleMeta(
        value=RoleValue.HEADQUARTERS,
        label="管理本部",
        rank=5,
        icon="🏛",
        color="purple",
        description="管理本部。全機能の最上位制御・戦略分析・キャンペーン運営を担当します。",
        upgrade_hint="",
    ),
}


def get_role_meta(role: str | None) -> RoleMeta:
    """ロール文字列から RoleMeta を返す。未知ロールは GUEST メタを返す。"""
    return ROLE_META.get(role or RoleValue.GUEST, ROLE_META[RoleValue.GUEST])


def get_upgrade_hint(current_role: str | None, required_role: str) -> str:
    """
    現在ロールから必要ロールへのアップグレードヒントを返す。
    current_role >= required_role なら空文字を返す。
    """
    if RoleRank.gte(current_role, required_role):
        return ""
    meta = ROLE_META.get(required_role)
    if meta is None:
        return ""
    current_meta = ROLE_META.get(current_role or RoleValue.GUEST, ROLE_META[RoleValue.GUEST])
    return current_meta.upgrade_hint or f"この機能は {meta.label} 以上のメンバーが利用できます。"


# ─────────────────────────────────────────────────────────────────────────────
# ロールセット — よく使うグループ定義
# ─────────────────────────────────────────────────────────────────────────────

# 管理者権限を持つロール (admin + headquarters)
ADMIN_ROLES: frozenset[str] = frozenset({
    RoleValue.ADMIN,
    RoleValue.HEADQUARTERS,
})

# 管理本部のみ
HQ_ROLES: frozenset[str] = frozenset({
    RoleValue.HEADQUARTERS,
})

# 有料会員以上のロール
PAID_ROLES: frozenset[str] = frozenset({
    RoleValue.MEMBER_PAID,
    RoleValue.MEMBER_MASTER,
    RoleValue.ADMIN,
    RoleValue.HEADQUARTERS,
})

# マスター会員以上
MASTER_ROLES: frozenset[str] = frozenset({
    RoleValue.MEMBER_MASTER,
    RoleValue.ADMIN,
    RoleValue.HEADQUARTERS,
})

# ログイン済みメンバー全員 (ゲスト除く)
MEMBER_ROLES: frozenset[str] = frozenset({
    RoleValue.MEMBER_FREE,
    RoleValue.MEMBER_PAID,
    RoleValue.MEMBER_MASTER,
    RoleValue.ADMIN,
    RoleValue.HEADQUARTERS,
})

# ─────────────────────────────────────────────────────────────────────────────
# 管理者 / 管理本部の違い (ドキュメント)
# ─────────────────────────────────────────────────────────────────────────────
#
# admin (管理者) — 現場運営担当
#   ✓ ユーザー管理 (承認・停止・権限変更)
#   ✓ コンテンツ管理 (投稿削除・モデレーション)
#   ✓ サーバー設定 (メンテナンスモード・告知バー)
#   ✓ トレンドシグナル編集
#   ✓ API 利用量確認
#   ✗ 戦略分析・KPI 閲覧 (HQ 専用)
#   ✗ キャンペーン管理 (HQ 専用)
#   ✗ 招待コード一括発行 (HQ 専用)
#
# headquarters (管理本部) — 司令室・最上位制御
#   ✓ admin の全権限に加えて
#   ✓ 全ユーザー活動の詳細分析
#   ✓ KPI・収益・コスト分析
#   ✓ キャンペーン / プロモーション戦略管理
#   ✓ A/B テスト設定 (将来)
#   ✓ 招待コード一括発行・管理
#   ✓ admin ユーザーの管理 (admin は他 admin を管理できない)
