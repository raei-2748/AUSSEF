# Stage 5: checking against real road-closure records

Descriptive only (no pass/fail). It matches the 2019-20 inferred cut-offs to the 37 curated closure records in `transport_criticality.duckdb` (`analysis.road_closure_candidates`).

Read `PREREGISTRATION.md`, `RESULTS.md` and `DEVIATIONS.md`.

```bash
.venv/bin/python pilot_exit_correlation/stage5/run_stage5.py
```

Outputs: `out/cutoff_record_summary.csv`, `out/exit_record_matches.csv`, `out/run_meta.json`.
