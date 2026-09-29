# Fiscal benchmark measure: does meeting NSW OLG's own benchmarks predict fire impact?

2026-09-29. Follow-up to Experiment 6 (`Experiment 6/REPORT.md`, not edited). All work is in this folder; nothing is committed.

## Plain summary (5 lines)

1. NSW OLG's benchmarks were read from the official documents. Your earlier guess was right on all seven; the correct list also has asset maintenance > 100% and a rates-outstanding test (Section 1).
2. The benchmark-count measure (share of 8 benchmarks met over the 3 financial years before the fire, fixed before looking at Y) has moderate face validity: it tracks the 2013 TCorp sustainability ratings (rho +0.41, n=128) and puts 4 of 5 councils with independent, documented financial trouble in the weakest third (Tenterfield is the miss). It also ranks Balranald, a governance-only administration, low (Section 3).
3. Against impact there is nothing. On all 207 rows Spearman with Y is +0.10 [-0.10, +0.28]; on fires burning >= 5% of a council (38 rows) +0.13 [-0.25, +0.46]; excluding Black Summer +0.10 [-0.13, +0.32]. DL, IL, FP and SL are the same. The old F is +0.04, and the difference between them includes 0 everywhere (Section 4).
4. The old F's stale 2014/15 snapshot is not the reason: recomputing the old six-ratio block for each fire's own 3 pre-fire years (F_tm) is also null, and after removing a common fire-year trend the primary estimate falls to +0.04 [-0.12, +0.20].
5. Read this as "no evidence of a link in these data", not "finances do not matter": on all rows the test would almost surely catch a correlation of 0.3 (power 100%; 80% at 0.2), but on the >= 5% fires it has 47% power at 0.3, and excluding Black Summer only 8 such rows remain.

## 1. The official benchmarks (verified, with sources)

| Ratio | Benchmark used | Wording in the source |
|---|---|---|
| Operating performance ratio | > 0% | "greater than zero per cent" (Audit Office, App. 9); "0% or greater" (OLG Your Council) |
| Own source operating revenue | > 60% | "greater than 60 per cent"; "60% or greater" |
| Unrestricted current ratio | > 1.5x | "greater than 1.5 times"; OLG page: "less than 1.5 is considered unsatisfactory" |
| Debt service cover ratio | > 2x | "greater than two times"; "greater than 2.0" |
| Cash expense cover ratio | > 3 months | "greater than three months" |
| Building and infrastructure renewals ratio | > 100% | "The benchmark is greater than 100%." (Code, Section 4) |
| Infrastructure backlog ratio | < 2% | "The benchmark is less than 2%." (Code, Section 4) |
| Asset maintenance ratio | > 100% | "The benchmark is greater than 100%." (Code, Section 4) |
| Rates and annual charges outstanding | < 5% metropolitan, < 10% rural | not used (see below) |

Sources read in full or in the relevant part (all fetched 2026-09-29):
- NSW Auditor-General, Report on Local Government 2018, Appendix nine, "OLG's performance indicators from the audited financial statement - Descriptions" (financial year 2017-18): https://www.audit.nsw.gov.au/sites/default/files/auditoffice/2019%20Reports/Report%20on%20Local%20Government%202018/Appendix%20nine%20-%20OLG%E2%80%99s%20performance%20indicators%20from%20the%20audited%20financial%20statement%20-%20Descriptions.pdf . Each entry says "The benchmark set by OLG" and gives the values above, and "less than five per cent for metropolitan and less than ten per cent for rural councils" for rates outstanding.
- OLG, Your Council June 2015 (Table 2, "Average financial results 2013/14", benchmark column `>0%, >3.0, >60%, >1.5:1, >0-<20%, >2.0, <5% Metro <10% Rural` for operating performance, cash expense cover, own source, unrestricted current, debt service ratio, debt service cover, rates outstanding; text: "The benchmark for this ratio is greater than 2.0."): https://www.olg.nsw.gov.au/sites/default/files/2026-02/your-council-june-2015-profile-and-performance-of-the-nsw-local-government-sector.pdf
- OLG, Local Government Code of Accounting Practice and Financial Reporting 2025/26, Section 4 Special Schedules, "Infrastructure asset performance indicators" (renewals > 100%, backlog < 2%, maintenance > 100%): https://www.olg.nsw.gov.au/sites/default/files/2026-02/local-government-code-of-accounting-practice-and-financial-reporting-section-4-special-schedules.pdf . Section 1 of the same Code no longer prints the financial-ratio table, so the financial thresholds come from the two documents above and the page below.
- OLG, Your Council NSW, Finances page (2024-25), which repeats the financial thresholds (0% or greater; 60% or greater; greater than 2.0; greater than 3 months; rates outstanding <5% city and coastal, <10% regional and rural): https://yourcouncil.nsw.gov.au/nsw-overview/finances/ (read through a page summary tool, not byte-checked).
- The Fit for the Future (2015) test judged several ratios on a 3-year average ("Greater than or equal to break-even average over 3 years", own source "Greater than 60% average over 3 years", renewals "Greater than 100% average over 3 years", backlog "Less than 2%", maintenance "Greater than 100% average over 3 years", debt service ratio "Greater than 0% and less than or equal to 20%"). Read in a council's improvement proposal on the IPART site (template text): https://www.ipart.nsw.gov.au/sites/default/files/cm9_documents/Attachment-2-Fit-for-the-Future-Documentation.PDF . I did not find OLG's own methodology page (the OLG circular 15-17 link returned 404).

The financial thresholds are the same in the 2013/14, 2017/18 and 2024/25 documents, and the three infrastructure thresholds are the same in the 2015 Fit for the Future template and the 2025/26 Code, so one fixed table is used for every year. Checks against the earlier guess: all seven confirmed. Added: asset maintenance > 100%. Differences of wording only: the unrestricted current ratio is written as a "below 1.5 is unsatisfactory" line by OLG and "greater than 1.5 times" by the Audit Office; operating performance ">0" vs "0% or greater" (equality does not occur in the data).

Not used: rates and annual charges outstanding (not in the workbook; the metropolitan/rural split is worded three different ways across the documents); debt service ratio 0-20% (a Fit for the Future test that would penalise debt-free councils); real operating expenditure per capita (a trend test).

## 2. The measure (fixed in `bench_common.py` before any Y was read)

- 8 benchmarks: operating performance, own source revenue, unrestricted current, debt service cover, cash expense cover, renewals, backlog, asset maintenance. A blank debt service cover with a debt service ratio of exactly 0 (no debt) counts as met (6 council-years).
- Window: the 3 financial years before the fire's own financial year (fire FY = FY of the first fire start; FY convention checked against the raw OLG file, `lga_year.year` = FY start year, so 2014 = FY2014-15). Source: `lga_year`, FY2014-2023, the same source as the old F. A council-year needs >= 5 of 8 measurable; a window needs >= 2 usable years.
- `bench_share` (primary, higher = healthier) = benchmark-years met / benchmark-years measurable over the window. This is the average number met per year (scaled to 8) and the average share of years each benchmark is met. `stress_bench = 1 - bench_share`, same direction as the old F; the hypothesis is a positive Spearman with impact.
- Secondary, reported but not used to choose: `years_share` (years meeting more than half), `avg3_share` (Fit-for-the-Future style, judged on the 3-year mean), `fin5_share`, `infra3_share`, and `F_tm` (the old six-ratio percentile block recomputed inside each financial year and averaged over the same window).
- Coverage: 207 of 218 rows (all 69 fire councils, 90 of the 96 fires). The 11 dropped rows are fires in FY2014-2018 whose window falls before FY2014 or on merged councils with blank early years. Mean 5.2 of 8 benchmarks met (range 2.7-8).

Two things about the measure itself, seen before Y and not tuned:
- Three benchmarks are met almost everywhere (unrestricted current 94%, debt service cover 96%, cash expense cover 98% of council-years). The variation comes from operating performance (64% met), own source revenue (55%), renewals (40%), backlog (41%) and maintenance (49%).
- The benchmark pass/fail indicators barely agree with each other (mean off-diagonal Spearman 0.08), the same "unrelated ratios" pattern as the old F. Council-level persistence is reasonable (share in FY2016-18 vs FY2019-21: rho 0.62).

The old F used a single FY2014-15 snapshot for every fire, including fires up to 10 years later.

## 3. Face validity (done before the Y test)

**(a) Against TCorp's 2013 Financial Sustainability Ratings** (NSW Treasury Corporation ratings as printed for each council in IPART, "Assessment of Council Fit for the Future Proposals: Appendix C", Oct 2015, https://www.ipart.nsw.gov.au/sites/default/files/documents/assessment_of_council_fit_for_the_future_proposals_-_appendix_c_-_council_assessments_-_october_2015.pdf ; parsed into `TCORP_FSR_2013_from_IPART_AppendixC.csv`). Measure from the raw OLG file, FY2013-14 and FY2014-15 (the earliest years, covering pre-merger councils). TCorp's ratings rest on earlier data, so this is a persistence check.
- Spearman(TCorp rating, benchmark share) = +0.41 (p < 0.001, n=128 single-council pages).
- Mean benchmark share by TCorp rating: Very Weak 0.27 (n=3), Weak 0.54 (23), Moderate 0.58 (71), Sound 0.71 (29), Strong 0.53 (2).
- AUC for picking out TCorp Weak/Very Weak councils (26) from the others (102) by low benchmark share: 0.71. The three Very Weak councils (Gwydir, Gloucester, Greater Taree) are among the lowest four of 128.

**(b) Councils named in official sources** (list, event year and windows fixed in `KNOWN_COUNCILS.csv` before running `02b_face_validity_named.py`). Window = the 3 financial years before the event year. Percentile 0 = weakest of all councils in the same window.

| Council | Basis (source) | Window | Benchmarks met (of 8, by year) | Share | Percentile |
|---|---|---|---|---|---|
| Central Coast | Suspended 30 Oct 2020 after revealing an $89m debt (ABC, https://www.abc.net.au/news/2020-10-30/nsw-government-suspends-central-coast-council-over-debt/12832878) | FY2017-19 | 6, 4, 3 | 0.54 | 0.20 |
| Central Darling | Audit opinion emphasis: uncertain it could continue operating without restricted water and sewer funds, FY2016-17 (Audit Office LG2017, PDF p.23, https://www.audit.nsw.gov.au/sites/default/files/pdf-downloads/LG2017_Report%20on%20Local%20Government%202017%20Website%20PDF%20version_22-05-18.pdf); under administration since 2013 with "severe financial issues" (ABC 2023-07-04, https://www.abc.net.au/news/2023-07-04/central-darling-shire-council-administration-review-nsw-gov/102560114) | FY2013-15 (2 usable) | -, 1, 2 | 0.19 | 0.00 |
| Kiama | Minister's letter before the 2022 Performance Improvement Order: "may not be able to pay its debts as they fall due" (ABC, https://www.abc.net.au/news/2022-10-11/kiama-council-on-notice-nsw-government-financial-mismanagement/101523364) | FY2019-21 (2 usable) | 3, -, 2 | 0.31 | 0.00 |
| Tenterfield | Negative unrestricted cash of $1.2m, breach of s409(3), FY2020-21 (Audit Office LG2021, PDF p.12, https://www.audit.nsw.gov.au/sites/default/files/documents/FINAL%20REPORT%20-%20Local%20Government%202021.PDF) | FY2017-19 | 4, 6, 6 | 0.67 | **0.52** |
| Snowy Monaro Regional | "continued to face financial sustainability pressure in 2021-22" (Audit Office LG2022, PDF p.39, https://www.audit.nsw.gov.au/sites/default/files/documents/TABLING%20REPORT%20-%20Local%20Government%202022.pdf) | FY2018-20 | 4, 3, 5 | 0.50 | 0.15 |
| Bathurst Regional | Met none of the Audit Office's three sustainability benchmarks for at least three years (LG2024, PDF p.7, https://www.audit.nsw.gov.au/sites/default/files/documents/Final%20report%20-%20Local%20government%202024_0.pdf). **Circular**: same OLG ratios | FY2020-22 | 2, 3, 4 | 0.38 | 0.03 |
| Shoalhaven | Same finding. **Circular** | FY2020-22 | 4, 3, 4 | 0.46 | 0.09 |
| Balranald (control) | Administration from Jan 2020 for governance and workplace failures, not finances (ABC, https://www.abc.net.au/news/2020-01-31/nsw-balranald-council-placed-under-administration-after-inquiry/11912656) | FY2016-18 | 4, 4, 3 | 0.46 | 0.04 |
| Wingecarribee (control) | Councillors dismissed Jul 2022 for conduct and governance (ABC, https://www.abc.net.au/news/2022-07-14/wingecarribee-councillors-sacked/101236902) | FY2019-21 | 7, 8, 7 | 0.92 | 0.96 |

Reading: of the five independent financial-distress cases, four sit in the weakest third (median percentile 0.15) and Tenterfield sits mid-table (0.52; its 2020-21 problem was a cash breach that appeared after a window of 4-6 of 8). Central Coast was already weakening before its 2020 crisis (6, 4, 3 of 8). The two councils that fail all Audit Office benchmarks rank low, but that is close to circular. The controls split: Wingecarribee ranks near the top as expected, but Balranald, a governance-only case, also ranks near the bottom, so the measure is not specific to "administration for financial reasons". With 5 independent cases this is a sanity check, not a validation.

Not used and not verified by me: the sub-agent that searched for sources also proposed Armidale Regional (mixed suspension), Liverpool City, MidCoast, Cessnock and others from the later Audit Office reports; I did not include these. Its label of Balranald as partly financial did not survive my check of the ABC text and was dropped. It also reported TCorp 2013 "Very Weak" for Central Darling and Broken Hill from a council-hosted copy of the TCorp report that I did not open.

## 4. Test against impact (run only after Section 3 was on disk)

Spearman rank correlation with a council-cluster bootstrap (2,000 draws, seed 20260929, same routine as `build_and_validate_score.py`). Impact columns are from `Experiment 6/results/ROWS_WITH_SCORE_v2.csv` as of today (other sessions are revising FP and DL; rerun `03_validate_vs_Y.py` if they change). Higher `stress_bench` = weaker pre-fire finances; a positive value would support the idea.

**Primary score `stress_bench`** (95% CI in brackets):

| Rows | n | Y | DL | IL | FP | SL |
|---|---|---|---|---|---|---|
| all rows | 207 | +0.10 [-0.10, +0.28] | +0.11 [-0.14, +0.33] (86) | +0.10 [-0.12, +0.29] | +0.04 [-0.11, +0.20] (192) | +0.01 [-0.13, +0.15] (206) |
| fires >= 5% of the council burned | 38 | +0.13 [-0.25, +0.46] | +0.09 [-0.28, +0.43] (37) | +0.05 [-0.33, +0.37] | +0.20 [-0.13, +0.47] | -0.05 [-0.41, +0.33] |
| all rows excl. Black Summer | 157 | +0.10 [-0.13, +0.32] | +0.31 [-0.08, +0.60] (36) | +0.09 [-0.14, +0.31] | +0.02 [-0.18, +0.21] (142) | -0.01 [-0.19, +0.14] |
| >= 5% burned excl. Black Summer | 8 | +0.05 [-0.67, +0.89] | n/a | +0.48 [-0.32, +0.95] | +0.32 [-0.35, +0.89] | -0.14 [-0.92, +0.80] |

Every interval includes 0. The last row has 8 rows and says nothing.

**Old F block on the same rows** (static FY2014-15 snapshot):

| Rows | Y | DL | IL | FP | SL |
|---|---|---|---|---|---|
| all rows (n=207) | +0.04 [-0.16, +0.22] | -0.06 [-0.30, +0.14] | +0.03 [-0.19, +0.22] | +0.01 [-0.17, +0.18] | +0.06 [-0.09, +0.22] |
| >= 5% burned (n=38) | +0.00 [-0.39, +0.36] | -0.14 [-0.41, +0.14] | +0.29 [-0.09, +0.61] | -0.07 [-0.36, +0.22] | -0.02 [-0.39, +0.34] |
| all rows excl. Black Summer (n=157) | +0.00 [-0.24, +0.23] | +0.01 [-0.38, +0.33] | -0.02 [-0.26, +0.18] | +0.00 [-0.24, +0.23] | +0.01 [-0.16, +0.20] |

**Difference (new minus old F), same rows, same bootstrap draws:** all rows Y +0.06 [-0.15, +0.27], DL +0.17 [-0.07, +0.44], IL +0.07 [-0.10, +0.26], FP +0.03 [-0.12, +0.21], SL -0.05 [-0.22, +0.13]; >= 5% burned Y +0.13 [-0.28, +0.52], DL +0.22 [-0.18, +0.61], IL -0.24 [-0.61, +0.14], FP +0.27 [-0.18, +0.65], SL -0.04 [-0.46, +0.41]. All include 0: the benchmark measure is not distinguishably better than the old F, and both are null.

**Secondary scores** (`stress_years`, `stress_avg3`, `stress_fin5`, `stress_infra3`, `F_tm`; full grid in `VALIDATION_VS_Y.csv`/`.txt`): 168 intervals in total (7 scores x 5 targets x 5 row sets, some with no estimate), and 2 exclude 0: financial-only five benchmarks vs IL on all rows (+0.19 [+0.03, +0.36]) and F_tm vs SL in the Black-Summer-only reference set (+0.39 [+0.10, +0.63]). About 8 of 168 would clear 0 by chance with nothing there, so these are not findings. The measures overlap only moderately with each other (`stress_bench` vs old F +0.41, vs `F_tm` +0.61) and with vulnerability (Spearman with V +0.08).

**Post-hoc diagnostic (`05_within_year_diagnostic.py`, not pre-specified):** Y drifts up with the fire year (Spearman +0.32) and `stress_bench` drifts a little too (+0.11), so a pooled correlation can pick up a common trend. Ranking both within each fire financial year: Y +0.04 [-0.12, +0.20] (all rows), +0.02 [-0.18, +0.22] (excl. Black Summer), +0.12 [-0.22, +0.43] (>= 5% burned). Two of 30 intervals exclude 0 (SL excl. Black Summer -0.18 [-0.36, -0.00], the opposite sign; F_tm vs SL on >= 5% +0.34 [+0.03, +0.59]), again about what chance gives. Some of the +0.10 in the primary table is therefore a time trend.

**Power** (`04_power_new_measure.py`, same design as Experiment 6's power check; X = `stress_bench` ranked within fire year; Y shuffled within Black Summer / start year and a known correlation planted; % of 300 simulations where the 95% interval excludes 0):

| Rows | rho 0 (false alarm) | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 |
|---|---:|---:|---:|---:|---:|---:|
| all rows (207) | 1 | 26 | 80 | 100 | 100 | 100 |
| all rows excl. Black Summer (157) | 2 | 20 | 63 | 95 | 100 | 100 |
| fires >= 5% burned (38) | 5 | 11 | 29 | 47 | 78 | 93 |
| >= 5% burned excl. Black Summer (8) | 2 | 7 | 8 | 9 | 18 | 29 |

A first run with the raw (not year-ranked) measure gave 9% false alarms at rho 0 and 53% "power" at rho 0.1 because of the year drift above; it was discarded and its partial log is kept in `power_new_measure_raw_x_partial.log`.

## 5. What this does and does not say

- With OLG's own benchmarks, counted over the three years before each fire, pre-fire council finances show no detectable link to fire impact. That holds on all rows, on the large fires, and without Black Summer, and matches the old F block's null.
- The null is informative on all rows (an effect of 0.2-0.3 would very likely have shown up) but not on the large fires or without Black Summer, where the data cannot tell "no effect" from "too few fires". Nothing here supports "finances do not matter".
- The measure is only moderately valid. It follows TCorp ratings and most documented distress cases, but three of its eight benchmarks are met by almost every council, the benchmark indicators barely agree, and it flagged a governance-only administration.
- Limits: 96 fires, Black Summer is 50 of the 218 rows; the CI clusters by council, not by fire or year; Y is a within-sample rank composite; the face-validity sample is 5 independent cases plus TCorp; the FP and DL columns are being revised in other sessions.

## 6. Files (all in this folder; run in order)

`bench_common.py` (pre-specification header and definitions) -> `01_build_measure.py` -> `02a_face_validity_tcorp.py`, `02b_face_validity_named.py` (reads `KNOWN_COUNCILS.csv`) -> `03_validate_vs_Y.py` -> `04_power_new_measure.py`, `05_within_year_diagnostic.py`.
Outputs: `BENCHMARK_YEAR_TABLE.csv`, `BENCHMARK_MEASURE_ROWS.csv`, `FACE_VALIDITY_TCORP.csv/.txt`, `FACE_VALIDITY_NAMED.csv/.txt`, `VALIDATION_VS_Y.csv/.txt`, `POWER_NEW_MEASURE.csv`, `WITHIN_YEAR_DIAGNOSTIC.txt`. Reads (read-only, main checkout): `Experiment 6/results/ROWS_WITH_SCORE_v2.csv`, `fire_event_dataset/data/olg/olg_wide.parquet`, `fire_event_dataset/src/olg.py`, and the XY workbook (`lga_year`, `master`). Seeds fixed (20260929; power 20260930).
