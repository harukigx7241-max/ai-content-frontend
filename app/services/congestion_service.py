"""
app/services/congestion_service.py
混雑状況表示サービス。サービスの利用状況・混雑度を返す。

Tiers:
  FREE  — 静的ステータス (常に「利用可能」)
  API   — リアルタイムキュー確認 (未実装)
  DISABLED — ENABLE_CONGESTION_DISPLAY=false 時
"""
from __future__ import annotations

from dataclasses import dataclass

from app.services.base import BaseService, ServiceMode, ServiceResult


@dataclass
class CongestionStatus:
    level: str        # "low" | "medium" | "high" | "unavailable"
    label: str        # 日本語ラベル
    message: str      # ユーザー向けメッセージ
    color: str        # UI カラーヒント (green / yellow / red / gray)
    mode: str = "free"

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "label": self.label,
            "message": self.message,
            "color": self.color,
            "mode": self.mode,
        }


# 静的ステータス (FREE tier)
_FREE_STATUS = CongestionStatus(
    level="low",
    label="快適",
    message="現在スムーズにご利用いただけます",
    color="green",
    mode="free",
)


class CongestionService(BaseService):
    FLAG_KEY = "CONGESTION_DISPLAY"

    def get_status(self) -> ServiceResult:
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()
        if mode == ServiceMode.API:
            try:
                return self._run_api()
            except Exception:
                return self._run_fallback()
        return self._run_free()

    # ── FREE: 静的ステータス ─────────────────────────────────────

    def _run_free(self, **_: object) -> ServiceResult:
        return ServiceResult.free(content=_FREE_STATUS.to_dict())

    # ── API: リアルタイム混雑確認 (未実装) ──────────────────────

    def _run_api(self, **_: object) -> ServiceResult:
        """
        TODO: 生成ログ・アクティブセッション数を参照してリアルタイム混雑度を返す。
        Phase 16 の生成ログテーブルが必要。
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_fallback(self, **_: object) -> ServiceResult:
        return self._run_free()


# グローバルシングルトン
congestion_service = CongestionService()
