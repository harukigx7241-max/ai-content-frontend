"""
app/prompts/suffixes/input_mode.py
input_mode (normal / auto_assist / full_auto) 別の補足文字列。
normal は追加なし。
"""

_AUTO_ASSIST = """

【補助入力モード】
ユーザーが入力した情報が不完全な場合は、副業コンテンツの専門家として
不足している情報を推測・補完して最適な出力を生成してください。
ただしユーザーが明示的に入力した情報は必ず最優先で使用してください。"""

_FULL_AUTO = """

【完全自動モード】
ユーザーは最小限の情報のみ提供しています。
副業コンテンツのプロとして、未入力のフィールドを全て自律的に判断・補完し、
最高品質の成果物を生成してください。
具体的な数字・固有の事例・ビフォーアフターを積極的に盛り込んでください。"""


def input_mode_suffix(mode: str) -> str:
    """input_mode に対応するサフィックスを返す。normal は空文字。"""
    if mode == "auto_assist":
        return _AUTO_ASSIST
    if mode == "full_auto":
        return _FULL_AUTO
    return ""
