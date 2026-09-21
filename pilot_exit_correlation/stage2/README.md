# Stage 2: pooled exit-failure test

Stage 2 pools all towns into one test, instead of testing each town separately as stage 1 did.
- **Part A** re-tests the 2019–23 fires.
- **Part B** is an independent re-test on NSW historical bushfires, 1950–2019.
- `TIMING_SCOPING.md` scopes step 3, which checks timing with satellite data.

Read `PREREGISTRATION.md` (frozen before any result), then `RESULTS.md`, `DECISIONS.md`, `DEVIATIONS.md` and `RUN_LOG.md`.

## Run

From the repository root:

```bash
uv run --no-sync --with matplotlib python pilot_exit_correlation/stage2/run_stage2.py
```

Post-hoc descriptive diagnostics (not pre-registered). These write `out/diagnostic_*.csv`; afterwards, regenerate RESULTS.md:

```bash
uv run --no-sync --with matplotlib python pilot_exit_correlation/stage2/diagnostics.py
```

```bash
uv run --no-sync --with matplotlib python pilot_exit_correlation/stage2/s2/report.py
```

Tests (synthetic fixtures only):

```bash
.venv/bin/python pilot_exit_correlation/stage2/tests/test_pooled.py
```

- Seed: 20260921, with 1,000 bootstrap resamples of whole fire events.
- Runtime: see `out/run_meta.json`. Loading the historical perimeters alone takes about 2.5 minutes per variant.

## Inputs (read-only, SHA-256 verified on every run)

- **All stage-1 inputs**, listed in `../RUN_LOG.md`: the 2019 network, the transport DB overlay and families, GA event perimeters, and the ABS UCL boundaries and population.
- **GA historical bushfire boundaries:** `…/dataset_phase1/raw/ga_original.zip`, layer `Bushfire_Boundaries_Historical`, EPSG:4283, reprojected to EPSG:3577. Its hash matches the earlier download record.
- **Stage-1 outputs**, reused as fixed inputs: `../out/exit_paths.parquet` and `../out/community_results.parquet`.

## Outputs (`out/`)

- `pooled_results.csv`: one row per part × rule × ring radius, giving observed and expected full cut-offs, R with its 95% CI, the "all cut given one cut" shares, and the verdict for the primary rows.
- `community_level.parquet`: per-town counts behind the pooled numbers.
- `pooled_ratio_forest.png`, `all_given_any.png`
- `run_meta.json`: hashes, part-B record counts, the overlay cross-check and the runtime.

## Code

- `run_stage2.py`: orchestration. It imports the stage-1 `src` package for inputs, exits and closure.
- `s2/historical.py`: reads the historical fires, removes composites and applies the window, groups fires into families, and builds the S0/S100 road-closure overlay.
- `s2/pooled.py`: the pooled ratio and the fire-event bootstrap.
- `s2/report.py`: RESULTS.md and the figures.
