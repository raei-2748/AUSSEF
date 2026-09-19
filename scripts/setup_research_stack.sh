#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required: https://brew.sh/" >&2
  exit 1
fi
if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required: https://docs.astral.sh/uv/" >&2
  exit 1
fi

if ! brew list --formula duckdb >/dev/null 2>&1; then
  brew install duckdb
fi
if ! brew list --formula dvc >/dev/null 2>&1; then
  brew install dvc
fi
if ! brew list --formula python@3.13 >/dev/null 2>&1; then
  brew install python@3.13
fi
if ! brew list --cask dbeaver-community >/dev/null 2>&1; then
  brew install --cask dbeaver-community
fi

if ! command -v quarto >/dev/null 2>&1; then
  echo "Quarto is not on PATH. Install it from https://quarto.org/ or place it at ~/.local/bin/quarto." >&2
  exit 1
fi

if [ ! -x "$ROOT/.venv/bin/python" ]; then
  uv venv --python 3.13 "$ROOT/.venv"
fi
uv sync --frozen

"$ROOT/.venv/bin/python" -m ipykernel install --user --name aussef-research --display-name "AUSSEF Research (Python 3.13)" >/dev/null

DUCKDB_BIN="$(brew --prefix duckdb)/bin/duckdb"
"$DUCKDB_BIN" "$ROOT/data/aussef.duckdb" -c "INSTALL spatial; LOAD spatial; SELECT extension_name, loaded FROM duckdb_extensions() WHERE extension_name = 'spatial';"
"$ROOT/.venv/bin/python" "$ROOT/scripts/export_parquet.py"
"$ROOT/.venv/bin/python" "$ROOT/scripts/validate_stack.py" --write-report

echo "AUSSEF research stack is ready."
