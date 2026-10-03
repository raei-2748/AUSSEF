# Experiment 7, Day 7: SA2 unemployment (unsmoothed), welfare and businesses

Date: 1 Oct 2026. Rules locked before download: `PRESPEC_DAY7.md` (LOCK_DAY7.txt). Run as a workflow: one agent per
dataset (download, panel, pre-registered model), then an independent auditor that re-derived each result.
Downloads (official sources, logged in `results/DAY7_DOWNLOADS.csv`): DEWR SALM unsmoothed SA2 (2.6 MB),
DSS payment demographics by SA2 (several quarterly files), ABS CABEE SA2 cubes (5 releases).
Scripts: `day7_U_unemployment.py`, `day7_W_welfare.py`, `day7_B_businesses.py`; results `results/DAY7_U/W/B.json`.

## Results (per 10 percentage points of an SA2's residents living within 1 km of a fire)
| Outcome | Estimate | 95% CI | Placebo (future fires) | Verdict |
|---|---|---|---|---|
| Unemployment rate, unsmoothed (fire quarter + next 4) | -0.002 pts | -0.040 to +0.035 | +0.038 [+0.001, +0.075], marginal fail | Not detected |
| Income-support recipients per 1,000 | +0.21 | -0.04 to +0.45 | +0.18 [-0.01, +0.37] | Not detected |
| Business count (sum of the two Junes after) | +0.1% | -1.3% to +1.6% | -0.3% [-1.5%, +0.9%] | Not detected |

All three audits reproduced the numbers independently; no bugs changed results.

## What the data rule out (an SA2 where everyone lived within 1 km of fire = 10 × the per-10pp numbers)
- Unemployment rising more than about 0.35 points.
- Income-support claims rising more than about 4.5 per 1,000 residents (about 4.6% of the average level).
- Business numbers falling more than about 13% over two years (about 6.6% a year if persistent).

## Caveats
- Welfare: lead coefficients are as large as lag coefficients, so affected areas were already drifting up
  (plus the DSS method break in Dec 2022 and COVID JobSeeker in 2020). Treat as "no fire effect visible".
- Black Summer alone: unemployment in affected SA2s was already rising before the fires (placebo fails strongly),
  so a Black Summer-only estimate cannot be read as a fire effect.
- "Heavy" and "Black Summer only" subsets were defined by the agents (the prespec named but did not define them).

## Bottom line
At small-area level too, income (Day 5), unemployment, welfare and business numbers show no measurable fire
effect, with tight upper limits. Bushfire socioeconomic damage beyond lost homes is small relative to normal
variation even where most residents were near the fire.
