# Experiment 14 findings: composite impact score, version 4 — "v4 (post-v3)"

2 Oct 2026. **v4 was chosen after seeing the v3 results** (and Experiments 11-12), so it is not an independent test.
Read every v4 number with that in mind. Rules: PRESPEC.md, hash-locked before any v4 value was computed
(LOCK_PRESPEC.txt); config and built inputs locked again before the models ran (LOCK.txt). Same 218 rows, same X,
same random forest settings, leave-one-fire-season-out validation and decision rules as Experiment 9. Sources:
`bibliography/parts/exp14_y_v4_2026-10-02.csv` (E14-01 to E14-36).

## Primary result (pre-registered for v4)
Y v4, PRE+FIRE X, random forest vs training mean, leave-one-season-out:
- Spearman rho **+0.43 [+0.28, +0.55]**, shuffled-Y p = 0.005 (200 shuffles): a real ranking signal.
- MAE 0.100 vs 0.113 for the training mean; difference **-0.013 [-0.020, -0.007]**: RF beats the mean.
- RF does **not** beat ridge regression (+0.41, MAE difference CI [-0.004, +0.007]). Council-grouped check: RF
  +0.25 [+0.07, +0.45].
- What drives it (permutation importance): homes inside the fire first, then X23 (homes owned outright), hazard H
  and fiscal F. So it is still mainly a fire-size score, with a smaller pre-fire part.
- The independent audit re-derived this result with its own code (+0.428 before the two audit fixes below; the
  fixes moved it to +0.432). Ranking within each fire season (audit check i8): +0.50, so the skill is not just
  "Black Summer vs the rest".

## What changed from v3, and why (measurement reasons)
| Pillar | v3 | v4 | Why |
|---|---|---|---|
| Comparison ("excess") | median of all councils with no row in that fire year | median of **FAR** councils: no row that year, no shared border with a burned council, < 0.5% of area burned | Exp 12: neighbours absorb rent effects; audit: burned councils without a row sat in the old pool |
| DL | homes destroyed per 1,000 dwellings | unchanged | |
| IL | traffic, income and businesses in affected small areas | **traffic removed**; income and businesses kept, with control small areas inside FAR councils | audit: half-counted traffic days. Experiment 13 not used (its audit folder was empty) |
| FP | grants per resident (1 year), fire-grant jump (FY, FY+1), capex jump, cash drawdown | grants per resident, fire-grant share and capex share all measured over **FY+1 to FY+3**; cash drawdown kept at FY and FY+1 | Exp 11: council money keeps coming for 3 years (+0.21 at FY+1, +0.43 at FY+3) |
| SL | rents (1 quarter), DV, rebuild gap | rents over **months 13-24**; DV unchanged; rebuild gap **adjusted for normal building growth**; **new: deaths per 100,000 residents** | Exp 11/12: rents move in year 2; the unadjusted rebuild gap tracks council growth |
| Not added | | household disaster payments; insurance | payments cover 1 of 218 rows; no public council-level insurance data (DATA_CHECK.md) |

## Data coverage (rows with a value, of 218)
| Indicator | Rows | Indicator | Rows |
|---|---|---|---|
| DL1 homes destroyed | 135 | FP4 cash drawdown | 199 |
| IL2 income, affected small areas | 112 (fires up to 2019) | SL1 rents, year 2 | 183 (rents start 2017) |
| IL3 businesses, affected small areas | 167 | SL2 domestic violence | 216 |
| FP1 grants per resident, FY+1..+3 | 199 | SL3 rebuild gap | 29 (>= 5 homes lost, from 2018) |
| FP2 fire-related grant share | 51 (audited statements) | SL4 deaths per 100,000 | 140 (17 above 0) |
| FP3 capital spending share | 52 | Injuries (descriptive only) | 10 rows, 48 injuries |

Pillars: DL 135, IL 177, FP 199, SL 218. Y v4: 218. Payments: 1 row (Kyogle, North Coast fire AGRN 880: 4.3
eligible household payments per 1,000 residents); not in Y.

## v1 / v3 / v4 side by side (RF, PRE+FIRE, leave-one-season-out; `results/V1_V3_V4_TABLE.csv`)
| | v1 rho [95% CI] | v3 | v4 (post-v3) | v4 shuffled p | v4 beats mean? |
|---|---|---|---|---|---|
| **Composite Y** | +0.33 [+0.17, +0.47] | +0.29 [+0.12, +0.45] | **+0.43 [+0.28, +0.55]** | 0.005 | yes |
| DL | +0.73 | +0.73 | +0.73 [+0.64, +0.79] | 0.01 | yes |
| IL | +0.30 (from V) | +0.07 | +0.09 [-0.24, +0.40] | 0.11 | no |
| FP | -0.02 | -0.21 | -0.09 [-0.33, +0.11] | 0.73 | no |
| SL | -0.05 | +0.27 (from V) | +0.02 [-0.17, +0.20] | 0.38 | no |
| Composite Y, pre-fire X only | +0.25 | -0.05 | +0.18 [-0.08, +0.37] | 0.02 | no |

v1 and v3 come from Experiment 9's results (same code, same seed). Only DL can be predicted for an unseen fire
season. IL, FP and SL still cannot, in any version. SL's v3 signal came from council vulnerability (V), a pre-fire
trait; with v4's indicators that signal is gone.

## Other v4 versions (secondary)
| Version | rho [95% CI] | Beats mean? | Reading |
|---|---|---|---|
| Magnitude-preserving (z-scores, clipped at +-3) | +0.25 [+0.05, +0.42] | no | keeping size adds noise from a few extreme rows |
| Immediate (DL, deaths, fire-year money) | +0.32 [+0.16, +0.45] | yes | carried by homes lost and deaths |
| 1-2 years | +0.28 [+0.06, +0.44] | no | ranking signal, but not better than the mean |
| 3+ years (FP, rents only) | -0.21 [-0.42, -0.02] | no | the same season artefact as v3 FP, not a real negative effect |
| FAR councils matched on OLG group | +0.40 [+0.27, +0.50] | yes | same picture |
| Deaths of residents only | +0.42 [+0.27, +0.54] | yes | same picture |

## Which indicators move with the fire (descriptive, NOT pre-registered)
Spearman of the indicator rank with log homes inside the fire per 1,000 (v3 value in brackets):
- **Track the fire:** homes destroyed +0.78 (+0.78); fire-related grant share **+0.52** (+0.41); deaths **+0.48**
  (new); rents in year 2 **+0.26** (-0.09); grants per resident over 3 years **+0.25** (+0.15); capital spending
  +0.22 (-0.11).
- **Do not:** income -0.12, businesses +0.07, cash drawdown +0.03, domestic violence +0.03, rebuild gap -0.10.
- Pillars: FP +0.24, SL +0.20, IL -0.06. **Y v4 +0.40** (v3 +0.34, v1 +0.31).
So the measurement changes (longer money window, far comparison, year-2 rents, deaths) made more of FP and SL move
with fire size. That is also why Y v4 ranks better than v3. But the pillars on their own still cannot be predicted
for a fire season the model has not seen.

## Deviations (numbered)
1. PRESPEC wording: payments cover **1** panel row, not "at most 7". Under AGRN 880 only Kyogle both had payments and
   has a panel row. Deaths are recorded for 142 rows, but SL4 has **140**: the 2 Mid-Coast 2016 rows have no council
   population (the council formed in 2016). No rule changed.
2. Audit a2: three pre-2016 councils (Dubbo City, Murrumbidgee Shire, Parramatta City) were joined to the merged
   councils that share their names. Now dropped. FP1 changes in 4 rows (max 0.008), FP4 in 15 rows (max 0.08 months).
3. Audit x5: the ABS 2018/2019 approval files use old codes for Armidale Regional and Inverell. Now mapped, so SL3
   has 29 rows instead of 27.
4. The first model run (before fixes 2 and 3) was stopped part-way and replaced; its partial outputs are kept in
   `results_prefix/`. The audit gives the pre-fix primary result: +0.428.
5. Unstated rules carried over from v3 (audit x7, x8): IL2 drops small areas with fewer than 100 residents, IL3 does
   not. SL1 needs at least 1 of the 4 post quarters. Not changed, now stated.
6. There are no v1 shuffled-Y p-values, because Experiment 9 ran shuffles only for v3 targets.

## Audit
A fresh reviewer agent (`audit/AUDIT.md`, scripts 01-16) re-derived every v4 indicator for all 218 rows from the raw
files with its own code: FP1-FP4, SL1-SL4, IL2, IL3 and the FAR sets. All match the build exactly (max difference
about 1e-15), and so do the ranks, the pillars, Y v4 and the primary metric. Council-name matching: no wrong matches.
The unmatched names are pre-2016 former councils (OLG) and Lord Howe Island, Unincorporated Far West and In Custody
(BOCSAR). Nothing found changes the conclusions. The two findings that changed numbers are fixed (deviations 2 and 3).

## What is still weak
- **Post hoc.** v4 was designed knowing what v3, Experiment 11 and Experiment 12 found. The higher composite rho
  (+0.43 vs +0.29) must not be read as v4 being "more true". It needs fresh fires to confirm.
- **Still mainly fire size.** Homes inside the fire drive Y v4. IL, FP and SL cannot be predicted for an unseen
  season on their own, and RF does no better than ridge regression.
- **Deaths:** 112 of 123 zeros are inferred from season totals. The 2016-17 zeros break the project's own rule (2
  official deaths left unassigned), and the source cited for the 2018-19 zero misses a death recorded in the master.
  Setting the 2016-17 zeros to missing barely matters (primary rho +0.434; audit e2), but the master should be fixed.
- **Recent fires are thin.** Fires in 2023 have only 1 year of grants data. For fires in 2024, 13 of 15 rows rest on
  the SL pillar alone (no OLG data for FY2025, no cash cover for FY2024).
- **Small samples:** fire-related grants and capital spending come from audited statements (51-52 rows); the rebuild
  gap has 29 rows. Duplicate statement lines (audit x3 / Experiment 12 f6) are still unchecked against the PDFs.
- **COVID and the regional rent boom** overlap Black Summer's year-2 rents. The far comparison helps, but cannot
  remove it.
- **Missing channels:** household disaster payments (no public data for Black Summer by council), insurance (only
  event-level or paid data), mental health, and tourism (traffic withdrawn).
