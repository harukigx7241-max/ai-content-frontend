"""
main.py (root) — 後方互換シム
uvicorn main:app --reload で起動できるように app をエクスポートする。
実体は app/main.py に移動済み。このファイルは変更しないこと。
"""
from app.main import app  # noqa: F401  (re-export)
