"""
app/db/models/invite.py — 招待コード / 招待使用ログ テーブル (Phase 8)

設計方針:
  - InviteCode: 管理者・一般ユーザーが発行する招待コードを管理する
  - InviteUse:  招待コードを使用して登録したユーザーを追跡する
  - 二つのテーブルで「誰が・どのコードで・誰を招待したか」を記録する
  - 将来の招待品質評価 / ランキング / ツリー可視化の基盤として設計する

status 遷移:
  active   → inactive (手動無効化)
  active   → expired  (used_count >= max_uses で自動セット)
  inactive → active   (管理者が再有効化, TODO: Phase N+)

TODO: Phase N+ campaign_name, invite_bonus_type, quality_score
TODO: Phase N+ InviteUse に became_approved_at, first_login_at を追加
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, UniqueConstraint

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class InviteCode(Base):
    __tablename__ = "invite_codes"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    code             = Column(String(20), nullable=False, unique=True, index=True)

    # 発行者情報
    created_by_user_id = Column(Integer, nullable=True, index=True)   # null = システム発行
    created_by_role    = Column(String(20), nullable=False, default="admin")  # "admin" | "user"
    is_admin_code      = Column(Boolean, nullable=False, default=True)

    # 使用制限
    max_uses   = Column(Integer, nullable=False, default=1)
    used_count = Column(Integer, nullable=False, default=0)

    # 挙動フラグ
    auto_approve = Column(Boolean, nullable=False, default=False)  # True で登録即承認

    # ステータス・有効期限
    status     = Column(String(20), nullable=False, default="active", index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    # 将来拡張受け皿
    label = Column(String(100), nullable=True)  # キャンペーン名・ラベル
    notes = Column(Text, nullable=True)          # 管理メモ
    # TODO: Phase N+ campaign_name = Column(String(100), nullable=True)
    # TODO: Phase N+ invite_bonus_type = Column(String(50), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<InviteCode id={self.id} code={self.code!r} "
            f"status={self.status} {self.used_count}/{self.max_uses}>"
        )


class InviteUse(Base):
    """招待コードの使用ログ。1ユーザー = 1レコード (unique on invited_user_id)。"""
    __tablename__ = "invite_uses"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    code_id         = Column(Integer, nullable=False, index=True)         # InviteCode.id
    invited_user_id = Column(Integer, nullable=False, unique=True, index=True)  # 招待された User.id
    inviter_user_id = Column(Integer, nullable=True, index=True)          # コード発行者 User.id
    registered_at   = Column(DateTime(timezone=True), nullable=False, default=_now)

    # 将来拡張受け皿 (招待品質評価・ランキングに使用)
    # TODO: Phase N+ became_approved_at = Column(DateTime, nullable=True)
    # TODO: Phase N+ first_login_at     = Column(DateTime, nullable=True)
    # TODO: Phase N+ quality_score      = Column(Integer,  nullable=True)

    def __repr__(self) -> str:
        return (
            f"<InviteUse code_id={self.code_id} "
            f"invited={self.invited_user_id} inviter={self.inviter_user_id}>"
        )
