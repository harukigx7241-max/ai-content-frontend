"""
app/db/migrations.py — 起動時簡易カラムマイグレーション

設計方針:
  - 既存カラムの "already exists" / "duplicate column" エラーは DEBUG で記録 (正常動作)
  - それ以外の例外は WARNING で記録し、起動は継続する (非致命的扱い)
  - 無言で握りつぶさない: 全ての結果をログに残す
  - 将来 Alembic へ移行する場合は:
      1. このファイルの COLUMN_MIGRATIONS を alembic/versions/ に変換する
      2. bootstrap_db() 内の run_migrations() 呼び出しを alembic upgrade head に置き換える
      3. このファイルは削除してよい

TODO: Phase N+ 破壊的変更 (カラム削除・型変更) が発生した場合は
      Alembic または専用の down-migration 手順を整備すること。
"""
import logging
from typing import NamedTuple

from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

# "すでに存在するカラム" を示す SQLite エラー文字列 (小文字で比較)
_ALREADY_EXISTS_MARKERS = ("duplicate column", "already exists")


class _Migration(NamedTuple):
    name: str   # ログ識別用ラベル (例: "users.bio")
    sql: str    # 実行する DDL 文


# ── カラム追加マイグレーション一覧 ────────────────────────────────────
# 追加した Phase を先頭コメントで示すことで、将来 Alembic 変換時の履歴が追いやすい。
COLUMN_MIGRATIONS: list[_Migration] = [
    # Phase 4 delta
    _Migration("users.bio",   "ALTER TABLE users ADD COLUMN bio   TEXT"),
    _Migration("users.xp",    "ALTER TABLE users ADD COLUMN xp    INTEGER NOT NULL DEFAULT 0"),
    _Migration("users.level", "ALTER TABLE users ADD COLUMN level INTEGER NOT NULL DEFAULT 1"),
    # Phase 7 second pass
    _Migration("xp_events.related_entity_type",
               "ALTER TABLE xp_events ADD COLUMN related_entity_type VARCHAR(50)"),
    _Migration("xp_events.related_entity_id",
               "ALTER TABLE xp_events ADD COLUMN related_entity_id   INTEGER"),
    # Phase 8
    _Migration("users.invited_by_user_id",
               "ALTER TABLE users ADD COLUMN invited_by_user_id INTEGER"),
    # Phase 9
    _Migration("feedback.priority",
               "ALTER TABLE feedback ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium'"),
    # admin bootstrap
    _Migration("users.must_change_password",
               "ALTER TABLE users ADD COLUMN must_change_password BOOLEAN NOT NULL DEFAULT 0"),
    # Like/Save system
    _Migration("community_posts.like_count",
               "ALTER TABLE community_posts ADD COLUMN like_count INTEGER NOT NULL DEFAULT 0"),
    _Migration("community_posts.save_count",
               "ALTER TABLE community_posts ADD COLUMN save_count INTEGER NOT NULL DEFAULT 0"),
    # Phase 9 — Fork/Remix
    _Migration("community_posts.remix_count",
               "ALTER TABLE community_posts ADD COLUMN remix_count INTEGER NOT NULL DEFAULT 0"),
    _Migration("community_posts.forked_from_id",
               "ALTER TABLE community_posts ADD COLUMN forked_from_id INTEGER"),
]


def run_migrations(engine: Engine) -> None:
    """
    COLUMN_MIGRATIONS を順番に実行する。

    結果の分類:
      ok      — カラムが新規追加された (INFO)
      skip    — カラムが既に存在する  (DEBUG, 正常動作)
      warning — 想定外の例外が発生した (WARNING, 起動は継続)
    """
    ok = skipped = warned = 0
    with engine.connect() as conn:
        for m in COLUMN_MIGRATIONS:
            try:
                conn.execute(text(m.sql))
                conn.commit()
                logger.info("migration ok: %s", m.name)
                ok += 1
            except Exception as exc:
                exc_lower = str(exc).lower()
                if any(marker in exc_lower for marker in _ALREADY_EXISTS_MARKERS):
                    logger.debug("migration skip (already exists): %s", m.name)
                    skipped += 1
                else:
                    logger.warning(
                        "migration warning [%s]: unexpected error — %s",
                        m.name, exc,
                    )
                    warned += 1

    logger.info(
        "migrations complete: %d added, %d skipped, %d warnings",
        ok, skipped, warned,
    )
