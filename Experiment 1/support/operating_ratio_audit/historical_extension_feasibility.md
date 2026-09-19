# Historical-extension feasibility

**Verdict: conditional feasibility for a continuing-council subset, not a certified append for all current councils.** Candidate common availability begins in FY2012–13: potentially five extra financial years before FY2017–18. This audit has not established an earliest fully harmonised year for all128 present-day entities.

## Sources and observed availability

The [official OLG time-series archive](https://www.olg.nsw.gov.au/public/your-council-data-and-reports) supplies the cached 1994–2015 workbook and separate 2015–16 and 2016–17 files. `historical_column_inventory.csv` gives sheet, column, header, numeric count and missing count for the inspected 2010–11 to 2016–17 window. Older sheets were retrieved but are not certified by this review.

| Requested measure | Earliest candidate in the inspected recent historical window | Harmonisation issue |
|---|---|---|
| Operating performance | 2011–12; common bundle from 2012–13 | 2011–12 cells are fractions, later cells percentages; exclusions and report vintages need verifying. |
| Cash expense cover | 2012–13 | Months; verify treatment of term deposits and cash-flow denominator across codes. |
| Unrestricted current ratio | Available in 2010–11 and 2011–12 | Earlier data may also exist; no claim of historical first availability. Externally restricted balances and liabilities must be defined consistently. |
| Own-source revenue | 2011–12; common bundle from 2012–13 | Fraction/percent change; capital-grant treatment and exclusions require checking. |
| Debt service cover | 2012–13 | Older debt-service ratios measure something different. Zero-debt cases and unavailable denominators need explicit treatment. |
| Maintenance adequacy | Ratio candidate in 2012–13 | FY2012–13 raw ratios are fractions; FY2013–14 onward percent-scale values. Actual/required expenditure definitions, units and special-schedule consistency need verifying. |

In 2012–13, 2013–14 and 2014–15 the six requested columns contain numeric entries for152 council rows in the archive. Numeric presence does not certify validity. The standalone2015–16 sheet has only108 council rows; absent entities are not counted as field-level missing observations. The2016–17 sheet lists128 councils but each of the six requested fields has108 numeric and20 missing entries. These gaps directly limit a common annual panel. The 2012–13 sheet places the group identifier in column C, unlike adjacent sheets; blindly using column B would falsely report no observations. Source extraction now identifies the group header instead.

## Major breaks

1. **Entities.** The [Audit Office 2017 report](https://www.audit.nsw.gov.au/our-work/reports/report-on-local-government-2017) records19 new councils in May2016 and one in September2016. Its [amalgamation appendix](https://www.audit.nsw.gov.au/sites/default/files/auditoffice/2018-Reports/Local%20Government%202017/Appendix%20four%20-%20Councils%20amalgamated%20in%202016.pdf) identifies predecessors. A present-day `council_key` must not be assigned merely through name similarity. Continuing councils are the practical first subset; predecessor ratios cannot be averaged without verified underlying amounts and boundaries.
2. **Periods.** [Hilltops first accounts](https://www.hilltops.nsw.gov.au/wp-content/uploads/2021/07/Annual-Financial-Statements-YE-1617-Hilltops-Council.pdf) run from13May2016 to30June2017. Bayside formed later. Neither period is an ordinary comparable annual row. Preserve/report these periods or exclude them transparently from a future design.
3. **Units.** Verify each source header, not just workbook year. Maintenance fractions and percentages, and dollar/thousand amounts, require separate rules. The current audit does not append or silently rescale the original panel.
4. **Definitions and revisions.** Cross-check historical accounting-code ratio definitions and audit notes, particularly grant recognition, non-cash gains/losses and cash/debt denominators. FY2019–20 revenue-standard adoption lies inside a longer panel, not outside the problem.
5. **Missingness.** Consult the generated per-field inventory for2015–16/2016–17 missing values. Zero numeric entries in an absent column are not a zero-valued fiscal observation. Missingness must be carried into target-specific eligibility.

## What would make extension acceptable?

Create a source-vintage and legal-entity crosswalk; verify six definitions and units against the original statements/code; identify normal12-month periods; select comparable continuing councils; retain every year and eligibility flag. Then assess how many *new complete target years* remain under the original t−1/t/t+1 design. Historical exposure measures must also be verified—additional fiscal years alone do not create complete disaster-prediction rows.

Five additional fiscal years could materially broaden the current short time window, but the usable forecast gain is conditional on exposure coverage, publication timing and minimum training requirements. Repeated councils do not create independent annual shocks, and older years need not represent future conditions. No older rows have been appended, no model refitted, and no claim of a harmonised128-council historical panel is made.
