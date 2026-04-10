"""
app/services/note_format_service.py
note.com 向けフォーマット装飾サービス。

format_mode:
  "markdown" (default) — Markdown 見出し・区切り線・太字を指示
  "plain"              — テキスト装飾なし、note 向けプレーン指示
"""
from app.prompts.modifiers.note_format import apply_note_format

_PLAIN_INSTRUCTION = """

【note.com向け出力ルール（プレーン版）】
・見出しには # 記号を使わず【タイトル】形式で表記する
・区切りには「---」ではなく空行2行を使用する
・太字は「**」ではなく「※」や「★」で強調する
・リストは「・」で統一し番号付きリストは使わない"""


def apply_note_format_service(prompt: str, format_mode: str = "markdown") -> str:
    """
    note.com 向けにプロンプトにフォーマット指示を追加する。
    既存の apply_note_format modifier を内部で使用。
    """
    if format_mode == "plain":
        return prompt + _PLAIN_INSTRUCTION
    return apply_note_format(prompt)
