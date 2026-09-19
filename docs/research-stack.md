# AUSSEF research stack

The canonical data store is [`data/aussef.duckdb`](../data/aussef.duckdb).
Experiment objects are DuckDB views derived from that database; they are not
copied into separate experiment databases.

## Setup

From the repository root:

```bash
bash scripts/setup_research_stack.sh
```

The setup uses Homebrew for DuckDB, DVC and DBeaver Community, a user-local
Quarto installation, and `uv` for the pinned Python environment in `.venv`.
The Python environment contains DuckDB, Pandera, GeoPandas, PyArrow,
JupyterLab and the DVC Python client.

If the macOS Quarto installer requests administrator access, install Quarto
from [quarto.org](https://quarto.org/) or place its executable at
`~/.local/bin/quarto`, then rerun the setup.

## Data derivatives

```bash
uv run python scripts/export_parquet.py
```

This creates new derived files under `data/parquet/`:

- `master/` and `provenance/` contain one Parquet file per canonical base table.
- `geo/continuing_councils_2023.parquet` is a GeoParquet copy of the existing
  cleaned council geometry, retaining its CRS and adding source/provenance
  keys.
- `manifest.json` records row counts, hashes and source lineage.

Experiment views are intentionally not exported: they remain reproducible
DuckDB views over the master database.

## Validation and DVC

```bash
uv run python scripts/validate_stack.py --write-report
dvc repro
dvc status
```

Pandera validates the stable-key tables and lineage fields. The DVC pipeline
tracks the Parquet export and validation stage without replacing or deleting
the Git-tracked canonical DuckDB file. No DVC remote is assumed; configure a
remote before `dvc push` if the derivative cache should be shared.

## Tools

Open `data/aussef.duckdb` in DBeaver Community as a DuckDB database. In a
DuckDB or Python session, load the spatial extension with:

```sql
LOAD spatial;
```

Run the complete smoke test with:

```bash
bash scripts/verify_research_stack.sh
```
