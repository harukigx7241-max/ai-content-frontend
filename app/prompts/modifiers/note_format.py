"""
app/prompts/modifiers/note_format.py
note.com 向け装飾モディファイア。
note がサポートする記法に限定した装飾指示を付加する。
TODO: Phase 3+ で tips / Brain 向けのフォーマット変種を追加できる。
"""

_INSTRUCTION = """\
【note.com向け装飾ルール】
・見出しは Markdown 形式（## H2 / ### H3）で統一する
・各セクション間は「---」で区切る
・重要ポイントには先頭に絵文字を付ける（💡ポイント / ⚠️注意 / ✅まとめ / 🔑キー）
・強調したい箇所は **太字** で囲む
・リストは「・」で統一する（ハイフンより読みやすい）
・> 引用形式で重要な一文をハイライトボックスとして示す
・各セクションの冒頭に 2〜3 行のリード文を入れる
・1 段落は最大 5 行以内にし、余白を多めに取る
・全角スペースは使わない（note のレンダリングが崩れる原因になる）"""


def apply_note_format(prompt: str) -> str:
    """プロンプトに note.com 向け装飾指示を追加する。"""
    return f"{prompt}\n\n{_INSTRUCTION}"
