# Deviations from stage6/PREREGISTRATION.md

| # | Date | Change | Reason | Effect on verdict |
|---|---|---|---|---|
| W1 | 2026-09-22 | Added a post-hoc sensitivity row that compares own-source share using `master.fiscal_panel_legacy`, which covers 128 councils in 2018-19, instead of the pre-registered `master.fiscal_panel_extended` (103 councils). | The first run showed that 18 councils containing stage-2 towns are missing from the extended panel. Most are 2016 amalgamations, including exposed councils such as Mid-Coast, Snowy Valleys and Snowy Monaro. This dropped 10 of 43 cut-off towns, so the coverage could bias the comparison. | None. The verdict comes only from the pre-registered extended-panel comparison. |
| W2 | 2026-09-22 | Fixed a missing index name in the town-to-council overlay after the first attempt crashed. | The crash happened before any result was computed. | None. |
