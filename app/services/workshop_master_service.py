"""
app/services/workshop_master_service.py
ワークショップマスターAIサービス。各工房専門のAIアシスタント。

Tiers:
  FREE     — 対応なし (API専用機能)
  API      — LLM工房アシスタント・質問応答 (未実装)
  DISABLED — ENABLE_WORKSHOP_MASTER_AI=false 時 (デフォルト)

デフォルト false のため、APIキーがあっても明示的に有効化が必要。
Phase 20+ で本実装予定。
"""
from __future__ import annotations

from app.services.base import BaseService, ServiceMode, ServiceResult


class WorkshopMasterService(BaseService):
    FLAG_KEY = "WORKSHOP_MASTER_AI"

    def ask(self, question: str, workshop: str = "note") -> ServiceResult:
        """工房マスターへの質問。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled(
                hint="ワークショップマスターAIは現在準備中です。"
            )
        if mode == ServiceMode.API:
            try:
                return self._run_api(question=question, workshop=workshop)
            except Exception:
                return self._run_fallback(question=question, workshop=workshop)
        # FREE: 対応なし → not_implemented
        return ServiceResult.not_implemented(ServiceMode.FREE)

    # ── API: LLM工房アシスタント (未実装) ─────────────────────────

    def _run_api(
        self, question: str = "", workshop: str = "note", **_: object
    ) -> ServiceResult:
        """
        TODO: 工房固有のナレッジ (knowledge/workshops/{workshop}/) を
        コンテキストとして LLM に与え、質問に答える。
        """
        return ServiceResult.not_implemented(ServiceMode.API)

    def _run_fallback(self, **kwargs: object) -> ServiceResult:
        return ServiceResult.not_implemented(ServiceMode.FALLBACK)


# グローバルシングルトン
workshop_master_service = WorkshopMasterService()
