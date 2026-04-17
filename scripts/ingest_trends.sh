#!/bin/bash
# scripts/ingest_trends.sh — 傾向収集シェルラッパー (Phase 15)
# systemd ExecStart や cron から呼び出す。
#
# 使用例:
#   ./scripts/ingest_trends.sh              # 全ワークショップ
#   ./scripts/ingest_trends.sh note         # note のみ
#   TRIGGERED_BY=cron ./scripts/ingest_trends.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="${PROJECT_ROOT}/.venv/bin/python"
PYTHON="${VENV_PYTHON:-python3}"

WORKSHOP="${1:-all}"
TRIGGERED_BY="${TRIGGERED_BY:-cron}"

cd "$PROJECT_ROOT"

echo "[ingest_trends.sh] 開始: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "  workshop=$WORKSHOP, triggered_by=$TRIGGERED_BY"

if [ "$WORKSHOP" = "all" ]; then
    "$PYTHON" scripts/ingest_trends.py --triggered-by "$TRIGGERED_BY"
else
    "$PYTHON" scripts/ingest_trends.py --workshop "$WORKSHOP" --triggered-by "$TRIGGERED_BY"
fi

echo "[ingest_trends.sh] 完了: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
