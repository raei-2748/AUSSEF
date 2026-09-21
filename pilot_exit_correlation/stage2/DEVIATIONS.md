# Deviations from stage2/PREREGISTRATION.md

| # | Date | Deviation | Reason | Effect on verdict |
|---|---|---|---|---|
| Y1 | 2026-09-21 | Fixed a date-type bug in `s2/historical.py` (fire-family grouping) after the first run crashed. | The crash happened before any stage-2 result was computed. The family rule itself is unchanged. | None. |
| Y2 | 2026-09-21 | Added `diagnostics.py` and a post-hoc section to RESULTS.md: the events behind each cut-off, the share of each town inside the fire, and R without the most influential event. | Results were concentrated in a few fires, and many cut-offs involve towns lying inside the fire perimeter. These checks are needed to interpret the result honestly. Labelled as not pre-registered. | None. The verdicts come only from the pre-registered run. |
