"""
app/services/base.py
サービス層の基底クラス・共通型定義。

サービスの動作モード (ServiceMode):
  FREE     — APIキー不要・ルールベース / テンプレートベース実装。常に動く。
  LITE     — 軽量 API 呼び出し (省トークン / 低コスト)。
  API      — フル機能・LLM API 必須。有効時のみ動く。
  FALLBACK — API 呼び出し失敗時の代替動作 (FREE へ降格など)。
  DISABLED — 機能フラグが OFF。呼び出し元には unavailable を返す。

UI 表示対応:
  DISABLED  → 「この機能は現在利用できません」
  FREE      → （表示なし、またはアイコンのみ）
  LITE      → 「Lite版で動作中」
  API       → 「AI連携版で動作中」
  FALLBACK  → 「AI接続に失敗しました。代替版で動作しています」
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ─────────────────────────────────────────────────────────────────────────────
# 定数
# ─────────────────────────────────────────────────────────────────────────────

_UI_LABELS: dict[str, str] = {
    "DISABLED": "この機能は現在利用できません",
    "FREE": "",
    "LITE": "Lite版で動作中",
    "API": "AI連携版で動作中",
    "FALLBACK": "AI接続に失敗しました。代替版で動作しています",
    "NOT_IMPLEMENTED": "準備中",
}


# ─────────────────────────────────────────────────────────────────────────────
# ServiceMode
# ─────────────────────────────────────────────────────────────────────────────

class ServiceMode(str, Enum):
    """各サービスの動作モードを表す列挙型。"""
    FREE = "free"
    LITE = "lite"
    API = "api"
    FALLBACK = "fallback"
    DISABLED = "disabled"

    @property
    def ui_label(self) -> str:
        return _UI_LABELS.get(self.name, "")

    @property
    def is_available(self) -> bool:
        return self not in (ServiceMode.DISABLED,)


# ─────────────────────────────────────────────────────────────────────────────
# ServiceResult
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ServiceResult:
    """
    全サービスの統一レスポンス型。

    available: bool          — コンテンツが有効かどうか
    mode: ServiceMode        — 実際に使われた動作モード
    content: Any             — 生成結果 (str / dict / list / None)
    hint: str                — UI に表示するヒント・メッセージ
    ui_label: str            — モードに応じたラベル (自動生成可)
    extra: dict              — 任意の追加メタデータ
    """
    available: bool
    mode: ServiceMode
    content: Any = None
    hint: str = ""
    ui_label: str = ""
    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.ui_label:
            self.ui_label = self.mode.ui_label

    # ── ファクトリメソッド ─────────────────────────────────────────────

    @classmethod
    def disabled(cls, hint: str = "") -> "ServiceResult":
        return cls(
            available=False,
            mode=ServiceMode.DISABLED,
            content=None,
            hint=hint or "この機能は現在無効です。",
        )

    @classmethod
    def not_implemented(cls, mode: ServiceMode = ServiceMode.FREE) -> "ServiceResult":
        return cls(
            available=False,
            mode=mode,
            content=None,
            hint="準備中",
            ui_label="準備中",
        )

    @classmethod
    def free(cls, content: Any, hint: str = "", **extra: Any) -> "ServiceResult":
        return cls(
            available=True,
            mode=ServiceMode.FREE,
            content=content,
            hint=hint,
            extra=extra,
        )

    @classmethod
    def lite(cls, content: Any, hint: str = "", **extra: Any) -> "ServiceResult":
        return cls(
            available=True,
            mode=ServiceMode.LITE,
            content=content,
            hint=hint,
            extra=extra,
        )

    @classmethod
    def api(cls, content: Any, hint: str = "", **extra: Any) -> "ServiceResult":
        return cls(
            available=True,
            mode=ServiceMode.API,
            content=content,
            hint=hint,
            extra=extra,
        )

    @classmethod
    def fallback(
        cls,
        content: Any,
        hint: str = "AI接続に失敗しました。代替版で動作しています。",
        **extra: Any,
    ) -> "ServiceResult":
        return cls(
            available=True,
            mode=ServiceMode.FALLBACK,
            content=content,
            hint=hint,
            extra=extra,
        )

    def to_dict(self) -> dict:
        return {
            "available": self.available,
            "mode": self.mode.value,
            "content": self.content,
            "hint": self.hint,
            "ui_label": self.ui_label,
            **self.extra,
        }


# ─────────────────────────────────────────────────────────────────────────────
# BaseService
# ─────────────────────────────────────────────────────────────────────────────

class BaseService:
    """
    全サービスの基底クラス。

    サブクラスで FLAG_KEY を設定すると、フィーチャーフラグの ON/OFF
    および API キーの有無に応じて動作モードが自動決定される。

    使い方:
        class FooService(BaseService):
            FLAG_KEY = "PROMPT_DOCTOR"

            def run(self, text: str) -> ServiceResult:
                mode = self.get_mode()
                if mode == ServiceMode.DISABLED:
                    return ServiceResult.disabled()
                if mode == ServiceMode.API:
                    try:
                        return self._run_api(text=text)
                    except Exception:
                        return self._run_fallback(text=text)
                return self._run_free(text=text)

            def _run_free(self, **kw) -> ServiceResult:
                # ルールベース実装
                ...

            def _run_api(self, **kw) -> ServiceResult:
                # LLM API 実装 (未実装の場合は not_implemented を返す)
                return ServiceResult.not_implemented(ServiceMode.API)
    """

    # サブクラスで上書き: feature_flags の属性名 (例: "PROMPT_DOCTOR")
    FLAG_KEY: str = ""

    # API モードを優先するかどうか (False = FREE 固定)
    PREFER_API: bool = True

    def get_mode(self) -> ServiceMode:
        """
        現在の動作モードを返す。

        1. フィーチャーフラグが OFF → DISABLED
        2. API キーが設定されており PREFER_API=True → API
        3. それ以外 → FREE
        """
        if self.FLAG_KEY and not self._is_flag_enabled():
            return ServiceMode.DISABLED
        if self.PREFER_API and self._has_api_key():
            return ServiceMode.API
        return ServiceMode.FREE

    def _is_flag_enabled(self) -> bool:
        """フィーチャーフラグが有効かどうかを確認する。"""
        if not self.FLAG_KEY:
            return True
        # 遅延インポートで循環参照を避ける
        try:
            from app.core.feature_flags import flags
            return getattr(flags, self.FLAG_KEY, True)
        except Exception:
            return True

    def _has_api_key(self) -> bool:
        """少なくとも1つの LLM API キーが設定されているか確認する。"""
        return bool(
            os.getenv("OPENAI_API_KEY")
            or os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

    def _get_preferred_api(self) -> str:
        """利用可能な API プロバイダー名を返す。"""
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        if os.getenv("GEMINI_API_KEY"):
            return "gemini"
        return "none"
