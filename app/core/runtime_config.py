"""
app/core/runtime_config.py — ランタイム可変設定ストア

管理者がダッシュボードから変更した設定をインメモリで保持する。
DB に永続化されているため、app 再起動後も load_from_db() で復元できる。

設計方針:
  - シンプルな str キー / str 値の dict
  - 読み書きは get / set_value で行う
  - bool 値は "true" / "false" 文字列で保持し get_bool() で変換
  - DB の system_settings テーブルと常に同期する
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# 設定キー定数
KEY_MAINTENANCE_ENABLED = "maintenance_enabled"
KEY_MAINTENANCE_MESSAGE = "maintenance_message"
KEY_NOTICE_BANNER_ENABLED = "notice_banner_enabled"
KEY_NOTICE_BANNER_TEXT = "notice_banner_text"
KEY_NOTICE_BANNER_LINK = "notice_banner_link"

_store: dict[str, str] = {}


def get(key: str, default: str = "") -> str:
    return _store.get(key, default)


def get_bool(key: str, default: bool = False) -> bool:
    val = _store.get(key)
    if val is None:
        return default
    return val.lower() == "true"


def set_value(key: str, value: str) -> None:
    _store[key] = value


def load_from_db(db: "Session") -> None:
    """
    アプリ起動時に DB から設定を読み込む。
    DB が未作成 (初回起動) の場合はスキップする。
    """
    try:
        from app.db.models.system_setting import SystemSetting
        rows = db.query(SystemSetting).all()
        for row in rows:
            _store[row.key] = row.value
    except Exception:
        pass  # テーブル未作成時 (初回起動) は無視
