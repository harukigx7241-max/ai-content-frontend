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
from app.services.generate_service import dispatch

router = APIRouter(prefix="/api/note", tags=["note"])


@router.post("/article")
def note_article(p: NoteArticleRequest):
    prompt, meta = dispatch(p, build_note_article_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})


@router.post("/titles")
def note_titles(p: NoteTitlesRequest):
    prompt, meta = dispatch(p, build_note_titles_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})


@router.post("/salescopy")
def note_salescopy(p: NoteSalesCopyRequest):
    prompt, meta = dispatch(p, build_note_salescopy_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})


@router.post("/gift")
def note_gift(p: NoteGiftRequest):
    prompt, meta = dispatch(p, build_note_gift_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})
