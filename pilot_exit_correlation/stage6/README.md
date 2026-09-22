# Stage 6: cut-off risk versus council finances

This is a descriptive public-finance comparison. It asks whether NSW councils whose towns were ever fully cut off by fire have weaker finances in 2018-19 (own-source revenue share as the primary measure).

Read `PREREGISTRATION.md`, `RESULTS.md`, `DEVIATIONS.md` and `RUN_LOG.md`.

```bash
uv run --no-sync --with matplotlib python pilot_exit_correlation/stage6/run_stage6.py
```

```bash
.venv/bin/python pilot_exit_correlation/stage6/tests/test_stats6.py
```

Outputs: `out/council_table.csv`, `out/stage6_results.csv`, `out/stage6_sensitivity.csv`, `out/council_finance_by_group.png`, `out/run_meta.json`.
