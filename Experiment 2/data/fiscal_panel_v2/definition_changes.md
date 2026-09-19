# Definition, unit and measurement audit

This is a candidate harmonisation, not a claim that every historical ratio has an invariant definition. Original values, headers, cell addresses and multiplication factors remain in the lineage files. Missing values are never imputed.

## Fiscal measures

| Measure | Common unit and handling | Unresolved issue |
|---|---|---|
| Operating performance | Percentage points; published ratio retained after explicit fraction-to-percent conversion | Adjusted numerator and revenue exclusions vary across report vintages; not reconstructed from broad income totals |
| Cash expense cover | Months; common column begins 2013–14 | 2012–13 uses an incompatible numerator/denominator; raw value retained separately |
| Unrestricted current ratio | Times; never multiplied by 100 | Restricted assets and excluded liabilities require consistent note definitions |
| Own-source revenue | Percent; continuing-revenue denominator can include capital grants | Adjusted exclusions differ; not automatically `100 − grants_pct` |
| Debt service cover | Times; zero values flagged for denominator review | Debt-free/zero-service cases must not be interpreted as ordinary low cover |
| Debt service ratio | Percent; separate from cover, not its reciprocal | Missing in 2012–13 source; keep distinct denominator definition |
| Maintenance adequacy | 100 × actual/required, positive required denominator only | Council-assessed required spending is not a uniform engineering standard |
| Monetary components | Nominal AUD; multiply only headers explicitly stated in thousands by 1,000 | No inflation deflation or reporting-vintage repair is implied |
| Road length | km; common column restricted to local/regional scope | Early series also includes state roads, so common measure is missing in those years |

### Cash cover: a verified definition break

The [2013–14 OLG profile](https://www.olg.nsw.gov.au/sites/default/files/2026-02/your-council-june-2015-profile-and-performance-of-the-nsw-local-government-sector.pdf), PDF p17 (printed p15), explicitly describes the addition of term deposits that were excluded previously. Its cash-flow-based denominator also differs from the expense-based description in the [2012–13 comparative report](https://www.olg.nsw.gov.au/sites/default/files/2026-02/comparative-information-on-nsw-local-government-measuring-local-government-performance-2012-2013.pdf), PDF p346. No universal conversion is defensible without cash, deposit and payment components. Consequently `cash_cover_reported_months` retains 2012 values while `cash_cover_months` withholds them. Numeric availability in 2012 is not comparability.

### Operating ratio and statement components

The early comparative report describes revaluation exclusions (PDF pp346 and348). Albury's [2013–14 statements](https://eservice.alburycity.nsw.gov.au/ACCPublicDocs/DocumentViewer.aspx?DocID=1072745), PDF p50, also exclude specified fair-value, disposal and joint-venture effects. Do not divide unadjusted before-capital surplus by an unadjusted income total and label the result the official operating ratio.

The Albury example supplies an explicit vintage check: its later 2012–13 comparative operating ratio is −0.94%, whereas the OLG archive candidate is −1.12%; own-source revenue is 82.52% versus 78.97%. These differences remain unresolved in `vintage_discrepancies.csv`. They are not silently overwritten or attributed to a particular cause without reconciliation.

Albury PDF p4 contains current 2013–14 and comparative 2012–13 consolidated income statements in $000. Revenue and expense sums, and the before-capital result, reconcile exactly. Depreciation plus separately reported impairment is labelled as a derived sum in lineage. `operating_revenue_ex_capital_aud` uses revenue and capital grants from the **same audited statement**, not mixed vintages. Other detailed observations are inherited from the earlier documented statement audit. Report-vintage and source-location fields remain attached.

### Accounting regimes

Potential breaks include AASB13/119 changes around 2013–14; AASB9 from 2018–19; revenue standards AASB15/1058 and leases AASB16 from 2019–20; and service-concession standard AASB1059 from 2020–21. These are review flags, not numerical adjustments and not proof that every council was materially affected. The [Audit Office 2019 report](https://www.audit.nsw.gov.au/our-work/reports/report-on-local-government-2019), section2.3, and [2020 report](https://www.audit.nsw.gov.au/sites/default/files/documents/Report%20on%20Local%20Government%202020.pdf) discuss the later transitions. Individual restatements and transition amounts remain unquantified.

### Maintenance

The 2015 profile, PDF p27 (printed p25), identifies the early Special Schedule7 figures as unaudited. Required spending depends on council asset-management estimates. Recalculation checks internal arithmetic only; it cannot harmonise the underlying engineering requirement.

Seven rows differ by more than one percentage point between reported and recomputed adequacy. Raw amounts, reported ratios and recomputed ratios remain available; the common eligible ratio is withheld. The fixed 1pp tolerance accommodates integer reporting in older years and is not selected by model performance. Four of these rows occur in the V1 overlap; `v1_overlap_differences.csv` records their changed eligibility. Other compared nonmissing overlap values agree within the stated rounding tolerance. No extreme fiscal outcomes were removed simply for being extreme.

### Source-specific scaling

`unit_conversion_rules.csv` records every source-year variable rule. Examples: 2012 maintenance fractions ×100; 2023 operating, own-source, grants and maintenance fractions ×100; debt-service ratio is already a percentage and receives no such conversion. In 2024 grants are fractional but maintenance is already a percentage. Currency scaling is per column, not per workbook. The 2024–25 source omits six fiscal ratios; those cells are missing, not zero.

Read `coverage_by_year_variable.csv` for target-specific missingness. The presence of a complete annual identity row does not imply complete measurements, a clean audit opinion, or ex-ante availability.
