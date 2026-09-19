#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PATH="$ROOT/.venv/bin:$PATH"

uv run python scripts/export_parquet.py
uv run python scripts/validate_stack.py --write-report
quarto render reports/stack_smoke.qmd --execute-dir "$ROOT" >/dev/null
dvc status

echo "End-to-end research-stack verification passed."
