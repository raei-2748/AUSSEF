# Experiment 7, Day 10: where did the loss go?

Date: 1 Oct 2026. Rules locked first: `PRESPEC_DAY10.md` (LOCK_DAY10.txt). Script: `day10_where_loss_went.py`;
results `results/DAY10_WHERE_LOSS_WENT.json`. One download: ABS 32180DS0003_2001-25.xlsx (SA2 population, 688 KB).

| Check | Result | Verdict |
|---|---|---|
| A. Money in: council grants per resident (year after) | +A$330 per resident per 10 homes destroyed per 1,000 [+65, +742] | **Detected** |
| B. Rents (council, new bonds, year after) | +0.1% per 10 homes per 1,000 [-1.6, +1.2] | not detected |
| C. Sectors (SA2, years 0-2, per 10 pp of homes inside fire): agriculture | +0.1% [-1.7, +1.8] | not detected |
| retail | -2.3% [-6.7, +2.1] | not detected |
| accommodation & food | +6.0% [-0.4, +12.4] (opposite of expected) | not detected |
| construction (expected up) | -1.0% [-3.4, +1.4] | not detected |
| D. Population (SA2 ERP, years 1-5) | -0.4% per 10 pp [-2.2, +1.4]; path drifts to -0.6% by year 3-5 | not detected |

Descriptive: Black Summer grant programs reported for these councils total A$677m against 2,480 homes destroyed in
the same rows (about A$270,000 per home; these programs fund councils and communities, not only rebuilding).
Literature (search, 1 Oct): insured losses A$2.32bn (ICA); Disaster Recovery Payments >A$283m; tourism A$1.7bn direct;
farm losses A$4-5bn (WWF/Univ. Sydney). No study found that measures out-migration from burned areas after Black
Summer with area data (Akter & Grafton 2025 full text not checked).

## What it means
- The clearest place the loss "went" is public money: councils that lost more homes received much more grant money
  per resident. Combined with insurance (A$2.3bn) and recovery payments, this is why local income, jobs and
  businesses look normal: losses were transferred to insurers and governments.
- The Day 9 reading "people left" is NOT confirmed by population counts: SA2 population fell only slightly and not
  significantly (-0.4% per 10 pp; the trend is in that direction). Total income fell (Day 9), mostly through fewer
  earners, but whether those earners left the area or stopped earning is unresolved.
- No rent rise at council level (Akter & Grafton's +10% was at very small areas, 2016 to 2021, including the COVID
  regional rent boom).
