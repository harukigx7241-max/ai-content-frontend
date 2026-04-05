cd /root/ai-content-pro

cat > main.py <<'EOF'
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="AI Content Pro", version="1.2.0")

class NotePromptRequest(BaseModel):
    theme: str = Field(..., min_length=1, max_length=200)
    target: str = Field(..., min_length=1, max_length=200)
    tone: str = Field(..., min_length=1, max_length=100)

def build_note_prompt(theme: str, target: str, tone: str) -> str:
    return f"""
あなたはnote記事のプロ編集者です。
以下の条件で、有料note用の高品質な記事作成プロンプトを作成してください。

【テーマ】
{theme}

【ターゲット】
{target}

【文体・トーン】
{tone}

【出力要件】
- 読者の悩みを明確化する
- 読者が得られるベネフィットを最初に提示する
- note向けに魅力的なタイトル案を3つ出す
- 見出し構成を作る
- 導入文の方向性を書く
- 本文で扱うべき重要ポイントを箇条書きで整理する
- 最後にCTA案を出す
""".strip()

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
      <meta charset="UTF-8">
      <title>AI Content Pro</title>
    </head>
    <body>
      <h1>AI Content Pro</h1>
      <p>本番デプロイ済みの最小動作確認ページです。</p>
      <p><a href="/health">/health</a></p>
    </body>
    </html>
    """

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/note/prompt")
def create_note_prompt(payload: NotePromptRequest):
    return {"prompt": build_note_prompt(payload.theme, payload.target, payload.tone)}
EOF