# AUSSEF

Research on disasters, local-government finance and infrastructure in New South Wales.

## Start here

- [Canonical data model](data/README.md)
- [Research stack setup](docs/research-stack.md)
- [Experiment 1 — fiscal forecasting](Experiment%201/README.md)
- [Experiment 2 — longer matched history](Experiment%202/README.md)
- [Experiment 3 — crowd-out measurement](Experiment%203/README.md)
- [Experiment 4 — quarterly budget revisions](Experiment%204/README.md)

Each experiment retains its notebook, code, audits and results. Cleaned structured data is consolidated in the canonical DuckDB model under `data/`.

## Repository map

```text
data/                canonical DuckDB model and build receipt
schemas/             Pandera validation schemas for canonical tables
scripts/             reproducible export, setup and verification scripts
docs/                concise stack and workflow documentation
NSW Data Panel.csv   frozen source panel
Experiment 1/        first forecasting test
Experiment 2/        extended panel and exposure construction
Experiment 3/        outcome-measurement feasibility study
Experiment 4/        current budget-reallocation pilot
generated/           generated graph index and cache
```

The `code/` folders contain scripts. `data/` contains source or derived tables. `results/` contains saved outputs. `audit/`, `archive/` and `related/` contain supporting or historical material.

The reproducible environment is declared in `pyproject.toml` and locked by
`uv.lock`. Parquet/GeoParquet derivatives are generated from
`data/aussef.duckdb`; source files and saved results remain untouched.

## Research boundaries

- No data or evidence files are deleted during organisation changes.
- Missing is kept distinct from zero, unavailable and not applicable.
- Saved results are descriptive unless a README explicitly says otherwise.
- The current research position is a measurement-first pilot; no unsupported causal or predictive claim is promoted to a result.
