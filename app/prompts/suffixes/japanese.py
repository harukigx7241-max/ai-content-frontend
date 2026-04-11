"""
app/prompts/suffixes/japanese.py
日本語ファースト出力サフィックス。

全プロンプトの末尾に付加することで、AI が必ず日本語で出力するよう強制する。
画像生成プロンプト (output_mode == "image_prompt") は英語が望ましいため除外すること。
"""

_JAPANESE_INSTRUCTION = """

【言語設定】
必ず**日本語**で出力してください。
英語・中国語・その他の言語は使用しないでください。
専門用語を使う場合は日本語の後に (英語) を括弧書きで添えることは可です。"""


def japanese_first_suffix() -> str:
    """全プロンプトに付加する日本語出力強制サフィックスを返す。"""
    return _JAPANESE_INSTRUCTION
