# Stage 2 (EXPLORATORY): filling the gaps from section 10 of the frozen result (2026-09-29)

**This is an exploratory re-estimate on rows whose outcomes were already seen. It sits beside, and never replaces, the frozen result in `../FINDINGS.md` (pooled Spearman +0.00 [-0.40, +0.40], verdict CANNOT TELL). The frozen files, locks and output were not touched; `run_frozen_test.py` was not re-run.**

## Plain summary (5 lines)
1. Verdict is unchanged: **CANNOT TELL**. Frozen: +0.00 [-0.40, +0.40]. Exploratory stage 2: **+0.12 [-0.27, +0.48]** on the same 26 rows (NSW +0.25, Victoria +0.10). The interval contains both 0 and +0.30, and the rows and score are the same, so the only thing that moved is the outcome measure.
2. What changed: a social-loss pillar (income-support recipients, DSS) was added for 13 NSW 2013 rows from two small approved CSVs. It moves 13 outcome values slightly and nudges the pooled estimate from 0.00 to +0.12. Nothing was added for Victoria: no new house-loss counts could be found and the vegetation layer was not downloaded.
3. Two of the three gaps stay open. **Victorian house loss per council: NOT FOUND** for 11 of 13 councils after a second round of reading (Royal Commission and VBRRA pages unreachable, the readable reports give fire-level figures only). **Victorian NV2005 vegetation: not downloaded**, because no file size is published and it is offered only through an order portal (polygon count about 2.4 million); I stopped as instructed and need your decision.
4. To settle the question the same design would need roughly 45-50 comparable council rows from independent fires to see a true correlation of 0.4 with 80% power (about 30 for 0.5, about 85 for 0.3; Fisher approximation, and the bootstrap table for the current 26 rows agrees: 52% at 0.4, 79% at 0.5). Rows within one fire are not independent, so the number of independent fires matters more than the number of rows.
5. Both workbook and database hashes are unchanged; two files were downloaded (150 KB each) and logged; nothing was committed.

## 1. What was done, in the order asked

| Item | Outcome |
|---|---|
| Stage-2 pre-spec written and hash-locked before any input was built | `PRESPEC_STAGE2.md` + `.lock`; amendment 1 (below) + `.lock`; `STAGE2_INPUTS.lock` (inputs and script, re-locked once after a column-name fix, before any result existed) |
| (i) Victorian homes destroyed, second round of reading | Nothing new. See section 3 |
| (ii-a) NV2005 EVC vegetation | **Not downloaded**: size unknown (see section 4) |
| (ii-b) DSS quarters | Downloaded and logged: Sep 2013 and Mar 2014 LGA-by-payment CSVs, 149,042 and 151,913 bytes |
| (iii) Re-run of the same primary test and power check | Done once, section 2 |

## 2. Results (exploratory), next to the frozen ones

| Test (score `risk_add_avail`) | Frozen stage 1 | Exploratory stage 2 |
|---|---|---|
| **Pooled, all 26 rows, Y (primary)** | **+0.00 [-0.40, +0.40]** | **+0.12 [-0.27, +0.48]** |
| NSW Oct 2013 (13 rows) | -0.07 [-0.64, +0.51] | +0.25 [-0.34, +0.63] |
| Victoria 2009 (13 rows) | +0.10 [-0.50, +0.62] | +0.10 [-0.49, +0.63] (same as stage 1: nothing changed) |
| DL only, pooled (11 rows) | -0.60 [-0.92, -0.04] | -0.60 [-0.92, -0.04] (unchanged) |
| IL pillar, pooled | +0.49 [+0.12, +0.75] | same |
| SL pillar, NSW (13 rows) | not built | +0.30 [-0.32, +0.77] |
| V alone (S1) vs Y, pooled | +0.14 [-0.24, +0.51] | +0.21 [-0.17, +0.55] |
| mean(H, V) (S2) vs Y, NSW = pooled | +0.04 [-0.50, +0.65] | +0.20 [-0.33, +0.72] |
| Rows 5%+ burned, pooled (14) | +0.20 [-0.39, +0.66] | +0.28 [-0.32, +0.71] |
| Y from 2+ pillars only, pooled (15) | -0.35 [-0.76, +0.23] | -0.10 [-0.57, +0.43] |
| Y without FP, pooled | +0.03 [-0.38, +0.41] | +0.17 [-0.23, +0.51] |
| Victorian IL from business counts only, pooled | -0.39 [-0.69, +0.02] | -0.27 [-0.61, +0.14] |

Verdict rule (unchanged): REPLICATED if the lower bound is above 0; NOT REPLICATED if the upper bound is below +0.30; otherwise CANNOT TELL. Stage 2: **CANNOT TELL**, the same as stage 1. Full tables: `results_stage2/exploratory_test/TEST_RESULTS_STAGE2.csv`.

**Does it change the conclusion?** No. The extra pillar made the point estimates a little more positive (NSW -0.07 to +0.25, pooled 0.00 to +0.12), but that difference comes from exploratory inputs added after the outcomes were seen, and every interval still spans zero. The DL result (negative, 11 rows) is unchanged because no DL cell changed.

**Power on the (unchanged) row set** (`POWER_CHECK_STAGE2.csv`; same X, same n=26, same seed, so identical to stage 1): detection probability 33% at a true correlation of 0.3, 52% at 0.4, 79% at 0.5, 93% at 0.6; under a true zero, only 31% of runs would end in "not replicated".

## 3. Victorian house loss (DL): still not found
A second reading round (WebSearch/WebFetch only; no Wikipedia, no ACM) covered CFA, AIDR, ABC, council pages, the PLOS ONE house-loss paper and the readable parts of the VBRRA 15-month and Three-Year reports. I also searched the cached text of the already-fetched Yarra Ranges evaluation and VBRRA report myself for council-level "destroyed" counts. Result:
- No council-level destroyed-only count for Yarra Ranges, Whittlesea, Mitchell, Latrobe, South Gippsland, Alpine, Baw Baw, Cardinia, Mount Alexander, Indigo or Wellington. No source gives a full LGA table that sums to a statewide total, so no zeros can be inferred.
- Fire-level figures (not attributable to a council under the locked rule): Kilmore East 1,242 (Whittlesea, Mitchell, Nillumbik, Yarra Ranges and parts of Murrindindi per the sources), Murrindindi 538, Churchill 145, Bunyip 31, Redesdale 14, Beechworth-Mudgegonga 38, Bendigo 58; statewide 2,029.
- The Royal Commission volumes, the VBRRA 100-day report, DisasterAssist, the RDV memorial pages and web archive copies could not be opened from here (connection resets, 403, or blocked by the fetch tool). The most likely place for a real council table is one of those; **if you can fetch the Royal Commission Volume 1 fire chapters or the 100-day report on your machine, please save the PDF text and I will extract from it.**
- **Source conflicts (new and kept):** Murrindindi 1,397 (council info sheet) vs 1,242 (a VBRRA report; also the Kilmore East fire total everywhere else, probably a mislabel) vs 538 (Murrindindi fire); 1,780 = 1,242 + 538 (two fires combined); Churchill 145 (CFA, AIDR) vs 247 (AJEM 2013) vs 133 (Bushfire CRC preliminary); statewide 2,029 vs 2,133 ("damaged or destroyed") vs "almost 2,500 properties"; the CFA per-fire rows add to 2,056, not 2,029; Bunyip 31 vs about a dozen (unopened snippet); Yarra Ranges 304 is destroyed-or-unliveable (not used). Case-count figures from an appeal fund and rebuilding-permit counts (Nillumbik 85, Murrindindi 1,023) are not house-loss counts and were not used.
- Result for the test: the DL cells are exactly the stage-1 cells (Murrindindi 1,397, Nillumbik 135 reported).

## 4. NV2005 vegetation layer: stopped, needs your decision
- File: NV2005_EVCBCS ("Modelled 2005 Ecological Vegetation Classes with Bioregional Conservation Status"), formats SHP/GDB/TAB/MIF/DXF/DWG, plus WMS/WFS.
- Source: DataVic dataset page https://discover.data.vic.gov.au/dataset/native-vegetation-modelled-2005-ecological-vegetation-classes-with-bioregional-conservation-sta ; the download resources point to the DELWP DataShare portal (https://datashare.maps.vic.gov.au/search?md=a502df15-7b90-5e96-b1a0-ba29e95558b2), which is an order form, not a direct file.
- Size: **unknown** (the catalogue lists size 0 for every resource). The scoping notes counted about 2.39 million polygons, so a statewide shapefile is very likely hundreds of MB. Under your 10 MB rule I did not download or order it.
- Effect: Victorian H and E stay unavailable, so the Victorian score stays V only and the score table is identical to stage 1. Options for you: (a) order the file and tell me its size, or (b) approve a larger limit; (c) leave Victoria as V only.

## 5. NSW 2013 social-loss pillar (SL): recipe and its limits
Fixed in `PRESPEC_STAGE2.md` 1.2 before anything was computed, from documentation only:
- The master recipe (quarter after the fire-start quarter minus the same quarter a year earlier) needs March 2013, which DSS did not publish (series starts September 2013). Used instead **Sep 2013 to Mar 2014** (six months, flagged low confidence, not rescaled).
- Income support total = the master's definition (13 payment columns). The files suppress small cells as "<20"; the master rule (blank if any component is missing) would have blanked every council, so **Amendment 1 (locked before any SL value existed) counts "<20" as 10**. Imputed cells per row: 4 to 14 of 26. Another low-confidence flag.
- Per 1,000 residents (ERP June 2012), minus the median for 66 NSW councils with ERP and no GA fire of 100 ha or more in FY2013-14 (median +2.74 per 1,000); placed in the master's 213-row SL distribution. 13 of 15 rows have SL (Wyong and Guyra have no 2025-boundary ERP).
- Stage-2 pillar count: 9 NSW rows have four pillars, 5 have three, 1 has two; Victoria unchanged (11 rows with one pillar, 2 with two).

## 6. Disclosures
- Peer instruction versus your approval: a teammate session relayed that you had approved the two downloads. I did not act on that relay; I asked you directly, and you answered yes before I downloaded anything.
- Downloaded (approved, small, hash-logged in `fire_event_dataset/data/raw/extra_fires/MANIFEST.csv`, folder `p_stage2_dss/`): `dss_sep2013_by2013lga_and_payment.csv` (149,042 B, sha256 `a237a3f1...73557d`, source data.gov.au "DSS Benefit and Payment Recipient Demographics - quarterly data", resource 22801f16-c709-4e4b-9426-ba943bf7aaf7) and `dss_mar2014_by2014lga_and_payment.csv` (151,913 B, sha256 `0c6c001d...fe036`, resource e5232153-d057-4a58-9583-78f5e7a21d9c). `MANIFEST.csv` now has 10 rows, so its own hash differs from the one recorded in the stage-1 lock (the original 8 rows are unchanged and were re-verified).
- No South Australian or other fire was researched or downloaded. **Recommendation only:** the next most useful additions remain the SA fires and Victorian Black Summer from the scoping list, because the limit is the number of independent fires (about 45-50 comparable council rows are needed), not the pillar coverage.
- Protected files (SHA-256): workbook `123423eaed7174987f72c63cc40ad334e26c636b2e28358f94cf4fcd60c32ec3` before and after (match); `data/aussef.duckdb` `ce294c7e...b59` (match); `fire_event_dataset/out/` tree hash `7b0feec36ee0891f5143f2000ad51ad08142f3fa009cc319b9cf747e8d4bf69c` (match). `Experiment 6/REPORT.md` untouched. Nothing committed or pushed.

## 7. Files (`stage2/`)
`PRESPEC_STAGE2.md/.lock`, `PRESPEC_STAGE2_AMENDMENT_1.md/.lock`, `STAGE2_INPUTS.lock`, `build_sl.py`, `run_stage2.py`, `results_stage2/` (`SL_nsw2013.csv`, `Y_stage2_rows.csv`, `exploratory_test/TEST_RESULTS_STAGE2.csv`, `POWER_CHECK_STAGE2.csv`, `VERDICT_STAGE2.json`), `inputs_dl/dl_stage2_additions.csv` (empty: nothing new found), `logs/stage2_run.log`.
