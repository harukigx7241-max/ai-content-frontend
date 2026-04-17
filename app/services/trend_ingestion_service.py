"""
app/services/trend_ingestion_service.py
傾向収集・インサイト更新サービス — Phase 15

Tiers:
  FREE  — 手動入力データを knowledge/workshops/<ws>/trend_insights.json に書き込む
  API   — Phase 16+ でスクレイピングによる自動収集 (未実装)
  DISABLED — ENABLE_TREND_INGESTION=false 時

フロー:
  1. run_for_workshop(workshop) を呼ぶ
  2. 既存の trend_insights.json を読み込む
  3. extracted_at / expires_at を現在日時で更新
  4. knowledge/trend_history.json に実行ログを追記
  5. ServiceResult を返す

Admin trigger:
  POST /api/admin/trends/ingest  → run_all() を非同期で実行
  GET  /api/admin/trends/history → history を返す
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Any

from app.services.base import BaseService, ServiceMode, ServiceResult

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

_KNOWLEDGE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "knowledge"
_WORKSHOPS_DIR = _KNOWLEDGE_DIR / "workshops"
_HISTORY_FILE = _KNOWLEDGE_DIR / "trend_history.json"

WORKSHOPS = ["note", "tips", "brain", "cw", "fortune", "sns", "sales"]

# 鮮度ポリシー (trend_schema.json の freshness_policy に準拠)
_EXPIRY_DAYS: dict[str, int] = {
    "note": 3,
    "sns": 3,
    "tips": 10,
    "brain": 10,
    "cw": 10,
    "fortune": 10,
    "sales": 45,
}


# ─────────────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class IngestionResult:
    workshop: str
    success: bool
    mode: str
    message: str
    extracted_at: str = ""
    expires_at: str = ""


@dataclass
class RunSummary:
    triggered_at: str
    triggered_by: str
    workshops_ok: list[str] = field(default_factory=list)
    workshops_fail: list[str] = field(default_factory=list)
    mode: str = "free"

    @property
    def total(self) -> int:
        return len(self.workshops_ok) + len(self.workshops_fail)

    @property
    def success_count(self) -> int:
        return len(self.workshops_ok)


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _insight_path(workshop: str) -> pathlib.Path:
    return _WORKSHOPS_DIR / workshop / "trend_insights.json"


def _load_json(path: pathlib.Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_json(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_history() -> dict:
    data = _load_json(_HISTORY_FILE)
    if not data:
        return {"_version": "1.0", "last_updated": None, "total_runs": 0, "history": []}
    return data


def _save_history(history: dict) -> None:
    _save_json(_HISTORY_FILE, history)


def _append_history(summary: RunSummary) -> None:
    history = _load_history()
    entry = {
        "triggered_at": summary.triggered_at,
        "triggered_by": summary.triggered_by,
        "mode": summary.mode,
        "workshops_ok": summary.workshops_ok,
        "workshops_fail": summary.workshops_fail,
        "success_count": summary.success_count,
        "total": summary.total,
    }
    history["history"].insert(0, entry)
    # Keep last 100 runs
    history["history"] = history["history"][:100]
    history["last_updated"] = summary.triggered_at
    history["total_runs"] = history.get("total_runs", 0) + 1
    _save_history(history)


# ─────────────────────────────────────────────────────────────────────────────
# Free-tier ingestion (timestamp refresh on existing JSON)
# ─────────────────────────────────────────────────────────────────────────────

def _refresh_timestamps(workshop: str) -> IngestionResult:
    """
    既存の trend_insights.json の extracted_at / expires_at を現在日時で更新する。
    Phase 16+ では実際のスクレイピングデータで content も更新する。
    """
    path = _insight_path(workshop)
    data = _load_json(path)
    if data is None:
        return IngestionResult(
            workshop=workshop,
            success=False,
            mode="free",
            message=f"trend_insights.json が見つかりません: {path}",
        )

    now = _now_utc()
    expiry_days = _EXPIRY_DAYS.get(workshop, 10)
    expires = now + timedelta(days=expiry_days)

    data["extracted_at"] = _iso(now)
    data["expires_at"] = _iso(expires)
    data["source"] = "admin_trigger"

    try:
        _save_json(path, data)
        # Invalidate knowledge_service cache so next read gets fresh data
        _invalidate_cache(workshop)
        return IngestionResult(
            workshop=workshop,
            success=True,
            mode="free",
            message="タイムスタンプを更新しました (フェーズ15: 手動データ)",
            extracted_at=_iso(now),
            expires_at=_iso(expires),
        )
    except Exception as exc:
        return IngestionResult(
            workshop=workshop,
            success=False,
            mode="free",
            message=f"書き込みエラー: {exc}",
        )


def _invalidate_cache(workshop: str) -> None:
    """knowledge_service のファイルキャッシュから該当エントリを削除する。"""
    try:
        from app.services import knowledge_service as ks
        keys_to_remove = [
            k for k in ks._cache
            if f"workshops/{workshop}/" in k
        ]
        for k in keys_to_remove:
            ks._cache.pop(k, None)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# TrendIngestionService
# ─────────────────────────────────────────────────────────────────────────────

class TrendIngestionService(BaseService):
    """
    傾向収集サービス。

    FREE モード: 既存 trend_insights.json のタイムスタンプを更新する。
    API モード:  Phase 16+ でスクレイピング実装予定。
    """

    FLAG_KEY = "TREND_INGESTION"
    PREFER_API = False

    def run_for_workshop(
        self,
        workshop: str,
        triggered_by: str = "admin",
    ) -> ServiceResult:
        """指定ワークショップの傾向収集を実行する。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()

        if workshop not in WORKSHOPS:
            return ServiceResult.free(
                content={"error": f"Unknown workshop: {workshop}"},
                available=False,
            )

        result = _refresh_timestamps(workshop)
        return ServiceResult.free(
            content={
                "workshop": result.workshop,
                "success": result.success,
                "message": result.message,
                "extracted_at": result.extracted_at,
                "expires_at": result.expires_at,
                "mode": result.mode,
            },
            available=result.success,
        )

    def run_all(self, triggered_by: str = "admin") -> ServiceResult:
        """全ワークショップの傾向収集をまとめて実行する。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()

        triggered_at = _iso(_now_utc())
        summary = RunSummary(
            triggered_at=triggered_at,
            triggered_by=triggered_by,
            mode="free",
        )

        results: list[dict] = []
        for ws in WORKSHOPS:
            r = _refresh_timestamps(ws)
            results.append({
                "workshop": r.workshop,
                "success": r.success,
                "message": r.message,
                "extracted_at": r.extracted_at,
                "expires_at": r.expires_at,
            })
            if r.success:
                summary.workshops_ok.append(ws)
            else:
                summary.workshops_fail.append(ws)

        _append_history(summary)

        return ServiceResult.free(
            content={
                "triggered_at": triggered_at,
                "triggered_by": triggered_by,
                "success_count": summary.success_count,
                "total": summary.total,
                "results": results,
                "mode": "free",
            },
            available=True,
        )

    def get_history(self, limit: int = 20) -> ServiceResult:
        """収集実行履歴を返す。"""
        history = _load_history()
        entries = history.get("history", [])[:limit]
        return ServiceResult.free(
            content={
                "last_updated": history.get("last_updated"),
                "total_runs": history.get("total_runs", 0),
                "history": entries,
            },
            available=True,
        )

    def get_status(self) -> ServiceResult:
        """全ワークショップの鮮度状態を返す。"""
        now = _now_utc()
        statuses: list[dict] = []

        for ws in WORKSHOPS:
            path = _insight_path(ws)
            data = _load_json(path)
            if data is None:
                statuses.append({
                    "workshop": ws,
                    "exists": False,
                    "freshness": "missing",
                    "extracted_at": None,
                    "expires_at": None,
                })
                continue

            extracted_at = data.get("extracted_at")
            expires_at = data.get("expires_at")
            freshness = "unknown"
            if expires_at:
                try:
                    exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                    if exp_dt < now:
                        freshness = "stale"
                    elif exp_dt < now + timedelta(days=1):
                        freshness = "expiring"
                    else:
                        freshness = "fresh"
                except Exception:
                    freshness = "unknown"

            statuses.append({
                "workshop": ws,
                "exists": True,
                "freshness": freshness,
                "extracted_at": extracted_at,
                "expires_at": expires_at,
                "source": data.get("source"),
                "confidence": data.get("confidence"),
            })

        return ServiceResult.free(content={"workshops": statuses}, available=True)

    def _run_api(self, **_: Any) -> ServiceResult:
        """
        TODO Phase 16+: trend_sources.json の URL からスクレイピングして
        title_patterns / selling_angles / theme_signals を自動抽出する。
        """
        return ServiceResult.not_implemented(ServiceMode.API)


# グローバルシングルトン
trend_ingestion_service = TrendIngestionService()
