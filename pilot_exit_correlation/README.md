# Correlated-exit-failure pilot

This pilot measures whether a community's exit roads fail together in mapped fires more often than
independent failure would predict. It is a measurement pilot with a pre-registered decision rule.

**Stage 1**, in this folder, tests each town separately; its verdict was FAIL. **Stage 2**, in `stage2/`,
pools all towns and re-tests on historical fires. Start with `stage2/RESULTS.md`.
Read in this order: `PREREGISTRATION.md` (frozen), `RESULTS.md`, `DECISIONS.md`, `DEVIATIONS.md`, `RUN_LOG.md`.

## Run

From the repository root:

```bash
uv run --no-sync --with matplotlib python pilot_exit_correlation/run_pilot.py
```

`--no-sync` leaves the project `.venv` untouched, and `--with matplotlib` adds matplotlib for the plots
without changing `pyproject.toml` or `uv.lock`.

- Seed: 20260921. Each community's bootstrap stream comes from `SeedSequence([seed, UCL code, R, rule])`, so results do not depend on processing order.
- Runtime: about 18 minutes on an Apple M2 Pro (R = 20 km 4 min, 10 km 1 min, 30 km 13 min). The exact figure is in `out/run_meta.json`.
- To regenerate only RESULTS.md and the maps from saved outputs: `uv run --no-sync --with matplotlib python pilot_exit_correlation/src/report.py`
- Logic tests on toy graphs: `.venv/bin/python pilot_exit_correlation/tests/test_logic.py`

## Inputs (read-only, SHA-256 verified on every run)

| Input | Where | Table / layer |
|---|---|---|
| 2019-01-01 OSM road network, 1,451,892 edges, EPSG:3577 | `~/.codex/.chatgpt-projects/g-p-6a5b…/transport_criticality_experiment/inputs/network_fingerprint.parquet` | — |
| Fire-family × road-edge overlay (21,712 rows) | `…/transport_criticality_experiment/transport_criticality.duckdb` | `analysis.fire_road_exposure_v2` |
| Fire-family membership (1,034 families) | same DB | `main.disaster_family_members` |
| Fire perimeters (Geoscience Australia), EPSG:3577 | `…/dataset_phase1/data/event_perimeters.gpkg` | layer `event_perimeters` |
| ABS UCL 2021 boundaries (GDA2020) | `data/ucl_2021/` | downloaded 2026-09-21 |
| 2021 Census G01 population by UCL (NSW) | `data/gcp_ucl_nsw/` | `Tot_P_P` |

`data/aussef.duckdb` is not an input; it holds no spatial road or fire data. Its hash is checked
before and after each run to confirm the pilot never writes to it.

Versions: Python 3.13.7, duckdb 1.5.5, networkx 3.6.1, geopandas 1.1.4, shapely 2.1.2,
pyproj 3.8.0, numpy 2.5.3, pandas 2.3.3, pyarrow 24.0.0, matplotlib 3.11.2 (per-run overlay).

## Outputs (`out/`)

- `community_results.parquet` and `.csv`: one row per community × ring radius (10/20/30 km) × rule (S0/S100). Columns: population, exits, relevant fires, isolations, P_obs, P_ind, rho with bootstrap CI (also on the log10 scale), N_eff, excluded-exit counts, and eligibility flags. Missing values are empty or NaN, never 0.
- `exit_paths.parquet`: the stored path decomposition, as edge_ids per exit.
- `map_rho_S0_R20.png`, `map_exits_vs_neff_S0_R20.png`
- `run_meta.json`: hashes, counts, runtime and verdict.

## Method notes

- Exits are unit-capacity max-flow on the undirected graph, where parallel edges add capacity. The decomposition is min-cost max-flow by length, which gives one minimum-total-length set of edge-disjoint paths. Such decompositions are not unique.
- Isolation is tested on the whole community subgraph, not on the stored paths.

## Layout

`run_pilot.py` (orchestration) · `src/inputs.py` (hash-verified loading) · `src/exits.py` (graph, max-flow,
paths, isolation) · `src/closure.py` (S0/S100 closed sets) · `src/metrics.py` (rho, bootstrap, N_eff) ·
`src/report.py` (RESULTS.md and maps) · `tests/test_logic.py`.
