# Evidence extension: Snowy Valleys and Wagga

This is progress, not a completion or source-exhaustion verdict. No model fitted.

Canonical tables now contain 104 councils (the inherited 103 plus Snowy Valleys as an explicitly unscreened extension), 45 project/program candidates and 225 five-stage slots, of which 31 have reported levels. SQLite integrity and foreign keys pass. None is a complete certified ordinary-project chain.

## Recovered

Snowy Valleys Annual Report 2021–22, printed/PDF pages 79 and 81, visually checked against text: 13 named-work candidates have June-2021-budget and June-2022-spending pairs. Two are explicitly labelled NSW Bushfire Recovery and are excluded from the ordinary-work interpretation. Completed/underway labels were read from the colour key, not inferred from OCR bullets. Exact completion dates remain unknown. The original adopted document and Q1–Q3 series are not yet recovered. A 2021 budget is not a pre-2019-fire plan.

Duplicate/scope concerns are retained: the report's additional-works table repeats Tumut Aerodrome actual spending and gives a different generator amount. Neither table should be added to the other without reconciliation. Named rows do not establish stable official project IDs. Snowy Valleys' entity history and fiscal data remain separate work; no other council's fiscal values were substituted.

Wagga July-2020 capital schedule, page 8, visually verified: job 45049 combines $24,940 confirmed, $28,506 estimated carryovers and $331,341 pending, summing to $384,787. This is a July review schedule, not a certified original/Q1 snapshot. Four component observations are retained in project_evidence.

## Negative access findings

Official Wagga annual-report URLs for 2016–17 and 2018–19 returned HTTP 403 on direct retrieval. The 2018–19 URL returned a web-reader 404. Search-index annual expenditure snippets are only leads and have not been accepted as verified actuals. These failures do not prove reports are unobtainable from the meeting archive.

## Next primary-source leads

- Snowy Q1 adoption announcement: https://www.snowyvalleys.nsw.gov.au/News-Media/Key-Decisions-from-18-November-2021-Council-Meeting — find the underlying minutes and attachment; announcement says review as at 30 September was adopted on 18 November.
- Snowy Q3 agenda: https://www.snowyvalleys.nsw.gov.au/files/assets/public/meeting-minutes-amp-agendas/council-meetings/20220519/00-20220519-business-paper-ordinary-council.pdf — inspect item 10.4, capital attachment and adoption minutes. Search text identifies specialist-availability deferrals; do not attribute those to disaster without evidence.
- Snowy 2022–23 Q3 follow-up: https://www.snowyvalleys.nsw.gov.au/files/assets/public/v/1/meeting-minutes-amp-agendas/council-meetings/20230622/09.3-late-report-quarterly-budget-review-31-march-2023.pdf — later project continuity lead; cannot substitute for 2021–22 Q3.

## Reproduce

Run `build_candidate_store.py NEW_FOLDER`, then `extend_verified_sources.py NEW_FOLDER`. The first refuses existing databases; the second refuses a duplicate import. Source PDFs remain unchanged. Rebuilds use the local source PDFs under raw_extension. Full project-by-project gaps are in field_gaps.csv (413 current entries); these are incomplete searches, not declarations that the fields cannot be obtained.
