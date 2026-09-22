# Stage 9: does counting exits find the towns fire cuts off, and who pays?

Applies the published count-based exit measure (Fong et al., PNAS 2026) to NSW, checks it against 70 years of fires, profiles who lives in the towns it misses, and labels each exit road as State, Regional or local using the TfNSW categorisation.

Read `PREREGISTRATION.md`, `RESULTS.md`, `DECISIONS.md`, `DEVIATIONS.md` and `RUN_LOG.md`.

```bash
uv run --no-sync --with matplotlib python pilot_exit_correlation/stage9/run_stage9.py
```

```bash
.venv/bin/python pilot_exit_correlation/stage9/tests/test_stage9.py
```

Needs the TfNSW download listed in `RUN_LOG.md`, placed in `../data/` (git-ignored).

Outputs: `out/town_classification.csv`, `out/stage9_results.csv`, `out/cutoff_rate_by_bucket.csv`, `out/ownership_by_town.csv`, `out/council_capacity.csv`, `out/cutoff_rate_by_exits.png`, `out/who_lives_in_blind_spot.png`, `out/run_meta.json`.
