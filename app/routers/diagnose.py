"""
app/routers/diagnose.py
診断系 API エンドポイント。

  POST /api/diagnose/prompt   — プロンプト診断 (PromptDoctorService)
  POST /api/diagnose/quality  — 日本語品質チェック (LanguageQualityService)
  GET  /api/diagnose/status   — 両サービスの動作モード確認
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.services.prompt_doctor_service import prompt_doctor_service
from app.services.language_quality_service import language_quality_service

router = APIRouter(prefix="/api/diagnose", tags=["diagnose"])


class PromptInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000, description="診断するプロンプトテキスト")


class QualityInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000, description="品質チェックするテキスト")


@router.post("/prompt")
def diagnose_prompt(body: PromptInput):
    """プロンプトの品質を診断する。ルールベース (Lite)。"""
    result = prompt_doctor_service.diagnose(body.text)
    return JSONResponse(result.to_dict())


@router.post("/quality")
def check_quality(body: QualityInput):
    """日本語品質をチェックする。ルールベース (Lite)。"""
    result = language_quality_service.check(body.text)
    return JSONResponse(result.to_dict())


@router.get("/status")
def diagnose_status():
    """診断サービスの動作モードを返す。"""
    return JSONResponse({
        "prompt_doctor": {
            "mode": prompt_doctor_service.get_mode().value,
            "available": prompt_doctor_service.get_mode().is_available,
        },
        "language_quality": {
            "mode": language_quality_service.get_mode().value,
            "available": language_quality_service.get_mode().is_available,
        },
    })
