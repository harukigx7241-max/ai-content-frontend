"""
app/services/hq_dashboard_service.py
管理本部 (headquarters) 専用ダッシュボードサービス (Phase 18)

5つの機能を提供:
  1. KPI サマリー        — プラットフォーム全体の健全性 KPI
  2. Trend Room         — クロスワークショップのトレンド分析
  3. Incident Room      — インシデント管理 (ファイルベース)
  4. Feature Flag Console — 全フラグの詳細管理・ランタイムオーバーライド
  5. Admin ユーザー管理  — admin ロールユーザー一覧 (HQ 専用閲覧)

Phase 18 は FREE tier スキャフォールド。
リアルデータ接続は Phase 19+ で本実装。
"""
from __future__ import annotations

import json
import pathlib
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.services.base import BaseService, ServiceResult

# ─────────────────────────────────────────────────────────────────────────────
# パス定数
# ─────────────────────────────────────────────────────────────────────────────

_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_INCIDENTS_FILE = _ROOT / "data" / "incidents.json"
_KNOWLEDGE_ROOT = _ROOT / "knowledge" / "workshops"

_WORKSHOPS = ["note", "tips", "brain", "cw", "fortune", "sns", "sales"]


# ─────────────────────────────────────────────────────────────────────────────
# データクラス
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Incident:
    id: str
    title: str
    severity: str           # info | warning | critical
    status: str             # open | monitoring | resolved
    description: str
    created_at: str
    resolved_at: Optional[str] = None
    resolution: str = ""
    created_by: str = "system"

    def to_dict(self) -> dict:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────
# HQDashboardService
# ─────────────────────────────────────────────────────────────────────────────

class HQDashboardService(BaseService):
    """
    管理本部専用ダッシュボードサービス。
    管理者認証はルーター層で担保するため FLAG_KEY は空 (常時有効)。
    """
    FLAG_KEY = ""

    # ── 1. KPI サマリー ────────────────────────────────────────────────

    def get_kpi_summary(self, db=None) -> ServiceResult:
        """
        プラットフォーム全体の KPI サマリーを返す。
        Phase 18: モックデータ。Phase 19+ でDB接続に差し替え。
        """
        incidents = self._load_incidents()
        open_count = sum(1 for i in incidents if i.status in ("open", "monitoring"))
        # サービス稼働数 (feature_flags から取得)
        from app.core.feature_flags import flags
        flag_dict = flags.as_dict().get("features", {})
        services_total = len(flag_dict)
        services_up = sum(1 for v in flag_dict.values() if v)

        # ユーザー数は DB 接続時に本実装 (現在はモック)
        users_data = self._get_user_stats(db)

        return ServiceResult.free(content={
            "users": users_data,
            "activity": {
                "prompts_7d": 142,   # mock
                "posts_7d": 38,       # mock
                "growth_pct": 12.5,   # mock
            },
            "costs": {
                "monthly_usd": 0.0,   # 接続前は 0
                "daily_avg_usd": 0.0,
                "budget_pct": 0.0,
                "note": "API未接続 — Phase 19+ でリアルデータ接続",
            },
            "health": {
                "services_up": services_up,
                "services_total": services_total,
                "incidents_open": open_count,
                "status": "normal" if open_count == 0 else ("warning" if open_count <= 2 else "critical"),
            },
            "mode": "mock",
        })

    def _get_user_stats(self, db=None) -> dict:
        """DB 接続時はリアルデータを返す。未接続時はモック。"""
        if db is None:
            return {"total": 0, "active_7d": 0, "pending": 0, "paid": 0, "note": "DB未接続"}
        try:
            from app.db.models.user import User
            from sqlalchemy import func
            from datetime import timedelta
            now = datetime.now(timezone.utc)
            total = db.query(func.count(User.id)).scalar() or 0
            pending = db.query(func.count(User.id)).filter(User.status == "pending").scalar() or 0
            return {
                "total": total,
                "active_7d": 0,   # generation_log 未実装のため
                "pending": pending,
                "paid": 0,        # subscription_plan 追跡は Phase 19+
            }
        except Exception:
            return {"total": 0, "active_7d": 0, "pending": 0, "paid": 0}

    # ── 2. Trend Room ─────────────────────────────────────────────────

    def get_trend_analysis(self) -> ServiceResult:
        """全ワークショップのトレンドデータを横断分析して返す。"""
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        workshop_rows = []
        top_categories: dict[str, float] = {}
        top_selling_angles: dict[str, float] = {}

        for ws in _WORKSHOPS:
            insight_path = _KNOWLEDGE_ROOT / ws / "trend_insights.json"
            signal_path = _KNOWLEDGE_ROOT / ws / "trend_signals.json"

            data: dict = {}
            if insight_path.exists():
                try:
                    data = json.loads(insight_path.read_text(encoding="utf-8"))
                except Exception:
                    pass
            elif signal_path.exists():
                try:
                    data = json.loads(signal_path.read_text(encoding="utf-8"))
                except Exception:
                    pass

            # 鮮度計算
            freshness = "missing"
            expires_raw = data.get("expires_at") or data.get("freshness_policy", {}).get("expires_at")
            if expires_raw:
                try:
                    exp = datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
                    if exp.tzinfo is None:
                        exp = exp.replace(tzinfo=timezone.utc)
                    diff = (exp - now).total_seconds() / 86400
                    if diff > 7:
                        freshness = "fresh"
                    elif diff > 0:
                        freshness = "expiring"
                    else:
                        freshness = "stale"
                except Exception:
                    freshness = "unknown"

            # トップカテゴリ (値は "hot"/"warm"/"stable" 文字列)
            _MOMENTUM_SCORE = {"hot": 1.0, "warm": 0.7, "stable": 0.4, "cool": 0.2}
            category_momentum = data.get("category_momentum", {})
            if category_momentum:
                top_cat = max(
                    category_momentum,
                    key=lambda k: _MOMENTUM_SCORE.get(
                        category_momentum[k] if isinstance(category_momentum[k], str)
                        else category_momentum[k].get("momentum_score", "cool"),
                        0,
                    ),
                    default="—",
                )
                raw_val = category_momentum.get(top_cat, "cool")
                top_score = _MOMENTUM_SCORE.get(
                    raw_val if isinstance(raw_val, str) else "cool", 0
                )
            else:
                top_cat = "—"
                top_score = 0

            # 販売角度
            selling = data.get("selling_angles", [])
            for sa in selling:
                ang = sa.get("angle", "")
                st = sa.get("strength", 0)
                if ang:
                    top_selling_angles[ang] = max(top_selling_angles.get(ang, 0), st)

            # カテゴリ集計 (クロス集計用)
            for cat, val in category_momentum.items():
                sc = _MOMENTUM_SCORE.get(
                    val if isinstance(val, str) else val.get("momentum_score", "cool"), 0
                )
                top_categories[cat] = max(top_categories.get(cat, 0), sc)

            workshop_rows.append({
                "workshop": ws,
                "freshness": freshness,
                "top_category": top_cat,
                "top_momentum": round(top_score, 2),
                "title_patterns_count": len(data.get("title_patterns", [])),
                "selling_angles_count": len(selling),
                "has_insights": insight_path.exists(),
            })

        # クロス集計
        sorted_cats = sorted(top_categories.items(), key=lambda x: x[1], reverse=True)[:5]
        sorted_angles = sorted(top_selling_angles.items(), key=lambda x: x[1], reverse=True)[:5]
        freshest_ws = next((r["workshop"] for r in workshop_rows if r["freshness"] == "fresh"), None)
        stale_ws = [r["workshop"] for r in workshop_rows if r["freshness"] in ("stale", "missing")]

        return ServiceResult.free(content={
            "workshops": workshop_rows,
            "cross_analysis": {
                "top_categories": [{"category": c, "max_score": round(s, 2)} for c, s in sorted_cats],
                "top_selling_angles": [{"angle": a, "max_strength": round(s, 2)} for a, s in sorted_angles],
                "freshest_workshop": freshest_ws,
                "stale_workshops": stale_ws,
                "recommended_refresh": stale_ws[:3],
            },
        })

    # ── 3. Incident Room ──────────────────────────────────────────────

    def get_incidents(self, status: Optional[str] = None) -> ServiceResult:
        """インシデント一覧を返す。status でフィルタ可能。"""
        incidents = self._load_incidents()
        if status:
            incidents = [i for i in incidents if i.status == status]
        incidents.sort(key=lambda i: i.created_at, reverse=True)
        return ServiceResult.free(content={
            "incidents": [i.to_dict() for i in incidents],
            "total": len(incidents),
            "open": sum(1 for i in incidents if i.status == "open"),
            "monitoring": sum(1 for i in incidents if i.status == "monitoring"),
            "resolved": sum(1 for i in incidents if i.status == "resolved"),
        })

    def create_incident(
        self,
        title: str,
        severity: str,
        description: str,
        created_by: str = "hq",
    ) -> ServiceResult:
        """新規インシデントを作成して保存する。"""
        if severity not in ("info", "warning", "critical"):
            return ServiceResult.free(content={"error": f"不正な severity: {severity}"})
        incident = Incident(
            id=str(uuid.uuid4())[:8],
            title=title.strip(),
            severity=severity,
            status="open",
            description=description.strip(),
            created_at=datetime.now(timezone.utc).isoformat(),
            created_by=created_by,
        )
        incidents = self._load_incidents()
        incidents.insert(0, incident)
        self._save_incidents(incidents)
        return ServiceResult.free(content={"incident": incident.to_dict(), "message": "インシデントを作成しました"})

    def update_incident_status(
        self,
        incident_id: str,
        new_status: str,
        resolution: str = "",
        updated_by: str = "hq",
    ) -> ServiceResult:
        """インシデントのステータスを更新する。"""
        if new_status not in ("open", "monitoring", "resolved"):
            return ServiceResult.free(content={"error": f"不正なステータス: {new_status}"})
        incidents = self._load_incidents()
        target = next((i for i in incidents if i.id == incident_id), None)
        if target is None:
            return ServiceResult.free(content={"error": f"インシデント {incident_id} が見つかりません"})
        target.status = new_status
        if new_status == "resolved":
            target.resolved_at = datetime.now(timezone.utc).isoformat()
            target.resolution = resolution or "解決済み"
        self._save_incidents(incidents)
        return ServiceResult.free(content={"incident": target.to_dict(), "message": f"ステータスを {new_status} に更新しました"})

    def _load_incidents(self) -> list[Incident]:
        _INCIDENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not _INCIDENTS_FILE.exists():
            return []
        try:
            raw = json.loads(_INCIDENTS_FILE.read_text(encoding="utf-8"))
            return [Incident(**d) for d in raw.get("incidents", [])]
        except Exception:
            return []

    def _save_incidents(self, incidents: list[Incident]) -> None:
        _INCIDENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {"incidents": [i.to_dict() for i in incidents]}
        _INCIDENTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── 4. Feature Flag Console ────────────────────────────────────────

    def get_flag_details(self) -> ServiceResult:
        """
        全フラグの詳細情報を返す。
        feature_flags の値 + access_policy のポリシー情報 + runtime override 状態を統合。
        """
        from app.core.feature_flags import flags
        from app.core.access_policy import FEATURE_POLICIES

        # access_policy のフラグキー → ポリシー情報マップ
        policy_by_flag: dict[str, dict] = {}
        for p in FEATURE_POLICIES.values():
            if p.flag_key:
                policy_by_flag[p.flag_key] = {
                    "feature_id": p.feature_id,
                    "label": p.label,
                    "status": p.status.value,
                    "category": p.category,
                    "description": p.description,
                    "required_role": p.required_role,
                }

        overrides = flags.get_overrides()
        flag_rows = []

        # FeatureFlags クラスの全クラス変数を走査
        for key, val in vars(type(flags)).items():
            if key.startswith("_") or callable(val) or not isinstance(val, bool):
                continue
            current_val = flags.is_enabled(key)
            has_override = key in overrides
            policy_info = policy_by_flag.get(key, {})
            flag_rows.append({
                "key": key,
                "enabled": current_val,
                "default": bool(val),
                "has_override": has_override,
                "override_value": overrides.get(key),
                "feature_id": policy_info.get("feature_id", ""),
                "label": policy_info.get("label", key),
                "status": policy_info.get("status", ""),
                "category": policy_info.get("category", "system"),
                "description": policy_info.get("description", ""),
                "required_role": policy_info.get("required_role", ""),
            })

        flag_rows.sort(key=lambda r: (r["category"], r["key"]))
        return ServiceResult.free(content={
            "flags": flag_rows,
            "total": len(flag_rows),
            "overrides_active": len(overrides),
            "enabled_count": sum(1 for r in flag_rows if r["enabled"]),
            "disabled_count": sum(1 for r in flag_rows if not r["enabled"]),
        })

    def set_flag_override(
        self,
        flag_key: str,
        enabled: bool,
        reason: str = "",
    ) -> ServiceResult:
        """ランタイムオーバーライドを設定する (サーバー再起動でリセット)。"""
        from app.core.feature_flags import flags
        flags.set_override(flag_key, enabled)
        return ServiceResult.free(content={
            "key": flag_key,
            "enabled": enabled,
            "message": f"{flag_key} を {'有効' if enabled else '無効'} に設定しました",
            "note": "この変更はサーバー再起動でリセットされます",
            "reason": reason,
        })

    def clear_flag_override(self, flag_key: str) -> ServiceResult:
        """ランタイムオーバーライドを解除してデフォルト値に戻す。"""
        from app.core.feature_flags import flags
        flags.clear_override(flag_key)
        return ServiceResult.free(content={
            "key": flag_key,
            "message": f"{flag_key} のオーバーライドを解除しました (環境変数の値に戻ります)",
        })

    # ── 5. Admin ユーザー管理 (HQ 専用) ──────────────────────────────

    def get_admin_users(self, db=None) -> ServiceResult:
        """admin / headquarters ロールのユーザー一覧を返す (HQ のみ閲覧可)。"""
        if db is None:
            return ServiceResult.free(content={"admins": [], "note": "DB未接続"})
        try:
            from app.db.models.user import User
            from app.core.roles import ADMIN_ROLES
            admins = (
                db.query(User)
                .filter(User.role.in_(ADMIN_ROLES))
                .order_by(User.role, User.created_at)
                .all()
            )
            return ServiceResult.free(content={
                "admins": [
                    {
                        "id": u.id,
                        "display_name": u.display_name,
                        "email": getattr(u, "email", ""),
                        "role": u.role,
                        "status": u.status,
                        "created_at": u.created_at.isoformat() if u.created_at else "",
                    }
                    for u in admins
                ],
                "total": len(admins),
            })
        except Exception as e:
            return ServiceResult.free(content={"admins": [], "error": str(e)})

    def change_admin_role(self, target_user_id: int, new_role: str, db=None) -> ServiceResult:
        """
        admin ユーザーのロールを変更する (HQ 専用)。
        admin は他の admin を変更できない。HQ のみ実行可。
        """
        if db is None:
            return ServiceResult.free(content={"error": "DB未接続"})
        from app.core.roles import ADMIN_ROLES, RoleValue
        if new_role not in (RoleValue.ADMIN, RoleValue.HEADQUARTERS, RoleValue.MEMBER_FREE):
            return ServiceResult.free(content={"error": f"変更可能なロールは admin / headquarters / member_free のみです"})
        try:
            from app.db.models.user import User
            user = db.query(User).filter(User.id == target_user_id).first()
            if user is None:
                return ServiceResult.free(content={"error": "ユーザーが見つかりません"})
            old_role = user.role
            user.role = new_role
            db.commit()
            return ServiceResult.free(content={
                "user_id": target_user_id,
                "old_role": old_role,
                "new_role": new_role,
                "message": f"{user.display_name} のロールを {old_role} → {new_role} に変更しました",
            })
        except Exception as e:
            return ServiceResult.free(content={"error": str(e)})


# グローバルシングルトン
hq_dashboard_service = HQDashboardService()
