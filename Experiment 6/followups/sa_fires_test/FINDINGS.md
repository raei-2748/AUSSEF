# Fresh test of the Experiment 6 risk score on the South Australian fires (2026-09-30)

**Verdict under the rule fixed in advance: NOT REPLICATED, but only just, and it does not survive removing the 2019-20 events.** The rule, the score, the outcome recipe, the rows and the pooled set were frozen before any SA outcome was computed (`PRESPEC.md`, hash in `PRESPEC.lock`; one clarifying amendment locked before any score existed; score table hashed in `SCORES.lock`; Y inputs and test script hashed in `Y.lock`). The test was run once.
Nothing was committed or pushed. `Experiment 6/REPORT.md` was not edited. The master workbook, `data/aussef.duckdb` and `fire_event_dataset/out/` are byte-identical before and after (section 9).

## 1. Plain summary (5 lines)

1. **Pooled with the 26 earlier independent rows (37 rows from 7 fire events in 5 separate weather periods), the score's rank correlation with the impact measure is -0.09, 95% interval [-0.42, +0.26].** The frozen rule says "not replicated" if the top of the interval is below +0.30. It is (0.26), so the label is NOT REPLICATED. The estimate is essentially zero, as it was in the previous round (+0.00, 26 rows).
2. **The label is fragile.** Without the three 2019-20 SA events (same season as NSW Black Summer) the pooled result is +0.05 [-0.30, +0.37], which the same rule reads as CANNOT TELL. Dropping Cudlee Creek or Kangaroo Island alone moves the top of the interval to 0.30. The new SA rows on their own (11 rows) say -0.28 [-0.72, +0.70]: they carry almost no information (a real correlation of 0.3 would show up in only 15% of runs).
3. **Only 11 SA council rows met the 1% burned rule (scoping had suggested about 15-20), so the new fires added 11 rows and two new independent weather periods (Jan 2015, Nov 2015) plus the 2019-20 season, not the 45-50 rows the design needs.** Pooled rows are now 37. To detect a true 0.4 with 80% power about 47 comparable rows are needed (10 more); for 0.3 about 85 (48 more). Rows in a fire share weather, so the number of independent fires matters more than the row count.
4. **What the pieces say (descriptive, none can change the verdict):** the vulnerability block alone is positive but not distinguishable from zero (+0.26 [-0.09, +0.55] pooled; +0.65 [-0.19, +0.89] on the 11 SA rows). Homes destroyed per 1,000 dwellings goes the wrong way again (-0.58 [-0.86, -0.14], 16 rows, only 5 of them SA). Income and business loss is positive (+0.24 [-0.12, +0.56]; +0.43 [+0.11, +0.67] without the 2019-20 events).
5. **What could be built for SA:** hazard and exposure from the SA Bushfire Protection Areas layer (a different classification from NSW, placed in the NSW scale) for 8 of 11 rows; vulnerability for all 11; the fiscal block for none (fewer than two items passed the 30% rule). Outcome: income, business counts (not for Sampson Flat), council finances (three substitutes, two for the 2019-20 events) and social loss for all 11 rows; homes destroyed for only 5 of 11 rows. Protected files unchanged.

## 2. What was tested (frozen; details in `PRESPEC.md`)

- **Score:** Experiment 6 v2 equal-weight `risk_add`, mean of the blocks available for a row among H, E v2, V, F, each item a 0-1 percentile placed in the original NSW 129-council distribution (nothing re-ranked). Secondary scores only V alone (S1) and mean(H, V) (S2).
- **Events (rule fixed now, five events):** Sampson Flat (Jan 2015), Pinery (Nov 2015), Cudlee Creek, Kangaroo Island and Keilira (Dec 2019 to Jan 2020). Wangary 2005 was excluded by the rule because its data window does not work (no unemployment, income or business series before FY2011-12; no SEIFA 2001 on disk). Bangor 2014 has no GA polygon of 1,000 ha or more.
- **Rows:** every council with at least 1% of its area inside the event's GA fire polygons: 11 rows (Pinery 4, Sampson Flat 3, Cudlee Creek 2, Kangaroo Island 1, Keilira 1). The roster reproduced the scoping shares exactly (for example Light 29.7%, Adelaide Hills 11.7% and 18.3%, Kangaroo Island 45.7%).
- **Y:** the master's construction: each indicator signed so higher = worse, percentile of the new raw value in the existing 218-row master distribution (never re-ranked), excess change over same-state councils with no fire of 100 ha or more in the window (45 to 58 SA comparison councils, 29 to 36 for the renewals ratio), pillar = mean of its indicators, `Y_new` = mean of the pillars present, `pillars_n` recorded.
- **Test:** Spearman with a council-cluster bootstrap (5,000 draws, seed 20261101). PRIMARY = pooled (SA rows plus the 26 frozen stage-1 rows). Verdict: replicated if the lower bound is above 0; not replicated if the upper bound is below +0.30; otherwise cannot tell.

## 3. Results

### 3.1 Primary and other scopes (score `risk_add_avail`, target `Y_new`)
| Scope | n | Spearman | 95% CI |
|---|---:|---:|---|
| **Pooled with the 26 earlier rows (verdict)** | **37** | **-0.09** | **[-0.42, +0.26]** |
| SA rows alone | 11 | -0.28 | [-0.72, +0.70] |
| Earlier 26 rows alone (reproduction of the frozen result, different bootstrap seed) | 26 | +0.00 | [-0.41, +0.39] (was +0.00 [-0.40, +0.40]) |
| Pooled without the three 2019-20 SA events | 33 | +0.05 | [-0.30, +0.37] |
| SA 2015 events only (Sampson Flat, Pinery) | 7 | +0.18 | [-0.75, +1.00] |
| Each SA event alone | 1 to 4 | not estimable | |

Verdict rule applied: lower bound -0.42 is not above 0, upper bound +0.26 is below +0.30, so **NOT REPLICATED**. The same rule on the pooled set without the 2019-20 events would give CANNOT TELL (upper bound 0.37). No single SA event has enough councils for its own estimate. The earlier 26 rows reproduce their frozen result.

### 3.2 Pre-declared secondary and descriptive results (58 tests were run in all; none can change the verdict)
| Test | Scope | n | Spearman | 95% CI |
|---|---|---:|---:|---|
| V block alone (S1) vs `Y_new` | pooled | 37 | +0.26 | [-0.09, +0.55] |
| V block alone (S1) | SA rows | 11 | +0.65 | [-0.19, +0.89] |
| V block alone (S1) | pooled without 2019-20 | 33 | +0.26 | [-0.09, +0.56] |
| mean(H, V) (S2) | pooled (rows having both) | 21 | +0.11 | [-0.34, +0.50] |
| **DL only** (homes destroyed per 1,000 dwellings) | pooled | 16 | **-0.58** | **[-0.86, -0.14]** |
| DL only | SA rows | 5 | not estimable | |
| IL pillar (income, business counts) | pooled | 37 | +0.24 | [-0.12, +0.56] |
| IL pillar | pooled without 2019-20 | 33 | +0.43 | [+0.11, +0.67] |
| FP pillar | pooled / SA | 24 / 11 | -0.15 / -0.12 | [-0.53, +0.30] / [-0.72, +0.62] |
| SL pillar | SA rows (the only ones with SL) | 11 | +0.05 | [-0.71, +0.78] |
| Sensitivity (a) rows with 5%+ burned | pooled / SA | 23 / 9 | -0.09 / -0.58 | [-0.50, +0.39] / [-0.92, +0.26] |
| Sensitivity (b) `Y_new` needing 2+ pillars | pooled | 26 | -0.28 | [-0.62, +0.12] |
| Sensitivity (c) `Y_new` without FP | pooled | 37 | -0.03 | [-0.36, +0.32] |
| Sensitivity (d) DL from reported values only | pooled | 10 | -0.14 | [-0.80, +0.59] |
| Sensitivity (e) without 2019-20 (pooled) | pooled | 33 | +0.05 | [-0.30, +0.37] |
| Sensitivity (f) pooled minus one SA event | Sampson Flat / Pinery / Cudlee / Kangaroo Is. / Keilira | 34 / 33 / 35 / 36 / 36 | -0.09 / -0.14 / -0.04 / -0.04 / -0.08 | upper bounds 0.25 / 0.22 / 0.30 / 0.30 / 0.27 |

Reading:
- **The composite is centred on zero on independent fires, in both rounds.** The previous round's +0.00 and this round's -0.09 are the same finding. The earlier headline on large NSW fires 2015-2025 (mostly Black Summer) does not carry to independent fires on this outcome measure.
- **V alone is the only positive score, and it is not established.** +0.26 pooled (interval reaches -0.09). The SA-only +0.65 rests on 11 rows from 5 SA events.
- **The 2019-20 events matter for the label.** With them the top of the interval is 0.26; without them 0.37. Two of the five leave-one-out results sit at 0.30. So "not replicated" here means "the interval only just clears the +0.30 line", not "clearly excluded".
- **The DL pillar is negative again** (councils with a higher score lost fewer homes per dwelling, among the councils with a sourced count). It rests on 16 rows, 5 SA; the SA value cells are Pinery (4) and Kingston (1).
- **IL is the one pillar that looks positive**, and mostly outside Black Summer's season. It is one of many descriptive comparisons, not the pre-set test.

### 3.3 Planted-effect power check (fake Y, real rows; 1,000 simulations per cell; no real outcome used)
| Rows | n | planted rho | detected (CI lower > 0) | "not replicated" (CI upper < 0.30) |
|---|---:|---:|---:|---:|
| pooled primary | 37 | 0 | 2% | 40% |
| | | 0.2 | 20% | 7% |
| | | 0.3 | 40% | 2% |
| | | 0.4 | 67% | 0% |
| | | 0.5 | 91% | 0% |
| | | 0.6 | 99% | 0% |
| SA rows | 11 | 0.3 / 0.4 / 0.5 | 15% / 23% / 35% | |
| pooled without 2019-20 | 33 | 0.3 / 0.4 / 0.5 | 40% / 64% / 87% | |

Two things follow. A true correlation of 0.3 would be missed 60% of the time; a true zero would be labelled "not replicated" only 40% of the time. So the rule that fired is a weak bar (the label does not mean the score has no value) and it fired on an interval that just cleared it. Full file: `results/frozen_test/POWER_CHECK.csv`.
**Rows still needed** (Fisher approximation, 80% power, `ROWS_NEEDED.csv`): true 0.5: 30 rows (met); true 0.4: 47 rows (10 more); true 0.3: 85 rows (48 more). The simulation treats rows as independent; the independent weather periods so far are NSW Oct 2013, Victoria 2009, Sampson Flat, Pinery and the 2019-20 season (counted as one), so the real position is weaker than the row count suggests.

## 4. Pillar coverage per row
Flags per cell are in `results/sa_fire_rows.csv` (copy in `fire_event_dataset/data/extra_fires/sa_fire_rows.csv`, git-ignored). DL: reported / blank. Blocks: H hazard, E exposure v2, V vulnerability, F fiscal.

| Event | Council | Burned % | Homes destroyed | Blocks | Score | V | DL | IL | FP | SL | Pillars | Y_new |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pinery 2015 | Light | 29.7 | 41 (reported) | HEV | 0.34 | 0.23 | 0.92 | 0.13 | 0.88 | 0.08 | 4 | 0.50 |
| Pinery 2015 | Mallala | 13.8 | 15 (reported) | HEV | 0.45 | 0.33 | 0.85 | 0.25 | 0.52 | 0.58 | 4 | 0.55 |
| Pinery 2015 | Wakefield | 5.3 | 36 (reported) | V | 0.61 | 0.61 | 0.93 | 0.66 | 0.50 | 0.27 | 4 | 0.59 |
| Pinery 2015 | Clare and Gilbert Valleys | 5.0 | 5 (reported) | V | 0.33 | 0.33 | 0.75 | 0.21 | 0.64 | 0.05 | 4 | 0.41 |
| Sampson Flat 2015 | Adelaide Hills | 11.7 | blank | HEV | 0.69 | 0.14 | | 0.39 | 0.48 | 0.08 | 3 | 0.32 |
| Sampson Flat 2015 | Playford | 5.5 | blank | HEV | 0.63 | 0.79 | | 0.36 | 0.46 | 0.92 | 3 | 0.58 |
| Sampson Flat 2015 | Tea Tree Gully | 3.2 | blank | HEV | 0.31 | 0.20 | | 0.67 | 0.47 | 0.22 | 3 | 0.45 |
| Cudlee Creek 2019 | Adelaide Hills | 18.3 | blank | HEV | 0.71 | 0.20 | | 0.27 | 0.59 | 0.07 | 3 | 0.31 |
| Cudlee Creek 2019 | Mount Barker | 11.6 | blank | HEV | 0.82 | 0.46 | | 0.19 | 0.46 | 0.71 | 3 | 0.45 |
| Kangaroo Island 2019-20 | Kangaroo Island | 45.7 | blank | HEV | 0.81 | 0.58 | | 0.30 | 0.67 | 0.05 | 3 | 0.34 |
| Keilira 2019-20 | Kingston | 6.8 | 3 (reported) | V | 0.46 | 0.46 | 0.78 | 0.35 | 0.44 | 0.95 | 4 | 0.63 |

Pillars absent by rule: FP is a mean of three indicators for the 2015 events and two for the 2019-20 events (renewals ratio not comparable); IL has one indicator (income) for Sampson Flat; DL is absent for 6 rows; every row has SL. Y_new is a mean of 3 or 4 pillars for all 11 rows (no 1-pillar rows, unlike Victoria in the previous round).
Low-confidence flags: SL is `computed_low_confidence` for the 7 rows of the 2015 events (suppressed "<20" cells counted as 10 in the 2013-2015 DSS workbooks); FP is `computed_substitute` for all rows; H and E `computed_low_confidence`.

## 5. What could and could not be built, and why
| Piece | Result |
|---|---|
| **H hazard** | Two items from the SA Bushfire Protection Areas layer: share of council area in class High and in High+Medium (analogues of BFPL Cat 1 and Cat 1+2), placed in the NSW scale. NVIS forest share omitted (NVIS 6.0 on disk is NSW only). **Different classification** (modelled risk, not vegetation category); a council is "mapped" if BPA of any class covers at least 1% of it (Amendment 1: two councils overlapped by only about 10 ha were being counted as mapped). Unmapped, so no H or E: Wakefield, Clare and Gilbert Valleys, Kingston. Adelaide Hills, Mount Barker and Kangaroo Island land at the top of the NSW scale (High share 67%, 94% and 47%). |
| **E exposure** | Share of dwellings and residents inside BPA High+Medium, by the master's recipe, with ABS **2021** mesh blocks and counts (2016 SA polygons were not downloaded). Vintage up to 6 years after the 2015 fires. |
| **V vulnerability** | SEIFA 2011 (2015 events) or 2016 (2019-20 events); PIA median income of the year before the fire year as a ratio to the NSW median of the same release; SALM smoothed unemployment as a ratio to the NSW median. All 11 rows. |
| **F fiscal** | **Omitted for all events.** SA cash cover, own-source % and operating ratio were built with the same formulae as OLG and tested against the 30% median rule: cash cover fails everywhere (SA median 2.7 to 3.9 months v NSW 10.6), operating ratio fails everywhere, own-source passes for Pinery and the 2019-20 events but not Sampson Flat (1.32). One item is not enough (rule: at least 2). The unrestricted current ratio, backlog ratio and debt-service ratio do not exist in the LGGC reports. |
| **DL** | 5 of 11 rows (section 6). |
| **IL** | Income for all 11 rows. Business counts for 8 rows; **N/A for Sampson Flat** (no on-disk release holds both June 2014 and June 2015; a change across two ABS products is not formed). |
| **FP** | Three LGGC substitutes: cash cover drawdown (own calculation), services crowd-out (function names mapped to the OLG definition), renewals ratio (**Asset Sustainability Ratio, 2015 events only**: from FY2018-19 the report prints a different measure, the Asset Renewal Funding Ratio, so the 2019-20 renewals indicator is N/A). Scale check on the comparison councils passed (IQR ratio 0.6 to 1.3 for kept indicators). Also note the LGGC Report 8 operating-surplus ratio uses a rates-revenue denominator to FY2014-15, total operating revenue later; my own calculation uses operating revenue in every year. |
| **SL** | All 11 rows. Sampson Flat June 2015 minus June 2014 (the June 2014 workbook does have an LGA sheet); Pinery March 2016 minus March 2015; 2019-20 events March 2020 minus March 2019. The Widow B pension is not in the 2018-vintage file, so the 2019-20 sum uses 12 components on both sides. |

Boundaries: SA has no council merger in the window; the only change is Mallala (code 43920, LGA 2015 and 2016) renamed Adelaide Plains (40150, from LGA 2018) with identical geometry, treated as one council. LGA editions 2018 and 2020 have identical SA codes and areas (checked, `results/boundary_edition_check.csv`).

## 6. Homes destroyed (DL): sources and conflicts
Every figure has a URL and a quote in `inputs_dl/dl_homes_sourced.csv`. No ACM masthead, no Wikipedia and no local newspaper was used. Rule: council-level counts only; fire-level counts attributed to a council only if the fire lies wholly inside it; conflicts of more than 10% leave the cell blank unless a government recovery, inquiry or coroner document decides it; inferred zeros only if an official event total equals the sum of the named councils and no source gives a higher total.
- **Pinery (4 rows, reported):** Light 41, Wakefield 36, Adelaide Plains (Mallala) 15, Clare and Gilbert Valleys 5, total 97, from the SA Government's Pinery Fire Recovery Final Report (July 2017) Table 4 as reproduced in the AIDR evaluation report. CFS says "about 91 homes" for the whole fire: a fire-level figure, so no conflict at council level. No inferred zeros needed.
- **Keilira (1 row, reported):** Kingston 3, CFS "three homes lost". CFS names no council; the GA outline is 99.6% inside Kingston, so the fire-level figure is attributed to Kingston. (Kingston Council reported only one was occupied; not re-verified here.)
- **Sampson Flat (3 rows, blank):** CFS "about 24 houses", AIDR "27 homes", both fire-level and 12.5% apart. A council-level count (Adelaide Hills Council annual report 2014-15, "24 homes ... in the Council area") was reported by an earlier scoping note, but the report file is over the fetch limit, so I could not read or quote it. No inferred zeros because the event totals conflict.
- **Cudlee Creek (2 rows, blank):** CFS 85, AIDR 84, ABC 86, all fire-level. The council split is probably in the SA Recovery plans, which are behind a sign-in.
- **Kangaroo Island (1 row, blank):** CFS "87 dwellings, 332 outbuildings" against AIDR and the Emergency Services Minister (ABC, 7 January 2020, early assessment) "56 homes". 55% apart; the government recovery documents that could settle it (SA Recovery interim and final reports) could not be opened. Blank by the conflict rule. Not computed for either value.

## 7. Amendments, decisions and disclosures
- **Amendment 1** (locked before any SA score or Y existed): (A1) "mapped" means BPA of any class covers at least 1% of the council (the literal "any polygon" test was defeated by 10 ha boundary slivers); (A2) implementation facts that follow from the frozen text: services-share denominator is Report 3's total (Report 9 prints a total only from FY2018-19), the renewals ratio is the Asset Sustainability Ratio only where both years carry that header, operating ratio from Reports 2 and 3, council names matched after normalisation with a listed hand table (four name pairs for the comparison group).
- **Seen before freezing, disclosed:** the roster and the shares (identical to scoping), the BPA class counts, the first rows of the DSS LGA sheets (New South Wales councils), the LGGC front-page column lists. **After the pre-spec lock and before the score lock:** the SA X-side values (H, E, V, F, score) were printed, and the F comparability numbers. **Before Y.lock:** comparison-group sizes and medians, the FP scale check, the count of unmatched council names (fixed with name aliases in `build_y.py`). No fire council's Y value, and no score-versus-Y relation, was seen before the frozen run. `build_y.py` was run twice (once to find the unmatched names); a dry run of the test script on random Y confirmed the code.
- **Web access disclosure:** the built-in browser was pointed at a SA Recovery PDF and triggered a **save dialog** (the site serves it as a download); I did not retry. The same site's plan pages redirect to a sign-in, which I did not use. The fetch tool cached the AIDR Pinery report in Claude's tool-results folder (not in the project).
- **Not used and not run:** no Excel write, no DuckDB write; no data file outside the 12 approved plus files on disk; no Victorian or Tasmanian data; no commit or push.

## 8. Honest verdict and what it does not say
- **Verdict: not replicated (pooled 37 rows, upper bound 0.26 < 0.30).** The pooled point estimate is -0.09 and the previous round's was +0.00. On independent fires, the composite score has not shown a positive rank relation with the impact measure.
- **What it does not say.** (i) It does not say the score has no value: V alone is +0.26 and the interval reaches -0.09; the composite includes SA hazard and exposure items on a different classification, placed in the NSW scale, which may just add noise. (ii) The rule is a weak bar and this interval only just clears it: it fires 40% of the time even when the true correlation is zero, and dropping the 2019-20 events turns it into "cannot tell". (iii) 37 rows from 7 fire events (5 separate weather periods) is a small sample, and the bootstrap treats councils as independent though councils in one fire share weather and burn, so the true uncertainty is larger. (iv) Homes destroyed exists for 16 of 37 rows. (v) Source vintages and products differ from the NSW 2015-2025 master (Census 2011 and 2016, EPISA and PIA, SA substitutes for council finances).
- **A fair reading:** across every independent fire tested so far the score's composite does not track impact; the earlier positive result is confined to Black Summer. The one line still alive is the vulnerability block. This test cannot confirm or kill it.

## 9. Protected inputs (SHA-256, before and after)
| Item | Before | After |
|---|---|---|
| `nsw_bushfires_2015_2025_XY.xlsx` (master workbook) | `123423eaed7174987f72c63cc40ad334e26c636b2e28358f94cf4fcd60c32ec3` | same (match) |
| `data/aussef.duckdb` | `ce294c7ef50964b334a13d83b627f0732e35d2237c70ddf7ce3a26b06f1cba59` | same (match) |
| `fire_event_dataset/out/` (tree hash of 19 files) | `7b0feec36ee0891f5143f2000ad51ad08142f3fa009cc319b9cf747e8d4bf69c` | same (match) |
| All 21 per-file hashes (workbook, database, 19 out files), recorded at the very start and again at the end | `HASHES_BEFORE_START_per_file.txt` | `HASHES_AFTER_END_per_file.txt` (diff: identical) |
| The 12 SA downloads (and the 10 earlier ones) | SHA-256 in `MANIFEST.csv` at download | re-verified: 22 of 22 match |

The three protected files are outside this worktree; rows were written only to the git-ignored `fire_event_dataset/data/extra_fires/sa_fire_rows.csv`.

## 10. What is next, and what needs your decision
1. **More fires are still needed:** the design wants about 47 comparable rows for a true 0.4 (10 more than now) and about 85 for 0.3, preferably from independent fires. Candidates from scoping, none downloaded: **Tasmania Jan 2013 Dunalley** (Sorell 24%, Tasman 14%: 2 rows, one of them at 20% or more; only 29 councils so the comparison group is about a dozen; no DSS or business-count baseline for 2013), Victoria Black Summer (3 rows, same season as NSW), WA Waroona (2 rows) and Wooroloo (1). The 1% rule keeps yields low (2 to 4 rows per fire). Please tell me before I download anything for Tasmania.
2. **DL for six SA rows:** the Sampson Flat, Cudlee Creek and Kangaroo Island cells could be filled if you can open (a) the Adelaide Hills Council annual report 2014-15, (b) the SA Recovery final report or Cudlee Creek and Kangaroo Island recovery plans. This would be exploratory (after the frozen run) and cannot change the verdict.
3. **Folding these rows into the master** is not done; they stay in `sa_fire_rows.csv`.
4. **Please cancel the save dialog** if it is still open in the app: it came from my attempt to open the SA Recovery final report in the built-in browser.

## 11. Files (`Experiment 6/followups/sa_fires_test/`)
`PRESPEC.md`, `PRESPEC.lock`, `PRESPEC_AMENDMENT_1.md/.lock`, `SCORES.lock`, `Y.lock`, `DOWNLOAD_LIST_FOR_APPROVAL.md`;
scripts in run order: `lock_prespec.py`, `build_rows.py` (polygons, roster, comparison groups, boundary check), `build_geo_items.py` (BPA and exposure), `lggc_lib.py` + `lggc_items.py` (PDF parser), `build_scores.py`, `lock_scores.py`, `build_y.py`, `lock_y.py`, `run_frozen_test.py`, `make_tables.py`, `verify_protected.py`, `lock_amendment.py`, `nf_lib.py`, `prep_mb_counts.py`;
`inputs/` (copies of Experiment 6 inputs and the frozen stage-1 rows), `inputs_dl/dl_homes_sourced.csv`, `results/` (`roster.csv`, `event_polygons.csv`, `comparison_groups.csv`, `boundary_edition_check.csv`, `geo_items_sa.csv`, `SCORES_new_rows.csv`, `SCORE_ITEMS_new_rows.csv`, `Y_indicators_new_rows.csv`, `sa_fire_rows.csv`, `lggc_items_all_councils.csv`, `lggc_column_map.csv`, `lggc_council_match.csv`, logs, `frozen_test/TEST_RESULTS.csv`, `POWER_CHECK.csv`, `ROWS_NEEDED.csv`, `VERDICT.json`, `TABLES.md`, `dryrun_fake_y/`), `logs/`, `HASHES_*`.
Run environments: project `.venv` (geopandas) for `build_rows.py` and `build_geo_items.py`; `/Users/ray/.venv/bin/python` (pandas, xlrd, openpyxl, pdfminer) for `lggc_items.py`, `build_scores.py`, `build_y.py`; anaconda python (scipy) for `run_frozen_test.py`.
