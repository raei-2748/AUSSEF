# PRE-SPECIFICATION (frozen before any Y is computed for the new fires)

Test of the Experiment 6 pre-fire council risk score on two fires that are independent of Black Summer:
**NSW October 2013** and **Victoria Black Saturday, 7 February 2009**.
Written 2026-09-29, before any income, business-count, council-finance or homes-destroyed value for a new-fire
council was read or computed, and before any score-versus-outcome relation for a new-fire council was looked at.
This file is hash-locked by `lock_prespec.py` (SHA-256 in `PRESPEC.lock`). `run_frozen_test.py` refuses to run if this file changes.
A change is only allowed as a dated amendment (section 12) written BEFORE the affected step is re-run; earlier outputs are kept.

## 0. What I looked at before freezing (disclosure)

- Read: Experiment 6 REPORT, `build_and_validate_score.py`, the dataset builder (`fire_event_dataset/src/`), the workbook's `README`/`indicators`
  sheets (read only), the scoping notes and overlay table (burned shares by council), and the layout of the input files (sheet names, column labels).
- Reproduced the master's own indicator ranks from its raw columns (all seven match to 1e-16), to be sure the ECDF placement rule below is the master's rule.
- Saw by accident the first lines of two ABS business-count CSVs for non-fire councils (Albury, Armidale Dumaresq). No fire council's value was read.
- Did NOT read or compute: any new-fire council's income, business count, finance ratio, unemployment, SEIFA, homes destroyed, or Y.
- Web research on homes destroyed per council was started in parallel (by sub-agents) and is only used through the sourcing rule in 5.1.

## 1. The exact score being tested

Score inputs and construction are those of `Experiment 6/build_and_validate_score.py` run with `v2` (exposure v2), unchanged:
four blocks H, E (v2), V, F. Each item is a 0-1 percentile in the **original NSW 129-council distribution**, oriented so 1 = worse;
a block is the mean of its available items; **`risk_add` = equal-weight mean of the blocks present**. No weight, item list or orientation is changed
except where section 2 says an item or block cannot be built for a row (then it is omitted, not replaced).

- **Primary score:** `risk_add` (mean of H, E v2, V, F; for a row, the mean of the blocks that exist for that row). Called `risk_add_avail`.
- **Secondary scores (declared now, no others):** (S1) the **V block alone**; (S2) **mean(H, V)** (`risk_HV_mean`).
  Secondary results are reported but can never turn a failed primary test into a replication.

### 1.1 Placement in the original distribution (never re-ranked with new rows)
For an item value v and the n original values x (the 129-council snapshot values in `COUNCIL_ITEMS_v2.csv`, non-missing only), the placed percentile is

**pct(v) = (n_better + n_equal/2 + 1) / (n + 1)**

where n_better = number of original values that are *less bad* than v (x < v for a "higher = worse" item, x > v for a "lower = worse" item) and
n_equal = number of original values equal to v. So a value worse than every original scores 1, one better than every original scores 1/(n+1).
This is the master's average-rank rule applied to the original values plus v alone. The original 129 councils' own percentiles are never changed.
Because H and E items are time-invariant maps, **NSW rows take the published H and E percentiles unchanged**; only items re-measured
for a pre-fire vintage (V and F items for NSW 2013; all V items for Victoria) are placed.

### 1.2 Pre-fire vintage rule (why V/F for NSW 2013 are not the published values)
The published NSW V and F items are the FY2014-15 snapshot (`year` 2014 in `lga_year`), i.e. measured after the Oct 2013 fire and equal to the
"plus-one" year used by the FP outcome (a mechanical link between F and FP would follow). So for both new events, each V and F item is taken from the
**last period that ended before the fire's financial year began** (NSW 2013: FY2012-13 or the quarter to June 2013 or Census 2011; Victoria 2009:
FY2007-08 or Census 2006), and placed in the original distribution as in 1.1.
- **Money and rate items are put on a unit-free scale first:** median income (dollars) and unemployment rate are divided by the median, across the
  129 NSW councils, of the same series in the same period (same source and year) before placement; original values are divided by the median of the snapshot
  column (a monotone change, so original percentiles do not move). SEIFA IRSD is used as published (nationally standardised each census).
- H and E use the current NSW maps (see 2): NSW BFPL is the current, post-2019 mapping, **not a 2013 snapshot**; NVIS 6.0 is time-invariant;
  E v2 uses 2016 Census mesh blocks. These are limits of the score itself (Experiment 6 limit 3), unchanged here.

## 2. Which blocks can be built, for which event, from what

| Block | NSW Oct 2013 | Victoria 7 Feb 2009 |
|---|---|---|
| **H** hazard | Yes. Published values (BFPL Cat 1 share, Cat 1+2 share, NVIS 6.0 forest share). BFPL is current post-2019, not 2013 | **Omitted.** No BFPL equivalent exists for Victoria, the national NVIS 7.0 on disk is a FileGDB raster this GDAL cannot read, and the Victorian NV2005 vegetation layer has not been approved for download |
| **E** exposure (v2) | Yes. Published values (dwellings and residents inside BFPL Cat 1-2, share) | **Omitted** (same reason: needs BFPL) |
| **V** vulnerability | Yes. SEIFA 2011 IRSD (ABS, released 18 Jul 2013); ABS PIA median income FY2012-13 (÷ NSW median); SALM smoothed unemployment rate, quarter to June 2013 (÷ NSW median) | Yes, two of three items. SEIFA 2006 IRSD (released Mar 2008); ABS EPISA median income FY2007-08 (÷ NSW-council median of the same EPISA release). **Unemployment omitted** (SALM starts Dec 2010) |
| **F** fiscal | Partly. FY2012-13 NSW OLG items, only those with a comparable definition: unrestricted current ratio, operating performance ratio, infrastructure backlog ratio. **Dropped by rule:** cash expense cover and own-source revenue (documented OLG definition break between FY2012-13 and FY2013-14; scoping A1), debt service ratio (not published for FY2012-13; the debt service *cover* ratio is a different measure). Any further item whose FY2012-13 across-council median differs by more than 30% from the median of the same councils in the original snapshot is also dropped (mechanical check, Step 2 log). F is used only if at least 2 items remain, else omitted | **Omitted.** Victorian finance ratios are defined differently from NSW OLG ratios and are not comparable (scoping section 7) |

Consequences (declared now):
- **NSW rows:** `risk_add_avail` = mean(H, E, V, F) (F possibly with 3 items or omitted).
- **Victorian rows:** `risk_add_avail` = V only, identical to S1. **mean(H, V) (S2) exists for NSW rows only.** The pooled `risk_add_avail`
  test therefore mixes a four-block score (NSW) with a one-block score (Victoria); the pooled **V-alone** test (S1) is the one clean like-for-like pooled comparison.
- NSW councils that were merged in 2016 (**Wyong**, **Guyra**) have no council in the original 129 and no like-for-like items; they stay in the row
  table with score `N/A` and are excluded from every score-based test (counted and listed in FINDINGS).

## 3. Events, fire polygons, rows

Fire outlines: Geoscience Australia national historical bushfire boundaries (`ga_original.zip` and `fire_attributes.csv`, on disk), as in the scoping
overlay (`overlay_candidates.py`, parameters copied unchanged). Excluded: prescribed burns.

| Event | State | Ignition window (inclusive) | Min polygon area | LGA layer | Fire financial year | Prior FY (t-1) / next FY (t+1) |
|---|---|---|---|---|---|---|
| NSW Oct 2013 | NSW | 2013-10-10 to 2013-10-31 | 1,000 ha | ABS LGA 2015 | FY2013-14 | FY2012-13 / FY2014-15 |
| Victoria Black Saturday | VIC | 2009-02-04 to 2009-02-09 | 1,000 ha | ABS LGA 2015 | FY2008-09 | FY2007-08 / FY2009-10 |

**Row inclusion rule (frozen): every council whose burned share (union of the event's polygons inside the council, ÷ council area, EPSG:3577) is at least 1%.**
"Unincorporated" areas are not councils and are excluded. Expected roster from the scoping overlay (recomputed in Step 2 with the same parameters; **the ≥1% rule governs, the list below is for reference**, and any difference is reported):
- NSW (15 rows, 13 scoreable): Hawkesbury 18.2%, Blue Mountains 14.1%, Muswellbrook 13.5%, Lithgow 8.3%, Port Stephens 7.0%, Wollondilly 3.0%,
  Wingecarribee 2.6%, Clarence Valley 2.4%, Wyong 2.2% (no score), Guyra 2.0% (no score), Cessnock 1.9%, Lake Macquarie 1.9%, Shoalhaven 1.7%, Wollongong 1.4%, Singleton 1.1%.
- Victoria (13 rows): Murrindindi 40.3%, Nillumbik 23.2%, Yarra Ranges 18.8%, Whittlesea 17.2%, Mitchell 12.6%, Latrobe 10.9%, South Gippsland 7.4%,
  Alpine 7.3%, Baw Baw 5.5%, Cardinia 4.4%, Mount Alexander 2.1%, Indigo 2.1%, Wellington 1.2%.
- Rows at 5% or more: 5 NSW + 9 Victoria = 14 (a **pre-declared descriptive subset**, not the verdict sample).

Council key: ABS LGA 2015 code. Victorian councils are unchanged 2009-2021 (scoping). NSW: LGA 2015 councils are the councils in force in 2013; the score exists
only for those that also exist unchanged (same ABS code and area within 1%) in LGA 2021; this is checked and reported.

## 4. Exact Y construction (per pillar, per event)

Y is built the master's way: each indicator is signed so higher = worse, converted to a percentile, a pillar is the mean of its indicators' percentiles,
and **Y_new = mean of the pillars present**, with `pillars_n` recorded. The pillar/indicator list, signs and source-column averaging are the master's:

| Pillar | Indicator (sign) | Raw value | Reference distribution (master, n) |
|---|---|---|---|
| DL | homes destroyed per 1,000 dwellings (+) | homes destroyed ÷ private dwellings × 1000 | 90 |
| IL | total personal income fall, excess (-) | % change in total personal income, fire FY vs t-1, minus median over comparison councils | 165 |
| IL | business count fall, excess (-) | % change in businesses at 30 June (t-1 to t), minus comparison median | 217 |
| FP | cash cover drawdown, excess (-) | mean of (cash cover change FY t vs t-1, and FY t+1 vs t-1), each minus its comparison median | 199 |
| FP | services crowd-out, excess (-) | change in the services share of spending, FY t+1 vs t-1, minus comparison median | 193 |
| FP | renewals ratio rise, excess (+) | change in building & infrastructure renewals ratio, FY t+1 vs t-1, minus comparison median | 199 |
| SL | income-support recipients rise, excess (+) | not buildable | 213 |

**Percentile rule for new rows (frozen):** each new row's raw (signed) indicator value is placed in the EXISTING master distribution of the same raw
indicator (the 218 master rows, non-missing): `pct = (n_less + n_equal/2 + 1)/(n + 1)` where n_less counts master values below the new value (in signed terms,
so higher = worse). The master's own ranks and the new rows are **never re-ranked together**. Ties (e.g. a DL of zero) take the average position.

### 4.1 Pillars by event
| Pillar | NSW Oct 2013 | Victoria 2009 |
|---|---|---|
| DL | Buildable where the council's homes destroyed is sourced (5.1); blank otherwise. Dwellings: Census 2011 (latest census at or before the fire year) | Same: sourced homes destroyed (5.1) ÷ Census 2011 dwellings (2011 is the first national pack after the fire; 2006 has no national pack; flagged) |
| IL | Both indicators. Total income: ABS PIA (release with FY2012-13 and FY2013-14; latest release covering both). Businesses: ABS National Regional Profile economy 2010-14 (30 June 2013 to 30 June 2014) | Both indicators. Total income: ABS EPISA 2005-06 to 2010-11 (FY2008-09 vs FY2007-08; one release, no cross-product changes). Businesses: NRP economy 2008-12 (30 June 2008 to 30 June 2009) |
| FP | Built as the master does from NSW OLG Time Series (FY2012-13, 2013-14, 2014-15). **Lower confidence:** OLG definition break FY2012-13 to FY2013-14 (cash cover); the excess design removes a uniform shift but not a council-specific one; flagged `computed_low_confidence` | **N/A (not comparable).** The VAGO 2010-11 audit ratios are different quantities (liquidity, self-financing, etc.) and not the three master FP indicators |
| SL | **N/A** (no DSS quarter a year before; DSS on disk from Mar 2016) | **N/A** |

Pillars expected absent: SL for every row; FP for Victoria. DL is blank wherever no sourced council figure exists (5.1). Y_new is therefore a mean of 1-3 pillars; rows with 1 pillar
(most Victorian rows, if council homes destroyed are not found) are kept in the primary Y_new and tested; the count is always reported.

### 4.2 Excess-change comparison group (frozen)
For each new event and each measure, the comparison group is the **councils of the same state with no fire of 100 ha or more burning inside them during the
measure's window** (fire ignition inside the fire FY for a measure that ends in FY t; inside FY t or t+1 for a measure that ends in FY t+1), using the same GA
non-prescribed polygons (all sizes; burned area per council = union of polygons ignited in the window, inside the council, ≥ 100 ha). The excess is the council's change minus
the **median** change over those councils. Limit: GA's NSW records are NSW National Parks (agency NSW PWS) outlines, so private-land fires are under-mapped and some
"no-fire" NSW councils may have had fires; this is reported. Comparison-group sizes are logged.

## 5. Homes destroyed (DL numerator): sourcing rule

### 5.1 Rule
Only from: RFS (Bush Fire Bulletins, annual reports, media), Victorian Bushfires Royal Commission (final report/exhibits), VBRRA, Victorian and NSW
government, council official documents, AIDR, Bushfire CRC, ABC News, audit offices. **Not** ACM mastheads, **not** Wikipedia.
Every figure carries source title, URL and a short verbatim quote in the row-level source table.
- `reported`: the source gives a count for the council (or for a fire wholly inside one council).
- `inferred`: an official whole-event total equals the sum of the fires/councils the source names, so a council not named gets 0 (same practice as the DL-fill follow-up). Flagged, never shown as reported.
- **Blank:** a fire's losses span several councils and the split is not stated, or no source is found. Nothing is guessed. Where a council-level figure is on a different basis from the official
  fire-level totals (e.g. a council's own count), it is used only as `reported` with the basis noted.
- NSW Oct 2013: fire-level RFS figures are attributed to a council only where the fire lies wholly inside it (Linksview Road and Mt York Road: Blue Mountains; Lower Hunter/Port Stephens fires: Port Stephens).
  State Mine (5) and Hall Road (2) are not attributed when their split is not stated.

## 6. Tests (all frozen)

- Rank correlation: Spearman (average ranks) between score and target on the new rows.
- Uncertainty: **council-cluster bootstrap**, 5,000 draws, percentile 95% CI, seed `20261001`. Each council appears once, so this equals a row bootstrap;
  it does not account for shared weather and burn within an event (stated limit). Estimable only with at least 6 rows and at least 3 distinct values on each side.
- **Primary test (the only one that decides the verdict):** Spearman(`risk_add_avail`, `Y_new`) on the **pooled** rows (both events), rows with burned share ≥ 1%, a score, and Y_new (≥1 pillar).
- Reported alongside, same score and target: each event separately (NSW Oct 2013, Victoria 2009); **DL-only** (pooled and per event): Spearman(`risk_add_avail`, DL pillar).
- Each pillar separately (DL, IL, FP), pooled and per event, `risk_add_avail` vs the pillar (descriptive).
- Secondary scores S1 (V alone) and S2 (mean(H, V)) against Y_new, pooled and per event, the same way (S2 NSW only).
- Pre-declared descriptive sensitivities (never used for the verdict): (a) rows with burned share ≥ 5% only; (b) Y_new requiring at least 2 pillars (the master's rule); (c) Y_new without the FP pillar;
  (d) DL using `reported` values only (no inferred zeros); (e) leaving out each event in turn (already covered by per-event results).
- No multiplicity adjustment. Only the primary test decides the verdict.

### 6.1 Replication rule (frozen, based on the pooled primary interval [lo, hi] and estimate r)
- **REPLICATED:** lo > 0.
- **NOT REPLICATED:** hi < +0.30 (the data exclude effects as large as the smaller Experiment 6 headline estimates, +0.34 on ≥5% fires with v1 and +0.36 on ≥2% fires with v2).
- **CANNOT TELL:** anything else (interval contains both 0 and +0.30).
- Extra caveats always stated with the verdict: whether each single event has a positive estimate; that the rows are few and events independent of Black Summer but only two;
  that Victoria's score is V alone; that source vintages differ from the NSW 2015-2025 master; a leaning-against note if r ≤ 0 with a wide interval (this is still "cannot tell").

### 6.2 Planted-effect power check (frozen; uses no real Y)
On the actual row set with a score and a Y_new (only which rows exist is used), fake Y is drawn as `Y_sim = ρ·z(rank(score)) + sqrt(1-ρ²)·ε`, ε standard normal,
for ρ ∈ {0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6}, 1,000 simulations per ρ, 500 bootstrap draws each (seed `20261002`). Reported: the share of simulations with lo > 0 (**power to replicate**),
and the share with hi < 0.30 at each ρ (**chance of "not replicated"**). A null (interval containing 0) is read against this table.
Also reported for the ≥5% subset and for each event alone.

## 7. Output files, flags, blank vs N/A
`fire_event_dataset/data/extra_fires/extra_fire_rows.csv` (git-ignored data folder): event id/name, region_id, region_name, first_fire_start, share burned, burn ha, X blocks (H, E, V, F, blocks_n),
`risk_add_avail`, S1, S2, each pillar, `pillars_n`, `Y_new`, one **source-flag column per cell group** (`reported` / `computed` / `computed_low_confidence` / `inferred` / `unavailable`) and a note column.
Blank = not computed or not found; `N/A` = the rule says it cannot exist. Master workbook, `data/aussef.duckdb` and `fire_event_dataset/out/` are never written; SHA-256 recorded before and after.

## 8. Downloads
Only the 8 files in `fire_event_dataset/data/raw/extra_fires/MANIFEST.csv` (hash-checked at lock time) plus files already on disk. The Victorian NV2005 layer and any
Victorian hazard layer are NOT used. Web pages are read but nothing else is fetched to disk.

## 9. Order of work (each step hashed)
1. This file locked (`PRESPEC.lock`). 2. Rows, polygons and X blocks built; the **score table is hashed (`SCORES.lock`) before any Y is computed**. 3. Y inputs built and written to `extra_fire_rows.csv`.
4. `run_frozen_test.py` run once. Any error found later is a dated amendment before re-running; earlier output files stay.

## 10. Interpretation limits (stated in advance)
Two events; ~26 scoreable rows; Victorian score is one block; NSW 2013 uses current maps and a reduced F block; Y_new is a mean of 1-3 pillars on sources of different vintage and, for IL/DL in Victoria,
different products (EPISA, NRP) from the NSW master (PIA, CABEE); the master reference distribution is 2015-2025 NSW; GA NSW outlines under-map private-land fire; cluster bootstrap ignores within-event dependence.

## 11. Seeds and versions
Python 3 with pandas, numpy, scipy (anaconda) for statistics; geopandas/pyogrio (project `.venv`) for overlays; `xlrd` (already installed under `/Users/ray/.venv`, pure Python) for old `.xls` files. Seeds: bootstrap 20261001, power 20261002.

## 12. Amendments
(none yet)
