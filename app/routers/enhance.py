"""
app/routers/enhance.py — Phase 1: プロンプト強化系エンドポイント
既存のプロンプトを「修飾・変換」する /api/enhance/* エンドポイント群。
既存 /api/note/* 等とは完全に分離しており、既存 API に影響を与えない。
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.enhance import (
    AiOptimizeRequest,
    AutocompleteRequest,
    DirectOutputRequest,
    ImagePromptRequest,
    NoteFormatRequest,
)
from app.prompts.builders.enhance import build_autocomplete_prompt, build_image_prompt
from app.prompts.modifiers.ai_optimize import apply_ai_optimize
from app.prompts.modifiers.direct_output import apply_direct_output
from app.prompts.modifiers.note_format import apply_note_format

router = APIRouter(prefix="/api/enhance", tags=["enhance"])


@router.post("/direct_output")
def enhance_direct_output(p: DirectOutputRequest):
    """前置き不要モード: 元のプロンプトに直接出力指示を追加して返す。"""
    return JSONResponse({"prompt": apply_direct_output(p.prompt)})


@router.post("/note_format")
def enhance_note_format(p: NoteFormatRequest):
    """note.com 装飾モード: 元のプロンプトに note 向け装飾指示を追加して返す。"""
    return JSONResponse({"prompt": apply_note_format(p.prompt)})


@router.post("/ai_optimize")
def enhance_ai_optimize(p: AiOptimizeRequest):
    """AI 深層最適化モード: AI プラン別の詳細な最適化指示を追加して返す。"""
    return JSONResponse({"prompt": apply_ai_optimize(p.prompt, p.ai_mode)})


@router.post("/autocomplete")
def enhance_autocomplete(p: AutocompleteRequest):
    """空欄補完モード: ヒントからフォーム入力案を生成するプロンプトを返す。"""
    return JSONResponse({
        "prompt": build_autocomplete_prompt(p.category, p.tool, p.hint, p.ai_mode)
    })


@router.post("/image_prompt")
def enhance_image_prompt(p: ImagePromptRequest):
    """画像生成プロンプト生成: 記事テーマから画像 AI 向けプロンプトを返す。"""
    return JSONResponse({"prompt": build_image_prompt(p)})
