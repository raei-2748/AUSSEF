# Experiment 7, Day 8: rapid damage estimate right after a fire

Date: 1 Oct 2026. Rules locked first: `PRESPEC_DAY8.md` (LOCK_DAY8.txt). Script: `day8_rapid_estimate.py`;
figure `results/fig5_rapid_estimate.png`.

## Verdict (pre-registered): "Rapid estimate works"
Every prediction made with its own fire season left out of training (125 council × fire rows, 54 with losses):

| Model | Rank accuracy (Spearman) | Prediction error (deviance) | Black Summer homes predicted (actual 2,483) |
|---|---|---|---|
| R0 area burned only | 0.54 | 17,394 | 133 |
| R1 homes inside / within 1 km of the fire | 0.78 | 2,024 | 1,668 |
| R2 + burn severity (pre-registered) | 0.75 | 2,060 | 1,442 |
| R3 + fire weather | 0.76 | 1,636 | 1,923 |

- R2 vs R0: rank accuracy +0.21 [+0.06, +0.37]; error down 88%.
- Rows with losses predicted within a factor of 2: 14% (area only) to 39% (R2).
- The Black Summer gap (area alone under-predicts 19-fold) shrinks to 1.3-1.7-fold. Black Summer was worse mainly
  because its fires reached far more homes, not because of something unmeasurable.
- Most of the gain comes from "homes inside the fire" (in-sample rate ratio 5.3 per log unit). Burn severity adds a
  little in-sample (1.8 per SD) but not out of season; fire weather helps the totals.

## Use and limits
- Inputs are available within days (mapped outline, Census dwelling counts, satellite severity), weeks before
  official counts. Useful for early recovery planning.
- Dwelling counts are Census-based and spread evenly within mesh blocks; severity is missing for some fires.
- Individual estimates are still rough (only 39% within a factor of 2); totals and rankings are much better.
