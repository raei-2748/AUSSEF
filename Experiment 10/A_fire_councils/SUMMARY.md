# Experiment 10, Source A: audited council financial statements (fire councils): summary

Date: 2 Oct 2026. Scope: the 69 fire councils in `../../Experiment 7/results/NEW_Y_X_TABLE.csv`, FY2015-16 to FY2023-24
(9 years each, so 621 council-years). No statistical tests were run, and nothing was committed.

## What we got
- **164 official PDFs** downloaded (951 MB, well under the 4 GB cap; every file is 40 MB or less). They are saved under
  OneDrive `Extracurriculars/AUSSEF/05 Data Archive/Council Financial Statements (NSW councils FY2015-16 to FY2023-24)/` (moved and renamed 2 Oct 2026; see `../PDF_RENAME_MAP_2026-10-02.csv`; originally saved under `fire_event_dataset/data/raw/council_pdfs/financial_statements/<region_id>/`).
- **27 of 69 councils** have at least one year. **9 councils have all 9 years**: Cobar, Coonamble, Muswellbrook, Penrith,
  Richmond Valley, Tenterfield, Upper Lachlan, Warren and Wollondilly.
- Council-years: **157 read from that year's own statement**, **23 filled only from the "last year" column of the
  following year's statement**, and **441 missing**.
- **3,178 extracted lines** (`extraction_raw.csv`) became **1,888 tidy values** (`statements_tidy.csv`).

## Why so much is missing
- **406 of the 441 missing council-years are missing because the council website blocked the downloader**
  (HTTP 403 "Access Denied" bot protection). In most of these cases the statements do exist on the site: the agents
  found the links but could not fetch them.
- The handoff rule is "no workarounds for blocked sites", so nothing else was tried for them.
- The other gaps are dead links (404, 20 cases), years not published online (about 9), and partial-period FY2015-16
  statements for councils created in the May 2016 amalgamations.
- **Decision for Ray:** fetching the blocked files would need either a manual download in a normal browser, or Ray's
  approval for an agent to use a real browser. Both counts as a new rule, so I did not do either. All blocked URLs are
  logged (as failed links) in the bibliography part file.

## What was extracted (each value carries the PDF page number and the exact printed label)
- Capital spending: cash-flow "Purchase of infrastructure, property, plant and equipment" (`capex_ippe`, stored as a
  positive number).
- Income statement: grants and contributions for operating purposes, grants and contributions for capital purposes,
  total expenses, and depreciation.
- Disaster lines: grants-note lines naming natural disaster, bushfire, flood, storm or recovery (operating and capital
  shown separately), plus any expense or other note naming disaster costs.
- Both the current-year and prior-year columns were extracted. The tidy table uses the current year and falls back to
  the prior-year column only when that year's own statement is missing (shown in the `source_basis` column).
- Amounts printed in $'000 were multiplied by 1,000 to get `value_aud`.

## Important caution about the "disaster grant" lines
- The most common matching lines are **"Bushfire and emergency services"** (202 lines) and **"Bushfire services"**
  (70 lines). These are standard grant categories for routine Rural Fire Service and emergency-services funding,
  **not disaster recovery money**.
- Lines that look like real recovery money are rarer: "Storm/flood damage", "Natural disaster funding", "Disaster
  recovery", "Flood restoration" and similar.
- I did not reclassify anything. Before these lines are used for FP, the two kinds should be split, which needs a
  rule Ray agrees to.
- Some lines also mix in other money (for example "bushfire and drought stimulus", or "Transport (3x3, flood works,
  roads to recovery)"). These are flagged in the `notes` column of `extraction_raw.csv`.

## Checking
- **First check:** a verifier per batch compared at least 10% of the values with the PDF. Several of these verifiers
  could not view the PDF pages and only re-read the text.
- **Second check:** I ran a second, visual check per batch. Pages were turned into images and read by eye.
  - It covered **2,139 of 3,178 lines (67%)**, well above the 10% rule.
  - It found **no errors**.
- **My own test:** I picked 40 random lines and looked for each printed value on its cited page.
  - 39 of 40 matched.
  - The 1 mismatch is a scanned page with no text layer. That value is confirmed by the next year's statement.
- Both checks are logged in `verification_log.csv` (the `pass` column says which check).

## Files (in this folder)
- `downloads_log.csv`: every download attempt (URL, bytes, sha256, local path, result).
- `extraction_raw.csv`: all lines found, including the prior-year columns and notes.
- `statements_tidy.csv`: columns region_id, council, fy, item, value_aud, page, label, file, plus source_basis.
- `coverage_report.md`: council x year grid with the main reason for each gap. `coverage_council_year.csv` and
  `coverage_matrix.csv` have the full detail.
- `verification_log.csv`: results of both checks.
- `tools/`: `dl.py` (guarded downloader), `pdfpages.py` (page search and dump), `merge.py` (rebuilds every output
  above from `work/`).
- `work/batch_NN/`: the agents' per-batch files.
- Bibliography: `../../bibliography/parts/exp10_A_fire_councils.csv` has 623 rows: 201 sources used, 421 searched but
  not used (including the blocked links), and 1 downloaded but not usable.

## Small notes
- `fy` means the financial year the value belongs to. A prior-year column in the 2020-21 statement is fy 2019-20.
- Councils created in 2016 have a short first period. For example, Dubbo's and Central Coast's first statements run
  from 13 May 2016 to 30 June 2017. This is noted on the affected rows.
- Some prior-year numbers were restated by the council. They are recorded exactly as printed in the later statement.
- For 2015-16 to 2018-19, "depreciation" can be depreciation and amortisation only; later years include impairment.
  The label shows which.
