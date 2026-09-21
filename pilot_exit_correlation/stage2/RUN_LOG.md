# Run log: stage 2

## 2026-09-21: frozen inputs (in addition to the stage-1 baseline in ../RUN_LOG.md)

| Input | Path | SHA-256 | Prior provenance |
|---|---|---|---|
| GA historical bushfire boundaries | `W/dataset_phase1/raw/ga_original.zip` | `715907c149e32e0917f2533639937f5716550783c11086428cc20d5dc143e9fa` | **matches** `W/dataset_phase1/data/source_provenance.csv` (GA product 149017) |
| Stage-1 exit paths | `../out/exit_paths.parquet` | `f6e2a81e291abac200898f7ca815b0eebee53199e33f45e82a5a37b08cc7df8a` | reproduced byte-identically by two stage-1 runs |
| Stage-1 community results | `../out/community_results.parquet` | `3c42ee2a0ff0e38afb05dd6dc197412ece9258d361de60a279a1ac9eb9234bee` | same |
| `aussef.duckdb` (not an input) | `data/aussef.duckdb` | `ce294c7ef50964b334a13d83b627f0732e35d2237c70ddf7ce3a26b06f1cba59` | unchanged since stage-1 Step 0 |

`W` = `/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0`

## Run entries

- 2026-09-21T13:19:18+00:00: run complete in 328.0 s; all input hashes matched; aussef.duckdb unchanged (ce294c7ef509…); part A: **FAIL** (R = 6.65); part B: **PASS** (R = 14.91).

- 2026-09-21T13:31:36+00:00: run complete in 320.0 s; all input hashes matched; aussef.duckdb unchanged (ce294c7ef509…); part A: **FAIL** (R = 6.65); part B: **PASS** (R = 14.91).
