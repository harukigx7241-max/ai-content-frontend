"""
app/prompts/suffixes/output_rules.py
output_mode 別のサフィックス文字列。
prompt (デフォルト) は追加なし。final_text は前置き不要指示を追加。
note_styled は generate_service 内で note_format_service に委譲するため
ここには定義しない。
"""

_FINAL_TEXT = """

【重要: 出力モード = 完成文直接出力】
前置き・解説・コメントは一切不要です。
最初の一文から完成した本文を直接書き始めてください。
「はい、作成します」「以下の通りです」「承知しました」等の確認文は入れないでください。"""


def output_suffix(mode: str) -> str:
    """output_mode に対応するサフィックスを返す。prompt モードは空文字。"""
    if mode == "final_text":
        return _FINAL_TEXT
    # "prompt" / "note_styled" / その他 → 追加なし（note_styled は service 側で処理）
    return ""
