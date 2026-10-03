# Experiment 10 handoff: council recovery costs from audited financial statements and quarterly budget reviews

Context: read ../Experiment 8/HANDOFF.md (project, Ray's rules, Bowen's framework: composite Y = DL + IL + FP + SL is the
main Y) and ../Experiment 7/FINDINGS_DAY10.md, FINDINGS_DAY11.md. The OLG time-series data we have show council
operating spending and all-purpose grants only; capital (rebuilding) spending and disaster-specific grants are missing,
which is likely why the FP pillar looked blurry. Ray approved (2 Oct 2026) collecting NSW council PDFs to fix this:

- FP gross (impact) = operating + capital recovery spending; FP reimbursement = disaster-specific grants;
  FP burden = gross - disaster grants.

## Sources to collect (official only: council websites, olg.nsw.gov.au, audit.nsw.gov.au, nsw.gov.au)
A. Audited general-purpose financial statements (annual reports), FY 2015-16 to 2023-24. Extract per council-year:
   - cash flow: payments for purchase of infrastructure, property, plant & equipment (capital spending)
   - income statement: grants & contributions for operating purposes; for capital purposes; total expenses; depreciation
   - grants note: any "natural disaster" (or bushfire / DRFA / disaster recovery) grant lines, operating and capital,
     current and prior year
   - any expense or note line naming natural disaster / bushfire costs
B. Quarterly Budget Review Statements (QBRS), FY 2018-19 to 2021-22 (Black Summer window): capital and operating
   budget revisions and any disaster-related lines, per quarter.

Councils: the 218-row master covers 69 fire councils (list: ../Experiment 7/results/NEW_Y_X_TABLE.csv, columns
region_id, region_name). Also comparison councils (all other NSW councils, ../Experiment 7/panels or
fire_event_dataset lga list) so effects can be compared with unburned councils.

## Download guardrails (approved by Ray)
Official domains only; each file <= 40 MB; stop and report if one session would exceed 4 GB in total; log every file
(URL, bytes, sha256, local path) in this experiment's downloads log AND in bibliography/parts/<session>.csv
(see ../bibliography/README.md). Save PDFs under fire_event_dataset/data/raw/council_pdfs/<type>/<region_id>/.
No login-only sources, no workarounds for blocked sites.

## Extraction quality
Values must carry page number and the exact line label from the PDF. A verifier agent spot-checks at least 10% of
extracted values against the PDF. Keep raw extraction (all lines found) and a tidy table
(region_id, council, fy, item, value_aud, page, label, file). Don't run statistical tests: Ray will approve a locked
prespec later.
