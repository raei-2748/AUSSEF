# Judgment calls: stage 2

| # | Date | Decision | Reason |
|---|---|---|---|
| E1 | 2026-09-21 | Pass rule: R ≥ 2 and lower 95% bound > 1. | User decision. |
| E2 | 2026-09-21 | Part B uses the local Geoscience Australia historical boundaries (`ga_original.zip`), read directly from the zip. | User decision. The zip hash `715907c1…` matches `dataset_phase1/data/source_provenance.csv` (downloaded 2026-09-16 from GA product 149017). |
| E3 | 2026-09-21 | Part B window is ignition 1950-07-01 to 2019-06-30. | Part A starts 2019-07; the window keeps the two samples disjoint. Pre-1950 records are sparse. |
| E4 | 2026-09-21 | Undated records (8,954 with no date information) are dropped from the primary test and used as a sensitivity only. | They cannot be placed inside the window, and some could overlap part A. The plan originally said "undated as single events"; this was refined before pre-registration after profiling the date fields. |
| E5 | 2026-09-21 | Season-composite records (1,217, 16% of burned area) are never used. | One shape per season would create artificial simultaneous closure. |
| E6 | 2026-09-21 | Exits and paths are reused from stage-1 outputs, not recomputed. | Stage 1 reproduced them byte-identically across two runs, and reuse keeps the exits fixed across stages. |
| E7 | 2026-09-21 | p̂ is not smoothed in the pooled ratio. | With independent exits, E is unbiased for O, and smoothing caused the stage-1 inflation. |
| E8 | 2026-09-21 | Bootstrap unit is the fire event (family), resampled globally. | One megafire affects many neighbouring towns, so resampling towns would understate uncertainty. |
| E9 | 2026-09-21 | An isolation BFS runs only when every stored exit path is closed. | Isolation implies all exits are closed (a stage-1 invariant), so this is exact and much faster. |
