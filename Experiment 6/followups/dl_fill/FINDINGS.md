# Experiment 6 follow-up: filling the missing direct loss (DL)

Date of the work: 2026-09-29. Author: Claude (Sonnet 5.5) for Ray. Nothing was committed or pushed. The workbook, `data/aussef.duckdb` and `Experiment 6/REPORT.md` were only read, never written (last-modified times: workbook 27 Sep, duckdb 21 Sep, REPORT.md 29 Sep 14:50, none changed by this work). Everything is under `Experiment 6/followups/dl_fill/`.

## Plain summary (5 lines)

1. DL is missing for 128 of 218 rows, almost all small fires (median 0.3% of the council burned vs 3.2% where DL exists); all 50 Black Summer rows and 37 of the 38 rows with 5% or more burned already have it.
2. No official source lists homes destroyed per small fire per council; searching RFS, NSW Reconstruction Authority, Disaster Assist, AIDR, the Coroner and ABC filled only 3 rows with a stated figure (plus 3 weak, 2 split by area).
3. The useful official fact is the RFS statewide season total of homes destroyed: for 2015/16, 2018/19 and 2022/23 the fires already in the data use it up (at most 1 home left), so 42 more rows are zero by arithmetic (flagged inferred); 2017/18 (3 left) supports 27 flagged estimates.
4. New file `DL_FILLED.csv` with a source flag on every cell: coverage 90 original, 93 reported, 135 with inferred zeros, 208 with flagged estimates (of 218); fires at 5% or more burned go from 37 to 38 of 38.
5. Conclusions hold: risk score vs DL on fires 5% or more burned +0.43 before, +0.39 [+0.07, +0.65] after; on all rows +0.43 before, +0.42 [+0.25, +0.54] with reported + inferred values, +0.27 [+0.12, +0.39] with the estimated zeros (72% ties); still above zero and present outside Black Summer.

---

## 1. Which rows have DL, and what is missing

Unit: 218 declared-event x council rows (96 events, 69 councils). "DL present" = `DL_homes_destroyed_in_council` exists (the DL pillar is the percentile rank of homes destroyed per 1,000 dwellings, reproduced exactly from the workbook). Row-by-row list: `out/DL_ROW_STATUS.csv` (one line per row) and the per-event listing in the appendix below.

- Present 90 (52 with homes destroyed above 0, 38 exact zeros). Basis: 66 council figures, 24 "one fire in the council" lower bounds.
- Missing 128. 67 of the 96 events have no DL row at all (29 have at least one); 13 of the 69 councils have none.

| Year of fire start | rows | DL present | missing | % missing |
|---|---:|---:|---:|---:|
| 2015 | 4 | 3 | 1 | 25 |
| 2016 | 8 | 5 | 3 | 38 |
| 2017 | 22 | 6 | 16 | 73 |
| 2018 | 34 | 8 | 26 | 76 |
| 2019 | 71 | 56 | 15 | 21 |
| 2023 | 63 | 10 | 53 | 84 |
| 2024 | 11 | 0 | 11 | 100 |
| 2025 | 5 | 2 | 3 | 60 |

| Share of council burned | rows | DL present | missing | % missing |
|---|---:|---:|---:|---:|
| under 0.1% | 43 | 6 | 37 | 86 |
| 0.1-1% | 92 | 23 | 69 | 75 |
| 1-2% | 21 | 6 | 15 | 71 |
| 2-5% | 24 | 18 | 6 | 25 |
| 5-10% | 10 | 9 | 1 | 10 |
| 10% or more | 28 | 28 | 0 | 0 |

- Black Summer (AGRN 871): 50 of 50 present. Everything else: 40 of 168 present.
- The only missing row at 5% or more: **AGRN 880 Clarence Valley** (7.9%, 82,668 ha).
- Councils with most missing rows: Singleton 8 of 9, Tamworth 7 of 8, Upper Hunter 7 of 9, Mid-Western 6 of 8, then Tenterfield, Mid-Coast, Narrabri, Muswellbrook, Cessnock and Gwydir with 5 each (`out/PROFILE_BY_COUNCIL.csv`). Events: `out/PROFILE_BY_EVENT.csv`. The 6 March 2023 declaration (AGRN 1052, 11 councils) is the largest single gap.
- Missingness is tied to fire size (Mann-Whitney p about 1e-16), so missing-at-random does not hold. Anything computed on "rows with DL" leans towards larger fires.

## 2. Sources searched

Reading was by the fetch tool, search, and the built-in browser (Disaster Assist). Three helper agents scanned the 128 missing rows by period (`research/notes_A.md`, `notes_B.md`, `notes_C.md`, `findings_*.csv`); I re-read the primary text for the numbers that decide a fill (RFS 2015/16, 2017/18, 2018/19 and 2022/23 season totals, the RFS 2018 and 2024 releases, Bees Nest, Grawin, Llandilo, AIDR Alpha Rd) and checked fire-to-row matches against the dataset's own fire records, rejecting several agent matches (section 4). Exception: the RFS Bush Fire Bulletin 45(1) sentence ("at least six") comes from the agent that read the PDF; AIDR 2022-23, which I read myself, gives the same six. **Nothing was downloaded into the project or Drive.** The fetch tool cached some PDFs in its own tool-results folder outside the repo; the agents read text from those copies. No ACM (Australian Community Media) source is cited or used (`check_sources.py` found 0 hits); ABC is used.

The 200-call web-search budget for the session ran out during the scans, so some periods were **not searched, not searched-and-empty** (listed in 2D).

### 2A. Already in the repo but not used for home counts (biggest yield)

| Source | URL | What it says | Rows it drives | Reliability |
|---|---|---|---:|---|
| RFS media release 28 Apr 2023, "Bush Fire Season ends for NSW" | https://www.rfs.nsw.gov.au/news-and-media/media-releases/end-of-fire-season-for-nsw | "the loss of eight homes, 15 outbuildings" in 2022/23 | 21 inferred zeros | Official; the step from total to per-row zero is my inference |
| RFS Annual Report 2018/19, fire season box p.26 | https://www.rfs.nsw.gov.au/__data/assets/pdf_file/0004/129892/NSW-RFS-Annual-Report-2018-19-web.pdf | "37 habitable structures destroyed and 27 damaged"; Tingha + Bruxner Hwy "32 homes lost" | 20 inferred zeros | Same |
| RFS Annual Report 2015/16, fire season box p.28 | https://www.rfs.nsw.gov.au/resources/publications/annual-reports/general/nsw-rural-fire-service-2015-16-annual-report/3-NSW-RFS-Annual-Report-2015-16-Summary-Review-of-Operations.pdf | "Loss/damage 1 habitable structure" | 1 inferred zero | Same |
| RFS Annual Report 2017/18, box p.28 | https://www.rfs.nsw.gov.au/__data/assets/pdf_file/0003/92262/NSW-RFS-Annual-Report-2017-18-web.pdf | 74 habitable structures destroyed | 27 estimates (3 spare) | Low |
| RFS Annual Report 2016/17, box p.28 | https://www.rfs.nsw.gov.au/__data/assets/pdf_file/0008/73673/NSW-RFS-Annual-Report-2016-17.pdf | 65 destroyed; February 2017 fires = 56 (45 + Carwoola 11) | 0 (8 homes unexplained) | Total is solid; too loose to fill |
| RFS Bush Fire Bulletin Vol 45 No 1 (2023), p.3 | https://www.rfs.nsw.gov.au/__data/assets/pdf_file/0007/253267/Bush-Fire-Bulletin-V45-No1-2023.pdf | Hill End/Tambaroora (Alpha Rd) fire: "At least six homes and five outbuildings ... destroyed and a further nine damaged" | 2 estimates (split by area) | Whole-fire figure solid; council split unknown |
| AIDR Major Incidents Report 2022-23, case study 5 (in repo, `data/house_loss/aidr/`) | https://knowledge.aidr.org.au/media/10344/aidr_major-incidents-report_2022-23.pdf | Alpha Rd fire: "Six houses and one facility were destroyed, four homes damaged" | same 2 rows | As above |
| NSW Coroner, 2019/20 Bushfires Inquiry Vol 1, ch.10 p.234 | https://coroners.nsw.gov.au/documents/reports/bushfires/2019-20-NSW-Bushfires-Coronial-Inquiry-Vol1.pdf | Bees Nest fire (Armidale Regional, Clarence Valley, Bellingen): "At least 9 residences were destroyed" | 1 weak (the only row at 5% or more) | Lower bound; council split unknown |
| RFS media release 5 Nov 2016, Llandilo assessment | https://www.rfs.nsw.gov.au/news-and-media/media-releases/llandilo-bush-fire-assessment | "No homes have been destroyed." (4 houses damaged) | 1 weak | Fire date differs from the row (4 Nov vs 13 Nov 2016) |

### 2B. New sources (not in the repo)

| Source | URL | What it says | Rows | Reliability |
|---|---|---|---:|---|
| RFS media release 3 Apr 2018, "Bush Fire Danger Period wraps up" (read in the browser) | https://www.rfs.nsw.gov.au/news-and-media/media-releases/bush-fire-danger-period-wraps-up | "2017/18 BFDP facts: ... 74 homes and 58 structures destroyed, 58 homes and 28 structures damaged" | supports the 27 estimates | Official |
| RFS media release 31 Mar 2024 | https://www.rfs.nsw.gov.au/news-and-media/media-releases/fire-season-comes-to-a-close-for-most-of-nsw | "A total of 29 homes, 142 outbuildings" in 2023/24 | 0 (14 homes unexplained) | Official total; too loose to fill |
| RFS media release 31 Mar 2017 (PDF) | https://www.rfs.nsw.gov.au/__data/assets/pdf_file/0011/53975/170331-Bush-fire-season-draws-to-a-close.pdf | 65 properties destroyed, 38 damaged | 0 | as above |
| ABC News 16 Aug 2018, Nowra/Kingiman | https://www.abc.net.au/news/2018-08-16/nsw-fires-shock-nowra-as-authorities-warn-conditions-dangerous/10123456 | "although no homes were destroyed" (RFS building impact teams: 1 house damaged, 11 outbuildings destroyed at Kingiman) | 1 reported (Shoalhaven, 0) | Medium; read through the fetch tool |
| ABC News 17 Feb 2023, Cowra | https://www.abc.net.au/news/2023-02-17/cowra-fire-threatens-properties-homes/101988150 | "A house has been destroyed in the blaze near Cowra." (RFS bulletin says only the roof was blown off) | 1 reported (duplicate link of AGRN 1055) | Medium |
| ABC News 21 Oct 2023, Girvan | https://www.abc.net.au/news/2023-10-21/nsw-weather-preview-hot-windy-bom-rfs-forecast-fire-danger/102998776 | "One home was been destroyed in the Booral Road fire at Girvan" | 1 reported (duplicate link of AGRN 1076) | Medium |
| ABC News 15 Jan 2024, Grawin | https://www.abc.net.au/news/2024-01-15/grawin-opal-fields-bushfire-recovery/103284620 | "locals believe about 16 camps and three residences where lost" (AIDR: 24 "properties") | 1 weak (Walgett) | Low |
| ABC News 16 Aug 2018, Bega (already used) | https://www.abc.net.au/news/2018-08-16/houses-destroyed-bega-fire/10129172 | RFS building impact list, 16 Aug 2018 | context | |

### 2C. Checked, cannot fill DL

| Source | URL | Finding |
|---|---|---|
| NSW Reconstruction Authority natural disaster declarations, FY2018-19 / 2022-23 / 2023-24 / 2024-25 (FY2017-18 page gives 404) | https://www.nsw.gov.au/departments-and-agencies/nsw-reconstruction-authority/about-us/recovery/natural-disaster-declarations/fy-2023-24 (same path with fy-2018-19, fy-2022-23, fy-2024-25) | Dates, LGAs and DRFA assistance only; no damage counts. All ten 2024-25 bushfire declarations list "counter disaster operations only" (weak sign of low loss, not a zero). |
| Disaster Assist event pages | https://www.disasterassist.gov.au/Pages/disasters/new-south-wales/tamworth-bushfire-26-October-4-November-2023.aspx | Read in the browser: assistance measures and LGAs only. The fetch tool gets HTTP 403. |
| NSW Natural Hazards Science hub, bushfire datasets | https://naturalhazardsscience-hub.seed.nsw.gov.au/bushfire-related-datasets | 19 datasets (vegetation, extent, severity, bush fire prone land); none records buildings destroyed. |
| RFS Building Impact Assessment program (service standard 3.1.15) | https://www.rfs.nsw.gov.au/__data/assets/pdf_file/0004/8932/3.1.15-Bush-Fire-Building-Impact-Analysis.pdf | Seen in search results only, not opened. The RFS collects the data for every fire that destroys or damages a habitable structure; only one-off PDFs (2019) are published. A GIPA or research request to the RFS is the systematic route. |
| RFS Major Fire Update pages | https://www.rfs.nsw.gov.au/fire-information/major-fire-updates/mfu?id=863 | Page shows only the site template to the fetch tool. |
| RFS end-of-season release 2025 | https://www.rfs.nsw.gov.au/news-and-media/media-releases/fire-season-wraps-up-for-most-of-nsw | 2025 (2024-25 season): no loss count at all. The RFS Bush Fire Bulletin Vol 47 No 1 foreword (read by a helper agent, URL not recorded) says "property losses across the season were minimal": qualitative only. |
| ICA catastrophe list (workbook column `DL_insurance_loss_raw`) | in the workbook | Only 3 of the 128 missing rows link to an ICA catastrophe (Tenterfield Nov 2016 $1m; Mid-Western and Upper Hunter, Feb 2017, $33.5m). Insured dollars at catastrophe level, no home counts. The 3 rows are deliberately left out of the estimated zeros. |
| ABS, DRFA claim data | not found | No ABS or DRFA product I could find records homes destroyed by fire and council. Not searched in depth. |

### 2D. Not done (needs a higher web-search limit and/or your OK)

- Not searched at all: Tamworth (AGRN 1134), Parkes (1137), Lake Macquarie (1133), Richmond Valley (1138), Lithgow (1136), Singleton Dec 2023 (1140), Mid-Western Dec 2023 (1139), Cootamundra-Gundagai (1065); council annual reports for 2017/18-2018/19 (Glen Innes, Inverell, Armidale, Tamworth, Snowy Valleys, Lithgow, Bathurst, Mid-Coast, Cessnock, Singleton, Muswellbrook, Richmond Valley, Kyogle, Clarence Valley); NSW Parliament questions on notice; Hansard for 2017-19 and 2023-25.
- Unreadable by the fetch tool (over its 10 MB cap): RFS Bush Fire Bulletins 38(3), 39(1), 45(2), 46(2), RFS Annual Report 2022/23. Trove holds the full Bulletin series.
- Would need your OK before downloading: council annual-report PDFs (typically 2-10 MB each), the bulletins above (over 10 MB each). Coroner Vol 1 (about 7.5 MB, 420 pp) is already in the repo.
- Wikipedia season pages gave leads (e.g. one home at Home Rule, Mid-Western, Oct 2023; two homes near Cessnock, Dec 2023) that no ABC page I opened confirmed; not used.

## 3. How many missing rows each source could fill

| Tier / flag | Rows | Source(s) | Reliability |
|---|---:|---|---|
| `original_sourced` | 90 | existing dataset | as before |
| `reported_new` | 3 | ABC (citing RFS building impact teams) | medium; two are the same physical fire already counted under another declaration |
| `inferred_zero_season` | 42 | RFS season totals: 2015/16 (1 row), 2018/19 (20), 2022/23 (21) | medium (see the assumptions below) |
| `reported_weak` | 3 | Coroner Bees Nest (>=9); ABC Grawin (3); RFS Llandilo (0) | low |
| `estimated_area_share` | 2 | RFS bulletin 45(1) / AIDR: Hill End 6 homes split Bathurst 0.58 / Mid-Western 5.42 by burned area | low (an estimate; the dataset's own "area share" proxy) |
| `estimated_zero_season_budget` | 27 | 2017/18 rows; RFS total leaves 3 homes unexplained | low |
| `estimated_zero_small_fire` | 41 | size rule: under 2% of the council and under 5,000 ha, no loss found | low |
| `missing` | 10 | see `out/STILL_MISSING.csv` | |

**Season budget** (`out/SEASON_BUDGET.csv`). Official total minus homes already attributed to named fires; a zero is inferred only if the leftover is at most 1 home.

| Season | RFS homes destroyed | In the 218 rows | Named fires outside the rows | Leftover | Rule |
|---|---:|---:|---:|---:|---|
| 2015/16 | 1 | 0 | 0 | 1 | inferred zero (1 row) |
| 2016/17 | 65 | 38 | 19 (Pappinbarra 6, Boggabri 1, Carwoola 11, Currandooley 1) | 8 | too loose |
| 2017/18 | 74 | 71 (Tathra 65, Port Macquarie-Hastings 6) | 0 | 3 | estimate (27 rows) |
| 2018/19 | 37 | 36 (Bega 4, Inverell 14, Tenterfield 18) | 0 | 1 | inferred zero (20 rows) |
| 2022/23 | 8 | 2 (Cowra 1, Upper Lachlan 1) | 6 (Hill End) | 0 | inferred zero (21 rows) |
| 2023/24 | 29 | 15 | 0 | 14 | too loose |

Assumptions behind the inferred zeros (each could fail): the RFS "habitable structures" equal the dataset's "homes" (one uninhabited building is counted inside 2016/17 lists); the values already in the dataset are right (if Bega Valley 2018 were 2 rather than 4, the 2018/19 leftover becomes 3 and those 20 rows drop to the estimate tier); "at least six" at Hill End is exactly six and Cowra is counted. At most one home can be wrong across all 42 inferred rows if the assumptions hold.

**Back-test of the size rule.** Among the 18 known non-Black-Summer rows that meet it (under 2% and under 5,000 ha), 13 are zero and 5 are not (Cowra 1, Cessnock 5, Port Macquarie-Hastings 6, Kempsey 2, and **Bega Valley 65, the Tathra fire, 0.22% of the council**). Known rows lean towards reported losses, so the true error rate is probably lower, but small fires can destroy many homes. Treat `estimated_zero_small_fire` as a sensitivity, not data.

## 4. Fill rule

1. Keep the 90 original values.
2. Add a value only when a source states it for a fire that is one of the row's fires, in that council (`reported_new`). Where the same physical fire is linked to two declarations, the figure is copied to the row that lacked it and the note says so. I rejected agent matches where the dates or fires differ (Penrith r12 down-graded to weak, Mid-Western r17 and Upper Hunter r23 left missing because the 35 Sir Ivan homes have no council split, Cessnock r16 which matched a January 2017 fire, Kempsey/Clarence Valley figures from the 1071 declaration that belong to other declarations).
3. If an official statewide season total is used up (leftover of 1 or less), set the other rows in that season to 0 (`inferred_zero_season`), the same logic the dataset already applies to deaths (`season_zero` / `statewide_zero`).
4. Everything else is flagged as an estimate and only enters variant v3. Never use v3 values as if they were reported.
5. Rates and the DL pillar rank are recomputed inside each variant exactly as `xy_format.build_y` does (homes / dwellings_census x 1000, then percentile rank); `DL_v0_original` reproduces the workbook DL to 1e-9.

## 5. New file and coverage

`DL_FILLED.csv` (218 rows). Columns: keys, `dwellings`, `value` (homes destroyed, original or filled), `DL_fill_flag`, `fill_source_url`, `fill_source_quote`, `fill_note`, `fill_scope`, and for each variant `homes_per_1000_v*` and the pillar `DL_v0_original`, `DL_v1_reported`, `DL_v2_inferred`, `DL_v3_estimated`. The sources per filled row are in `fill_table.csv`.

| Variant | Flags included | Rows with DL (of 218) | Non-Black-Summer (of 168) | Fires >= 5% (of 38) |
|---|---|---:|---:|---:|
| v0 original | original | 90 (41%) | 40 | 37 |
| v1 reported | + reported_new | 93 (43%) | 43 | 37 |
| v2 inferred | + inferred_zero_season | 135 (62%) | 85 | 37 |
| v3 estimated | + reported_weak, estimated_* | 208 (95%) | 158 | 38 |

Share of zero values: v0 42%, v1 42%, v2 60%, v3 72%.

## 6. Before vs after: Spearman of the Experiment 6 v2 score and its blocks against DL

Council-cluster bootstrap, 2,000 draws, 95% interval, same algorithm as Experiment 6 with one seeded stream per cell and the same resampled councils for before and after (so the change has its own interval). The "before" point estimates are identical to `VALIDATION_ROW_LEVEL_v2.csv` (risk_add 0.435, H 0.369, E 0.411, V 0.384); interval ends can differ in the second decimal because Experiment 6 used one random stream across all cells. Scores are pre-fire and do not change. Full table incl. F and the exploratory H+V mean: `out/RERUN_SPEARMAN.csv`.

**All 218 rows**

| Score | v0 original (n=90) | v1 reported (93) | v2 inferred (135) | v3 estimated (208) |
|---|---|---|---|---|
| risk_add | +0.43 [+0.22, +0.61] | +0.42 [+0.20, +0.59] | +0.42 [+0.25, +0.54] | +0.27 [+0.12, +0.39] |
| H hazard | +0.37 [+0.14, +0.58] | +0.34 [+0.11, +0.54] | +0.39 [+0.20, +0.55] | +0.27 [+0.11, +0.41] |
| E exposure | +0.41 [+0.15, +0.61] | +0.40 [+0.15, +0.59] | +0.42 [+0.24, +0.55] | +0.23 [+0.06, +0.37] |
| V vulnerability | +0.38 [+0.16, +0.56] | +0.37 [+0.15, +0.55] | +0.29 [+0.11, +0.43] | +0.25 [+0.11, +0.35] |
| change in risk_add vs v0 | | -0.02 [-0.06, +0.00] | -0.02 [-0.14, +0.12] | -0.16 [-0.30, -0.01] |

**Fires burning >= 5% of the council (38 rows; 37 have DL before)**

| Score | v0 (n=37) | v1 | v2 | v3 (n=38) |
|---|---|---|---|---|
| risk_add | +0.43 [+0.10, +0.68] | same | same | +0.39 [+0.07, +0.65] |
| H | +0.17 [-0.17, +0.48] | same | same | +0.15 [-0.18, +0.44] |
| E | +0.35 [-0.07, +0.67] | same | same | +0.33 [-0.09, +0.65] |
| V | +0.39 [+0.11, +0.61] | same | same | +0.36 [+0.08, +0.58] |

The one added row is Clarence Valley (AGRN 880). With that row set to 0, 9 (used) or 168 (the whole-season council figure), risk_add is +0.37, +0.39 or +0.44 and V is +0.35, +0.36 or +0.40.

**Extras that go beyond what was asked (where the fill matters most)**

| Excluding Black Summer | v0 (n=40) | v2 (n=85) | v3 (n=158) |
|---|---|---|---|
| risk_add | +0.48 [+0.13, +0.71] | +0.41 [+0.16, +0.57] | +0.24 [+0.03, +0.39] |
| H | +0.21 [-0.18, +0.52] | +0.28 [+0.01, +0.49] | +0.15 [-0.06, +0.35] |
| E | +0.44 [+0.10, +0.66] | +0.35 [+0.08, +0.54] | +0.15 [-0.07, +0.32] |
| V | +0.59 [+0.31, +0.78] | +0.43 [+0.23, +0.57] | +0.34 [+0.19, +0.44] |

Multiple imputation: the 68 rows filled by rules (`estimated_zero_*`) were replaced 300 times by draws from the known non-Black-Summer rows under 2% burned (a pool with 38% non-zero, so it leans towards more loss). Point estimates across draws (median, 2.5-97.5%): risk_add all rows +0.29 [+0.23, +0.34], excluding Black Summer +0.24 [+0.15, +0.32]; V +0.22 [+0.17, +0.29] and +0.24 [+0.14, +0.34]. (`out/SENSITIVITY.csv`, `out/06_sensitivity.log`.)

**Reading**

- **Fires at least 5% burned: no change.** DL was already there for 37 of 38, so filling small fires cannot move it; the one new row moves risk_add by less than 0.06 for any value from 0 to 168. V stays the clearest block (interval excludes zero); H and E still cross zero.
- **All rows, reported + inferred (v2, 135 rows):** risk_add, H and E are unchanged to two decimals (+0.42, +0.39, +0.42); V falls from +0.38 to +0.29 but the change interval [-0.20, +0.03] includes zero. This is the version I would use: about 1.5 times as many rows, with no estimated cell.
- **Adding the estimated zeros (v3):** every coefficient shrinks by roughly a third (risk_add -0.16 [-0.30, -0.01]); all four still exclude zero. Expected: 72% of values are then zero (heavy ties cap Spearman) and the added rows are small fires where DL is about 0 whatever the council. A loss-leaning imputation gives +0.29, so the shrinkage is not driven by the "zero" assumption alone.
- **Outside Black Summer** (never testable before with only 40 rows): risk_add +0.41 [+0.16, +0.57] on 85 rows without estimates. The DL link is not a Black Summer artefact.
- No sign flips, no reordering of blocks that the intervals could support. The F block stays at about zero (-0.08 to +0.03), unchanged from Experiment 6.
- Not re-run: the composite Y, Y_class, or the other pillars. Filling DL re-bases every DL percentile rank, so Y would shift; a class floor (10 or more homes) is only hit by the rows that were already positive.

## 7. Things noticed in the existing values (not changed)

- Kempsey / AGRN 1076 holds 4 homes (ABC 19 Oct 2023, interim). A helper agent found later ABC/AAP counts of 7 for the Willi Willi Rd fire (medium/low confidence, news). Worth a check.
- Clarence Valley / AGRN 871 = 168 is the NBRA whole-season council figure and already contains the Bees Nest homes; do not add the AGRN 880 figure to it.
- Two fires appear under two declarations (Conimbla Rd, Booral Rd); the dataset counts the home under one only, so before the fill the same fire had DL in one row and none in the other.
- Port Macquarie-Hastings / NSW1718-05 = 6 (RFS Bush Fire Bulletin 39(1), official) versus 2 in the day-after ABC report; the official figure is the one in use, and 2017/18's leftover depends on it.
- RFS "homes" and "habitable structures" include uninhabited buildings in some lists (White Cedars Rd, Dondingalong, 2017).
- Hudson fire: AIDR says 24 "properties"; the RFS 2023/24 statewide total is only 29 homes, so the 24 cannot all be houses.

## 8. Limits

- The estimated tier is a rule, not evidence. Use v1 or v2 for anything that needs to stand up; use v3 only as a sensitivity.
- Quotes from ABC/RFS web pages passed through the fetch tool's summariser; I re-read the ones that decide a number (RFS 2018 and 2024 releases, Bees Nest, Grawin, local RFS and AIDR text). PDF text was read locally by the agents from the tool's cache.
- Agents' searches were cut off by the search budget; 10 rows are still empty and some rows are zero only by the rules.
- Process: no commits, no writes outside this folder, no ACM sources.

## 9. Files

| File | What |
|---|---|
| `DL_FILLED.csv` | **new filled DL columns with flags** |
| `fill_table.csv` | every filled cell with value, flag, source URL, quote, note |
| `out/DL_ROW_STATUS.csv`, `out/ROW_LISTING_BY_EVENT.md` | DL present or missing for each of 218 rows |
| `out/PROFILE_BY_YEAR.csv`, `PROFILE_BY_SIZE.csv`, `PROFILE_BY_COUNCIL.csv`, `PROFILE_BY_EVENT.csv` | missingness profile |
| `out/SEASON_BUDGET.csv` | official totals vs attributed homes |
| `out/RERUN_SPEARMAN.csv`, `out/SENSITIVITY.csv`, `out/*.log` | before/after and sensitivity numbers |
| `out/STILL_MISSING.csv` | the 10 rows with no value in any variant |
| `research/` | helper-agent briefs, findings and notes (source-by-source detail) |
| `01_...06_*.py`, `common.py`, `spearman_check.py`, `check_sources.py`, `run_all.sh` | code; `./run_all.sh` reproduces everything (about 2 minutes) |

---

## Appendix: DL present or missing for every event and council (218 rows)

Values in brackets: homes destroyed (present) or share of the council burned (missing).

| agrn | event (declaration) | start | councils with DL (homes destroyed) | councils MISSING DL (share burned) |
|---|---|---|---|---|
| RAA-raa_2015_p15_r01 | Bushfire (NSW RAA annual report, onset 2015-03-01) | 2015-03-04 | Narrabri (0) | - |
| RAA-raa_2015_p15_r05 | Bushfire (NSW RAA annual report, onset 2015-08-02) | 2015-07-31 | Blue Mountains (0) | - |
| RAA-raa_2015_p15_r11 | Bushfire (NSW RAA annual report, onset 2015-12-11) | 2015-12-09 | Hawkesbury (0) | - |
| RAA-raa_2015_p15_r09 | Bushfire (NSW RAA annual report, onset 2015-11-26) | 2015-12-10 | - | Shoalhaven (0.00%) |
| RAA-raa_2016_p13_r08 | Bushfire (NSW RAA annual report, onset 2016-11-05) | 2016-11-04 | Cessnock (0); Dungog (0); Mid-Coast (0); Port Stephens (0) | - |
| RAA-raa_2016_p13_r07 | Bushfire (NSW RAA annual report, onset 2016-11-05) | 2016-11-05 | - | Tenterfield (1.03%) |
| RAA-raa_2016_p13_r06 | Bushfire (NSW RAA annual report, onset 2016-11-05) | 2016-11-05 | Kempsey (0) | - |
| RAA-raa_2016_p13_r12 | Bushfire (NSW RAA annual report, onset 2016-11-13) | 2016-11-13 | - | Penrith (0.68%) |
| RAA-raa_2016_p13_r16 | Bushfire (NSW RAA annual report, onset 2016-12-13) | 2016-12-13 | - | Cessnock (0.61%) |
| RAA-raa_2016_p13_r17 | Bushfire (NSW RAA annual report, onset 2017-01-12) | 2017-01-11 | - | Mid-Western Regional (0.14%) |
| RAA-raa_2016_p13_r22 | Bushfire (NSW RAA annual report, onset 2017-01-18) | 2017-01-14 | Cessnock (0) | - |
| RAA-raa_2016_p13_r23 | Bushfire (NSW RAA annual report, onset 2017-02-11) | 2017-02-04 | Kempsey (2); Mid-Western Regional (1); Warrumbungle Shire (35) | Mid-Coast (1.84%); Upper Hunter Shire (1.73%) |
| RAA-raa_2016_p13_r26 | Bushfire (NSW RAA annual report, onset 2017-02-19) | 2017-02-11 | - | Singleton (0.49%) |
| 771 | Kempsey Bushfire: 27 August 2017 onwards | 2017-08-08 | - | Kempsey (3.11%) |
| 772 | Mid-Coast and Port Macquarie-Hastings Bushfires: 30 August 2017 onward | 2017-08-16 | - | Mid-Coast (0.40%); Port Macquarie-Hastings (0.67%) |
| 770 | Cessnock Bushfire: 12 September 2017 onwards | 2017-09-03 | Cessnock (0) | - |
| NSW1718-05 | Mid-Coast, Port Macquarie-Hastings, Dungog and Upper Hunter Bushfires: | 2017-09-05 | Port Macquarie-Hastings (6) | Dungog (0.57%); Mid-Coast (0.66%); Upper Hunter Shire (0.04%) |
| 776 | Tenterfield Bushfires: 8 September 2017 onwards | 2017-09-06 | - | Tenterfield (1.70%) |
| NSW1718-06 | Kempsey and Port Macquarie-Hastings Bushfire: 5 December 2017 onwards | 2017-12-05 | - | Kempsey (0.85%); Port Macquarie-Hastings (1.98%) |
| NSW1718-08 | Tamworth Bushfire: 25 December 2017 onwards | 2017-12-17 | - | Tamworth Regional (0.29%) |
| NSW1718-09 | Tamworth, Uralla and Gwydir Bushfires: 2 January 2018 onwards | 2017-12-17 | - | Gwydir (0.32%); Tamworth Regional (1.72%); Uralla (0.39%) |
| 792 | Singleton Bushfires: 18 December 2017 onwards | 2017-12-18 | - | Singleton (0.02%) |
| NSW1718-15 | Upper Hunter Bushfires: 23 January 2018 onwards | 2018-01-02 | - | Upper Hunter Shire (0.31%) |
| NSW1718-10 | Port Stephens Bushfire: 8 January 2018 onwards | 2018-01-08 | Port Stephens (0) | - |
| NSW1718-11 | Singleton, Cessnock and Muswellbrook Bushfires: 13 January 2018 onward | 2018-01-08 | - | Cessnock (0.03%); Muswellbrook (0.01%); Singleton (4.12%) |
| NSW1718-12 | Narrabri and Warrumbungle Bushfires: 17 January 2018 onwards | 2018-01-17 | - | Narrabri (3.19%); Warrumbungle Shire (1.63%) |
| NSW1718-13 | Upper Lachlan (Long Gully) Bushfire: 19 January 2018 onwards | 2018-01-19 | - | Upper Lachlan Shire (0.35%) |
| NSW1718-14 | Sutherland (Royal National Park) Bushfire: 20 January 2018 onwards | 2018-01-21 | Sutherland Shire (0) | - |
| NSW1718-16 | Muswellbrook and Mid-Western Bushfires: 23 January 2018 onwards | 2018-01-23 | - | Mid-Western Regional (0.09%); Muswellbrook (0.15%) |
| NSW1718-17 | NSW Central West Bushfires: 9 February 2018 onwards | 2018-02-09 | Cabonne (0) | Bathurst Regional (0.07%) |
| NSW1718-19 | Narrabri and Gwydir (Bobbiwaa Creek) Bushfire: 12 February 2018 onward | 2018-02-11 | - | Gwydir (0.32%); Narrabri (0.14%) |
| NSW1718-18 | Lithgow Bushfire: 12 February 2018 onwards | 2018-02-12 | - | Lithgow (0.06%) |
| NSW1718-20 | Bega Bushfire (Tathra / Reedy Swamp): 18 March 2018 onwards | 2018-03-18 | Bega Valley (65) | - |
| NSW1718-21 | Liverpool and Sutherland Bushfire: 14 April 2018 onwards | 2018-04-14 | Liverpool (0); Sutherland Shire (0) | - |
| 823 | Richmond Valley, Lismore and Kyogle bushfires: 12 August 2018 onwards | 2018-07-23 | - | Kyogle (0.05%); Richmond Valley (4.08%) |
| 819 | Cessnock and Port Stephens bushfires: 15 August 2018 onwards | 2018-07-23 | Port Stephens (0) | Cessnock (0.37%) |
| 824 | Clarence Valley and Glen Innes Severn bushfires: 14 August 2018 onward | 2018-07-26 | - | Clarence Valley (3.44%); Glen Innes Severn (0.30%) |
| 818 | Shoalhaven bushfires: 11 August 2018 onwards | 2018-07-29 | - | Shoalhaven (0.51%) |
| 820 | Bega Valley and Eurobodalla bushfires: 15 August 2018 onwards | 2018-08-13 | Bega Valley (4) | Eurobodalla (0.13%) |
| 841 | Tamworth (Rockview) Bushfire: 30 October 2018 onwards | 2018-10-30 | - | Tamworth Regional (0.14%) |
| 842 | Port Stephens and Cessnock Bushfires: 22 November 2018 onwards | 2018-11-21 | - | Cessnock (0.06%); Port Stephens (2.45%) |
| 847 | Armidale (Melrose) Bushfire: 1 December 2018 onwards | 2018-12-01 | - | Armidale Regional (0.44%) |
| 851 | Glen Innes Severn (Highland Creek) Bushfire: 25 December 2018 onwards | 2018-12-25 | - | Glen Innes Severn (0.88%) |
| 855 | Tamworth (Halls Creek Road) Bushfire: 3 January 2019 onwards | 2019-01-03 | - | Tamworth Regional (0.26%) |
| 853 | Parkes and Cabonne (Curembenya) Bushfire: 5 January 2019 onwards | 2019-01-03 | Cabonne (0); Parkes (0) | - |
| 866 | Newcastle (Kooragang Island) Bushfires: 5 January 2019 onwards | 2019-01-04 | - | Newcastle (0.56%) |
| 862 | Tamworth Regional and Upper Hunter Bushfires: 11 February 2019 onwards | 2019-01-16 | - | Tamworth Regional (0.02%); Upper Hunter Shire (0.00%) |
| 860 | Snowy Valleys Bushfires: 17 January 2019 onwards | 2019-01-17 | - | Snowy Valleys (0.93%) |
| 867 | Singleton and Muswellbrook Bushfires: 11 February 2019 onwards | 2019-02-04 | - | Muswellbrook (0.01%); Singleton (0.00%) |
| 843 | Northern NSW Bushfires: 11 February 2019 onwards | 2019-02-09 | Inverell (14); Tenterfield (18) | Armidale Regional (0.00%) |
| 864 | Tenterfield Bushfires: 9 March 2019 onwards | 2019-03-09 | - | Tenterfield (0.91%) |
| 880 | NSW North Coast Bushfires: Commencing 18 July 2019 onwards | 2019-07-12 | Kempsey (1); Richmond Valley (2) | Clarence Valley (7.93%); Kyogle (0.18%); Mid-Coast (0.30%); Nambucca Valley (0.00%); Port Macquarie-Hastings (0.61%) |
| 871 | NSW Bushfires: 31 August 2019 onwards | 2019-07-17 | Armidale Regional (12); Ballina (0); Bega Valley (467); Bellingen (0); Blue Mountains (22); Byron (0); Central Coast (NSW) (4); Cessnock (21); Clarence Valley (168); Coffs Harbour (17); Cootamundra-Gundagai Regional (0); Dungog (0); Eurobodalla (510); Glen Innes Severn (75); Goulburn Mulwaree (1); Greater Hume Shire (8); Gwydir (0); Hawkesbury (19); Inverell (1); Kempsey (68); Ku-ring-gai (0); Kyogle (6); Lake Macquarie (0); Lismore (2); Lithgow (54); Mid-Coast (125); Mid-Western Regional (10); Muswellbrook (0); Nambucca Valley (64); Narrabri (0); Oberon (4); Penrith (0); Port Macquarie-Hastings (26); Queanbeyan-Palerang Regional (57); Richmond Valley (62); Shoalhaven (285); Singleton (1); Snowy Monaro Regional (31); Snowy Valleys (193); Sutherland Shire (0); Tamworth Regional (0); Tenterfield (54); Tweed (1); Upper Hunter Shire (0); Upper Lachlan Shire (3); Uralla (0); Wagga Wagga (0); Walcha (22); Wingecarribee (68); Wollondilly (19) | - |
| 1053 | Gwydir and Narrabri NSW Bushfires – 18 January 2023 | 2023-01-14 | - | Gwydir (0.32%); Narrabri (0.02%) |
| 1065 | Cootamundra Gundagai Bushfires from 25 January 2023 | 2023-01-25 | - | Cootamundra-Gundagai Regional (0.17%) |
| 1055 | Western and North West NSW Bushfires – 17 February 2023 | 2023-02-06 | Cowra (1) | Blayney (0.00%); Cabonne (0.03%); Liverpool Plains (0.28%); Upper Hunter Shire (0.07%) |
| 1066 | Upper Lachlan and Yass Valley Bushfires from 11 February 2023 | 2023-02-10 | - | Upper Lachlan Shire (0.17%); Yass Valley (0.56%) |
| 1052 | NSW Bushfires 6 March 2023 | 2023-02-16 | - | Bathurst Regional (0.48%); Bogan (0.47%); Brewarrina (0.00%); Cabonne (0.03%); Coonamble (0.01%); Cowra (0.17%); Dubbo Regional (0.26%); Mid-Western Regional (1.96%); Upper Hunter Shire (0.06%); Walgett (0.20%); Warren (0.00%) |
| 1054 | Gwydir, Moree Plains and Narrabri NSW Bushfires – 1 March 2023 | 2023-02-28 | - | Gwydir (0.00%); Moree Plains (0.02%); Narrabri (0.39%) |
| 1056 | Upper Lachlan Bushfires – 16 March 2023 | 2023-03-09 | Upper Lachlan Shire (1) | Cobar (0.25%) |
| 1131 | Upper Hunter NSW Bushfire 10 – 17 August 2023 | 2023-08-10 | - | Upper Hunter Shire (0.25%) |
| 1071 | North Eastern NSW Bushfires from 21 August 2023 | 2023-08-12 | - | Armidale Regional (0.31%); Clarence Valley (1.72%); Kempsey (1.95%); Nambucca Valley (0.24%) |
| 1099 | Singleton NSW Bushfires 11 September – 18 October 2023 | 2023-08-29 | - | Singleton (0.29%) |
| 1089 | Mid Coast NSW Bushfires – 20 September 2023 | 2023-09-09 | - | Mid-Coast (0.63%) |
| 1090 | Lower Hunter NSW Bushfires – 20 September 2023 | 2023-09-12 | - | Cessnock (0.33%); Dungog (1.07%); Port Stephens (0.01%) |
| 1132 | Snowy Monaro NSW Bushfire 20 September – 4 October 2023 | 2023-09-14 | - | Snowy Monaro Regional (0.27%) |
| 1076 | Mid North NSW Bushfires from 16 October 2023 | 2023-09-18 | Kempsey (4); Mid-Coast (1) | Port Macquarie-Hastings (0.43%) |
| 1084 | Snowy Monaro NSW Bushfires – 2 October 2023 | 2023-09-18 | - | Snowy Monaro Regional (0.23%) |
| 1133 | Lake Macquarie NSW Bushfire 1 – 18 October 2023 | 2023-09-27 | - | Lake Macquarie (0.21%) |
| 1075 | Far North NSW Bushfires from 13 October 2023 | 2023-09-30 | Clarence Valley (2); Tenterfield (1) | Inverell (1.62%); Kyogle (0.75%) |
| 1083 | Mid-Western NSW Bushfires – 2 October 2023 | 2023-10-02 | - | Mid-Western Regional (0.22%) |
| 1070 | Bega Valley NSW Bushfire from 3 October 2023 | 2023-10-03 | Bega Valley (2) | - |
| 1135 | Byron NSW Bushfire 14 October – 5 November 2023 | 2023-10-14 | - | Byron (1.38%) |
| 1091 | Hunter NSW Bushfires – 22 October - 5 November 2023 | 2023-10-22 | Upper Hunter Shire (0) | Muswellbrook (0.65%) |
| 1134 | Tamworth NSW Bushfire 26 October – 4 November 2023 | 2023-10-26 | - | Tamworth Regional (0.09%) |
| 1081 | North Western NSW Bushfires from 14 November 2023 | 2023-11-09 | - | Walgett (0.97%) |
| 1136 | Lithgow NSW Bushfire 11 – 17 November 2023 | 2023-11-10 | - | Lithgow (0.01%) |
| 1137 | Parkes NSW Bushfire 19 – 27 November 2023 | 2023-11-19 | - | Parkes (0.09%) |
| 1138 | Richmond Valley NSW Bushfire 4 – 15 December 2023 | 2023-12-01 | - | Richmond Valley (0.17%) |
| 1114 | Inverell and Tenterfield NSW Bushfires 7 – 24 December 2023 | 2023-12-03 | - | Inverell (1.53%); Tenterfield (0.74%) |
| 1139 | Mid-Western NSW Bushfire 6 – 16 December 2023 | 2023-12-06 | - | Mid-Western Regional (0.01%) |
| 1140 | Singleton NSW Bushfire 8 – 18 December 2023 | 2023-12-07 | - | Singleton (0.05%) |
| 1093 | Narrabri NSW Bushfires - 8 December 2023 | 2023-12-08 | Narrabri (0) | - |
| 1112 | Armidale NSW Bushfires 09 – 24 December 2023 | 2023-12-08 | - | Armidale Regional (1.05%) |
| 1092 | Cessnock NSW Bushfires - 14 December 2023 | 2023-12-11 | Cessnock (5) | - |
| 1121 | Clarence Valley NSW Bushfires, 21 January – 13 February 2024 | 2024-01-21 | - | Clarence Valley (0.47%) |
| 1156 | Tenterfield NSW Bushfire 2 September 2024 – 16 September 2024 | 2024-08-31 | - | Tenterfield (0.30%) |
| 1191 | Singleton NSW Bushfire from 16 December to 24 December 2024 | 2024-12-16 | - | Singleton (0.44%) |
| 1193 | Bathurst and Lithgow NSW Bushfire from 23 December 2024 to 11 January  | 2024-12-23 | - | Bathurst Regional (0.19%); Lithgow (0.60%) |
| 1189 | Singleton and Muswellbrook NSW Bushfires from 27 December 2024 to 18 J | 2024-12-24 | - | Muswellbrook (0.83%); Singleton (0.46%) |
| 1190 | Yass Valley NSW Bushfire from 27 December 2024 to 7 January 2025 | 2024-12-27 | - | Yass Valley (0.03%) |
| 1192 | Tamworth and Uralla NSW Bushfires from 27 December 2024 to 9 January 2 | 2024-12-27 | - | Tamworth Regional (0.35%); Uralla (0.22%) |
| 1196 | Mid-Western NSW Bushfires from 27 December 2024 to 8 January 2025 | 2024-12-27 | - | Mid-Western Regional (0.02%) |
| 1197 | Hawkesbury NSW Bushfire from 5 January to 16 January 2025 | 2025-01-05 | - | Hawkesbury (0.17%) |
| 1199 | NSW Narrabri and Gwydir Bushfire from 27 January to 10 February 2025 | 2025-01-20 | - | Gwydir (0.06%); Narrabri (0.00%) |
| 1203 | NSW Warrumbungle and Narrabri Bushfires from 26 February to 13 March 2 | 2025-02-18 | Narrabri (0); Warrumbungle Shire (0) | - |