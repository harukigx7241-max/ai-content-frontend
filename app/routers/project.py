"""app/routers/project.py — 一括生成（プロジェクトバンドル）エンドポイント"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.common import ProjectBundleRequest
from app.prompts.builders.project import build_project_bundle

router = APIRouter(prefix="/api/project", tags=["project"])


@router.post("/bundle")
def project_bundle(p: ProjectBundleRequest):
    prompts = build_project_bundle(p.theme, p.target, p.ai_mode)
    return JSONResponse(prompts)
