# STAGE 2 PRE-SPECIFICATION (exploratory re-estimate on SEEN rows) - written 2026-09-29, before any stage-2 input is built

**Status of this stage.** The frozen first-stage result (`../FINDINGS.md`: pooled Spearman +0.00 [-0.40, +0.40], verdict CANNOT TELL; locks `PRESPEC.lock`, `SCORES.lock`, `Y.lock`; output `../results/frozen_test/`) is untouched and remains THE result. The 26 rows' outcomes have been seen, so anything below is an **exploratory re-estimate**, reported next to the frozen result and never replacing it. Nothing here is chosen by looking at a correlation with Y; every choice is written down first from documentation.

## 1. What stage 2 may change (and nothing else)
Only INPUTS that were missing in stage 1. The score table (`../results/SCORES_new_rows.csv`), the row set (26 scored rows, burned share >= 1%), all existing Y recipes/cells, the verdict rule, seeds and bootstrap settings are reused unchanged.

### 1.1 Victorian hazard (H) via NV2005 - NOT built
Ray approved fetching the NV2005 EVC layer only if 10 MB or smaller. The DataVic catalogue lists it only as shapefile/GDB/TAB/DWG orders through the DELWP DataShare portal (size field 0, no size stated), or WMS/WFS; scoping counted 2.39 million polygons. Size unknown and not findable, so per the instruction NO download was attempted and Victorian H, E stay unavailable. Consequence: the Victorian score remains V only, so the score table is identical to stage 1. (Recorded for Ray's decision in FINDINGS_STAGE2.md.)

### 1.2 NSW 2013 social-loss pillar (SL) from DSS - the master recipe cannot be reproduced exactly
Master SL (`src/vulnerable.py`): working-age income-support recipients in the quarter after the fire-start quarter minus the same quarter a year earlier, per 1,000 residents (ERP, year before the fire), minus the median of the same change over same-state councils with no fire >= 100 ha in the window; signed +; percentile in the master's 213 SL values. For Oct 2013 the fire-start quarter is 2013Q4, the after-quarter 2014Q1 (March 2014) and the year-earlier quarter is March 2013, which DSS did not publish (the series starts September 2013). Documentation-based decision, fixed now:
- Use **before = September 2013 (2013Q3) and after = March 2014 (2014Q1)**: a six-month change from the last quarter before the fire to the quarter after the fire-start quarter. Flag `computed_low_confidence` (window half the master's, different season; the excess step removes only a common shift). No rescaling to 12 months.
- `income_support_total` = the master's definition (`src/dss.py`): Newstart_Allowance + Youth_Allowance_other + Parenting_Payment_Single + Parenting_Payment_Partnered + Disability_Support_Pension + Carer_Payment + Special_Benefit + Sickness_Allowance + Partner_Allowance + Widow_Allowance + Widow_B_Pension + both Wife_Pension columns; NaN if any component is non-numeric.
- Files (approved, logged in MANIFEST): `dss_sep2013_by2013lga_and_payment.csv` (LGA 2013 codes) and `dss_mar2014_by2014lga_and_payment.csv` (LGA 2014 codes); joined by ABS LGA code, checked by name; pre-merger councils (Wyong, Guyra) kept by their own code but they are unscored anyway.
- Residents: ABS ERP 30 June 2012 (`32180DS0004_2001-25.xlsx`, 2025 boundaries, by LGA code; councils whose 2013 code is absent there get no SL).
- Comparison group: NSW councils (2013/2014 codes) with ERP available and no GA fire >= 100 ha inside during FY2013-14 (the `FY2013-14`, LGA 2015 flags in `../results/comparison_groups.csv`).
- Raw signed value = +excess per 1,000; percentile placed in the master SL reference (`../inputs/master_reference_indicators.csv`, column `SL_income_support_excess_signed`) by the same rule as in stage 1. The SL pillar = that percentile. SL stays N/A for Victoria (pre-2013 DSS not available).

### 1.3 Victorian homes destroyed (DL)
Continue reading official pages with WebSearch/WebFetch only. A council cell is filled only if a source gives a **destroyed-only** count for that council (houses/homes/dwellings), from: Victorian Bushfires Royal Commission, VBRRA, Victorian/Commonwealth government, council official documents, AIDR, CSIRO/Bushfire CRC, ABC, audit offices; never ACM or Wikipedia. Each with URL and quote. Rules fixed now:
- Combined "destroyed or damaged" counts are not used.
- If an official inquiry/authority figure (VBRC, VBRRA) for the council exists, it supersedes a council's own narrative figure; otherwise the stage-1 values (Nillumbik 135, Murrindindi 1,397) are kept.
- Fire-level figures are attributed to a council only if the source itself states that the fire lies wholly within it (stage-1 rule).
- Zeros are inferred only if a source gives a full LGA table that sums to its stated statewide total (then unlisted councils = 0, flagged `inferred`). Otherwise blank.
- Where two allowed sources for the same council differ by more than 10%, the cell is left blank unless one is an inquiry/authority figure (previous rule).

## 2. Re-estimate
- Y_new2 = mean of the pillars present (DL, IL, FP, SL), `pillars_n` recorded, exactly as in stage 1 but with the new SL cells (NSW) and any newly filled Victorian DL cells.
- Primary (labelled EXPLORATORY): Spearman(`risk_add_avail`, `Y_new2`), pooled 26 rows, council-cluster bootstrap 5,000 draws seed 20261001, percentile 95% CI. Same verdict rule: REPLICATED if lo > 0, NOT REPLICATED if hi < +0.30, otherwise CANNOT TELL. Also the same per-event, DL-only, pillar (adding SL), S1, S2 and descriptive sensitivities as stage 1, and the same planted-effect power check (seed 20261002) on the new row set.
- Reported side by side with the frozen stage-1 result in one table. If the stage-2 verdict differs from stage 1 the write-up must say the difference comes from exploratory inputs added after the outcomes were seen.
- Stage 2 is run once. Errors found afterwards are dated amendments with earlier output kept.

## 3. Not done in stage 2
No South Australia or other new fires; no downloads other than the two DSS CSVs; no writes to the master workbook, `aussef.duckdb` or `fire_event_dataset/out/`; `Experiment 6/REPORT.md` unedited; no commit or push.
