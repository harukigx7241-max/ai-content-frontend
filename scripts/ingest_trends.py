#!/usr/bin/env python3
"""
scripts/ingest_trends.py — 傾向収集 CLI スクリプト (Phase 15)

使用例:
  python scripts/ingest_trends.py              # 全ワークショップ
  python scripts/ingest_trends.py --workshop note
  python scripts/ingest_trends.py --workshop note --triggered-by cron

cron / systemd timer から呼び出されることを想定している。
アプリサーバーが起動していなくても動作する (直接サービスクラスを呼ぶ)。
"""

import argparse
import sys
import pathlib

# プロジェクトルートを sys.path に追加
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from app.services.trend_ingestion_service import trend_ingestion_service, WORKSHOPS  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="傾向収集スクリプト")
    parser.add_argument(
        "--workshop",
        choices=WORKSHOPS + ["all"],
        default="all",
        help="対象ワークショップ (デフォルト: all)",
    )
    parser.add_argument(
        "--triggered-by",
        default="cron",
        help="トリガー識別子 (デフォルト: cron)",
    )
    args = parser.parse_args()

    triggered_by = args.triggered_by
    workshop = args.workshop if args.workshop != "all" else None

    print(f"[trend_ingest] 傾向収集開始: workshop={workshop or 'all'}, triggered_by={triggered_by}")

    if workshop:
        result = trend_ingestion_service.run_for_workshop(workshop, triggered_by)
        data = result.content or {}
        if result.available:
            print(f"  ✅ {workshop}: {data.get('message', 'OK')}")
        else:
            print(f"  ❌ {workshop}: {data.get('message', 'Failed')}", file=sys.stderr)
            return 1
    else:
        result = trend_ingestion_service.run_all(triggered_by)
        data = result.content or {}
        ok = data.get("success_count", 0)
        total = data.get("total", 0)
        print(f"  完了: {ok}/{total} ワークショップ成功")
        for r in data.get("results", []):
            mark = "✅" if r.get("success") else "❌"
            print(f"  {mark} {r['workshop']}: {r.get('message', '')}")
        if ok < total:
            return 1

    print("[trend_ingest] 完了")
    return 0


if __name__ == "__main__":
    sys.exit(main())
