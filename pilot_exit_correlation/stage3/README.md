# Stage 3: stricter checks on the pooled result

Stage 3 runs two checks on the stage-2 finding:
- **3a** counts only roads cut **outside** the town.
- **3b** uses satellite fire detections (DEA Hotspots) to test whether fire reached every exit road within 12 hours.

Read `PREREGISTRATION.md` (frozen and committed before any result), then `RESULTS.md`, `DECISIONS.md`, `DEVIATIONS.md` and `RUN_LOG.md`.

## Run

From the repository root:

```bash
uv run --no-sync --with matplotlib python pilot_exit_correlation/stage3/run_stage3.py
```

- The first run downloads hotspots for the 12 fire events that cut a town off in the satellite era (about 590,000 detections) into `data/hotspots/`, which is git-ignored.
- Later runs use that cache, verify its SHA-256 against the manifest, and never re-query.
- The runtime is about 3 minutes once cached.

Tests (synthetic fixtures only):

```bash
.venv/bin/python pilot_exit_correlation/stage3/tests/test_timing.py
```

## Inputs

- The same hash-verified inputs as stage 2.
- DEA Hotspots WFS `public:hotspots` (Geoscience Australia; public, no account). Every query URL, row count and file hash is in `out/hotspot_manifest.csv`.

## Outputs (`out/`)

- `stage3_results.csv`: every ratio with its CI, with verdicts on the pre-registered rows.
- `timing_pairs.parquet`: for each full cut-off, the exits dated, the first hit and the hours between the first and last exit hit.
- `hotspot_manifest.csv`, `run_meta.json`
- `stage3_ratio_forest.png`, `cutoff_timing_hist.png`

## Code

- `run_stage3.py`: orchestration. It reuses the stage-1 `src` and stage-2 `s2` modules unchanged.
- `s3/hotspots.py`: paged WFS download with a frozen cache.
- `s3/timing.py`: exit hit times and the simultaneity rule.
- `s3/report.py`: RESULTS.md and the figures.
