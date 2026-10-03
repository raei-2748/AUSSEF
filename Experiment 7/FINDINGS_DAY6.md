# Experiment 7, Day 6: unemployment (Bowen's suggestion)

Date: 1 Oct 2026. Rules locked first: `PRESPEC_DAY6.md` (LOCK_DAY6.txt). Script: `day6_unemployment.py`.
Data already in the project: DEWR SALM smoothed council unemployment rate, quarterly, Dec 2010 to Mar 2026.

## Result: not detected
- Unemployment change in the year after the fire vs the year before (relative to similar councils), per 10% of
  residents living in or within 1 km of the fire: -0.01 points [-0.35, +0.59]. Pre-trend check passes.
- Councils with >= 5% of residents affected: -0.08 points on average (34 rows); councils with < 1%: -0.26 points.
- Same with area burned as the dose and without Black Summer.
- Upper limit: per 10% of residents affected, council unemployment did not rise by more than about 0.6 points.

## Caveat
SALM council figures are smoothed model estimates (4-quarter averages), which damps short shocks. DEWR also
publishes UNSMOOTHED SA2 (small-area) files, which would test this properly where affected people live; that needs
a download (Ray to approve).
