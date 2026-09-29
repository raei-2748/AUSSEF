# Fresh test of the Experiment 6 risk score on two independent fires (2026-09-29)

**Verdict: CANNOT TELL.** Rule and numbers were frozen before any outcome was computed (`PRESPEC.md`, hash in `PRESPEC.lock`; one dated amendment; score table hashed in `SCORES.lock` before Y was built; Y inputs and test script hashed in `Y.lock`). The test was run once.
Nothing was committed or pushed. `Experiment 6/REPORT.md` was not edited. The master workbook, `data/aussef.duckdb` and `fire_event_dataset/out/` are byte-identical before and after (section 9).

## 1. Plain summary (5 lines)

1. On 26 council rows from two fires that are independent of Black Summer (NSW Oct 2013, 13 rows; Victoria Black Saturday 7 Feb 2009, 13 rows), the score's rank correlation with the new impact measure is **+0.00, 95% interval [-0.40, +0.40]**. Each fire alone is also about zero (NSW -0.07, Victoria +0.10). By the rule fixed in advance (replicated only if the interval is above 0, not replicated only if its top is below +0.30) this is "cannot tell".
2. The interval rules out effects as large as the earlier headline (+0.58 on large NSW fires) but not effects around +0.3. The power check says why: with these 26 rows a true correlation of 0.4 would be detected only 52% of the time (0.5: 79%), and a true zero would be declared "not replicated" only 31% of the time. The test was too small to settle it either way; nothing here supports the score, and nothing convicts it.
3. The best-covered pillar goes the wrong way: score vs homes destroyed per 1,000 dwellings (DL) is **-0.60 [-0.92, -0.04] on 11 rows** (NSW alone -0.29, interval includes 0). Only 5 of those 11 values are reported counts; 6 NSW zeros are inferred; Victoria has a council figure for just 2 of 13 councils. Descriptive, pre-declared, not the verdict.
4. Less could be built than hoped. NSW 2013: hazard, exposure and vulnerability blocks (the finance block was dropped by the frozen comparability rule). Victoria: vulnerability only (no hazard layer, no comparable finance). Impact: income and business counts for both fires, council finances for NSW only (low confidence), homes destroyed for 13 of 28 rows, no social-loss pillar for anyone; 11 of 13 Victorian rows have a single pillar.
5. Two events, 26 rows, different source vintages and Victoria's score is one block; this is a small, honest, inconclusive test, not a refutation. Getting further needs a Victorian hazard/vegetation layer (needs your OK) and council-level house-loss counts for Victoria that I could not reach.

## 2. What was tested (frozen; details in `PRESPEC.md`)

- **Score:** `Experiment 6` v2 equal-weight `risk_add` (mean of hazard H, exposure E v2, vulnerability V, fiscal F), each item a 0-1 percentile in the **original 129-council NSW distribution** (new values placed in it, nothing re-ranked). For each row `risk_add_avail` = mean of the blocks that exist. Secondary: V alone (S1), mean(H, V) (S2).
- **Rows:** every council with at least 1% of its area inside the event's fire polygons (Geoscience Australia outlines, same selection as the scoping overlay; the roster reproduced the scoping list exactly). NSW 15 rows (Wyong and Guyra were merged in 2016, no like-for-like council in the original 129, so no score: 13 scored); Victoria 13 rows (Unincorporated Vic excluded). 14 rows are at 5% or more.
- **Y_new:** the master's construction: each indicator signed so higher = worse, percentile of the new raw value in the **existing 218-row master distribution of that indicator** (I reproduced the master's ranks exactly first), pillar = mean of its indicator percentiles, `Y_new` = mean of pillars present, `pillars_n` recorded. Excess = change minus the median change of same-state councils with no fire of 100 ha or more in the window.
- **Test:** Spearman with a council-cluster bootstrap (5,000 draws, seed 20261001). Only the pooled primary test decides.

## 3. Results

### 3.1 Primary and per-event (score `risk_add_avail`, target `Y_new`)
| Scope | n | Spearman | 95% CI |
|---|---:|---:|---|
| **Pooled (verdict)** | 26 | **+0.00** | **[-0.40, +0.40]** |
| NSW Oct 2013 | 13 | -0.07 | [-0.64, +0.51] |
| Victoria 2009 | 13 | +0.10 | [-0.50, +0.62] |

Verdict rule applied: lower bound -0.40 is not above 0, upper bound +0.40 is not below +0.30, so **CANNOT TELL**. Both events have essentially zero estimates; pooling did not hide an effect. The pooled score mixes a three-block score (NSW, range 0.59-0.90) with a one-block score (Victoria, 0.07-0.62), which the pre-spec flagged; the cleaner pooled comparison is V alone (next table).

### 3.2 Pre-declared secondary and descriptive results (37 tests were run in all; none of these can change the verdict)
| Test | Scope | n | Spearman | 95% CI |
|---|---|---:|---:|---|
| V block alone (S1) vs Y_new | pooled | 26 | +0.14 | [-0.24, +0.51] |
| mean(H, V) (S2) vs Y_new (NSW only) | NSW = pooled | 13 | +0.04 | [-0.50, +0.65] |
| **DL only** (homes destroyed per 1,000 dwellings) | pooled | 11 | **-0.60** | **[-0.92, -0.04]** |
| DL only | NSW | 9 | -0.29 | [-0.83, +0.43] |
| DL only | Victoria | 2 | not estimable | |
| IL pillar (income, business counts) | pooled | 26 | +0.49 | [+0.12, +0.75] |
| IL pillar | NSW / Victoria | 13 / 13 | +0.05 / +0.40 | [-0.44, +0.61] / [-0.17, +0.79] |
| FP pillar | NSW (only event with FP) | 13 | -0.05 | [-0.68, +0.64] |
| Sensitivity (a): rows with 5%+ burned | pooled | 14 | +0.20 | [-0.39, +0.66] |
| Sensitivity (b): Y_new needs 2+ pillars (master rule) | pooled | 15 | -0.35 | [-0.76, +0.23] |
| Sensitivity (c): Y_new without FP | pooled | 26 | +0.03 | [-0.38, +0.41] |
| Sensitivity (d): DL from reported counts only | pooled | 5 | not estimable | |
| Sensitivity (f): Victorian IL from business counts only | pooled / Victoria | 26 / 13 | -0.39 / -0.26 | [-0.69, +0.02] / [-0.77, +0.34] |

Reading:
- **DL** (the pillar the earlier work said the score tracked, +0.43 in NSW 2015-2025) does not replicate here, but on 11 rows with mostly inferred zeros. NSW alone is -0.29 with a wide interval. The pooled -0.60 is inflated by the score mix: Victoria's two DL rows (Murrindindi, Nillumbik) are large losses but have modest V-only scores (Murrindindi 0.51, Nillumbik 0.07).
- **IL** is the one pillar with a positive pooled interval (+0.49). It is one of many descriptive comparisons, not the pre-set test, it is weaker inside each event (NSW +0.05), Victoria's income series has a documented break across the fire year, and the 218-row master result for IL was only +0.09. I do not read it as a replication.
- The sign of the primary result moves between definitions of Y (+0.03 without FP, -0.35 with two pillars, -0.39 when Victorian IL uses business counts only). That instability is what a near-zero underlying correlation on 13-row events looks like.

### 3.3 Planted-effect power check (fake Y, real rows; 1,000 simulations per cell; no real outcome used)
| Rows | n | planted rho | detected (CI lower > 0) | "not replicated" (CI upper < 0.30) |
|---|---:|---:|---:|---:|
| pooled primary | 26 | 0 | 2% | 31% |
| | | 0.1 | 7% | 13% |
| | | 0.2 | 14% | 6% |
| | | 0.3 | 33% | 2% |
| | | 0.4 | 52% | 0% |
| | | 0.5 | 79% | 0% |
| | | 0.6 | 93% | 0% |
| rows with 5%+ | 14 | 0.4 / 0.5 / 0.6 | 27% / 47% / 64% | |
| NSW rows | 13 | 0.4 / 0.5 / 0.6 | 27% / 44% / 62% | |
| Victoria rows | 13 | 0.4 / 0.5 / 0.6 | 25% / 43% / 59% | |

A null on 26 rows cannot exclude a true correlation of 0.3 (67% of runs would miss it) and even for 0.4 misses about half the time. Full file: `results/frozen_test/POWER_CHECK.csv`.

## 4. Pillar coverage per row
Source flags per cell are in the table file; `DL` status: reported / inferred (zero inferred, see 6) / blank. `Blocks` = which score blocks exist.

| Event | Council | Burned % | Homes destroyed (status) | Blocks | Score | V | DL | IL | FP | Pillars | Y_new |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| NSW 2013 | Hawkesbury | 18.2 | 2 (reported, lower bound) | HEV | 0.76 | 0.41 | 0.49 | 0.55 | 0.37 | 3 | 0.47 |
| NSW 2013 | Blue Mountains | 14.1 | 205 (reported) | HEV | 0.76 | 0.33 | 0.89 | 0.74 | 0.57 | 3 | 0.73 |
| NSW 2013 | Muswellbrook | 13.5 | 0 (inferred) | HEV | 0.60 | 0.30 | 0.22 | 0.88 | 0.49 | 3 | 0.53 |
| NSW 2013 | Lithgow | 8.3 | blank | HEV | 0.79 | 0.72 | | 0.81 | 0.36 | 2 | 0.58 |
| NSW 2013 | Port Stephens | 7.0 | 4 (reported) | HEV | 0.59 | 0.45 | 0.54 | 0.62 | 0.87 | 3 | 0.68 |
| NSW 2013 | Wollondilly | 3.0 | blank | HEV | 0.67 | 0.18 | | 0.30 | 0.54 | 2 | 0.42 |
| NSW 2013 | Wingecarribee | 2.6 | blank | HEV | 0.66 | 0.39 | | 0.44 | 0.42 | 2 | 0.43 |
| NSW 2013 | Clarence Valley | 2.4 | 0 (inferred) | HEV | 0.90 | 0.88 | 0.22 | 0.77 | 0.55 | 3 | 0.52 |
| NSW 2013 | Wyong (no score) | 2.2 | blank | none | | | | 0.10 | 0.61 | 2 | 0.35 |
| NSW 2013 | Guyra (no score) | 2.0 | 0 (inferred) | none | | | 0.22 | 0.42 | 0.26 | 3 | 0.30 |
| NSW 2013 | Cessnock | 1.9 | 0 (inferred) | HEV | 0.78 | 0.61 | 0.22 | 0.72 | 0.63 | 3 | 0.52 |
| NSW 2013 | Lake Macquarie | 1.9 | blank | HEV | 0.59 | 0.40 | | 0.70 | 0.19 | 2 | 0.44 |
| NSW 2013 | Shoalhaven | 1.7 | 0 (inferred) | HEV | 0.86 | 0.82 | 0.22 | 0.60 | 0.44 | 3 | 0.42 |
| NSW 2013 | Wollongong | 1.4 | 0 (inferred) | HEV | 0.61 | 0.51 | 0.22 | 0.60 | 0.70 | 3 | 0.51 |
| NSW 2013 | Singleton | 1.1 | 0 (inferred) | HEV | 0.63 | 0.14 | 0.22 | 0.92 | 0.22 | 3 | 0.46 |
| Vic 2009 | Murrindindi | 40.3 | 1,397 (reported, council figure) | V | 0.51 | 0.51 | 1.00 | 0.74 | N/A | 2 | 0.87 |
| Vic 2009 | Nillumbik | 23.2 | 135 (reported) | V | 0.07 | 0.07 | 0.89 | 0.33 | N/A | 2 | 0.61 |
| Vic 2009 | Yarra Ranges | 18.8 | blank | V | 0.27 | 0.27 | | 0.57 | N/A | 1 | 0.57 |
| Vic 2009 | Whittlesea | 17.2 | blank | V | 0.41 | 0.41 | | 0.05 | N/A | 1 | 0.05 |
| Vic 2009 | Mitchell | 12.6 | blank | V | 0.33 | 0.33 | | 0.39 | N/A | 1 | 0.39 |
| Vic 2009 | Latrobe | 10.9 | blank | V | 0.47 | 0.47 | | 0.55 | N/A | 1 | 0.55 |
| Vic 2009 | South Gippsland | 7.4 | blank | V | 0.49 | 0.49 | | 0.54 | N/A | 1 | 0.54 |
| Vic 2009 | Alpine | 7.3 | blank | V | 0.60 | 0.60 | | 0.40 | N/A | 1 | 0.40 |
| Vic 2009 | Baw Baw | 5.5 | blank | V | 0.37 | 0.37 | | 0.37 | N/A | 1 | 0.37 |
| Vic 2009 | Cardinia | 4.4 | blank | V | 0.26 | 0.26 | | 0.46 | N/A | 1 | 0.46 |
| Vic 2009 | Mount Alexander | 2.1 | blank | V | 0.62 | 0.62 | | 0.51 | N/A | 1 | 0.51 |
| Vic 2009 | Indigo | 2.1 | blank | V | 0.39 | 0.39 | | 0.47 | N/A | 1 | 0.47 |
| Vic 2009 | Wellington | 1.2 | blank | V | 0.42 | 0.42 | | 0.68 | N/A | 1 | 0.68 |

Social loss (SL) is N/A for every row (no DSS quarter a year before either fire on disk). "H" = hazard, "E" = exposure v2, "V" = vulnerability.
The full table with a source flag per cell and a note per row is `fire_event_dataset/data/extra_fires/extra_fire_rows.csv` (git-ignored data folder; identical copy in `results/`).

## 5. What could and could not be built, and why
| Piece | NSW Oct 2013 | Victoria 2009 |
|---|---|---|
| H, E | Built from the published Experiment 6 values. BFPL is the **current, post-2019 map, not a 2013 snapshot**; NVIS is time-invariant | **Not built.** No BFPL equivalent; the national NVIS 7.0 on disk is a FileGDB raster this GDAL cannot read; Victorian NV2005 not downloaded (needs your OK) |
| V | SEIFA 2011, ABS PIA median income FY2012-13, SALM unemployment Jun 2013 (each placed in the original distribution, income and unemployment as a ratio to the NSW median of the same series) | SEIFA 2006 and **EPISA average** total income FY2007-08 (EPISA has no median; Amendment 1). Unemployment omitted (SALM starts Dec 2010) |
| F | **Dropped by the frozen rule.** FY2012-13 OLG items were used only if their median was within 30% of the original snapshot's. Unrestricted current ratio passed (3.16 vs 3.25), operating ratio (-3.78 vs +0.57) and infrastructure backlog (6.77 vs 2.86) did not; cash cover and own-source had a documented OLG definition break and debt service ratio is not published for FY2012-13. One item left, so F was omitted | Not comparable (Victorian ratios are different quantities) |
| DL | 10 of 15 rows: 3 reported (Blue Mountains, Hawkesbury, Port Stephens), 7 inferred zeros | 2 of 13 rows (Murrindindi, Nillumbik) |
| IL | PIA total income (13 of 15; Wyong and Guyra merged in 2016 so not in the 2018 PIA table) and ABS business counts June 2013 to June 2014 (15 of 15) | EPISA total income (series break across the fire year, flagged low confidence) and ABS business counts June 2008 to June 2009 (13 of 13) |
| FP | Built as the master does (OLG FY2012-13, 2013-14, 2014-15), flagged low confidence (definition break in cash cover) | N/A (not comparable) |
| SL | N/A | N/A |

Comparison groups (councils of the same state with no fire of 100 ha or more in the window, from the GA outlines): NSW income 79, NSW business counts 99, NSW finance 93-99, Victoria 50. GA's NSW layer is National Parks outlines, so some NSW "no-fire" councils may have had private-land fires.

## 6. Homes destroyed (DL): sources and conflicts
Every figure has a URL and a quote in `inputs_dl/dl_homes_sourced.csv`. No ACM masthead and no Wikipedia was used (the URL list was checked against the dataset's ACM guard pattern). Two research sub-agents read pages with WebSearch/WebFetch only; the fetch tool cached some PDFs in Claude's own tool-results folder, nothing was downloaded into the project.
- **NSW Oct 2013:** the RFS Bush Fire Bulletin extract "Red October summary" has a Building Impact Assessment table of habitable dwellings destroyed by fire and council (BIA teams visited all firegrounds; printed total 224 = sum of its rows, which I verified). It gives Blue Mountains 195 (Linksview Road) + 10 (Mt York Road) = 205, Port Stephens 4 (Salt Ash) + 0 (Hank Street), Hawkesbury 2 (Webbs Creek), Wingecarribee 2 (Hall Road), Wyong 4 (Ruttleys Road), Lithgow 5 (State Mine). Rule applied: a fire's count goes to a council only if the fire lies wholly inside it. State Mine (burned Lithgow, Blue Mountains, Hawkesbury), Hall Road (Wingecarribee and Wollondilly) and Ruttleys Road (Wyong and Lake Macquarie) are not split by the source, so those councils are left blank and Blue Mountains and Hawkesbury are slightly low.
- **Zeros for NSW councils with no row in the BIA table are inferred, not reported.** Correction to the scoping note: I had assumed the RFS statewide total of 216 equals the sum of the listed fires. The October rows actually sum to 222 (216 omits Ruttleys Road and Webbs Creek). Other totals differ (ICA 221; Blue Mountains 196-210 in other sources; Port Stephens "about half a dozen" in an ABC item). The zeros rest on the BIA statement that teams visited all firegrounds; sensitivity (d) drops them.
- **Victoria:** no readable source gives a full council table. Reported: Nillumbik 135 houses destroyed (council health plan) and Murrindindi 1,397 homes destroyed (council memorial sheet; conflicts with 1,242 in a VBRRA report and with VBRC per-fire totals; any value above about 500 gives the same top rank). Yarra Ranges 304 is "destroyed or damaged so people could not live in them" (combined), so it is not used. Royal Commission chapters, the VBRRA 100-day report and the RDV memorial pages returned errors. The other 10 councils are blank.
- Dwellings per council: Census 2011 (B31, total private dwellings). For Victoria 2011 is the first national pack after the fire.

## 7. Amendments, decisions and disclosures
- **Amendment 1** (locked before any Y or score was computed): the Victorian income item is average, not median, income; the EPISA total income series has a documented break between FY2007-08 and FY2008-09 (exactly the fire year), kept and flagged, with sensitivity (f) added. `PRESPEC_AMENDMENT_1.md`.
- **Outcome of frozen rules, not new choices:** F omitted for NSW 2013 (30% comparability rule); Wyong and Guyra unscored; Victorian score = V only.
- **Seen before freezing, disclosed:** the first lines of two ABS business-count CSVs for non-fire councils (Albury, Armidale Dumaresq); after the lock, the first rows of the Victoria wages block for Alpine, Ararat, Ballarat and Banyule while reading layouts. No calculation was done on them. X-side values (score blocks) for the fire councils were printed after the score was built, before Y; the score table was then hashed.
- Not used and not run: no Excel write, no DuckDB write; no data file outside the 8 approved plus files already on disk; no Victorian hazard layer. Publication dates: EPISA was released after the 2013 fires but its FY2007-08 values describe the pre-fire year.

## 8. Honest verdict and what it does not say
- **Verdict: cannot tell.** The pooled interval [-0.40, +0.40] contains both zero and +0.30. The point estimate is essentially zero and so is each event's.
- The two events are independent of Black Summer, but they are two events with 13 rows each. Rows in a fire share weather and burn and the bootstrap treats councils as independent, so the true uncertainty is larger than shown.
- Victorian finance and hazard inputs are not comparable with NSW, so Victoria tests only the vulnerability block. The new rows use different source vintages (Census 2006/2011, EPISA, NRP, PIA release 2020, OLG 2012-15) from the 2015-2025 master, and NSW 2013 uses current hazard maps.
- Nothing here supports the score as a predictor of impact, and nothing is strong enough to say it fails. Any stronger statement needs more independent fires or more complete Victorian house-loss counts.

## 9. Protected inputs (SHA-256, before and after)
| Item | Before | After |
|---|---|---|
| `nsw_bushfires_2015_2025_XY.xlsx` (master workbook) | `123423eaed7174987f72c63cc40ad334e26c636b2e28358f94cf4fcd60c32ec3` | `123423eaed7174987f72c63cc40ad334e26c636b2e28358f94cf4fcd60c32ec3` (match) |
| `data/aussef.duckdb` | `ce294c7ef50964b334a13d83b627f0732e35d2237c70ddf7ce3a26b06f1cba59` | same (match) |
| `fire_event_dataset/out/` (tree hash of all files) | `7b0feec36ee0891f5143f2000ad51ad08142f3fa009cc319b9cf747e8d4bf69c` | same (match) |
| The 8 approved downloads | hash-checked against `MANIFEST.csv` at lock time | unchanged (nothing extracted into their folder) |

`HASHES_BEFORE.txt`, `HASHES_AFTER.txt`.

## 10. What needs your decision
1. **Victorian vegetation/hazard layer** (NV2005 EVC, from the Victorian environment department, size unknown) would let me build a hazard block for Victoria; not downloaded.
2. **Victorian house-loss by council:** the Royal Commission volumes, VBRRA 100-day report and RDV memorial pages were unreachable from here; if you can fetch them, DL for the other 10 councils could be filled and Victorian rows would move from one pillar to two.
3. **DSS quarterly data from Sep 2013** (not approved) would give a social-loss pillar for NSW 2013.
4. Whether to fold these rows into the master. They are kept separate in `fire_event_dataset/data/extra_fires/extra_fire_rows.csv`.

## 11. Files (`Experiment 6/followups/new_fires_test/`)
`PRESPEC.md`, `PRESPEC.lock`, `PRESPEC_AMENDMENT_1.md/.lock`, `SCORES.lock`, `Y.lock`, `lock_prespec.py`, `lock_amendment.py`, `lock_scores.py`, `lock_y.py`;
`build_rows.py` (polygons, roster, comparison groups) -> `build_scores.py` -> `build_y.py` -> `run_frozen_test.py` -> `make_tables.py`, `verify_protected.py`, `nf_lib.py`;
`inputs/` (copies of Experiment 6 inputs, master reference distribution, overlay code), `inputs_dl/dl_homes_sourced.csv`, `results/` (`roster.csv`, `event_polygons.csv`, `comparison_groups.csv`, `SCORES_new_rows.csv`, `SCORE_ITEMS_new_rows.csv`, `Y_indicators_new_rows.csv`, `extra_fire_rows.csv`, logs, `frozen_test/TEST_RESULTS.csv`, `POWER_CHECK.csv`, `VERDICT.json`, `TABLES.md`), `logs/`.
Run order: `lock_prespec.py`, `build_rows.py` (project `.venv`), `build_scores.py`, `lock_scores.py`, `build_y.py`, `lock_y.py`, `run_frozen_test.py`, `verify_protected.py` (anaconda python with `xlrd` on the path for the old `.xls` files).
