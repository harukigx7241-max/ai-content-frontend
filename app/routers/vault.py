"""
app/routers/vault.py — プロンプト保管庫 API
GET/POST/DELETE/PATCH /api/vault/*
認証必須 (require_member)。ゲストはローカルストレージのみ。
"""
from __future__ import annotations

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from app.auth.dependencies import require_member
from app.db.models.saved_prompt import SavedPrompt
from app.db.session import get_db

router = APIRouter(prefix="/api/vault", tags=["vault"])

MAX_VAULT = 50


class SaveRequest(BaseModel):
    title:   str           = Field(..., min_length=1, max_length=100)
    content: str           = Field(..., min_length=1, max_length=10000)
    source:  str           = Field(default="forge", max_length=20)
    tags:    Optional[str] = Field(default="", max_length=200)


class FavRequest(BaseModel):
    is_favorite: bool


def _to_dict(item: SavedPrompt) -> dict:
    return {
        "id":          item.id,
        "title":       item.title,
        "content":     item.content,
        "source":      item.source,
        "is_favorite": item.is_favorite,
        "tags":        item.tags or "",
        "created_at":  item.created_at.isoformat(),
    }


@router.get("")
def list_vault(user=Depends(require_member), db: Session = Depends(get_db)):
    """保管庫アイテム一覧 (新しい順)。"""
    items = (
        db.query(SavedPrompt)
        .filter(SavedPrompt.user_id == user.id)
        .order_by(SavedPrompt.created_at.desc())
        .all()
    )
    return JSONResponse([_to_dict(i) for i in items])


@router.post("", status_code=201)
def save_to_vault(req: SaveRequest, user=Depends(require_member), db: Session = Depends(get_db)):
    """保管庫に保存 (最大 50 件)。"""
    count = db.scalar(
        sa.select(sa.func.count(SavedPrompt.id)).where(SavedPrompt.user_id == user.id)
    )
    if count >= MAX_VAULT:
        raise HTTPException(400, f"保管庫が満杯です（最大{MAX_VAULT}件）。古いアイテムを削除してください。")

    item = SavedPrompt(
        user_id=user.id,
        title=req.title,
        content=req.content,
        source=req.source,
        tags=req.tags or "",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return JSONResponse(_to_dict(item))


@router.delete("/{item_id}", status_code=200)
def delete_from_vault(item_id: int, user=Depends(require_member), db: Session = Depends(get_db)):
    """保管庫アイテム削除。"""
    item = db.query(SavedPrompt).filter(
        SavedPrompt.id == item_id,
        SavedPrompt.user_id == user.id,
    ).first()
    if not item:
        raise HTTPException(404, "アイテムが見つかりません。")
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
    """お気に入りフラグ切り替え。"""
    item = db.query(SavedPrompt).filter(
        SavedPrompt.id == item_id,
        SavedPrompt.user_id == user.id,
    ).first()
    if not item:
        raise HTTPException(404, "アイテムが見つかりません。")
    item.is_favorite = req.is_favorite
    db.commit()
    return JSONResponse({"ok": True, "is_favorite": item.is_favorite})
