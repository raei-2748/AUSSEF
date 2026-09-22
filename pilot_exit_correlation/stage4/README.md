# Stage 4: timing near the town

Stage 4 repeats the stage-3 satellite timing check, but dates each exit road by when fire reached it
within about 5 km of the town, instead of anywhere along its 20 km route. It is a follow-up motivated
by the stage-3 results. Read `PREREGISTRATION.md`, `RESULTS.md`, `DEVIATIONS.md` and `RUN_LOG.md`.

```bash
uv run --no-sync --with matplotlib python pilot_exit_correlation/stage4/run_stage4.py
```

```bash
.venv/bin/python pilot_exit_correlation/stage4/tests/test_near_town.py
```

- The run uses the frozen stage-3 hotspot cache (hash-verified) and makes no network requests.
- It takes about 3 minutes.
- It reuses stage-3 helpers from `../stage3/run_stage3.py` without changing them.

Outputs in `out/`:
- `stage4_results.csv`
- `timing_pairs_near_town.parquet` (near-town and whole-route timing for each cut-off)
- `timing_near_town_vs_route.png`
- `run_meta.json`
