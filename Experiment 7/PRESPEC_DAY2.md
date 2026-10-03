# Experiment 7, Day 2: can pre-fire data predict how many homes a fire will destroy? Rules fixed first

Written 2026-09-30 after Day 1 (FINDINGS_DAY1.md) and before any Day 2 number. Locked by SHA-256 in
`LOCK_DAY2.txt`; later changes are deviations and are listed in FINDINGS_DAY2.md.

## Why this target
Day 1: of the four pillars, only direct loss rises with fire size (homes destroyed per 1,000 dwellings: 0.2 in
councils with < 1% burned, 8.0 in councils with >= 20% burned). So the consequence part of the risk score is tested
against homes destroyed per 1,000 dwellings, given the fire's size.

Honest status of the predictor: Experiment 6 already showed that E2 (share of a council's dwellings inside Bush
Fire Prone Land Cat 1-2, from 2016 mesh-block counts) correlates with DL across all rows (+0.41). What is new here:
the link GIVEN fire size, predicted season-by-season out of sample, and on independent 2013 fires.

## Data
- Rows: the 218 NSW council × fire rows, 2015-25. Target: homes destroyed per 1,000 dwellings from
  Experiment 6's DL_FILLED.csv, version v2 (reported figures plus zeros inferred from RFS season totals, 135 rows).
  Sensitivity: v1 (reported only, 93 rows) and v3 (plus flagged estimates, 208 rows).
- Fire size: share of the council burned (master). Dwellings: DL_FILLED `dwellings`.
- Pre-fire council traits, built in Experiment 6 before this test (COUNCIL_ITEMS_v2.csv): E2 (raw share),
  H (hazard block), V (vulnerability block), F (fiscal block); each standardised across the 129 councils.

## Models (Poisson pseudo-likelihood, log link, offset log dwellings; count = homes destroyed)
- M0: log(share burned)
- M1: M0 + E2                      <- the pre-specified consequence model
- M2: M1 + V
- M3: M2 + H + F

## Primary test
Leave-one-fire-season-out (financial year) prediction on the 2015-25 rows. Statistic: Spearman between
out-of-sample predicted and observed homes destroyed per 1,000 dwellings, M1 minus M0, with a council-cluster
paired bootstrap (2,000 draws; seed 20260930).
- "Consequence confirmed" if the 95% interval of the difference is above 0.
- "Not confirmed" otherwise. Also reported: out-of-sample Poisson deviance of M0-M3.

## Secondary (reported whatever they show)
1. In-sample rate ratios per SD (M1-M3), council-cluster bootstrap (1,000 refits).
2. Rank check: partial Spearman of E2, V, H with DL controlling for rank of share burned.
3. Sensitivity: DL versions v1 and v3.
4. Independent fires: NSW October 2013 rows with a homes figure (reported or inferred zero) and an E2 value for
   the same council code; M0 and M1 trained on all 2015-25 rows; Spearman(predicted, observed) and predicted vs
   observed total homes. Descriptive only (about 10 rows). SA and Victoria are not used (no comparable E2).
5. Disadvantage check (Experiment 6 claimed poorer councils suffer more): Spearman(V, S) where S is the
   socioeconomic part of Y (v1), in rows with < 1% burned vs >= 5% burned; and Spearman(V, placebo S) using
   Day 1's trend-robust counterfactual (V2c). If V relates to S equally at tiny fires or at pseudo fires, the link
   is not a fire effect.
6. V given fire size on homes destroyed: M2's V rate ratio (does disadvantage add housing loss?).

## The maps (defined now, drawn after)
- Likelihood L: logistic regression of "council had a fire burning >= 5% of it in 2015-25" on H, 129 councils;
  leave-one-council-out AUC reported.
- Consequence C: M1's expected homes destroyed per 1,000 dwellings if 20% of the council burned (a Black
  Summer-scale scenario). M2 replaces M1 only if M2's cross-validated Spearman beats M1's by >= 0.05.
- Expected loss index = L × C; priority map = terciles of L × terciles of C.
- Council-level check (in-sample, descriptive): Spearman across councils between H, E2, C, L × C and realised homes
  destroyed per 1,000 dwellings summed over 2015-25 fires.
