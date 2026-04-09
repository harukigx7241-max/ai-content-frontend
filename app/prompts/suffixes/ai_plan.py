"""
app/prompts/suffixes/ai_plan.py
ai_plan (free / plus / pro / unknown) 別の追加指示。
free: トークン節約を促す / pro: 拡張出力を促す / plus・unknown: 追加なし。
"""

_FREE = """

【プランに関する注意】
無料プランのためトークン数に制限があります。
各セクションは要点を絞って簡潔にまとめ、最重要ポイントに絞って出力してください。"""

_PRO = """

【プレミアムモード】
高精度プランを利用中です。以下を最大限に活用してください:
・より詳細な事例と具体的な数字（実データに基づく）
・複数のアプローチやバリエーション（最低3案以上）
・深い分析と専門的な洞察（背景・理由・根拠を含む）
・拡張出力（より長く詳細な内容・省略なし）"""


def ai_plan_suffix(plan: str) -> str:
    """ai_plan に対応するサフィックスを返す。plus / unknown は空文字。"""
    if plan == "free":
        return _FREE
    if plan == "pro":
        return _PRO
    return ""
