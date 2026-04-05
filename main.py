from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

app = FastAPI(title="AI Content Pro", version="1.3.0")

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
""".strip()


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/note/prompt")
def create_note_prompt(payload: NotePromptRequest):
    return JSONResponse(
        {"prompt": build_note_prompt(payload.theme, payload.target, payload.tone)}
    )