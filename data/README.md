# Canonical AUSSEF data

[`aussef.duckdb`](aussef.duckdb) is the single maintained DuckDB database for cleaned AUSSEF structured data.

Build or rebuild it from the repository root with:

```text
python3 data/build_aussef_duckdb.py
```

The build is atomic and writes a verification receipt to [`checks/aussef_build_manifest.json`](checks/aussef_build_manifest.json). It reads only the cleaned CSV inputs declared in `data/build_aussef_duckdb.py`; raw downloads, PDFs and files under `raw/` or `sources/` are not build inputs and are not modified.

## Database layout

| Schema | Purpose |
|---|---|
| `master` | Canonical dimensions and facts: councils, disasters, exposure, fiscal observations, projects, budgets, revisions, evidence and timing records. |
| `provenance` | Input-file hashes, row counts, source paths and document/source keys. |
| `experiments` | Views only. Each experiment view is derived from `master`; no experiment database or copied experiment table is maintained. |
| `metadata` | Build policy, object counts and view dependencies. |

Stable keys are deterministic and source-bounded:

- `council_id` hashes the exact normalized council label. `master.council_aliases` retains every observed source label/key, so variants are not silently merged.
- `disaster_id` uses AGRN when present and otherwise the exact reported label. Source variants remain in `master.disaster_sources`.
- `project_id` uses an explicit source project identifier when available; legacy program rows remain source-scoped when no certified cross-document identifier exists.
- `source_key` identifies the hashed input file or registered document; `source_record_key` identifies the row within that source.

The expanded evidence register is available as `master.evidence_records` and the view `experiments.experiment_4_evidence_register`. Its 244 rows are preserved with exact-only council/project resolution; unresolved project references remain unresolved, and the source `model_ready` values are not promoted.

The former SQLite stores and any local legacy model bundle are preserved as historical files. They are not canonical build targets. No data is deleted by this consolidation.

## Research stack

Set up DuckDB Spatial, Parquet/GeoParquet, Pandera, DVC, Jupyter, GeoPandas,
PyArrow, DBeaver Community and Quarto with:

```bash
bash scripts/setup_research_stack.sh
```

Generate the additive Parquet derivatives and validate them with:

```bash
uv run python scripts/export_parquet.py
uv run python scripts/validate_stack.py --write-report
```

The DVC pipeline is defined in [`dvc.yaml`](../dvc.yaml). It tracks the
generated Parquet tree and validation receipt while leaving this canonical
DuckDB file and all existing inputs/results in place.
