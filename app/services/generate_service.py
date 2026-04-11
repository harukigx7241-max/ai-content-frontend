"""
app/services/generate_service.py
生成オーケストレーター。ルーターから呼ばれる唯一の窓口。

dispatch(p, builder_fn) の処理フロー:
  1. builder_fn(p) で基本プロンプト構築 (ai_suffix 込み)
  2. input_mode_service で補足文を追記
  3. output_mode に応じた処理:
     - image_prompt  → ImagePromptService で置換 (日本語サフィックス除外)
     - note_styled   → note_format_service で装飾
     - final_text    → output_suffix を追記
     - prompt (default) → 追加なし
  4. ai_plan_suffix を追記
  5. japanese_first_suffix を追記 (image_prompt 以外)
  6. (prompt, meta) を返す

builders は変更不要。options が None の場合は既存動作と完全互換。
"""
from typing import Any, Callable, Tuple

from app.prompts.suffixes.ai_plan import ai_plan_suffix
from app.prompts.suffixes.japanese import japanese_first_suffix
from app.prompts.suffixes.output_rules import output_suffix
from app.services.input_mode_service import get_supplement
from app.services.note_format_service import apply_note_format_service


def dispatch(p: Any, builder_fn: Callable) -> Tuple[str, dict]:
    """
    p          : リクエストスキーマ。options フィールドは Optional (なければ None)。
    builder_fn : build_*_prompt(p) → str  (既に ai_suffix を含む)
    returns    : (final_prompt, meta)
    """
    opts = getattr(p, "options", None)

    # ai_mode の互換レイヤー: options.ai_provider 優先、なければ p.ai_mode
    ai_mode = (
        (opts.ai_provider if opts and opts.ai_provider else None)
        or getattr(p, "ai_mode", "ChatGPT")
    )

    # ── 1. 基本プロンプト構築 ──────────────────────────────────────────
    prompt = builder_fn(p)

    # options がなければ日本語サフィックスのみ追加して返す
    if opts is None:
        prompt += japanese_first_suffix()
        return prompt, {
            "ai_mode": ai_mode,
            "output_mode": "prompt",
            "ai_plan": "unknown",
            "quality_mode": "standard",
            "input_mode": "normal",
        }

    # ── 2. input_mode 補足 ────────────────────────────────────────────
    supplement = get_supplement(opts.input_mode)
    if supplement:
        prompt += supplement

    # ── 3. output_mode 処理 ───────────────────────────────────────────
    if opts.output_mode == "image_prompt":
        # 画像プロンプト: 既存プロンプトをテーマとして利用し置換
        from app.services.image_prompt_service import ImagePromptService

        theme = (
            getattr(p, "theme", "")
            or getattr(p, "topic", "")
            or prompt[:100]
        )
        prompt = ImagePromptService(
            theme=theme,
            image_type=opts.image_type,
            image_platform=opts.image_platform,
            ai_mode=ai_mode,
        ).build()

    elif opts.output_mode == "note_styled":
        prompt = apply_note_format_service(prompt)

    else:
        # "prompt" / "final_text" など
        sfx = output_suffix(opts.output_mode)
        if sfx:
            prompt += sfx

    # ── 4. ai_plan サフィックス ───────────────────────────────────────
    plan_sfx = ai_plan_suffix(opts.ai_plan)
    if plan_sfx:
        prompt += plan_sfx

    # ── 5. 日本語ファースト強制 (画像プロンプトは除外) ───────────────
    if opts.output_mode != "image_prompt":
        prompt += japanese_first_suffix()

    meta = {
        "ai_mode": ai_mode,
        "output_mode": opts.output_mode,
        "ai_plan": opts.ai_plan,
        "quality_mode": opts.quality_mode,
        "input_mode": opts.input_mode,
    }

    return prompt, meta
