"""
app/services/prompt_forge_service.py
プロンプト鍛冶場サービス。既存の generate_service.dispatch() のラッパー。

Tiers:
  FREE     — 既存のテンプレート+ルールベース生成 (generate_service.dispatch)
  API      — LLM強化プロンプト最適化 (未実装)
  FALLBACK — FREE と同じ
  DISABLED — ENABLE_PROMPT_FORGE=false 時

既存コードとの互換性:
  generate_service.dispatch(p, builder_fn) はそのまま動作する。
  このサービスは上位ラッパーとして動作モードの管理を担う。
"""
from __future__ import annotations

from typing import Any, Callable, Tuple

from app.services.base import BaseService, ServiceMode, ServiceResult


class PromptForgeService(BaseService):
    FLAG_KEY = "PROMPT_FORGE"
    PREFER_API = False  # 現時点では API tier は未実装のため FREE 固定

    def forge(
        self,
        p: Any,
        builder_fn: Callable,
    ) -> Tuple[str, dict]:
        """
        プロンプトを生成して (prompt_str, meta_dict) を返す。
        generate_service.dispatch() と同じシグネチャ。

        モード判定は行うが、現時点では FREE のみ実装。
        """
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return "この機能は現在無効です。", {"mode": "disabled"}

        # FREE / FALLBACK → 既存 dispatch を呼ぶ
        from app.services.generate_service import dispatch
        return dispatch(p, builder_fn)

    def forge_as_result(
        self,
        p: Any,
        builder_fn: Callable,
    ) -> ServiceResult:
        """ServiceResult 形式で返すバリアント (将来の API tier 移行時に活用)。"""
        mode = self.get_mode()
        if mode == ServiceMode.DISABLED:
            return ServiceResult.disabled()

        from app.services.generate_service import dispatch
        prompt, meta = dispatch(p, builder_fn)
        return ServiceResult.free(content={"prompt": prompt, "meta": meta})

    # ── 将来の API tier 実装プレースホルダー ─────────────────────────
    def _run_api(self, p: Any, builder_fn: Callable) -> ServiceResult:
        """
        TODO: LLM を使ってプロンプト品質を高める。
        - まず FREE で生成
        - 生成プロンプトを LLM に渡して洗練
        - 洗練後プロンプトを返す
        """
        return ServiceResult.not_implemented(ServiceMode.API)


# グローバルシングルトン
prompt_forge_service = PromptForgeService()
