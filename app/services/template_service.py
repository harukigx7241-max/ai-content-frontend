"""
app/services/template_service.py
テンプレートライブラリ ローダー / セレクター / パーサー。

Phase 5 で導入。templates_library/ 以下の JSON テンプレートを
読み込み、フィルタリング・検索して ServiceResult を返す。

ディレクトリ構造:
  templates_library/
    _index.json          — 全テンプレートの索引 (21件)
    _schema.json         — メタデータスキーマ定義
    _parts/              — 共通部品 (hooks / title / intro / body / cta / closings / examples / anti_patterns)
    {category}/          — カテゴリ別テンプレート JSON
      {name}.json

フィルタリング対応フィールド:
  category / subcategory / difficulty / rarity / platform / tags

動作モード: FREE (ファイルベース、APIキー不要)
"""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, List, Optional

_TMPL_BASE = pathlib.Path(__file__).resolve().parent.parent.parent / "templates_library"
_INDEX_PATH = _TMPL_BASE / "_index.json"

# ── キャッシュ ──────────────────────────────────────────────────────────────
_index_cache: Optional[Dict[str, Any]] = None
_template_cache: Dict[str, Any] = {}
_parts_cache: Dict[str, Any] = {}


def _load_index() -> Dict[str, Any]:
    global _index_cache
    if _index_cache is None:
        try:
            _index_cache = json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
        except Exception:
            _index_cache = {"templates": []}
    return _index_cache


def _load_template_file(rel_path: str) -> Optional[Dict[str, Any]]:
    if rel_path in _template_cache:
        return _template_cache[rel_path]
    full = _TMPL_BASE / rel_path
    if not full.exists():
        _template_cache[rel_path] = None
        return None
    try:
        data = json.loads(full.read_text(encoding="utf-8"))
        _template_cache[rel_path] = data
        return data
    except Exception:
        _template_cache[rel_path] = None
        return None


def _load_part(filename: str) -> Any:
    """_parts/ 以下のファイルをロードする (JSON → dict, .md → str)。"""
    if filename in _parts_cache:
        return _parts_cache[filename]
    full = _TMPL_BASE / "_parts" / filename
    if not full.exists():
        _parts_cache[filename] = None
        return None
    try:
        if full.suffix == ".json":
            data = json.loads(full.read_text(encoding="utf-8"))
        else:
            data = full.read_text(encoding="utf-8")
        _parts_cache[filename] = data
        return data
    except Exception:
        _parts_cache[filename] = None
        return None


# ── 公開 API (モジュール関数) ──────────────────────────────────────────────

def list_templates(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    difficulty: Optional[str] = None,
    rarity: Optional[str] = None,
    platform: Optional[str] = None,
    tag: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    インデックスから条件に合うテンプレート一覧を返す。
    全引数 None で全件返す。
    """
    entries: List[Dict[str, Any]] = _load_index().get("templates", [])
    if category:
        entries = [e for e in entries if e.get("category") == category]
    if subcategory:
        entries = [e for e in entries if e.get("subcategory") == subcategory]
    if difficulty:
        entries = [e for e in entries if e.get("difficulty") == difficulty]
    if rarity:
        entries = [e for e in entries if e.get("rarity") == rarity]
    if platform:
        entries = [e for e in entries if platform in e.get("platform", [])]
    if tag:
        entries = [e for e in entries if tag in e.get("tags", [])]
    return entries


def get_template(template_id: str) -> Optional[Dict[str, Any]]:
    """ID でテンプレートのフル JSON を返す。見つからなければ None。"""
    for entry in _load_index().get("templates", []):
        if entry.get("id") == template_id:
            return _load_template_file(entry["file"])
    return None


def get_form_defaults(template_id: str) -> Optional[Dict[str, Any]]:
    """テンプレートの form デフォルト値だけを返す。"""
    tmpl = get_template(template_id)
    if tmpl is None:
        return None
    return tmpl.get("form")


def get_meta(template_id: str) -> Optional[Dict[str, Any]]:
    """テンプレートの _meta だけを返す。"""
    tmpl = get_template(template_id)
    if tmpl is None:
        return None
    return tmpl.get("_meta")


def get_categories() -> List[str]:
    """利用可能なカテゴリ一覧を返す (重複なし・ソート済み)。"""
    cats = {e.get("category", "") for e in _load_index().get("templates", [])}
    cats.discard("")
    return sorted(cats)


def get_part(filename: str) -> Any:
    """
    _parts/ 以下の部品ファイルを返す。
    例: get_part("hooks.json") → dict
        get_part("examples.md") → str
    """
    return _load_part(filename)


def invalidate_cache() -> None:
    """全キャッシュをクリア (開発時・テスト用)。"""
    global _index_cache
    _index_cache = None
    _template_cache.clear()
    _parts_cache.clear()


# ─────────────────────────────────────────────────────────────────────────────
# BaseService 準拠クラス
# ─────────────────────────────────────────────────────────────────────────────

from app.services.base import BaseService, ServiceMode, ServiceResult  # noqa: E402


class TemplateService(BaseService):
    """
    テンプレートライブラリサービス (BaseService準拠)。
    FLAG_KEY なし = 常に有効 (FREE)。
    """
    FLAG_KEY = ""

    def list(
        self,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        difficulty: Optional[str] = None,
        rarity: Optional[str] = None,
        platform: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> ServiceResult:
        """フィルタ付きテンプレート一覧を ServiceResult で返す。"""
        results = list_templates(
            category=category,
            subcategory=subcategory,
            difficulty=difficulty,
            rarity=rarity,
            platform=platform,
            tag=tag,
        )
        return ServiceResult.free(content=results)

    def get(self, template_id: str) -> ServiceResult:
        """テンプレートのフル JSON を ServiceResult で返す。"""
        tmpl = get_template(template_id)
        if tmpl is None:
            return ServiceResult.free(
                content=None,
                hint=f"テンプレートが見つかりません: {template_id}",
            )
        return ServiceResult.free(content=tmpl)

    def form_defaults(self, template_id: str) -> ServiceResult:
        """フォームデフォルト値を ServiceResult で返す。"""
        form = get_form_defaults(template_id)
        if form is None:
            return ServiceResult.free(
                content=None,
                hint=f"テンプレートが見つかりません: {template_id}",
            )
        return ServiceResult.free(content=form)

    def categories(self) -> ServiceResult:
        return ServiceResult.free(content=get_categories())

    def part(self, filename: str) -> ServiceResult:
        """_parts/ 部品を ServiceResult で返す。"""
        data = get_part(filename)
        if data is None:
            return ServiceResult.free(
                content=None,
                hint=f"部品ファイルが見つかりません: {filename}",
            )
        return ServiceResult.free(content=data)

    def _run_api(self, **_: object) -> ServiceResult:
        """TODO: ベクトル類似検索 (未実装)。"""
        return ServiceResult.not_implemented(ServiceMode.API)


# グローバルシングルトン
template_service = TemplateService()
