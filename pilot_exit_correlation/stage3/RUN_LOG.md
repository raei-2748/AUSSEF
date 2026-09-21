# Run log: stage 3

Inputs are the same frozen, hash-verified inputs as stage 2 (see `../RUN_LOG.md` and `../stage2/RUN_LOG.md`).

- **New input:** DEA Hotspots detections, downloaded on the first run into `data/hotspots/` (git-ignored).
  - Each event's query URL, row count, download time and SHA-256 are in `out/hotspot_manifest.csv`.
  - Later runs verify those hashes and never re-query.
- `aussef.duckdb` SHA-256 at start: `ce294c7ef50964b334a13d83b627f0732e35d2237c70ddf7ce3a26b06f1cba59`.

## Run entries

- 2026-09-21T22:31:29+00:00: run complete in 165.9 s; all input hashes matched; aussef.duckdb unchanged (ce294c7ef509…); 3a A: **FAIL** (R = 6.65); 3a B: **PASS** (R = 13.79); 3b satellite er: **FAIL** (R = 6.91).

- 2026-09-21T22:35:09+00:00: run complete in 164.9 s; all input hashes matched; aussef.duckdb unchanged (ce294c7ef509…); 3a A: **FAIL** (R = 6.65); 3a B: **PASS** (R = 13.79); 3b satellite er: **FAIL** (R = 6.91).
