"""
app/services/knowledge_service.py
ナレッジベース読み込みサービス。

knowledge/ ディレクトリ以下の Markdown / JSON ファイルをアプリ内で
利用するためのローダーモジュール。

設計:
  - ファイルは起動時ではなく初回アクセス時にキャッシュ (lazy load)
  - キャッシュは辞書。本番では再起動で更新。
  - JSON ファイルは dict として、Markdown は文字列として返す
  - ワークショップ ID: 'note' | 'tips' | 'brain' | 'cw' | 'fortune' | 'sns' | 'sales'
"""

import json
import pathlib
from typing import Any, Dict, Optional

_BASE = pathlib.Path(__file__).resolve().parent.parent.parent / "knowledge"

_cache: Dict[str, Any] = {}


def _load(rel_path: str) -> Any:
    """rel_path は knowledge/ からの相対パス (例: 'workshops/note/trend_signals.json')"""
    if rel_path in _cache:
        return _cache[rel_path]

    full = _BASE / rel_path
    if not full.exists():
        _cache[rel_path] = None
        return None

    try:
        if full.suffix == ".json":
            data = json.loads(full.read_text(encoding="utf-8"))
        else:
            data = full.read_text(encoding="utf-8")
        _cache[rel_path] = data
        return data
    except Exception:
        _cache[rel_path] = None
        return None


# ── 公開 API ──────────────────────────────────────────────────────────

def get_trend_signals(workshop: str) -> Optional[dict]:
    """ワークショップの trend_signals.json を返す。存在しない場合は None。"""
    return _load(f"workshops/{workshop}/trend_signals.json")


def get_workshop_overview(workshop: str) -> Optional[str]:
    """ワークショップの overview.md を文字列で返す。"""
    return _load(f"workshops/{workshop}/overview.md")


def get_workshop_rules(workshop: str) -> Optional[str]:
    """ワークショップの rules.md を文字列で返す。"""
    return _load(f"workshops/{workshop}/rules.md")


def get_patterns(workshop: str) -> Optional[dict]:
    """ワークショップの patterns.json を返す。"""
    return _load(f"workshops/{workshop}/patterns.json")


def get_branding() -> Optional[str]:
    """ブランドガイド overview.md を返す。"""
    return _load("branding/overview.md")


def invalidate_cache(rel_path: Optional[str] = None) -> None:
    """キャッシュを無効化する。rel_path=None で全クリア。"""
    if rel_path is None:
        _cache.clear()
    else:
        _cache.pop(rel_path, None)
