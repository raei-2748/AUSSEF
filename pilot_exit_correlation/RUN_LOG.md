# Run log: correlated-exit-failure pilot

## 2026-09-21: Step 0 inventory and frozen input baseline

Repository commit at start: `13d8176236a6201ec11e8a15b4b07d9336b7cfc7` (working tree has uncommitted data-build changes).
Machine: Apple M2 Pro, 16 GiB RAM. Python 3.13.7 (`.venv`).

### Canonical AUSSEF database (not a pilot input; recorded as required)

| File | SHA-256 | Bytes |
|---|---|---:|
| `data/aussef.duckdb` | `ce294c7ef50964b334a13d83b627f0732e35d2237c70ddf7ce3a26b06f1cba59` | 1,630,810,112 |

The database was opened read-only for the inventory. It holds no road network, fire footprints,
fire × road overlay or community boundaries. The transport DB's `analysis.input_hashes` records
an older `aussef.duckdb` hash (`af213a27…`, 39,333,888 bytes), which no longer matches because the
canonical DB has been rebuilt since.

### Pilot inputs (frozen baseline; verified by `run_pilot.py` on every run)

`W` = `/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0`

| Input | Path | SHA-256 | Prior provenance |
|---|---|---|---|
| 2019-01-01 OSM snapshot (source of network) | `data/Manual/australia-190101.osm.pbf` | `77f32fdfeee3074273aceb726ed2e27c23954d3e3bc065d11ae78e8d353efbd1` | **matches** `analysis.supplementary_input_hashes` |
| Fire event perimeters (Geoscience Australia) | `W/dataset_phase1/data/event_perimeters.gpkg` | `75fb91a17a6ce65c44a34ccc8e0f2350151e38201ef715feecb5c26c6efb542c` | **matches** `W/bushfire_lga_season/outputs/additional_input_manifest.csv` |
| Road network edges (derived from PBF) | `W/transport_criticality_experiment/inputs/network_fingerprint.parquet` | `5d6049c30fcb63f66c21b3cf75edbc5d542c05a4a385e07352d7668bc90a5026` | **none recorded**; baseline frozen today (user decision) |
| Transport DB (overlay + fire families) | `W/transport_criticality_experiment/transport_criticality.duckdb` | `b9779b309dcacb0a7b5c65168537e85e41c6c77b5e8c80e01e1e8e25f3bb3119` | **none recorded**; baseline frozen today (user decision) |

Tables used from the transport DB (read-only): `analysis.fire_road_exposure_v2` (21,712 rows),
`main.disaster_family_members` (1,226 rows, 1,034 families).

### Downloaded community inputs (approved by user 2026-09-21)

| File | Source URL | SHA-256 |
|---|---|---|
| `data/UCL_2021_AUST_GDA2020_SHP.zip` | https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/UCL_2021_AUST_GDA2020_SHP.zip | `dd913e44591b947f0cd9796210cc7ad7095028ccab2494e68cdbc78056e8b26e` |
| `data/2021_GCP_UCL_for_NSW_short-header.zip` | https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_GCP_UCL_for_NSW_short-header.zip | `19eca38d9d92c612d4083551535a53c730f30683205a16b26098235d17fc7aaf` |
| extracted `ucl_2021/UCL_2021_AUST_GDA2020.shp` | (from zip) | `c8b3902ca189abe7acf7676cf5339cd8673682a9a05a20592aad7d80fb937641` |
| extracted `2021Census_G01_NSW_UCL.csv` | (from zip) | `bded5c0201c9f92168db6497a239c8227ae68f4a3a643bc0c18971a29fa4374c` |

### Package versions

duckdb 1.5.5, networkx 3.6.1, geopandas 1.1.4, shapely 2.1.2, pyproj 3.8.0, numpy 2.5.3,
pandas 2.3.3, pyogrio 0.13.0, pyarrow 24.0.0. matplotlib is supplied per-run via
`uv run --with matplotlib` (not added to the project lock).

## Run entries

(Appended automatically by `run_pilot.py`.)

- 2026-09-21T12:23:36+00:00: run complete in 1082.8 s; all input hashes matched; aussef.duckdb unchanged (ce294c7ef509…); verdict **FAIL** (0/217 eligible).

- 2026-09-21T12:40:52+00:00: run complete in 931.8 s; all input hashes matched; aussef.duckdb unchanged (ce294c7ef509…); verdict **FAIL** (0/217 eligible).
