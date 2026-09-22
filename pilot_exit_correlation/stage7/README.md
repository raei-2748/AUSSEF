# Stage 7: who lives in towns that get fully cut off?

This stage is descriptive. It compares 2021 Census vulnerability (age 65+, no car, need for assistance, income) in towns fires have fully cut off against other towns, and links each council's own-source revenue to its vulnerable residents in cut-off towns.

Read `PREREGISTRATION.md`, `RESULTS.md`, `DEVIATIONS.md` and `RUN_LOG.md`.

```bash
uv run --no-sync --with matplotlib python pilot_exit_correlation/stage7/run_stage7.py
```

Outputs: `out/town_vulnerability.csv`, `out/stage7_results.csv`, `out/council_vulnerability_finance.csv`, `out/vulnerability_by_group.png`, `out/run_meta.json`.
