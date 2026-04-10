"""
app/admin/analytics.py — 管理者向け分析サービス (スタブ)

このファイルは Phase 3 での受け皿として作成。
現時点では generation_log / post_log / invite_log テーブルが存在しないため
すべてスタブ実装になっている。

将来の拡張ポイント:
  - Phase N+: generation_log テーブルが実装されたら summarize_user / aggregate_daily を本実装する
  - Phase N+: posts テーブルが実装されたら get_post_stats を本実装する
  - Phase N+: invite_code テーブルが実装されたら get_invite_stats を本実装する
  - Phase N+: report テーブルが実装されたら get_report_summary を本実装する

利用方法:
  from app.admin.analytics import summarize_user
  usage = summarize_user(db, user_id=42)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def summarize_user(db: "Session", user_id: int) -> dict:
    """
    ユーザーの利用サマリーを返す。
    TODO: Phase N+ generation_log から generation_count, last_active, favorite_category を集計する
    """
    return {
        "generation_count": 0,
        "last_active": None,
        "favorite_category": None,
    }


def aggregate_daily(db: "Session", days: int = 30) -> list[dict]:
    """
    日次の生成回数推移を返す。
    TODO: Phase N+ generation_log から集計する
    例: [{"date": "2026-04-01", "count": 42}, ...]
    """
    return []


def get_post_stats(db: "Session") -> dict:
    """
    投稿（公開広場）の集計を返す。
    TODO: Phase N+ posts テーブル実装後に本実装する
    """
    return {"total_posts": 0, "published": 0, "draft": 0}


def get_invite_stats(db: "Session") -> dict:
    """
    招待コードの利用状況を返す。
    TODO: Phase N+ invite_code テーブル実装後に本実装する
    """
    return {"total_codes": 0, "used": 0, "expired": 0}


def get_report_summary(db: "Session") -> dict:
    """
    通報・モデレーション状況を返す。
    TODO: Phase N+ report テーブル実装後に本実装する
    """
    return {"open": 0, "resolved": 0}
