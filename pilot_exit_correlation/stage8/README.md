# Stage 8: did towns cut off in Black Summer change differently, 2016 to 2021? (exploratory)

This stage compares 2016 to 2021 Census change (population, income, jobs) in towns fully cut off by Black Summer fires against towns that were burned but not cut off. Towns are linked across Censuses by boundary overlap (IoU >= 0.7).

Read `PREREGISTRATION.md`, `RESULTS.md`, `DEVIATIONS.md` and `RUN_LOG.md`.

```bash
uv run --no-sync --with matplotlib python pilot_exit_correlation/stage8/run_stage8.py
```

It needs the two ABS downloads listed in `RUN_LOG.md`, placed in `../data/`.

Outputs: `out/town_change_2016_2021.csv`, `out/stage8_results.csv`, `out/change_by_group.png`, `out/run_meta.json`.
