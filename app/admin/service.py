"""
app/admin/service.py — 管理者サービス

ユーザー承認処理・統計取得・システム設定管理をここに集約する。
router は薄く保ち、重いロジックはこのモジュールに寄せる。

TODO: Phase 4+ 一括操作 / 監査ログ / 通知
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core import runtime_config as rc
from app.core.config import settings
from app.db.models.system_setting import SystemSetting
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
    """停止ユーザーを復元する (suspended → approved)。"""
    user = _get_user_or_404(db, user_id)
    if user.status != "suspended":
        raise HTTPException(400, "復元できるのは停止中のユーザーのみです")
    user.status = "approved"
    user.approved_by = admin_id
    db.commit()
    db.refresh(user)
    return user


# ── 統計 ─────────────────────────────────────────────────────────

def get_stats(db: Session) -> dict:
    """管理ダッシュボード向け基本統計を返す。"""
    total = db.query(User).count()
    by_status = {
        s: db.query(User).filter(User.status == s).count()
        for s in ("pending", "approved", "rejected", "suspended")
    }
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent = db.query(User).filter(User.created_at >= week_ago).count()
    return {"total": total, **by_status, "signups_last_7days": recent}


# ── システム設定 ──────────────────────────────────────────────────

def get_settings(db: Session) -> dict:
    """現在のシステム設定を返す。DB 値 > 環境変数 の優先順位。"""
    return {
        "maintenance_enabled": rc.get_bool(rc.KEY_MAINTENANCE_ENABLED, settings.ENABLE_MAINTENANCE_MODE),
        "maintenance_message": rc.get(rc.KEY_MAINTENANCE_MESSAGE, settings.MAINTENANCE_MESSAGE),
        "notice_banner_enabled": rc.get_bool(rc.KEY_NOTICE_BANNER_ENABLED, settings.ENABLE_NOTICE_BANNER),
        "notice_banner_text": rc.get(rc.KEY_NOTICE_BANNER_TEXT, settings.NOTICE_BANNER_TEXT),
        "notice_banner_link": rc.get(rc.KEY_NOTICE_BANNER_LINK, settings.NOTICE_BANNER_LINK),
    }


def update_settings(db: Session, data: dict, admin_id: int) -> dict:
    """
    システム設定を DB と runtime_config の両方に保存する。
    None のフィールドはスキップ。bool は "true"/"false" 文字列に変換して保存。
    """
    now = datetime.now(timezone.utc)
    for key, value in data.items():
        if value is None:
            continue
        str_val = str(value).lower() if isinstance(value, bool) else str(value)
        row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if row:
            row.value = str_val
            row.updated_at = now
            row.updated_by = admin_id
        else:
            db.add(SystemSetting(key=key, value=str_val, updated_at=now, updated_by=admin_id))
        rc.set_value(key, str_val)  # インメモリも即時更新
    db.commit()
    return get_settings(db)
