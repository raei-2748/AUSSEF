# Experiment 4 canonical candidate evidence

Latest collection update: [Ballina and original-budget findings](BALLINA_AND_BASELINE_FINDINGS.md). Earlier sections below describe the initial build.

Status: collection in progress; **not model-ready**. No model fitted.

Current extension status and updated counts: [EXTENSION_STATUS.md](EXTENSION_STATUS.md). The initial-build description below is retained; run both build and extension scripts to reproduce the current store.

`experiment4.sqlite` and the matching CSV files hold the canonical candidate records. All imported raw documents and previous experiment outputs remain untouched. The initial register is a selected evidence sample, not a census of ordinary projects. It contains bundled programs as well as project candidates; `unit_status` prevents treating these as certified independent projects.

## Tables and keys

| Table | Grain/key | Meaning and limits |
|---|---|---|
| councils | council_key | 103 inherited continuing NSW councils; inclusion does not imply budget coverage |
| disasters | disaster_id | Seven inherited event labels; identity remains subject to cross-source checks |
| projects | project_id | 32 project/program candidates; source job numbers distinguished from analyst record IDs |
| budget_snapshots | project_id × year_start × stage | Original/Q1/Q2/Q3/actual slots; blank amount means unknown, never zero |
| fiscal_annual | council_key × year_start | 1,339 inherited fiscal observations; definition flags retained and publication vintage not certified |
| damage_status | damage_record_id | Unknown damage/access retained; no disaster attribution fabricated |
| comparisons | comparison_id | Three directed council comparisons; none certified and no three-year budget pretrend yet |
| sources | source_id | URL, local document path, hash where available and publication-date uncertainty |
| disaster_observations | observation_id | Separates regional event starts, ignition dates, local impacts and other dated observations |
| project_revisions | revision_id | Changes and before/after figures; a revision amount is not a budget level |
| project_evidence | evidence_id | Additional scoped findings that cannot safely populate the five-stage funded-budget chain |

Amounts are nominal AUD. CSV blanks become SQL NULL. Official Wagga job numbers were normalised from imported `45049.0` and `45109.0` to identifier strings without the decimal suffix. No project-name fuzzy matching, imputation or missing-to-zero conversion was used. Dates inherited from review-level minutes are labelled as such; they do not independently certify project-level adoption. All `model_eligible` flags remain zero.

The `field_gaps.csv` lists 283 specific missing or uncertified fields for current candidates. These are **not yet recovered**, not demonstrated to be unobtainable. Additional councils and episodes still require searching. Aggregate category chains remain in the pilot results and are deliberately excluded from project snapshots.

## New evidence

Wagga's 2021–22 adopted LTFP, printed/PDF page 66, lists job 45049 (Treatment of Re-use Water) with $331,341 in **2021/22 Pending**, with the confirmed cell blank. This was checked against a rendered page. It must not become a confirmed original funded allocation. The later December review's $359,030 before-revision figure therefore does not establish the original adopted budget. The finding is retained in `project_evidence`, not silently joined into B0.

## Rebuild and validation

Run `python3 build_candidate_store.py /path/to/new/output-folder`. It uses only the Python standard library and reads the inherited evidence and locally stored new PDF. Existing databases are not overwritten. SQLite enforces primary keys, snapshot uniqueness and foreign keys. `validation.json` records counts, integrity and the original source CSV hash. Five project-stage budget levels are currently observed; zero complete certified ordinary chains exist.

## Next collection actions

1. Retrieve Wagga annual project schedules from 2016–17 onward, then Q1–Q3 reviews and 2021–22 final project expenditure. Verify scope, confirmed funding and job recodes across years.
2. Inspect Snowy Valleys 2021–22 annual capital tables as a new council lead; screen amalgamation, disaster exposure and the three-year pre-event history before comparison inclusion.
3. Continue the Richmond Valley, Lismore and Eurobodalla candidate chains with original adoption minutes, quarterly project schedules and same-scope actuals.
4. Expand the declaration ledger and match councils without treating date labels as full physical-exposure histories. Audit overlapping disasters and spillovers before selecting comparisons.
5. Recover asset damage/access evidence, actual completion dates and pre-event publication vintages. A public report's silence is not evidence of no damage.

The goal remains active. Public-source exhaustion and model readiness have not been established.
