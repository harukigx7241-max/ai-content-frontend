"""
app/services/llm_client.py — LLM API クライアント共通ファクトリ

優先プロバイダー: Anthropic > OpenAI > Gemini (preferred_api() の返り値に従う)

使い方:
    from app.services.llm_client import call_llm

    text = call_llm(prompt="...", max_tokens=600)

例外:
    - API キー未設定: RuntimeError
    - パッケージ未インストール: RuntimeError
    - API 呼び出し失敗: 各 SDK の例外をそのまま raise
    → BaseService の try/except で FREE tier にフォールバックされる
"""
from __future__ import annotations

from app.core.config import settings
from app.core.feature_flags import flags


_DEFAULT_SYSTEM = (
    "あなたは日本語コンテンツ制作・副業支援を専門とするアシスタントです。"
    "簡潔・実用的・読みやすい日本語で回答してください。"
)


def call_llm(
    prompt: str,
    max_tokens: int = 1024,
    system: str = "",
) -> str:
    """
    設定済み API キーで LLM を呼び出し、テキスト応答を返す。

    Args:
        prompt:     ユーザーメッセージ
        max_tokens: 最大出力トークン数
        system:     システムプロンプト (空文字 → デフォルト)

    Returns:
        生成テキスト (str)

    Raises:
        RuntimeError: API キー未設定 / パッケージ未インストール
        各 SDK の例外: API 呼び出し失敗
    """
    provider = flags.preferred_api()
    sys_prompt = system or _DEFAULT_SYSTEM

    if provider == "anthropic":
        return _call_anthropic(prompt, max_tokens, sys_prompt)
    if provider == "openai":
        return _call_openai(prompt, max_tokens, sys_prompt)
    if provider == "gemini":
        return _call_gemini(prompt, max_tokens, sys_prompt)

    raise RuntimeError(
        "LLM API キーが設定されていません。"
        " ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY のいずれかを .env に設定してください。"
    )


# ── プロバイダー実装 ────────────────────────────────────────────────

def _call_anthropic(prompt: str, max_tokens: int, system: str) -> str:
    try:
        from anthropic import Anthropic
    except ImportError:
        raise RuntimeError(
            "anthropic パッケージが未インストールです。"
            " `pip install anthropic` を実行してください。"
        )
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def _call_openai(prompt: str, max_tokens: int, system: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError(
            "openai パッケージが未インストールです。"
            " `pip install openai` を実行してください。"
        )
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content


def _call_gemini(prompt: str, max_tokens: int, system: str) -> str:
    try:
        import google.generativeai as genai
    except ImportError:
        raise RuntimeError(
            "google-generativeai パッケージが未インストールです。"
            " `pip install google-generativeai` を実行してください。"
        )
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        system_instruction=system,
    )
    resp = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens),
    )
    return resp.text
