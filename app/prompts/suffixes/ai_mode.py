"""
app/prompts/suffixes/ai_mode.py
AI モード別の補足文。プロンプト末尾に付加することで
ChatGPT / Gemini / Claude それぞれに最適化されたヒントを与える。
TODO: Phase 3+ で AI モードを拡張する際にここを編集する。
"""


def ai_suffix(mode: str) -> str:
    """
    モード文字列に対応する AI 補足テキストを返す。
    未知のモードは ChatGPT 扱いにフォールバック。
    """
    if mode == "Gemini":
        return (
            "\n\n※ Gemini向け補足: Googleの最新情報・トレンドデータを積極的に"
            "Web検索で引用してください。最新性を最優先にしてください。"
        )
    if mode == "Claude":
        return (
            "\n\n※ Claude向け補足: <output>タグ内に最終回答を整理して出力してください。"
            "構造化された読みやすいフォーマットで記述してください。"
        )
    # デフォルト: ChatGPT
    return (
        "\n\n※ ChatGPT向け補足: マークダウン形式で見やすく出力してください。"
        "見出し・箇条書き・太字を積極的に活用してください。"
    )
