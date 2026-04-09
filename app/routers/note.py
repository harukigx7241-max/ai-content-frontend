"""app/routers/note.py — Tab1: 有料コンテンツ系エンドポイント"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.note import (
    NoteArticleRequest,
    NoteGiftRequest,
    NoteSalesCopyRequest,
    NoteTitlesRequest,
)
from app.prompts.builders.note import (
    build_note_article_prompt,
    build_note_gift_prompt,
    build_note_salescopy_prompt,
    build_note_titles_prompt,
)

router = APIRouter(prefix="/api/note", tags=["note"])


@router.post("/article")
def note_article(p: NoteArticleRequest):
    return JSONResponse({"prompt": build_note_article_prompt(p)})


@router.post("/titles")
def note_titles(p: NoteTitlesRequest):
    return JSONResponse({"prompt": build_note_titles_prompt(p)})


@router.post("/salescopy")
def note_salescopy(p: NoteSalesCopyRequest):
    return JSONResponse({"prompt": build_note_salescopy_prompt(p)})


@router.post("/gift")
def note_gift(p: NoteGiftRequest):
    return JSONResponse({"prompt": build_note_gift_prompt(p)})
