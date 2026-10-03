# Canonical AUSSEF data

[`aussef.duckdb`](aussef.duckdb) is the single maintained DuckDB database for AUSSEF structured data. It deliberately separates source-preserving landing tables from cleaned research tables.

Build or rebuild it from the repository root with:

```text
python3 data/build_aussef_duckdb.py
```

The build is atomic and writes a verification receipt to [`checks/aussef_build_manifest.json`](checks/aussef_build_manifest.json). Every declared CSV input is retained in `raw` with all source columns stored as text and with stable source-row lineage. Canonical inputs feed the typed, cleaned `master` layer; large manual mobility/traffic files and Experiment 4B-A audit tables are deliberately `raw`-only until a separate data contract validates promotion. Registered PDFs, HTML files and other external evidence remain in their original locations; their hashes are verified during each build and they are never modified.

## Database layout

| Schema | Purpose |
|---|---|
| `raw` | Source-preserving, all-text landing copies of every declared CSV input, plus table and registered-file manifests. No cleaning or entity resolution. |
| `master` | Canonical dimensions and facts: councils, disasters, exposure, fiscal observations, projects, budgets, revisions, evidence and timing records. |
| `provenance` | Input-file hashes, row counts, source paths and document/source keys. |
| `experiments` | Views only. Each experiment view is derived from `master`; no experiment database or copied experiment table is maintained. |
| `metadata` | Build policy, object counts, view dependencies and repository-wide structured-file inventory. |
| `archive` | Exact byte-preserving copies of every catalogued structured file that is not already represented by a declared `raw` table. These are preserved for recovery/future research, not certified as clean. |

`metadata.dataset_inventory` catalogues every structured file currently visible in the repository, including loaded inputs, audit/model outputs, snapshots, spreadsheets, Parquet files and historical stores. `archive.structured_file_manifest` proves whether each file is represented by a queryable raw table or by an exact embedded blob. A file being preserved does not certify it as a canonical input.

Stable keys are deterministic and source-bounded:

- `council_id` hashes the exact normalized council label. `master.council_aliases` retains every observed source label/key, so variants are not silently merged.
- `disaster_id` uses AGRN when present and otherwise the exact reported label. Source variants remain in `master.disaster_sources`.
- `project_id` uses an explicit source project identifier when available; legacy program rows remain source-scoped when no certified cross-document identifier exists.
- `source_key` identifies the hashed input file or registered document; `source_record_key` identifies the row within that source.

The expanded evidence register is available as `master.evidence_records` and the view `experiments.experiment_4_evidence_register`. Its 244 rows are preserved with exact-only council/project resolution; unresolved project references remain unresolved, and the source `model_ready` values are not promoted.

The former SQLite stores and any local legacy model bundle are preserved as historical files. They are not canonical build targets. No data is deleted by this consolidation.

## Raw versus cleaned data

- Query `raw.<input_name>` when you need the imported source cells exactly as supplied. The builder adds only `source_row_number` and `source_key`.
- Query `master.<table_name>` for cleaned, typed and linked research data.
- Query `experiments.<view_name>` for experiment-specific cohorts and derived fields.
- `raw.table_manifest` proves that every declared input row was retained.
- `raw.registered_source_files` records the existence and SHA-256 verification result for each locally registered evidence file. Binary documents are catalogued, not embedded as database blobs.
- `metadata.dataset_inventory` makes files that are intentionally not loaded visible, with a class and inclusion status. Derived results and backups are not duplicated into `raw`.
- `archive.structured_file_blobs` stores the exact bytes of every other catalogued structured file, including CSV/JSON/GeoJSON/Parquet/spreadsheet/map/database formats. Use `archive.structured_file_manifest` to check the source hash, embedded hash and preservation status.

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
