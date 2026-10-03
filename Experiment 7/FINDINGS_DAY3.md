# Experiment 7, Day 3: the new Y and X (built), and whether fire weather helps

Date: 1 Oct 2026. Rules locked first: `PRESPEC_DAY3.md` (LOCK_DAY3.txt). Script: `day3_new_y_x.py`.
Table for modelling: `results/NEW_Y_X_TABLE.csv` (one row per council × fire, 218 rows).

## New Y
- Main Y: homes destroyed per 1,000 dwellings (135 rows with a figure: reported or zero inferred from RFS totals).
- Severity class by real loss: Light 90, Moderate 19, Severe 22, Extreme 6, Unknown 81 (no homes figure, no death).
- Old vs new class (`DAY3_CLASS_V1_VS_V3.csv`): of rows with a figure, 25 old "Moderate", 7 old "Severe" and 3 old
  "Extreme" had no homes lost and no deaths. The old percentile classes were labelling noise.
- Income, businesses, council finances and welfare are no longer part of the per-fire Y.

## New X
Fire: share of council burned, peak fire danger (FFDI). Pre-fire: exposure (share of homes in bush-prone land),
disadvantage (SEIFA, income, unemployment), hazard (bush-prone land, forest). Council finances dropped.

## Fire weather test (pre-registered): "weather helps", but only a little
| | Without weather (M2) | With peak FFDI (M4) |
|---|---|---|
| Out-of-season Spearman | 0.562 | 0.582 (+0.021 [+0.002, +0.044]) |
| Out-of-season error (deviance) | 10,594 | 9,106 (-14%) |
| Black Summer homes predicted (observed 2,483) | 346 | 502 |
| Other seasons predicted (observed 164) | 233 | 235 |

- Black Summer's average peak FFDI was 58 vs 35 in other seasons, and adding it narrows the gap, but Black Summer
  is still under-predicted about 5-fold.
- In-sample, once share burned is known, FFDI adds nothing (rate ratio 1.01 [0.52, 1.74]): big fires already happen
  on bad-weather days, so fire size carries most of the weather signal.
- Other in-sample rate ratios (M4, per SD): share burned 2.58 per log unit, exposure 1.58 [0.89, 2.82], disadvantage
  1.88 [0.94, 3.56]; with weather in the model neither interval clears 1.

## Plain summary
Homes lost ≈ fire size, a bit more in exposed and poorer councils, a bit more on extreme-weather days. Most of the
variation between fires is fire size plus something about extreme seasons that the available weather index only
partly captures.
