"""
app/routers/templates.py
テンプレートライブラリ公開 API。

エンドポイント:
  GET /api/templates           — 全テンプレート一覧 (フィルタ対応)
  GET /api/templates/packs     — パック定義一覧
  GET /api/templates/{id}      — テンプレート詳細
  GET /api/templates/{id}/form — フォームデフォルト値

クエリパラメータ (/api/templates):
  pack=<pack_id>         — パック絞り込み
  category=<category>    — カテゴリ絞り込み
  free_only=true/false   — 無料テンプレートのみ
  difficulty=<level>     — 難易度絞り込み
"""

import json
import pathlib
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.services.template_service import (
    get_template,
    get_form_defaults,
    list_templates,
    invalidate_cache,
)

router = APIRouter(prefix="/api/templates", tags=["templates"])

_TMPL_BASE = pathlib.Path(__file__).resolve().parent.parent.parent / "templates_library"
_PACKS_PATH = _TMPL_BASE / "_packs.json"
_packs_cache: Optional[dict] = None


def _load_packs() -> dict:
    global _packs_cache
    if _packs_cache is None:
        try:
            _packs_cache = json.loads(_PACKS_PATH.read_text(encoding="utf-8"))
        except Exception:
            _packs_cache = {"packs": {}}
    return _packs_cache


@router.get("")
def get_templates(
    pack: Optional[str] = Query(None, description="パックIDで絞り込み"),
    category: Optional[str] = Query(None),
    free_only: Optional[bool] = Query(None, description="trueで無料テンプレートのみ"),
    difficulty: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
):
    """テンプレート一覧を返す。pack 指定時はそのパックのIDセットで絞り込む。"""
    pack_ids: Optional[set] = None
    if pack:
        packs = _load_packs().get("packs", {})
        if pack not in packs:
            raise HTTPException(status_code=404, detail=f"Pack '{pack}' not found")
        pack_ids = set(packs[pack]["template_ids"])

    results = list_templates(
        category=category,
        difficulty=difficulty,
        tag=tag,
    )

    if pack_ids is not None:
        results = [t for t in results if t["id"] in pack_ids]
        id_order = {tid: i for i, tid in enumerate(_load_packs()["packs"][pack]["template_ids"])}
        results = sorted(results, key=lambda t: id_order.get(t["id"], 999))

    if free_only is True:
        results = [t for t in results if t.get("free_available", True)]

    return JSONResponse({"templates": results, "total": len(results)})


@router.get("/packs")
def get_packs():
    """全パック定義を返す。"""
    packs_data = _load_packs()
    simplified = {
        pid: {
            "label": p["label"],
            "emoji": p["emoji"],
            "description": p["description"],
            "count": len(p["template_ids"]),
        }
        for pid, p in packs_data.get("packs", {}).items()
    }
    return JSONResponse({"packs": simplified})


@router.get("/parts/{filename}")
def get_template_part(filename: str):
    """_parts/ ディレクトリのファイルを返す。拡張子は .json または .md を自動補完。"""
    from app.services.template_service import get_part
    data = get_part(filename)
    if data is None:
        # 拡張子なしで試みた場合、.json / .md を補完して再試行
        for ext in (".json", ".md"):
            if not filename.endswith(ext):
                data = get_part(filename + ext)
                if data is not None:
                    filename = filename + ext
                    break
    if data is None:
        raise HTTPException(status_code=404, detail=f"Part '{filename}' not found")
    return JSONResponse({"filename": filename, "data": data})


@router.get("/{template_id}/form")
def get_template_form(template_id: str):
    """テンプレートのフォームデフォルト値を返す。"""
    form = get_form_defaults(template_id)
    if form is None:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return JSONResponse({"id": template_id, "form": form})


@router.get("/{template_id}")
def get_template_detail(template_id: str):
    """テンプレートの完全な JSON を返す。"""
    tmpl = get_template(template_id)
    if tmpl is None:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return JSONResponse(tmpl)
