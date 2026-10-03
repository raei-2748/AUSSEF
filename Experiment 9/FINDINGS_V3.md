# Experiment 9 v3 findings: Bowen's pipeline with fire-matched pillar indicators

2 Oct 2026. Rules: PRESPEC.md "Addendum v3" (locked before the build, LOCK_v3.txt; config + inputs in LOCK.txt).
Same 218 rows, same models, leave-one-fire-season-out, 95% CIs by council bootstrap. v1 results kept in results_v1/.

## Primary result (pre-registered)
Composite Y v3, PRE+FIRE X, random forest vs training mean:
- Spearman rho **+0.29 [+0.12, +0.45]**, shuffled-Y p = 0.005; MAE 0.100 vs 0.107, difference **-0.007 [-0.013, -0.001]**.
- Passes both rules (real ranking signal; beats the mean). About the same as v1 (+0.28; +0.33 for the v1 config
  with X23 added). Permutation importance: almost all from homes inside the fire (DL).

## Pillar by pillar (RF, PRE+FIRE)
| Pillar | v1 indicators | v3 fire-matched | v3 shuffled-Y p | Beats mean? |
|---|---|---|---|---|
| DL | +0.73 | +0.73 [+0.64, +0.79] (unchanged) | 0.01 | yes |
| IL | +0.30 (from V, a pre-fire trait) | +0.07 [-0.13, +0.23] | 0.27 | no |
| FP | -0.02 | -0.21 [-0.43, +0.02] | 0.95 | no |
| SL | -0.05 | **+0.27 [+0.08, +0.41]** | 0.01 | no (-0.009 [-0.020, +0.001]) |

SL now has a real ranking signal, but it comes from V (council vulnerability) and is the same with pre-fire X only
(+0.28): it says which kind of council, not how big the fire was. FP's negative out-of-season rho is not a real
negative effect (shuffled p = 0.95); it is the same leave-one-season-out artefact seen for the mean baseline.

## Pre-fire risk map
Composite Y v3 with pre-fire X only: rho **-0.05 [-0.29, +0.14]**, shuffled p = 0.60, does not beat the mean.
The left panel of figures/fig6_nsw_map_y_v3.png is therefore **not a validated risk map** for composite Y v3; its
range is narrow (0.42-0.60). The validated pre-fire map remains Experiment 7's housing-loss map (AUC 0.91).

## Which indicators move with the fire (descriptive, NOT pre-registered)
Spearman of each indicator rank with homes inside the fire per 1,000 / share burned:
- **Track the fire:** DL homes destroyed (+0.78 / +0.67); **FP2 fire-grant jump (+0.41 / +0.37, n = 61)**;
  ~~IL1 tourism traffic fall (+0.25)~~ withdrawn after the audit (half-counted days; corrected about 0, see Experiment 12/audit/AUDIT.md); FP1 grants per resident (+0.15 / +0.02).
- **Do not:** IL2 income and IL3 businesses in affected small areas, FP3 capital-spending jump, FP4 cash drawdown,
  SL1 rents, SL2 domestic violence (all within about +-0.1); SL3 rebuild gap (n = 27, measures recovery speed, not
  size, so not expected to track size).
So one new fire-matched measure (fire-related grants) carries a fire signal, but each pillar averages them with indicators that
do not, which dilutes the pillar.

## Deviations (v3)
1. X23: 3 councils (6 rows) whose 2016 Census code changed use Census 2021.
2. run_models.py: config-v1 pillars and composite added as extra (sensitivity) targets for side-by-side reporting.
3. SL3 rebuild gap is not compared with unburned councils (as written); fast-growing councils can look rebuilt.

## Limits
Coverage: FP2/FP3 61-64 rows (audited statements), SL3 27 rows, IL1 98 rows (councils with traffic stations),
IL2 to fires up to FY2019 (income data end 2021-22). One dominant season (Black Summer, 57 rows).
