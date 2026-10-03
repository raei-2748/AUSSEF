# Experiment 12 pre-specification: spillover to neighbouring councils, and how big a missed effect could be

Written 2 Oct 2026 before any neighbour or bound value is computed. Hash in LOCK.txt. Deviations go in FINDINGS.md.
(The independent code audit of Experiments 9 v3 and 11 runs separately and writes audit/AUDIT.md.)

## Why
Experiments 9 and 11 found no fire link for rents, domestic violence and income support. Two ways that could happen
even if the harm is real: (1) displaced households move to NEIGHBOURING councils, raising rents and claims there, and
those neighbours sit in the "unburned" comparison group, pulling the measured difference toward zero; (2) the effect
per affected household is real but too small, spread over a whole council, to see. Part A tests (1); Part C states (2).

## Data (on disk, no downloads)
Council boundaries 2021 (fire_event_dataset/data/cache/lga2021_nsw_geom.parquet); master rows and homes destroyed
(Experiment 9 results/ANALYSIS_TABLE.csv: homes_v2 = homes destroyed count); rents (DCJ new-bond median by council,
quarterly 2017Q3-2026Q2); domestic-violence-related assault (BOCSAR, monthly by council); income-support recipients
(Experiment 7 panels/dss_quarter.parquet, quarterly by council, `income_support_total`).

## Definitions
- **Heavy row:** a master row with homes_v2 >= 5. A season F is used if it has at least one heavy row.
- **Neighbour:** a council with NO master row in season F that shares a border (polygons touch, buffer 50 m) with a
  council that has a heavy row in F. Its exposure = log(1 + homes destroyed in all its heavy neighbours in F); its m0 =
  the m0 (month of first_fire_start) of the adjacent heavy row with the most homes destroyed.
- **Far:** a council with no master row in F and no shared border with ANY council that has a row in F.
- Outcomes (same windows as Experiment 11): rent R = mean log rent in quarters q0+5..q0+8 minus mean log rent in the
  4 quarters before q0 (q0 = quarter of m0); DV = log(mean monthly count in months m0+13..m0+24 / mean monthly count in
  m0-24..m0-1); income support S = log(mean recipients in the quarters covering months m0+4..m0+12 / mean of the 4
  quarters before q0).
- **Neighbour excess** = neighbour's outcome minus the median outcome of far councils at the same m0.

## Part A (primary): do neighbours rise?
For each outcome (R, DV, S): mean neighbour excess over neighbour x season units, 95% CI by council-cluster bootstrap
(2,000), and sign-flip permutation p (2,000). Expected sign: positive (neighbours absorb displaced households).
Holm across the three. "Detected" = Holm p < 0.05 and positive. Secondary: Spearman between neighbour excess and
exposure (same bootstrap).

## Part B (sensitivity, descriptive): redo Experiment 11 with far councils only
For burned rows, recompute the Experiment 11 rent (H2) and DV (H2) excess using only FAR councils as the comparison,
and report the Spearman with log homes inside the fire per 1,000 next to the Experiment 11 value.

## Part C: how big could a missed effect be (per destroyed home)
On burned rows with outcome data, least-squares slope of the change (unburned-adjusted as in Experiment 11) on homes
destroyed (count), 95% CI by council-cluster bootstrap. Reported per destroyed home in natural units:
rents: % change in the council median rent per 100 homes destroyed; DV: extra incidents per year per destroyed home
(change in mean monthly count x 12); income support: extra recipients per destroyed home (change in mean quarterly
count). The upper CI end = the largest effect the data cannot rule out. Descriptive.

## Outputs
results/SPILLOVER.csv, results/BOUNDS.csv, FINDINGS.md (plain English).
