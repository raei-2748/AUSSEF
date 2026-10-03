# Experiment 10 / Source A / comparison councils: agent spec

Scope (changed 2 Oct by Ray via coordinator): audited General Purpose Financial Statements (GPFS) of the 25 comparison
councils in selected_25.csv (regional/rural, similar to the fire councils), FY 2015-16 to 2023-24 (9 years). Do not
download anything for councils outside selected_25.csv. FY "2019-20" = year ended
30 June 2020. Do NOT touch ../A_fire_councils or any other session's files. No statistical tests. No git commits.

## Tools (all in tools/, run with python3; network commands need Bash with sandbox DISABLED)
- dl.py: the ONLY way to download (fetches with plain curl; many council sites refuse Python but serve curl). Enforces official *.gov.au hosts, 40 MB/file, 4 GB session cap, PDF check, sha256,
  writes downloads_log.csv + work/bib/downloads_bib.csv. Exit 3 = BUDGET_STOP -> stop downloading, report it.
- discard.py: if a downloaded PDF turns out to be the wrong council/year/document, discard it (keeps the record).
- logsrc.py: log every web page you visited or searched (council listing pages, OLG pages, etc.) to the bibliography,
  used_in "searched, not used" or "Experiment 10/A_comparison_councils (located GPFS links)".
- pdftext.py: per-page text (1-based PDF page index), --grep, --page. Scanned PDFs: use the Read tool with pages=.

## Finding rules
- Official sources only: the council's own website (incl. its document servers on *.nsw.gov.au), olg.nsw.gov.au,
  audit.nsw.gov.au, nsw.gov.au. No login-only sources, no workarounds for blocked sites (403/captcha = record & move on).
  Non-.gov.au hosts (e.g. a CDN, issuu, a .com.au site) are not allowed: record them as "not downloaded: non-official
  host" via logsrc.py.
- Prefer the standalone GPFS PDF ("General Purpose Financial Statements", "Annual Financial Statements") over the whole
  annual report; use the annual report (financial statements appendix) only if no standalone GPFS exists. If GPFS are
  split into several PDFs (statements / notes), get the parts that contain the income statement, cash flow statement
  and the grants note. Skip Special Purpose FS and Special Schedules.
- After each download, open page 1-3 text and confirm council name and "year ended 30 June YYYY". Wrong -> discard.py.
- 2016 amalgamations (Bayside, Canterbury-Bankstown, Cumberland, Georges River, Inner West, Northern Beaches,
  Parramatta, Hilltops, Edward River, Federation, Murray River, Murrumbidgee): FY2015-16 GPFS belong to predecessor
  councils; record "predecessor councils only" unless the new council itself publishes them. Their first GPFS
  (FY2016-17) may cover a period from the proclamation date (May 2016) to 30 June 2017; note that.

## Extraction items (item codes)
Statement / where | item code | typical exact label
--- | --- | ---
Cash flow statement | capex_ippe | "Payments for purchase of infrastructure, property, plant and equipment" / "Purchase of infrastructure, property, plant and equipment" (IPPE line ONLY; not real estate, not intangibles)
Income statement | grants_contrib_operating | "Grants and contributions provided for operating purposes"
Income statement | grants_contrib_capital | "Grants and contributions provided for capital purposes"
Income statement | total_expenses | "Total expenses from continuing operations"
Income statement | depreciation | "Depreciation, amortisation and impairment (of non-financial assets)"
Grants note | disaster_grant_operating | any operating grant line naming natural disaster / bushfire recovery / flood / storm / disaster recovery / DRFA / NDRRA / "Natural disaster"
Grants note | disaster_grant_capital | same, capital
Expense / other notes | disaster_expense | any expense or note line naming natural disaster / bushfire / flood / storm costs
Grants note | bushfire_emergency_services_grant | "Bushfire and emergency services" (this is RFS/SES funding, NOT disaster recovery: keep it separate)
Any | other_disaster_line | any other line with disaster wording (e.g. a contributions line, a contingency, a revenue line)

Search patterns (pdftext --grep): "purchase of infrastructure|grants and contributions provided|total expenses from
continuing|depreciation, amort|natural disaster|disaster|bushfire|flood|storm|DRFA|NDRRA|recovery".
Pre-2019 grants notes are usually Note 3(e)/3e; 2019+ Note 3.4 / B2-4 ("Grants" table, operating & capital columns,
current & prior year).

## Output of an extraction agent: work/extract/<region_id>.csv
Columns (UTF-8, header): region_id, council, fy, item, label, raw_value, units, value_aud, column, page, printed_page,
statement, hazard, file, doc_fy, notes
- fy = the financial year the VALUE refers to. column = current_year | prior_year. Record BOTH columns when a
  statement shows them (prior-year values are cross-checks and fill gaps when a year's GPFS is missing).
- label = the exact line label as printed (copy text verbatim, including capitalisation and punctuation).
- raw_value = number as printed (e.g. "(12,345)" or "12,345"); units = "$'000" or "$"; value_aud = numeric value in
  dollars (multiply $'000 by 1000), outflows recorded as POSITIVE numbers for capex_ippe; blank if the line shows "-".
- page = 1-based PDF page index in `file`; printed_page = the page label printed on the page if visible.
- hazard (disaster items only) = bushfire | flood | storm | multiple | unspecified.
- file = local_path relative to /Users/ray/Research/AUSSEF - Local exactly as in downloads_log.csv. doc_fy = FY of the document.
- If an item genuinely does not appear (e.g. no disaster grants that year), do NOT invent a row; the coverage step
  treats "searched, none found" from your returned summary.

## Verifier output: work/verify/batch_<NN>.csv
Columns: region_id, fy, item, column, value_aud_extracted, page, label_extracted, file, verdict
(confirmed | wrong_value | wrong_label | wrong_page | not_found), observed_value, observed_label, observed_page, comment

## Network note (2 Oct)
Use plain `curl -sL URL` (curl's default User-Agent) to read listing pages. Do NOT set a browser User-Agent: several
council firewalls return 403 to fake browser strings but serve curl normally. If plain curl also gets 403/captcha,
the site is blocked: record it and move on (no workarounds). WebFetch may also be used to read HTML listing pages.
