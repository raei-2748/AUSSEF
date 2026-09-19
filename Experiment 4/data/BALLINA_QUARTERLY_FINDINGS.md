# Ballina quarterly reconstruction: FY2020–21

Three official capital schedules have been preserved with URL and SHA256 provenance. Page 1 of each was visually checked. The complete Open Spaces sub-block yields 42 quarterly annual estimates: 13 in Q1, 13 in Q2, and 16 in Q3. Subtotals reconcile to $3,531,500, $2,274,000 and $2,369,000 respectively. These are annual estimates, not quarterly expenditure.

Thirteen projects now have numerical B0 → Q1 → Q2 → Q3 → ACTUAL chains. This is not a certified adopted-budget chain: the schedules include new proposed variations, and the council resolutions still require checking. Original estimates remain retrospectively reported; year-end actuals are cash spending, excluding accruals and commitments. No model eligibility flag was changed.

Matching uses the official reference within this financial year. Stable asset scope across years remains unverified. Rows absent from earlier schedules remain unknown, never zero. Four year-end rows have explicitly reported zero original allocations and are not a preplanned positive-budget portfolio.

The current candidate store contains 62 projects, 310 snapshot slots and 107 observed amounts. There are still zero certified model rows. Disaster and asset-damage alignment, approved changes, exact completion/deferral dates, three pre-event years, comparison validity and fiscal publication vintages remain outstanding. This is progress in measurement, not evidence of disaster-caused displacement.

## Reproduction

Run build_candidate_store.py, extend_verified_sources.py, audit_snowy_quarterly.py, extend_ballina.py and then extend_ballina_quarters.py sequentially against a new output directory. Each importer rejects duplicate application. The final step updates the CSV exports and SQLite store; field-gap records retain the remaining adoption checks.

## Next evidence checks

Retrieve the October 2020, January 2021 and April 2021 meeting resolutions; reconcile approval scope against every reported new variation. Extract dated deferral reasons separately from inferred movements in estimates. Extend the same-reference chain into surrounding financial years and screen overlapping declared events before selecting comparisons.

## Resolution verification update

Official minutes now verify six revised project amounts: Q2 Wollongbar District Park $773,000, Ross Park $400,000 and Pop Denison $186,000 (28 January 2021, resolution 280121/20, page 13); Q3 Wollongbar District Park $903,000, Various Shelters and BBQs $75,000 and Ross Park $250,000 (22 April 2021, resolution 220421/18, page 11). Five of these six decisions explicitly defer part of the budget into 2021/22; the remaining change transfers $130,000 from amenities into District Park. Dated deferral observations are stored separately so repeated decisions are preserved. None establishes a disaster cause.

The October resolution 221020/23, page 13, notes the report and approves listed amendments; it does not independently establish the adoption history of each unchanged Open Spaces allocation. Other schedule rows retain this narrower status. Six recovered-amount gaps are now resolved as explicit approvals; remaining gates remain open.

Ross Park illustrates an important measurement distinction: Q1 $707,500 becomes a current budget of $800,000 before the approved Q2 cut of $400,000. The Q2 schedule separately records a $92,500 approved increase. Therefore Q2 minus Q1 is not the size of the particular deferral decision. Both snapshot balances and explicit revision records are retained.

For reproduction, run verify_ballina_decisions.py after extend_ballina_quarters.py. There are now 124 sources, 43 explicit revision records and 22 milestone observations. No models have been fitted and no rows certified model-ready. Publication dates remain unknown; resolution dates must not be substituted for document-release dates.

## Original adoption verification

The 25 June 2020 agenda Table 19 (PDF85, printed81) gives Riverview Park $94,000 and Pop Denison $945,000 for FY2020/21. Resolution 250620/4 clause18 (minutes PDF6; general adoption clause1 PDF4) adopts that table. These two B0 allocations now have direct adoption provenance. The table lacks project codes, so linkage is by distinct project name and matching later allocation, with asset scope still unverified. The exhibited Pop Denison draft was $745,000; using it would understate the adopted baseline by $200,000. Riverview was brought forward from the exhibited 2022/23 allocation, so exhibition and adoption cannot be interchanged.

The file named ballina_original2020.pdf is the meeting supporting-attachments bundle, not a complete original capital plan. Its source status explicitly records that limitation; it must not be used to certify the remaining eleven positive B0 allocations. The original filename is retained for raw-source immutability.

There are now 127 registered sources and two independently verified Ballina original allocations. Reproduction adds verify_ballina_baseline.py after verify_ballina_decisions.py. The overall panel remains uncertified for modelling; full ordinary-asset scope, damage/access, event overlap, comparison histories and capacity publication dates remain open. No negative evidence here establishes public-data exhaustion.
