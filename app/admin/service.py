"""
app/admin/service.py — 管理者承認処理サービス

このフェーズでは管理者ダッシュボードの UI は最小限。
ただし status 変更ロジックはここに集約し、将来の admin UI から呼べるようにする。

TODO: Phase 3+ ダッシュボード完成版 / 一括操作 / 監査ログ / 通知
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.user import User


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, f"ユーザー ID={user_id} が見つかりません")
    return user


def list_users(db: Session, status: Optional[str] = None) -> list[User]:
    """全ユーザーを返す。status 指定時はフィルタリングする。"""
    q = db.query(User)
    if status:
        q = q.filter(User.status == status)
    return q.order_by(User.created_at.desc()).all()


def approve_user(db: Session, user_id: int, admin_id: int) -> User:
    """ユーザーを承認する (pending / rejected → approved)。"""
    user = _get_user_or_404(db, user_id)
    if user.status == "approved":
        raise HTTPException(400, "このユーザーはすでに承認済みです")
    user.status = "approved"
    user.approved_at = datetime.now(timezone.utc)
    user.approved_by = admin_id
    db.commit()
    db.refresh(user)
    return user


def reject_user(db: Session, user_id: int, admin_id: int) -> User:
    """ユーザー登録を却下する (pending → rejected)。"""
    user = _get_user_or_404(db, user_id)
    if user.status not in ("pending",):
        raise HTTPException(400, "却下できるのは承認待ちのユーザーのみです")
    user.status = "rejected"
    user.approved_by = admin_id
    db.commit()
    db.refresh(user)
    return user


def suspend_user(db: Session, user_id: int, admin_id: int) -> User:
    """ユーザーを停止する (approved → suspended)。管理者は停止不可。"""
    user = _get_user_or_404(db, user_id)
    if user.role == "admin":
        raise HTTPException(400, "管理者アカウントは停止できません")
    if user.status != "approved":
        raise HTTPException(400, "停止できるのは承認済みのユーザーのみです")
    user.status = "suspended"
    db.commit()
    db.refresh(user)
    return user


def restore_user(db: Session, user_id: int, admin_id: int) -> User:
    """停止ユーザーを復元する (suspended → approved)。TODO: Phase 3+ UI 実装"""
    user = _get_user_or_404(db, user_id)
    if user.status != "suspended":
        raise HTTPException(400, "復元できるのは停止中のユーザーのみです")
    user.status = "approved"
    user.approved_by = admin_id
    db.commit()
    db.refresh(user)
    return user
