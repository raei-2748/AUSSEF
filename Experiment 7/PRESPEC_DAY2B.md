# Experiment 7, Day 2B: could a map built before Black Summer have flagged the councils that lost homes?

Written 2026-09-30 after the Day 2 result (primary rank test not confirmed; exposure cut out-of-season error by
40%) and before this test was run. Locked in `LOCK_DAY2B.txt`.

## Test (prospective in time: nothing from the Black Summer season is used to build the map)
- Layers from data dated before July 2019: H (hazard block), E2 (share of dwellings inside BFPL Cat 1-2, 2016 Census
  mesh blocks). Caveat: the BFPL layer is today's map, not a 2019 snapshot.
- Likelihood L_pre: logistic regression of "council had a fire burning >= 5% of it" on H, fitted on FY2015-2018 fires only.
- Consequence C_pre: M1 (Poisson, homes destroyed, offset log dwellings, log share + E2) fitted on FY2015-2018 rows
  only (DL_FILLED v2), evaluated at a 20% burned scenario.
- Index_pre = L_pre × C_pre.
- Outcome: council lost >= 1 home per 1,000 dwellings in the Black Summer season (FY2019 rows, DL_FILLED v2;
  councils with no FY2019 row = 0; councils with FY2019 rows but no figure are dropped).

## Reported
1. AUC of Index_pre, H alone, E2 alone for that outcome (129 councils), with council bootstrap intervals.
2. Of the 20 councils ranked highest by Index_pre, how many lost >= 1 home per 1,000 dwellings; and how many of the
   councils that did were in that top 20.
3. Consequence alone: among councils with >= 5% burned in Black Summer, Spearman of E2 (and of C_pre) with homes
   destroyed per 1,000 dwellings.
