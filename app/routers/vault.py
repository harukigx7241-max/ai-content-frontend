"""
app/routers/vault.py — プロンプト保管庫 API (Phase A: 完全永続化)

エンドポイント一覧:
  GET    /api/vault                         — アイテム一覧 (検索・フィルタ付き)
  POST   /api/vault                         — アイテム保存
  GET    /api/vault/folders                 — フォルダ一覧
  POST   /api/vault/folders                 — フォルダ作成
  PATCH  /api/vault/folders/{folder_id}     — フォルダ名変更
  DELETE /api/vault/folders/{folder_id}     — フォルダ削除 (中身は未分類へ移動)
  GET    /api/vault/{item_id}               — アイテム詳細
  PATCH  /api/vault/{item_id}               — アイテム更新 (title/tags/folder/status/summary)
  DELETE /api/vault/{item_id}               — アイテム削除
  PATCH  /api/vault/{item_id}/fav           — お気に入り切替 (後方互換)

権限: 全エンドポイント require_member (ゲスト不可)
上限: アイテム 200件 / フォルダ 20個 (将来のプラン差分を入れやすい定数)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import require_member
from app.db.models.saved_prompt import SavedPrompt
from app.db.models.vault_folder import VaultFolder
from app.db.session import get_db

router = APIRouter(prefix="/api/vault", tags=["vault"])

# ── 上限定数 (プラン差分はここを参照) ────────────────────────────────────
MAX_ITEMS   = 200
MAX_FOLDERS = 20


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Pydantic スキーマ ─────────────────────────────────────────────────────

class SaveRequest(BaseModel):
    title:     str           = Field(..., min_length=1, max_length=100)
    content:   str           = Field(..., min_length=1, max_length=10000)
    source:    str           = Field(default="forge", max_length=20)
    tags:      Optional[str] = Field(default="", max_length=200)
    folder_id: Optional[int] = None
    summary:   Optional[str] = Field(default=None, max_length=500)
    status:    str           = Field(default="draft", max_length=20)


class UpdateRequest(BaseModel):
    title:     Optional[str] = Field(None, min_length=1, max_length=100)
    content:   Optional[str] = Field(None, min_length=1, max_length=10000)
    tags:      Optional[str] = Field(None, max_length=200)
    folder_id: Optional[int] = None   # -1 = フォルダ解除
    summary:   Optional[str] = Field(None, max_length=500)
    status:    Optional[str] = Field(None, max_length=20)


class FavRequest(BaseModel):
    is_favorite: bool


class FolderRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


# ── シリアライザ ─────────────────────────────────────────────────────────

def _item_dict(item: SavedPrompt) -> dict:
    return {
        "id":          item.id,
        "title":       item.title,
        "content":     item.content,
        "source":      item.source,
        "is_favorite": item.is_favorite,
        "tags":        item.tags or "",
        "folder_id":   item.folder_id,
        "summary":     item.summary or "",
        "status":      item.status or "draft",
        "created_at":  item.created_at.isoformat(),
        "updated_at":  item.updated_at.isoformat() if item.updated_at else None,
    }


def _folder_dict(f: VaultFolder, item_count: int = 0) -> dict:
    return {
        "id":         f.id,
        "name":       f.name,
        "item_count": item_count,
        "created_at": f.created_at.isoformat(),
    }


# ══════════════════════════════════════════════════════════════════════
# アイテム API
# ══════════════════════════════════════════════════════════════════════

@router.get("")
def list_vault(
    user=Depends(require_member),
    db: Session = Depends(get_db),
    folder_id: Optional[int]  = Query(None),
    fav:       Optional[bool]  = Query(None),
    source:    Optional[str]   = Query(None, max_length=20),
    status:    Optional[str]   = Query(None, max_length=20),
    q:         Optional[str]   = Query(None, max_length=100),
    tag:       Optional[str]   = Query(None, max_length=50),
):
    """保管庫アイテム一覧 (新しい順)。複数フィルタ・全文検索対応。"""
    query = db.query(SavedPrompt).filter(SavedPrompt.user_id == user.id)
    if folder_id is not None:
        query = query.filter(SavedPrompt.folder_id == folder_id)
    if fav is not None:
        query = query.filter(SavedPrompt.is_favorite == fav)
    if source:
        query = query.filter(SavedPrompt.source == source)
    if status:
        query = query.filter(SavedPrompt.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            sa.or_(
                SavedPrompt.title.ilike(like),
                SavedPrompt.content.ilike(like),
                SavedPrompt.tags.ilike(like),
            )
        )
    if tag:
        query = query.filter(SavedPrompt.tags.ilike(f"%{tag}%"))
    items = query.order_by(SavedPrompt.created_at.desc()).all()
    return JSONResponse([_item_dict(i) for i in items])


@router.post("", status_code=201)
def save_to_vault(
    req: SaveRequest,
    user=Depends(require_member),
    db: Session = Depends(get_db),
):
    """保管庫にアイテムを保存 (最大 MAX_ITEMS 件)。"""
    count = db.scalar(
        sa.select(sa.func.count(SavedPrompt.id)).where(SavedPrompt.user_id == user.id)
    )
    if count >= MAX_ITEMS:
        raise HTTPException(
            400, f"保管庫が満杯です（最大{MAX_ITEMS}件）。古いアイテムを削除してください。"
        )
    if req.folder_id:
        _require_own_folder(req.folder_id, user.id, db)

    item = SavedPrompt(
        user_id=user.id,
        title=req.title,
        content=req.content,
        source=req.source,
        tags=req.tags or "",
        folder_id=req.folder_id,
        summary=req.summary,
        status=req.status,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return JSONResponse(_item_dict(item), status_code=201)


# ── フォルダ API (/{item_id} より先に定義して競合回避) ─────────────────

@router.get("/folders")
def list_folders(user=Depends(require_member), db: Session = Depends(get_db)):
    """フォルダ一覧 (アイテム件数付き)。"""
    folders = (
        db.query(VaultFolder)
        .filter(VaultFolder.user_id == user.id)
        .order_by(VaultFolder.created_at)
        .all()
    )
    result = []
    for f in folders:
        cnt = db.scalar(
            sa.select(sa.func.count(SavedPrompt.id)).where(
                SavedPrompt.user_id == user.id,
                SavedPrompt.folder_id == f.id,
            )
        ) or 0
        result.append(_folder_dict(f, cnt))
    return JSONResponse(result)


@router.post("/folders", status_code=201)
def create_folder(
    req: FolderRequest,
    user=Depends(require_member),
    db: Session = Depends(get_db),
):
    """フォルダを作成 (最大 MAX_FOLDERS 個)。"""
    cnt = db.scalar(
        sa.select(sa.func.count(VaultFolder.id)).where(VaultFolder.user_id == user.id)
    )
    if cnt >= MAX_FOLDERS:
        raise HTTPException(400, f"フォルダは最大{MAX_FOLDERS}個までです。")
    folder = VaultFolder(user_id=user.id, name=req.name.strip())
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return JSONResponse(_folder_dict(folder), status_code=201)


@router.patch("/folders/{folder_id}")
def update_folder(
    folder_id: int,
    req: FolderRequest,
    user=Depends(require_member),
    db: Session = Depends(get_db),
):
    """フォルダ名を変更する。"""
    folder = _require_own_folder(folder_id, user.id, db)
    folder.name = req.name.strip()
    db.commit()
    return JSONResponse(_folder_dict(folder))


@router.delete("/folders/{folder_id}")
def delete_folder(
    folder_id: int,
    user=Depends(require_member),
    db: Session = Depends(get_db),
):
    """フォルダを削除。中のアイテムは未分類 (folder_id=NULL) に移動。"""
    folder = _require_own_folder(folder_id, user.id, db)
    db.query(SavedPrompt).filter(
        SavedPrompt.user_id == user.id,
        SavedPrompt.folder_id == folder_id,
    ).update({"folder_id": None})
    db.delete(folder)
    db.commit()
    return JSONResponse({"ok": True})


# ── アイテム個別 API ──────────────────────────────────────────────────

@router.get("/{item_id}")
def get_item(item_id: int, user=Depends(require_member), db: Session = Depends(get_db)):
    """アイテム詳細取得。"""
    item = _require_own_item(item_id, user.id, db)
    return JSONResponse(_item_dict(item))


@router.patch("/{item_id}")
def update_item(
    item_id: int,
    req: UpdateRequest,
    user=Depends(require_member),
    db: Session = Depends(get_db),
):
    """アイテムのタイトル・タグ・フォルダ・ステータス・メモを更新。"""
    item = _require_own_item(item_id, user.id, db)
    if req.title   is not None: item.title   = req.title
    if req.content is not None: item.content = req.content
    if req.tags    is not None: item.tags    = req.tags
    if req.summary is not None: item.summary = req.summary
    if req.status  is not None: item.status  = req.status
    if req.folder_id is not None:
        if req.folder_id == -1:
            item.folder_id = None
        else:
            _require_own_folder(req.folder_id, user.id, db)
            item.folder_id = req.folder_id
    item.updated_at = _now()
    db.commit()
    db.refresh(item)
    return JSONResponse(_item_dict(item))


@router.delete("/{item_id}", status_code=200)
def delete_from_vault(
    item_id: int,
    user=Depends(require_member),
    db: Session = Depends(get_db),
):
    """アイテムを削除。"""
    item = _require_own_item(item_id, user.id, db)
    db.delete(item)
    db.commit()
    return JSONResponse({"ok": True})


@router.patch("/{item_id}/fav", status_code=200)
def toggle_favorite(
    item_id: int,
    req: FavRequest,
    user=Depends(require_member),
    db: Session = Depends(get_db),
):
    """お気に入りフラグ切替 (後方互換エンドポイント)。"""
    item = _require_own_item(item_id, user.id, db)
    item.is_favorite = req.is_favorite
    item.updated_at  = _now()
    db.commit()
    return JSONResponse({"ok": True, "is_favorite": item.is_favorite})


# ── 内部ヘルパー ─────────────────────────────────────────────────────

def _require_own_item(item_id: int, user_id: int, db: Session) -> SavedPrompt:
    item = db.query(SavedPrompt).filter(
        SavedPrompt.id == item_id,
        SavedPrompt.user_id == user_id,
    ).first()
    if not item:
        raise HTTPException(404, "アイテムが見つかりません。")
    return item


def _require_own_folder(folder_id: int, user_id: int, db: Session) -> VaultFolder:
    folder = db.query(VaultFolder).filter(
        VaultFolder.id == folder_id,
        VaultFolder.user_id == user_id,
    ).first()
    if not folder:
        raise HTTPException(404, "フォルダが見つかりません。")
    return folder
