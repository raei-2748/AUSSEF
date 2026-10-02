# PRE-SPECIFICATION: South Australian fires as a second fresh test of the Experiment 6 risk score (frozen before any SA outcome is built)

Written 2026-09-29, after the approved SA downloads were logged and before (i) any SA council roster, score item or outcome value was computed, and
(ii) any SA score-versus-outcome relation was looked at. Hash-locked by `lock_prespec.py` (SHA-256 in `PRESPEC.lock`). `run_frozen_test.py` refuses to run if
this file or any locked step changes. A change is only allowed as a dated amendment (section 12), written BEFORE the affected step is re-run; earlier outputs are kept.
Nothing below was chosen by looking at a correlation with Y. Where a judgement call was needed it was made from documentation and is recorded here.

## 0. What I looked at before freezing (disclosure)

- Read: Experiment 6 REPORT/scripts, the previous round (`../new_fires_test/`: PRESPEC, FINDINGS, stage-2 FINDINGS and scripts), the scoping FINDINGS and notes A3, A5, A7, `overlay_candidates.py` parameters.
- Approved downloads (12 files, `MANIFEST.csv`, SHA-256 logged 2026-09-29). Layout only was read, no council value for any SA fire council: the three DSS workbooks (sheet names, the first six rows of the LGA sheet: they list New South Wales councils),
  the LGGC PDFs (the front-page list of what each of the ten reports contains), the Bushfire Protection Areas attribute table (column names and class counts only: bf_code High 88, Medium 135, General 43, Excluded 87 polygons; 353 in all) and the ABS 2015-to-2016 LGA correspondence rows for Mallala.
- Checked on disk (existence and coverage only): SEIFA 2011 and 2016; PIA releases; CABEE releases (no June 2014 sheet in any release on disk); SALM; ERP; 2016 and 2021 mesh-block counts (national); 2021 mesh-block polygons (national);
  NVIS 6.0 on disk is NSW only.
- Did NOT read or compute: any SA council's burned share, SEIFA/income/unemployment, BPA share, finance ratio, business count, DSS count, homes destroyed, or Y. Web research on homes destroyed per SA council has not started.

## 1. The exact score being tested

Score inputs and construction are those of `Experiment 6/build_and_validate_score.py` run with `v2`, unchanged: four blocks H, E (v2), V, F; each item a 0-1 percentile in the **original NSW 129-council distribution**
(`inputs/COUNCIL_ITEMS_v2.csv`), oriented so 1 = worse; a block is the mean of its available items; **`risk_add` = equal-weight mean of the blocks present**.

- **PRIMARY score (`risk_add_avail`):** mean of the blocks that exist for that row among H, E v2, V, F. `blocks_n` recorded.
- **SECONDARY scores, declared now and no others:** (S1) the **V block alone**; (S2) **mean(H, V)** (only rows that have both). Secondary results can never turn a failed primary test into a replication.

### 1.1 Placement in the original distribution (never re-ranked with the new councils)
For an item value v and the original non-missing values x (the 129-council snapshot columns of `COUNCIL_ITEMS_v2.csv`), the placed percentile is
`pct(v) = (n_better + n_equal/2 + 1) / (n + 1)`, n_better = number of original values less bad than v. Original percentiles never change, no new council is re-ranked with another.
Money and rate items (median income, unemployment rate) are divided by the **median across the 129 NSW councils of the same series in the same period and release** before placement
(original values by the median of the snapshot column, a monotone change). SEIFA IRSD is used as published. Code: `nf_lib.place`, tested by a self-check that reproduces the original ranks.

### 1.2 Pre-fire vintage rule (as in the previous round)
Each V and F item is taken from the **last period that ended before the fire's financial year began**, never the published FY2014-15 NSW snapshot and never a period that overlaps the outcome:

| Event | Fire FY | Vintage of V and F |
|---|---|---|
| Sampson Flat (Jan 2015) | FY2014-15 | SEIFA 2011; PIA FY2013-14; SALM smoothed rate Jun-2014; LGGC FY2013-14 |
| Pinery (Nov 2015) | FY2015-16 | SEIFA 2011; PIA FY2014-15; SALM Jun-2015; LGGC FY2014-15 |
| Cudlee Creek, Kangaroo Island, Keilira (Dec 2019 - Jan 2020) | FY2019-20 | SEIFA 2016; PIA FY2018-19; SALM Jun-2019; LGGC FY2018-19 |

(SEIFA 2016 was published in March 2018, before the December 2019 fires; SEIFA 2011 in March 2013. The SEIFA 2016 in the user's brief is therefore used for the 2019-20 events and the 2011 index for the 2015 events.)
Income (PIA) comes from the **latest release in `income_area_year_by_release.csv` that contains both the fire FY and the year before it**; the V-income for that event is taken from that same release. SALM values are on ASGS 2025 codes. **Mallala / Adelaide Plains is one council under two codes**: 43920 (Mallala) in ABS LGA 2015 and 2016, 40150 (Adelaide Plains) from LGA 2018 on; the ABS 2016-to-2018 correspondence records it as `renamed_same_geometry`
(100% overlap, 932.5 km2 in every edition). Rule: series on 2011/2015/2016 codes (SEIFA 2011, Census 2011, LGGC by name) are read under 43920, series on 2018+ codes (SALM, ERP, DSS 2018 file, PIA/CABEE releases) under 40150; the row keeps the code of its LGA edition (43920 for Pinery). All other SA council codes are stable across editions (checked in the build, reported).

## 2. Which blocks can be built for SA, and from what

| Block | SA recipe (fixed now) | Status |
|---|---|---|
| **H** hazard | Two items from the **SA Bushfire Protection Areas layer** (Development Act mapping, amendments 2006-2015, a genuine pre-fire layer for all five SA events): (h1) share of council area in BPA class **High**  (analogue of BFPL Category 1 share); (h2) share of council area in **High + Medium** (analogue of BFPL Category 1+2 share). Shares are area shares in EPSG:3577, overlapping polygons unioned. **NVIS forest share is omitted** (NVIS 6.0 on disk is NSW only, the 7.0 raster is unreadable). Each item is placed in the original NSW distribution of `bfpl_share_cat1` / `bfpl_share_cat12`; H = mean of the two | Built if the council has any BPA polygon (any class) |
| **E** exposure v2 | (e1) share of the council's **dwellings** and (e2) share of its **residents** inside BPA High + Medium, by the recipe of `build_exposure_bfpl.py` (dwellings and residents spread evenly over each mesh block, mesh blocks split at council lines, weighted by the share of area inside the layer). **Inputs: ABS 2021 mesh-block counts and 2021 mesh-block polygons (both national, already on disk); the 2016 counts used for NSW are national too but the 2016 SA polygons are not on disk and were not downloaded** so the vintage is 2021 (flagged). Placed in the original distributions of `dwellings_in_bfpl12_share` and `residents_in_bfpl12_share` | Built if the council has any BPA polygon |
| **V** vulnerability | (v1) SEIFA IRSD (1.2), (v2) PIA median income as a ratio to the NSW median of the same release and year, (v3) SALM smoothed unemployment rate as a ratio to the NSW median of the same quarter | Built for every SA row (an item missing for a council is dropped, the block is the mean of the rest) |
| **F** fiscal | Only analogues that can be computed from LGGC reports with the **same formula** as the OLG ratio; then the frozen **30% rule** (below). Candidates: cash expense cover, own-source revenue %, operating ratio. **Dropped by documentation, no test:** unrestricted current ratio and infrastructure backlog ratio (not in LGGC), debt service ratio (LGGC has finance costs but no loan principal repayments) | Built only if at least 2 candidate items pass, else F is omitted for that event |

**Honest limits declared in advance.** (1) BPA is a modelled risk classification (fuel, slope, aspect, weather); NSW BFPL is a vegetation-category map. They are **not the same classification**; an SA value placed in the NSW distribution is a *rank in a different scale*,
so SA H and E are lower-quality than NSW H and E. (2) A council with no BPA polygon at all is **not mapped**, which is not the same as low hazard: its H and E are omitted, never set to zero. (3) BPA covers 39 of 68 councils. (4) E uses 2021 mesh blocks (up to 6 years after the 2015 fires).
(5) The pooled primary mixes rows with 1 to 4 blocks; the V-alone score (S1) is the like-for-like pooled comparison and is reported next to it.

### 2.1 F comparability rule for SA (reuses the previous round's 30% rule)
Item formulae (LGGC Reports 2, 3, 4, 5, 8, 9; column names of the report list on the first page of each PDF):
- cash cover (months) = (Cash and Cash Equivalents + Other Financial Assets) / ((Total Operating Expenses - Depreciation, Amortisation and Impairment) / 12)
- own-source revenue % = 100 x (1 - Grants, Subsidies and Contributions / Total Operating Revenue)   [SA operating revenue excludes capital grants for new/upgraded assets, NSW total revenue includes them]
- operating ratio % = 100 x Operating Surplus/(Deficit) / Total Operating Revenue (cross-checked against Report 8 "Operating Surplus Ratio"; Report 8 is used only if the two agree)
For each event and each item, the **median across all SA councils of that item in the vintage year (1.2)** is compared with the **median of the same item in the original NSW 129-council snapshot** (`fiscal_cash_cover_months_fy`, `fiscal_own_source_pct_fy`, `fiscal_operating_ratio_pct_fy`).
The item is kept only if `|SA median / NSW median - 1| <= 30%` (as in the previous round). F is used only if at least 2 items are kept, else omitted for that event. Kept items are placed in the original NSW distribution.
This is a mechanical Y-blind check on the item level, fixed before the medians are seen.

## 3. Events, fire polygons, rows

Fire outlines: Geoscience Australia national historical bushfire boundaries (on disk), selection code `inputs/overlay_candidates.py` and parameters **copied unchanged from the scoping overlay**. Prescribed burns excluded.

| Event | Ignition window (inclusive) | Min polygon ha | Name filter | LGA edition (in force at the fire) | Fire FY | t-1 / t+1 |
|---|---|---:|---|---|---|---|
| SA_2015_sampson_flat | 2015-01-01 to 2015-01-10 | 5,000 | none | ABS LGA 2015 | FY2014-15 | FY2013-14 / FY2015-16 |
| SA_2015_pinery | 2015-11-24 to 2015-11-28 | 10,000 | none | ABS LGA 2015 (the scoping table used 2016; Mallala is the same code and geometry in both) | FY2015-16 | FY2014-15 / FY2016-17 |
| SA_2019_cudlee_creek | 2019-12-15 to 2019-12-25 | 1,000 | `Cudlee` | ABS LGA 2018 | FY2019-20 | FY2018-19 / FY2020-21 |
| SA_2019_20_kangaroo_island | 2019-12-15 to 2020-01-31 | 1,000 | `^(Ravine|KI Complex)` | ABS LGA 2018 | FY2019-20 | FY2018-19 / FY2020-21 |
| SA_2019_20_keilira | 2019-12-25 to 2020-01-05 | 1,000 | `Keilira` | ABS LGA 2018 | FY2019-20 | FY2018-19 / FY2020-21 |

**Event selection rule (fixed now):** the SA events in the scoping list whose fire financial year is FY2014-15 or later (the earliest year for which PIA, SALM, LGGC with a function split and a prior-year baseline all exist) and which have a GA polygon at the size above.
This gives exactly the five above. **Excluded by this rule:** Wangary (Jan 2005: SALM starts Dec 2010, PIA FY2011-12, SEIFA 2001 not on disk, no business-count pair; its data window does not work), Bangor Jan-Feb 2014 (no GA polygon of 1,000 ha or more in the window; 5 homes) and every event before FY2014-15.
**Independence:** the three 2019-20 events are in the same fire season as NSW Black Summer (separate events, not independent weather years). Every result is therefore also reported **without them** (sensitivity (e), section 6).
LGA editions 2018 and 2020 are checked for identical SA codes and areas within 1% (the ABS notes no SA change 2017-2020); a difference is reported.

**Row inclusion rule (frozen): every council whose burned share (union of the event's polygons inside the council / council area, EPSG:3577) is at least 1%.** "Unincorporated" areas are excluded (not councils). Expected from the scoping overlay, for reference only (the 1% rule governs): Sampson Flat: Adelaide Hills 11.7%, Playford 5.5%;
Pinery: Light 29.7%, Mallala 13.8%, Wakefield 5.3%, Clare and Gilbert Valleys 4.97%; Cudlee Creek: Adelaide Hills 18.3%, Mount Barker 11.6%; Kangaroo Island 45.7%; Keilira: Kingston 6.8%; plus councils between 1% and 5% found by the overlay. The roster is written to `results/roster.csv` and hash-locked before any Y is built.
Council key: ABS LGA code of the edition in force. Pre-2016 SA councils: no SA merger in the window, only the Mallala to Adelaide Plains rename (code 43920 to 40150, same geometry, section 1.2), so every SA council is one continuous unit; the pre-2016 names in the LGGC reports are matched by name (normalised) and, where the name differs from the ABS name, by a hand table recorded in the build.

## 4. Exact Y construction (per pillar, per event)

Identical in principle to the previous round: each indicator is signed so higher = worse, converted to a percentile **in the existing 218-row master distribution of the same raw indicator** (`inputs/master_reference_indicators.csv`, rule `pct = (n_less + n_equal/2 + 1)/(n+1)`, master rows never re-ranked, ties averaged),
a pillar is the mean of its indicators' percentiles, and **Y_new = mean of the pillars present**, `pillars_n` recorded. Each pillar is also tested alone.

| Pillar | Indicator (sign, as master) | SA construction |
|---|---|---|
| DL | homes destroyed per 1,000 dwellings (+) | sourced homes destroyed (section 5) / private dwellings x 1000; dwellings: Census 2011 table B31 for the 2015 events (latest census at or before the fire year; national pack on disk), Census 2016 table G32 for the 2019-20 events (`2016_GCP_LGA_for_AUS`, approved) |
| IL | total personal income fall, excess (-) | % change in PIA total income, fire FY vs t-1 (one release, section 1.2) minus median over the state's comparison councils |
| IL | business count fall, excess (-) | % change in ABS business counts (total businesses) 30 June t-1 to 30 June t, **both dates from one release** (the earliest-published on-disk CABEE release that contains both), minus the comparison median. **Sampson Flat: N/A (no release on disk contains June 2014 and June 2015; a change across the NRP and CABEE products is not formed)** |
| FP | cash cover drawdown, excess (-) | mean of the (t vs t-1) and (t+1 vs t-1) changes in cash cover (formula 2.1), each minus its comparison median |
| FP | services crowd-out, excess (-) | change in services share of operating expenses, t+1 vs t-1, minus comparison median. Services share = 100 x (Community Support + Community Amenities + Library Services + Cultural Services + Recreation + Waste Management + Other Environment) / Total Operating Expenses (Report 9). Mapping to the NSW definition (community services/housing + recreation/culture + environment) is by function name |
| FP | renewals ratio rise, excess (+) | change in the **Asset Sustainability Ratio** (Report 8: renewal/replacement capex less sale proceeds of replaced assets, over depreciation; all asset classes), t+1 vs t-1, minus comparison median. A substitute for the NSW buildings-and-infrastructure ratio |
| SL | income-support recipients rise, excess (+) | DSS payment recipients by LGA: quarter after the fire-start quarter minus the same quarter a year earlier, per 1,000 residents (ERP at 30 June of the calendar year before the fire), minus the median of the same quantity over the state's comparison councils (`src/vulnerable.py`) |

### 4.1 FP comparability (fixed now)
All three FP indicators are **substitutes** built from LGGC (different formulae from OLG for services share and renewals ratio, a near-identical formula for cash cover) and are flagged `computed_substitute`. Because a change in a ratio has median near 0, the 30% median rule is not usable on them; the rule is instead a **scale check** on the comparison councils:
an FP indicator for an event is kept only if the inter-quartile range of its raw change across the SA comparison councils is between 0.5 and 2 times the inter-quartile range of the same-signed raw change in the master reference column. Otherwise that indicator is `N/A (scale not comparable)` for the whole event. This uses no fire council and no Y.
The FP pillar is absent for an event where no indicator passes. LGGC footnotes report definition changes between years in some items; the excess design removes only a uniform shift.

### 4.2 Excess-change comparison group (frozen)
For each SA event and measure, the comparison group is the **SA councils with no fire of 100 ha or more burning inside them in the measure's window** (fire ignition in the fire FY for a change that ends in FY t; in FY t or t+1 for a change that ends in FY t+1; the 5 quarters from four quarters before the fire-start quarter for SL), from the same GA non-prescribed polygons (all sizes, union inside the council, at least 100 ha). Excess = own change minus the group median.
Limit: whether GA's SA layer maps all 100 ha fires is unknown; the 2019-20 window overlaps the COVID shock (same-state median cancels a uniform shock, not tourism-specific effects on Kangaroo Island). Group sizes are logged.

### 4.3 Pillars expected to be absent
IL business counts for Sampson Flat rows. SL for Sampson Flat if the June 2014 workbook's income-support components are not all published (see below). FP for an event if fewer than one indicator passes the scale check. DL wherever no source (section 5). Y_new is a mean of 1 to 4 pillars; the count is always reported.
Blank = not computed or not found; `N/A` = the rule says it cannot exist.

### 4.4 SL details (fixed now)
Fire-start quarter q0 and the pair of quarters: Sampson Flat q0 = 2015Q1 (Jun 2015 minus Jun 2014, two approved workbooks); Pinery q0 = 2015Q4 (Mar 2016, on disk, minus Mar 2015, approved workbook); Cudlee Creek, Kangaroo Island, Keilira q0 = 2019Q4 (Mar 2020 minus Mar 2019, both on disk, LGA 2018 file).
`income_support_total` = the master's 13 components (`src/dss.py`), restricted to the components published in **both** quarterly files of the pair; the same restriction is applied to the comparison group. The 2013-2015 workbooks suppress small cells as `<20` (the master rule "blank if any component missing" would blank almost every council):
**a `<20` cell counts as 10** (same rule as the previous stage 2, Amendment 1 there). Flag `computed_low_confidence` when any cell in a row's sum was imputed. The 2016+ files publish 1-4 as 0 or 5 (documented) and are used as published.

## 5. Homes destroyed (DL numerator): sourcing rule
Only from: SA Country Fire Service (CFS) and SA Government recovery reports, DisasterAssist, council official documents (annual reports, audited statements), AIDR Knowledge Hub, ABC News, audit offices, coroner or inquiry reports. **Not** ACM mastheads, **not** Wikipedia, no local newspaper. Every figure carries source title, URL and a short verbatim quote (`inputs_dl/dl_homes_sourced.csv`).
- `reported`: the source gives a destroyed-home/dwelling count for the council (or for a fire wholly inside it).
- `inferred`: **only** if an official (government/agency) whole-event total equals the sum of the councils' figures a source names, and no allowed source gives an event total more than 10% higher; then a council not named gets 0. Flagged, never shown as reported.
- **Blank:** fire losses span councils with no stated split, or no source found. Nothing is guessed. **Conflict rule:** where two allowed sources give council-level figures more than 10% apart, the cell is blank unless one is a government recovery/inquiry/coroner document (which then wins and the conflict is recorded).
  Event-level totals that differ (e.g. 24 v 27) do not by themselves create a council-level conflict but block inferred zeros as above.
- Homes vs other buildings: only dwellings/homes/houses count; "structures", "assets" and sheds do not (recorded in the note).

## 6. Tests (all frozen)

Rows: burned share >= 1%, with a score and (primary) a Y_new from >= 1 pillar. Spearman (average ranks); **council-cluster bootstrap**, 5,000 draws, percentile 95% CI, seed `20261101`, clusters = ABS LGA code (a council in two events, e.g. Adelaide Hills, is one cluster).
Estimable only with at least 6 rows and at least 3 distinct values on each side. Pooled set for (ii) = the new SA rows plus the **26 earlier independent rows** (NSW Oct 2013 13 rows, Victoria 2009 13 rows) taken from the frozen stage-1 file `inputs/stage1_extra_fire_rows.csv` (a hash-locked copy of `../new_fires_test/results/extra_fire_rows.csv`): their `risk_add_avail`, `S1_V`, `S2_HV`, `Y_new` and pillars are used exactly as frozen then (not the stage-2 exploratory outcomes).

- **PRIMARY (the only test that decides the verdict): (ii) Spearman(`risk_add_avail`, `Y_new`) on the pooled set.** Reported alongside: (i) the same on the new SA rows alone; each SA event alone (when estimable).
- **DL-only, IL, FP, SL pillars** vs `risk_add_avail`: pooled and SA alone (descriptive).
- **Secondary scores** S1 (V alone) and S2 (mean(H, V)) vs `Y_new`, pooled and SA alone (descriptive).
- **Pre-declared descriptive sensitivities** (never used for the verdict): (a) rows with burned share >= 5%; (b) `Y_new` requiring >= 2 pillars (the master's rule); (c) `Y_new` without FP; (d) DL from `reported` values only (no inferred zeros, no conflict cells);
  **(e) without the three 2019-20 SA events** (pooled, and SA 2015 events alone); (f) leaving out each SA event in turn.
- No multiplicity adjustment. Only the primary test decides.

### 6.1 Replication rule (frozen; pooled primary interval [lo, hi], estimate r)
- **REPLICATED:** lo > 0.
- **NOT REPLICATED:** hi < +0.30.
- **CANNOT TELL:** anything else.
Always stated with the verdict: whether each single event and the SA rows alone have a positive estimate; that events are few; which score blocks each group had; that source vintages differ from the NSW 2015-2025 master; the effect of dropping the 2019-20 events; a leaning note if r <= 0 with a wide interval (still "cannot tell").

### 6.2 Planted-effect power check and rows still needed (frozen; uses no real Y)
On the actual pooled row set with a score and a Y_new (only which rows exist is used), fake Y `Y_sim = rho * z(rank(score)) + sqrt(1 - rho^2) * eps`, eps standard normal, rho in {0, 0.1, ..., 0.6}, 1,000 simulations per rho, 500 bootstrap draws each, seed `20261102`.
Reported: share with lo > 0 (power to replicate) and share with hi < 0.30 ("not replicated") at each rho, for the pooled set, the SA rows, and the pooled set without the 2019-20 events.
**Rows still needed:** Fisher approximation for 80% power at a two-sided 5% lower-bound test, n = ((1.96 + 0.84) / atanh(rho))^2 + 3, at rho = 0.3, 0.4, 0.5, minus the number of pooled rows; and the count of independent fire events (NSW 2013, Victoria 2009, Sampson Flat 2015, Pinery 2015, and the 2019-20 season as one).

## 7. Output files, flags, blank vs N/A
`fire_event_dataset/data/extra_fires/sa_fire_rows.csv` (git-ignored data folder; a copy in `results/`): event id/name, ABS LGA code and name, first fire start, share burned, burn ha, X blocks (H, E, V, F, `blocks_n`), `risk_add_avail`, S1, S2, each pillar and its indicators, `pillars_n`, `Y_new`,
**a source-flag column per cell group** (`reported` / `computed` / `computed_low_confidence` / `computed_substitute` / `inferred` / `unavailable` / `N/A`) and a note. Blank = not computed or not found; `N/A` = the rule says it cannot exist.
The master workbook, `data/aussef.duckdb` and `fire_event_dataset/out/` are never written; SHA-256 recorded before and after (`HASHES_BEFORE_START_per_file.txt`, `HASHES_BEFORE.txt`, `HASHES_AFTER.txt`).

## 8. Downloads
Only the 12 files logged in `fire_event_dataset/data/raw/extra_fires/MANIFEST.csv` (`p2_sa_dss`, `p2_sa_lggc`, `p2_sa_bpa`, `p0_census2016`) plus files already on disk. Web pages are read, nothing else is fetched to disk. The LGGC PDFs are the web-archive originals of the SA government files (live host blocks programs).
Text extracted from the PDFs is written to the git-ignored data folder.

## 9. Order of work (each step hashed)
1. This file locked (`PRESPEC.lock`). 2. Polygons, roster, comparison groups (`build_rows.py`); score table built (`build_scores.py`); **`SCORES.lock` before any Y is computed**. 3. Homes-destroyed sources collected (`inputs_dl/`), Y inputs built (`build_y.py`), `Y.lock`.
4. `run_frozen_test.py` run once. Any error found later is a dated amendment before re-running; earlier output files stay.

## 10. Interpretation limits (stated in advance)
About 15-20 SA rows from 5 events, 3 of them in the Black Summer season; Adelaide Hills appears in two events; SA H and E are in a different classification from NSW and are placed in NSW scales; SA E uses 2021 mesh blocks; V and IL sources are national but on different releases;
SA FP is built from substitutes with a scale check; Sampson Flat lacks the business-count indicator; DL exists only where a sourced council figure is found; the cluster bootstrap ignores within-event dependence (shared weather and burn), so the true uncertainty is larger than shown.

## 11. Seeds and versions
Python 3 with pandas, numpy, scipy (anaconda) for statistics; geopandas/pyogrio (project `.venv`) for overlays; `xlrd`/`openpyxl`/`pdfminer.six` (`/Users/ray/.venv`) for old `.xls`, `.xlsx` and PDFs. Seeds: bootstrap `20261101`, power `20261102`.

## 12. Amendments
(none yet)
