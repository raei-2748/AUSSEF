# Stage 10: were the roads really closed, how long was the escape window, and what did isolation cost?

- Checks the fire-outline closure rule against TfNSW traffic counters.
- Restates the escape window.
- Measures short-run disruption to traffic and freight near Black Summer fires.
- Applies a pre-set go/no-go gate for a council finance model.

Read `PREREGISTRATION.md`, `RESULTS.md`, `DEVIATIONS.md` and `RUN_LOG.md`.

```bash
uv run --no-sync --with matplotlib python pilot_exit_correlation/stage10/run_stage10.py
```

```bash
.venv/bin/python pilot_exit_correlation/stage10/tests/test_stage10.py
```

Uses the raw traffic tables in `aussef.duckdb` (user-approved; fingerprinted each run).

Outputs: `out/closure_validation_pairs.csv`, `out/closure_validation_summary.csv`, `out/escape_window.csv`, `out/corridor_disruption.csv`, `out/corridor_disruption_totals.csv`, `out/fiscal_index.csv`, figures, `out/run_meta.json`.
