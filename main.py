from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

app = FastAPI(title="AI Content Pro", version="1.1.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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
- 実践的で再現性がある内容にする
- 日本語で自然かつ読みやすく出力する

【出力形式】
1. タイトル案
2. 想定読者の悩み
3. ベネフィット
4. 見出し構成
5. 導入文の方向性
6. 本文で書くべき要点
7. CTA案
""".strip()


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/note/prompt")
async def create_note_prompt(payload: NotePromptRequest):
    prompt = build_note_prompt(
        theme=payload.theme,
        target=payload.target,
        tone=payload.tone,
    )
    return JSONResponse({"prompt": prompt})