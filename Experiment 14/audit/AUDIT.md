# Audit of Experiment 14 (Y v4)

2 Oct 2026. Independent re-derivation from raw files. I wrote my own loaders (`common.py`) and check scripts
(`01_...` to `11_...`). I did not import or copy the project build code. I read `build_v4_indicators.py` only
after my versions were written and run. No file outside `audit/` was edited, and nothing was downloaded. Every
number below comes from a script in this folder; its printed output is in the `.txt` file with the same number.

## Bottom line

**The main numbers stand.** I rebuilt FP1, FP4, SL1, SL2 and SL4 for all 218 rows from the raw files. All of them
match the built file row by row (max difference about 1e-15), with the same rows missing. The FAR comparison sets
match council by council in all 9 fire years. Ranks, all four pillars and Y_v4 match for all 218 rows (max
difference 6e-17). My own random forest (leave-one-season-out, PRE+FIRE) gives the same primary result as
`results/METRICS.csv`:

- **Spearman rho = +0.428** (my council-cluster bootstrap 95% CI [+0.275, +0.540])
- **RF MAE = 0.1001**, against a training-mean MAE of 0.1129
- **RF minus mean MAE: 95% CI [-0.0190, -0.0070]**, entirely below 0, so RF beats the baseline

I found no error that changes results. There are six minor issues: one name-matching quirk, two problems with how
deaths are recorded, two coverage or timing limits that are allowed by the spec but should be stated, and one
wording error in the PRESPEC count (142 vs 140).

## Table of checks

| # | Check | Result | Severity |
|---|---|---|---|
| a1 | OLG name matching | 41 unmatched OLG names, all pre-2016 former councils (none has data from FY2016 on). All 128 councils with OLG data match every year from FY2016. Unincorporated NSW has no OLG data. No council-FY gets two source names. | none |
| a2 | OLG pre-2016 namesakes | Old Dubbo City, Murrumbidgee Shire and Parramatta City (FY2013-14) share a name key with the post-merger councils, so they are joined to them. **The build keeps them.** I match the build exactly when I keep them too. Dropping them changes only the FAR medians for early fire years. FP1_main changes in 4 rows (F 2014-15, max 0.0076). FP4_main changes in 15 rows (max 0.083 months). FP4_h12 changes in 14 rows (max 0.285). Same issue as Exp 12 audit a3. | minor |
| a3 | OLG groups sheet | 128 of 128 matched, no duplicates. Unincorporated NSW has no group, so it is missing in the OLG sensitivity. | none |
| a4 | BOCSAR names | Unmatched: Lord Howe Island, Unincorporated Far West, In Custody. No two names map to one council. Every council except Unincorporated NSW has a series. | none |
| a5 | region_id joins (rent, adjacency, fires.csv, master) | No id outside the 129-council list. Adjacency is symmetric (636 pairs). Rent has no Unincorporated NSW. fires.csv has no row for 12 metro councils (no fires), which is correct for the burned-area rule. 3 rent ids carry old file names (Gundagai, Western Plains Regional, Glen Innes), but the ids are right. | none |
| b | FAR sets | Rebuilt for each fire year: identical to FAR_SETS.csv in all 9 years (counts and ids). FAR sizes are 43 (F=2019) to 120 (F=2014). | none |
| c | FP1_main and FP1_h0/h12/h3 | n = 199 / 214 / 199 / 134. Identical to the build (max abs diff 2e-16), with the same missing rows. At least 42 FAR councils have a value in every row that has FP1. | none |
| d | SL1_main and SL1_h3 | n = 183 / 166. Identical to the build (max abs diff 3e-15). The build needs at least 1 post quarter. If 2 are required instead, 5 rows drop. | none |
| e1 | SL4 deaths per 100,000 | n = 140, identical to the build. **The PRESPEC says 142 rows have deaths recorded.** That is true, but 2 of them (Mid-Coast, F 2016, both 0 deaths) have no council population because Mid-Coast was formed in 2016, so SL4 has 140 rows. | minor (wording) |
| e2 | Inferred zero deaths | 112 of the 123 zeros are inferred from season totals. The rule (Exp 6 dl_fill FINDINGS) is: set a season's other rows to zero when the official season total minus deaths already given to rows is 1 or less. 2019-20: 25 coroner deaths, 25 given to rows, so the 43 zeros are well founded. 2017-18: official 0, fine. 2015-16: 1 death left over, which the rule allows. **2016-17 breaks the rule.** The cited RFS report lists 2 deaths (1 firefighter, 1 civilian). None is given to a panel row, yet all 11 rows are set to 0. **2018-19:** the cited Inquiry table says 0 deaths, but the master gives the Kingiman helicopter pilot (Shoalhaven, Aug 2018) to an F=2018 row. So the "statewide zero" source undercounts, although zero for the other 24 rows is still plausible. Effect of setting the 2016-17 zeros to missing: Y_v4 Spearman with the built Y_v4 is 0.9955, and the primary rho goes from 0.428 to 0.434 (MAE 0.1002 both ways). | minor |
| f1 | FP4_main, h0, h12 | n = 199 / 199 / 161. Identical to the build (max abs diff 2e-15). Cash cover is missing for all councils in FY2024. So F=2024 rows have no FP4, and F=2023 FP4_main uses FY F only (no FP4_h12). | none (coverage noted) |
| f2 | SL2 domestic violence | n = 216. Identical to the build. BOCSAR runs to 2026-06 with real counts. | none |
| f3 | 10 hand spot checks | `10_spot_checks.md` prints the raw grants per resident, cash cover, rent quarters and deaths for 10 rows. The windows, FY labels and fire quarters are as specified. | none |
| g | Ranks, pillars, Y_v4 | Recomputed for all 218 rows: each of the 11 indicator ranks, 4 pillars and Y_v4 matches (max diff 1e-16, no missing mismatches). IL2, IL3, FP2, FP3 and SL3 come from the built file (not re-derived). DL1 comes straight from DL_FILLED.csv and is identical. | none |
| h | Primary metric (own code) | rho +0.428, RF MAE 0.1001, mean MAE 0.1129: identical to METRICS.csv (rf rho 0.428066, MAE 0.100147; mean MAE 0.112916). With PRE only, rho is +0.185, same as METRICS. | none |
| i1 | Time alignment | F (info_fire_fy) equals the FY of first_fire_start for all 218 rows. OLG fy_start follows the start-year convention. The fire quarter and m0 come from first_fire_start. | none |
| i2 | Signs | IL -1, FP4 -1, everything else +1, as in the PRESPEC and config. The signed ranks of DL1, FP1, FP2, SL1 and SL4 rise with log homes in the fire per 1,000, which is the expected direction. | none |
| i3 | F = 2024 rows | No FP1 (no FY2025 OLG) and no FP4 (no FY2024 cash cover). 13 of 15 rows rest on the SL pillar alone. 14 rows have SL1 from only 1-3 of the 4 post quarters (rent ends 2026Q2). | minor (coverage; should be stated) |
| i4 | FP1_main window length differs by season | 3 post years for F up to 2019, 2 for F=2022 (26 rows), 1 for F=2023 (38 rows). Since grants keep arriving for 3 years, FP1 for recent seasons covers less of the response. This is allowed by the PRESPEC ("at least one"). | minor (state it) |
| i5 | FAR councils that burn later | Some FAR councils have a master row, or burned at least 0.5%, in F+1..F+3 (up to 32 per year) or in F-2..F-1 (up to 19). Excluding the later-burned ones from FP1's comparison: n is still 199, Spearman with the built FP1 is 0.997, and the largest mean shift in any season is 0.034. | none |
| i6 | Comparison sets below 5 | None among rows that have a value: FP1 has at least 42, SL1 at least 38. The OLG-group sensitivity loses rows as expected (FP1 199 -> 169, IL2 112 -> 63, SL3 27 -> 12). | none |
| i7 | Several rows in one council-FY | 98 rows share 47 council-FYs and carry identical FP1/FP4 values (as in Exp 12 f3). | none (known) |
| i8 | Is rho only a between-season effect? | Within-season rho of the out-of-fold predictions (seasons with at least 10 rows) is +0.497. Per season it is +0.26 to +0.73. The season-mean correlation is only +0.15. So the ranking skill is within seasons. | none |
| i9 | X columns | All 10 X columns and the season are identical to Experiment 9 ANALYSIS_TABLE. Y_v3 equals Exp 9 Y_comp. | none |

## Re-derived vs built

| Quantity | Built | Auditor |
|---|---|---|
| FAR set sizes F 2014/15/16/17/18/19/22/23/24 | 120/106/86/62/68/43/78/62/80 | identical (same ids) |
| FP1_main n, max abs diff | 199 | 199, 2.2e-16 (4 rows differ if pre-2016 namesakes are dropped, max 0.0076) |
| FP1_h0 / h12 / h3 n | 214 / 199 / 134 | same, max diff 1e-16 |
| FP4_main / h0 / h12 n | 199 / 199 / 161 | same, max diff 2e-15 |
| SL1_main / SL1_h3 n | 183 / 166 | same, max diff 3e-15 |
| SL2 n | 216 | 216, max diff 1e-16 |
| SL4 / SL4_resident n | 140 / 140 | 140 / 140, max diff 4e-15 |
| Pillars DL / IL / FP / SL n | 135 / 177 / 199 / 218 | same, max diff 1e-16 |
| Y_v4 (218 rows) | mean 0.501, SD 0.134 | identical, max diff 6e-17 |
| Primary: rho, RF MAE, mean MAE | 0.428, 0.1001, 0.1129 | 0.428, 0.1001, 0.1129 |
| RF minus mean MAE, 95% CI | [-0.0194, -0.0070] | [-0.0190, -0.0070] (own bootstrap) |
| Spearman 95% CI | [+0.276, +0.545] | [+0.275, +0.540] (own bootstrap) |

## Unmatched names

**OLG (41 names, all pre-2016 former councils, no data after FY2015):** Armidale Dumaresq, Ashfield, Auburn,
Bankstown, Bombala, Boorowa, Botany Bay, Canterbury, Conargo, Cooma-Monaro, Cootamundra, Corowa, Deniliquin,
Gloucester, Gosford, Great Lakes, Greater Taree, Gundagai, Guyra, Harden, Holroyd, Hurstville, Jerilderie,
Kogarah, Leichhardt, Manly, Marrickville, Murray, Palerang, Pittwater, Queanbeyan, Rockdale, Snowy River,
Tumbarumba, Tumut, Urana, Wakool, Warringah, Wellington, Wyong, Young (`01_unmatched_olg.csv`).
Matched on purpose: Nambucca Shire / Nambucca -> Nambucca Valley (same council, renamed); "Municipality of" Hunters
Hill / Kiama; "Parramatta (new)", "Murrumbidgee (new)". Silently joined pre-2016 namesakes: Dubbo City Council,
Murrumbidgee Shire Council, Parramatta City Council (FY2013-14), see a2.

**BOCSAR (3):** Lord Howe Island, Unincorporated Far West, In Custody.

**OLG groups:** none. **Rent / adjacency / fires.csv:** joined by id; no unknown ids.

## Not re-derived
IL2, IL3 (SA2 FAR controls), FP2, FP3 (statements) and SL3 (approvals) were taken from the built file for the
composite check. Their ranks and their part in Y_v4 were checked, but the raw values were not.

## Files
`common.py` (own loaders); `01_name_matching.py` (a); `02_far_sets.py` (b); `03_fp1.py` (c); `04_sl1.py` (d);
`05_sl4.py`, `05b_death_zero_refs.py`, `05c_death_zero_rule.py` (e); `06_fp4_sl2.py` (f); `07_composite.py` (g);
`08_primary_metric.py` (h); `09_misc_checks.py`, `11_comparison_sizes.py` (i); `10_spot_checks_and_x.py` (f3, i9).
Each writes CSV/TXT/MD outputs next to it. `_bocsar_dv.parquet` is a cache of the BOCSAR DV rows.

## Extension (requested later): FP2, FP3, SL3, IL2, IL3 rebuilt from raw files

**Bottom line of the extension: all five indicators match the built file.** For FP2 and FP3 (all four windows),
IL2 and IL3 the match is full: all rows, same missing rows, max difference about 1e-15. SL3 also matches 27 of 27,
but two rows are lost because the ABS changed council codes between files (x5). The bottom line above does not
change. My own code does the label rule, windows, comparison, the SA2 to council map and the control and
weighting logic. The only project code I called is the Experiment 7 income loader `day5_sa2_income.panel()`, as
permitted.

| # | Check | Result | Severity |
|---|---|---|---|
| x1 | FP2 fire-related grant share, _main/_h0/_h12/_h3 (`13_fp2_fp3.py`) | n = 51 / 61 / 51 / 28, identical to the build. To match I had to use two rules: (1) the same label rule (bushfire, bush fire, rural fire, fire protection, fire service, emergency services, disaster recovery, natural disaster; not storm or flood) for the comparison councils too; (2) the "has-lines" rule. Without the label rule on the comparison side, 45-61 rows differ by up to 0.013. Without the has-lines rule, 1-3 more rows get a value. Rule (2) affects 4 fire councils: Gwydir, Newcastle, Oberon, Queanbeyan-Palerang. Both rules follow the PRESPEC wording. Each row has 12-15 comparison councils with a value (`13b_fp_cmp_sizes.txt`). No FP2/FP3 for F = 2023-24 (statements end FY2023-24). | none |
| x2 | FP3 capex share, all windows | n = 52 / 64 / 52 / 29, identical to the build. | none |
| x3 | Duplicate statement lines | Some fire-file council-FY-label lines appear twice and both are summed (as in the build). This is the same open question as Exp 12 f6. | minor (unverified, carried over) |
| x4 | SL3 rebuild gap (`14c_sl3_v2.py`) | 27 of 27 identical (max diff 1e-16). The build needs at least 6 pre-fire months from July 2018 onward, not a full 12. With a full 12-month pre window, Tenterfield 2018 (agrn 843) drops out (`14_sl3.py`). The FAR growth adjustment matters: without it, 9 rows change by up to 0.26. Each row's growth factor uses 39-61 FAR councils. | none |
| x5 | **ABS council codes change between approval files** | The 2018-19 and 2019-20 files (`BA_LGA2018/2019.csv`) use code 10130 for Armidale Regional and 14200 for Inverell. Later files use 10180 and 14220, which are the codes in the 129-council list. Joining by code loses those 24 months for both councils, so **2 SL3 rows are missing**: Inverell 2018 (14 homes, gap 0.63) and Armidale Regional 2019 (12 homes, gap 0.00). With the codes mapped, no existing SL3 value changes. Y_v4 changes in 29 rows (max 0.018, Spearman with the built Y_v4 0.9999). The primary metric goes from rho 0.428 / MAE 0.1002 to 0.430 / 0.1001 (`16_sl3_codefix_effect.txt`). `BA_LGA2016.csv` and `BA_LGA2017.csv` contain only an ABS error message, so approvals start in July 2018 as the spec says. | minor |
| x6 | SA2 to council map (`12_sa2_to_council.py`) | Built from the mesh-block files: 644 NSW SA2s. All 640 SA2s in `sa2_info` map to one of the 129 councils. 13 SA2s have less than 60% of their residents in their assigned council. | none |
| x7 | IL2 income in affected SA2s (`15_il2_il3.py`) | n = 112, identical to the build (max diff 3e-15), but only when SA2s with fewer than 100 residents are dropped (the filter used in Experiment 7 Day 5). Without that filter, 15 rows differ by up to 0.0069. This filter is not stated in Exp 9 Addendum v3 or the Exp 14 PRESPEC. Comparing per SA2 GCCSA or per council GCCSA gives the same result. | minor (undocumented rule, tiny effect) |
| x8 | IL3 businesses in affected SA2s | n = 167, identical to the build (max diff 8e-16) with **no** population filter. Adding the IL2 filter changes 106 rows by up to 0.027. So IL2 and IL3 use different SA2 sets. | minor (inconsistent, undocumented) |
| x9 | IL coverage | IL2 needs income for FY F+2, so it exists only for F ≤ 2019, as the spec says. All rows were rebuilt, not just a sample. | none |

**Re-derived vs built (extension):**

| Indicator | Built n | Auditor n | Max abs diff |
|---|---|---|---|
| FP2 _main/_h0/_h12/_h3 | 51/61/51/28 | 51/61/51/28 | 1e-16 |
| FP3 _main/_h0/_h12/_h3 | 52/64/52/29 | 52/64/52/29 | 1e-16 |
| SL3 | 27 | 27 (29 with the ABS code fix) | 1e-16 |
| IL2 | 112 | 112 | 3e-15 |
| IL3 | 167 | 167 | 8e-16 |

Extension files: `12_sa2_to_council.py` (-> `12_sa2_to_council.csv`); `13_fp2_fp3.py`, `13b_fp_cmp_sizes.py`;
`14_sl3.py` (strict pre-window variant), `14b_sl3_checks.py`, `14c_sl3_v2.py` (matching rule; argument `fixcodes`),
`14d_sl3_diff.py`; `15_il2_il3.py`; `16_sl3_codefix_effect.py`.
