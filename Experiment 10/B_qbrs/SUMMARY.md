# Experiment 10, Source B: Quarterly Budget Review Statements (QBRS) — STOPPED

Status (2 Oct 2026): **stopped on Ray's instruction** (relayed by the coordinator session). Reason: QBRS are budget
revisions, not actual spending, and the audited financial statements (Experiment 10 Source A) cover the same need
better. No new downloads or extraction after the stop. Nothing was deleted. No statistical tests were run, no commits.

## What was collected
- **27 of 84 planned councils** have at least one QBRS document downloaded (26 fire councils with Black Summer rows, plus
  Coonamble). **263 PDF files on disk, 1.5 GB**, all from official council sites (or the council's own Infocouncil
  business-paper portal, linked from its .nsw.gov.au site). Folder: `fire_event_dataset/data/raw/council_pdfs/qbrs/<region_id>/`.
- Together these cover **192 council-quarters** out of 1,008 planned (84 councils x 12 quarters).
  Quarters with a document, summed over councils:

  | FY | Q1 (Sep) | Q2 (Dec) | Q3 (Mar) |
  |---|---|---|---|
  | 2018-19 | 13 | 13 | 13 |
  | 2019-20 | 19 | 16 | 18 |
  | 2020-21 | 19 | 17 | 18 |
  | 2021-22 | 15 | 15 | 16 |

- Full (or nearly full) 12-quarter sets: Bega Valley (11), Snowy Valleys, Tenterfield, Richmond Valley,
  Port Macquarie-Hastings, Blue Mountains, Walcha, Greater Hume, Mid-Western Regional (11). Per-council detail:
  `council_status.csv`, `coverage_by_council.csv`, `coverage_by_quarter.csv`.
- **Figures extracted for only 3 councils** before the stop: Bega Valley, Snowy Valleys, Clarence Valley
  (`extraction_raw.csv`: 1,245 rows; `qbrs_tidy.csv`: 1,175 rows with page and exact label). The other 24 councils'
  PDFs are downloaded but **not extracted**.

## Important caveats
1. **No verification was done.** The verifier step never ran (the stop came first). The extracted values are
   unchecked. I checked one value by hand: Snowy Valleys Sep 2018 capital budget. It is internally consistent
   (revised $22.157m - $0.427m = projected $21.730m).
2. **Many PDFs are scanned images or have rotated text.** The extractor used page rendering + OCR for those, so the
   error risk is higher.
3. **The "disaster" lines are mixed.** The extractor also caught routine items (Emergency Services Levy, Fire Service
   Levy, RFS maintenance grants). In `qbrs_tidy.csv`, the `disaster_class` column splits them by keyword. The split is
   rough and needs a human check: disaster_recovery 396 rows, routine_emergency_services 28, other_check 354.
4. Clarence Valley's QBRS have no capital/operating totals in the form we wanted. Only the budget-result lines and
   disaster lines were extracted.
5. The QBRS show budgets (original vs revised), not actual spending, so they are a weaker FP measure than the audited
   statements.

## What was not done, and why (57 councils with no documents)
- **15 councils never searched.** They include all 15 comparison councils, because the work stopped before reaching them.
- **22 councils: search incomplete.** In the second run, the session's web-search allowance (200 searches) and usage
  limit ran out, so these councils were barely searched. Their absence is **not** evidence that their QBRS don't exist.
- **15 councils: site blocked automated access (HTTP 403).** No workaround was tried, per the rules. Examples: Eurobodalla,
  Mid-Coast, Hawkesbury, Glen Innes Severn, Sutherland. For 6 Eurobodalla quarters the direct links are known and logged.
- **5 councils: searched, nothing obtainable within the rules.** Reasons:
  - only ZIPs or agendas over 40 MB (Cessnock);
  - non-gov.au domain (Lithgow: council.lithgow.com);
  - old archive removed (Kyogle);
  - and so on (see `council_status.csv`, `finder_notes`).
- **Some councils stopped early at the per-council download cap** (120 MB, later 50 MB), e.g. Shoalhaven and Upper Lachlan.
  The cap was there to protect the 4 GB budget. Shoalhaven also has two downloaded bundles that turned out not to
  contain a QBRS (kept, noted in the log).

## Files
- `downloads_log.csv`: every download attempt (415 rows). It records URL, page where the link was found, meeting/item,
  bytes, sha256 and status. Status values are downloaded, http_403, http_404, skipped_over_40MB, refused_council_cap,
  refused_non_official_host, not_a_pdf and failed. Column `on_disk` flags 5 logged files no longer at their logged path:
  4 duplicates whose identical content is kept under another name, and 1 wrong-meeting Coffs Harbour agenda removed by an agent.
- `bibliography/parts/exp10_B_qbrs.csv`: 662 rows. That is every downloaded file, every page visited, and every failed or
  refused file URL (`used_in = "searched, not used"`).
- `extraction_raw.csv`, `qbrs_tidy.csv`, `verification.csv` (empty), `councils_plan.csv`, `council_status.csv`.
- `tools/`: guarded downloader, bibliography logger, PDF page-text tool, `merge.py` (re-builds the merged tables
  from `work/`; safe to re-run).

## If anyone resumes this later
Extract the 24 downloaded-but-unextracted councils first, then run the 10% verifier. Councils marked "search incomplete"
or "not searched" need a fresh search. Rerunning search for the 403-blocked councils will not help: their documents
need a manual browser download by Ray.
