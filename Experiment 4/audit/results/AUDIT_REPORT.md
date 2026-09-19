# Experiment 4 — ordinary infrastructure budget deviations

**Research question:** Do natural disasters cause NSW councils to make abnormal downward revisions to pre-planned ordinary infrastructure spending, and are those deviations larger for councils with weaker pre-disaster fiscal capacity?

**Verdict: CONDITIONAL GO for a focused budget-document/ledger pilot; NO-GO for modelling or causal claims with the existing data.** The redesign is better aligned with some evidence already held than Experiment 3’s narrow routine-maintenance outcome. It does not remove the need to identify a fixed pre-event portfolio and a credible comparison.

This is a fresh audit of the local repository, not a new web collection. All **1081 existing files** were hash-protected, including Experiments 1–3, the older funding-access Experiment 4 and Queensland Experiment 4B. The new name is **Experiment 4 — Budget Deviation Audit**, saved in a distinct folder to avoid overwriting those studies. The root README predates Experiments 3–4B and is not a complete inventory; it was left unchanged.

## What already works, and what does not

| Component | Usable now | Remaining limitation |
|---|---|---|
| Annual deviations | Four audited-statement original-budget/actual **gross IPPE cash-payment** examples, across three councils | Broad capital scope; ordinary infrastructure and reconstruction not separated |
| Quarterly revisions | Six original-to-March full-year budget comparisons for **one Lismore council-year** | One snapshot, no full quarterly sequence; baseline after the February 2022 flood |
| Deferrals | Named capital-delay narratives and maintenance-continuation counterevidence | No linked baseline/revised deadlines, complete project population or verified delay days |
| Disaster timing | 819 NSW council-event activation rows / 165 AGRNs / 122 location codes, plus older V2 archives | Event-wide start is not local impact onset; incomplete snapshot, name/boundary and overlap checks remain |
| Pre-event capacity | 1,339 annual identity rows / 103 councils / 13 financial years | Numeric coverage is incomplete and comparable public availability is not certified |
| Municipal comparisons | E3’s six-council pilot and 306 candidate comparison links | Not comparable quarterly outcomes; later control exposure and limited capacity/event variation |

The detailed [readiness matrix](readiness_matrix.csv) distinguishes existing evidence, cleaning and genuinely additional data. **There are still zero certified ordinary-infrastructure outcomes and zero complete quarterly sequences in this audit.** This is a statement about evidence certified here, not proof that every unreviewed document lacks useful information.

## Annual basis: usable descriptive amounts, not the final outcome

The following same-year pairs were newly transcribed from saved original PDFs and visually checked. Parenthesised cash outflows in $000 were converted to positive expenditure amounts in AUD. A negative deviation means less spent than originally budgeted.

| Council / FY | Original IPPE cash budget | Actual IPPE cash payment | Deviation |
|---|---:|---:|---:|
| Richmond Valley 2021–22 | $43.690m | $26.431m | −$17.259m (−39.50%) |
| Lismore 2021–22 | $64.888m | $32.656m | −$32.232m (−49.67%) |
| Griffith 2019–20 | $40.933m | $22.210m | −$18.723m (−45.74%) |
| Lismore 2023–24 | $235.791m | $122.821m | −$112.970m (−47.91%) |

Sources and PDF pages are in [annual_deviation_examples.csv](annual_deviation_examples.csv): Richmond accounts p10; Lismore accounts p9 in each year; Griffith accounts p9. These are **all-IPPE cash flows**, not matched ordinary renewal/capital project spending and not estimates of disaster effects. The Griffith row is not an event-matched counterfactual for either Lismore row. Lismore 2023–24’s budget is itself post-2022-disaster.

Richmond’s B5-1 narrative reports a **$17.030m capital underspend**, which differs from the **$17.259m gross-IPPE cash-payment gap**. The $229,000 difference is unresolved scope/accounting evidence: do not silently equate them. Net investing cash flows are even broader, including investments and asset sales, and must not substitute for infrastructure spending. Likewise, actual versus original budget is not proof of an approved downward budget revision: delivery can undershoot an unchanged budget.

## Quarterly basis: preserve positive as well as negative evidence

Lismore’s saved 2023–24 Budget by Program, PDF p17 / printed p15, compares **original FY2022–23** with **revised full-year budget at 31 March 2023**:

* Rural unsealed maintenance: $1,026,300 → $626,300, **−$400,000 (−38.98%)**.
* Urban sealed maintenance: $2,450,600 → $3,008,921, **+$558,321**.
* Rural sealed maintenance: $2,295,400 → $3,337,000, **+$1,041,600**.
* Regional block-grant maintenance: $1,150,600 → $1,200,600, **+$50,000**.
* Footpath and state-road routine maintenance: unchanged in these columns.

These six illustrative lines are not a complete ordinary infrastructure portfolio. They show why the negative line must not be selected alone. They are **annual forecasts observed at a quarter end**, not spending in that quarter. The document’s “Movement 2023/2024” column refers to another comparison and is not the FY2022–23 March revision; our differences use the first two columns only.

Both the FY2022–23 plan and March 2023 revision follow the February 2022 flood. That pair cannot demonstrate a cut to a plan fixed before that flood. It might become relevant to a later separately verified shock, but that requires adoption timing, local impact evidence and a complete revision history; no such treatment assignment is made here. The March approval/publication date is not automatically 31 March. September and December snapshots and the year-end reconciliation remain missing from the certified series.

## Define separate outcomes before collecting more

Use a fixed set of ordinary projects/work codes budgeted **before the relevant event**, with council × financial year × snapshot as the main budget grain and project × snapshot as supporting detail. Keep ordinary capital renewal/new works and routine operating maintenance as **separate blocks**. Exact asset/fund coverage is a design choice to lock before any effect estimation; a roads/bridges pilot is a practical starting scope, not a claim to all council infrastructure.

Let B0 be that portfolio’s original adopted full-year budget, Rq its revised full-year budget at snapshot q, and A its same-scope year-end actual:

* Cumulative revision: `(Rq − B0) / B0`.
* Incremental revision: `(Rq − Rprevious) / B0`.
* Annual delivery deviation: `(A − B0) / B0`.
* Final-budget execution gap: `(A − Rlast) / B0`.

The annual deviation equals the final cumulative revision plus the execution gap **only on identical scope and basis**. Preserve signed AUD changes and ratios; a zero/nonpositive baseline makes the percentage undefined, not zero. Do not truncate increases. A negative deviation is not yet **abnormal**: that requires comparison with councils’ ordinary revision patterns and comparable less/unaffected councils in the same period.

For NSW financial years, label Q1 July–September, Q2 October–December, Q3 January–March, Q4 April–June. Collect September/December/March review snapshots and a separately identified final budget/year-end close; do not fabricate a Q4 review if it does not exist. Keep review period end, information cutoff, report preparation and council adoption dates separately. Quarter-end YTD actuals require a phased YTD budget for pacing analysis; comparing YTD spend to the full annual budget would manufacture underspending.

Keep both the originally adopted budget and the last approved pre-event revision. If a November disaster already affected the December review, that review is not an untreated baseline for a later February episode without an explicit repeated-event design. A delayed project carried into next year needs a linked record so it is not mistaken for permanent cancellation. Reclassifications, grant additions and changed project scope must be reconciled before aggregation. Cost inflation means nominal budget revisions alone cannot measure a change in physical work delivered.

## Deferral evidence and competing explanations

E3’s ledger identifies Lismore’s $650,000 solar-carpark project delay and Eurobodalla’s Garlandtown bridge/resource diversion narrative. It also retains Eurobodalla’s report that scheduled road inspection and maintenance continued. [project_deferral_audit.csv](project_deferral_audit.csv) preserves these observations without inventing stable IDs or original/revised due dates. Project total value is not an amount cut or deferred.

For the proposed question, projects damaged by the disaster, physically inaccessible, redesigned for resilience or delayed by procurement may behave differently from undamaged ordinary projects losing resources. Record those dimensions explicitly. A delay alone does not establish budget reprioritisation; a downward forecast alone does not establish financial constraint. Fiscal, staffing, weather, access, contractor and grant-timing explanations remain unresolved.

## Disaster timing and joins

The existing August 2026 activation extract has **819 NSW LGA-event rows**, **122 location codes**, **165 AGRNs**, no missing listed starts and no duplicate location-code/AGRN rows. Listed starts range from **8 September 2017 to 16 April 2026**. This is not a complete disaster chronology: Eurobodalla’s Black Summer episode is not represented as a 2019–20 fire row in this extract. Use the V2 event ledger/council links and exposure status fields alongside it; absence must remain unknown where coverage is incomplete.

A conservative normalised exact-name join to V2 matches **618 rows across 91 councils**. The other 201 rows require alias/boundary or cohort review; not all are mere spelling errors, because V2 intentionally excludes amalgamated councils. No fuzzy join or zero exposure is assigned. The 122 codes also include a record labelled Unincorporated NSW; they should not be described as 122 certified study municipalities. Existing older crosswalks are review aids, not a reason to silently match every record.

All 618 matched event rows can link to a last completed fiscal period; **570** have both cash cover and operating ratio values. These are candidate links only. The last completed year may lack published data at onset, and current historical values may be restated. Financial-year completion and public availability remain separate tests. [nsw_disaster_timing_audit.csv](nsw_disaster_timing_audit.csv) marks the event-wide quarter without treating it as the council’s exact impact or revision quarter.

## Capacity and comparison support

V2 covers FY2012–13–2024–25, with no duplicate council-year keys. Operating ratio, unrestricted current ratio and own-source ratio each have **1,232/1,339** nonmissing values; harmonised cash cover has **1,129/1,339**. Existing audits document the incompatible 2012 cash definition, early road-scope differences, reviewed debt-service denominators, ratio/currency scaling and missing latest-year fiscal ratios. Reuse those audits and cell lineage; do not start from raw inconsistent units or silently impute outcomes.

Use separate pre-event capacity variables. Avoid a composite “weak capacity” index and do not update baseline capacity using post-disaster cash, grants or budget results. For a causal study, a pre-event measurement is necessary but does not itself make capacity exogenous: councils differ in infrastructure, exposure, remoteness and administrative resources.

The E3 pilot has three affected councils but only **two event groups**. Pre-event cash cover is 14.07 months (Eurobodalla), 13.33 (Lismore) and 11.31 (Richmond Valley): all are above the inherited three-month threshold. Two negative-operating-position councils share the Northern Rivers event. There is little independent support for the proposed interaction. Multiplying quarterly or project rows does not add independent councils/events.

Griffith, Kiama and Wagga Wagga are provisional comparisons only. Later declarations require quarter-specific screening; the saved activation data confirm Wagga Wagga’s August/September 2022 events, for example. Existing rankings used annual characteristics and aggregate maintenance, not original-budget revision histories. The redesign needs comparable pre-event revision patterns, ordinary project mix and independent exposure evidence. Two event groups and six pilot councils do not establish causal identification, regardless of whether future arithmetic deviations can be calculated.

## Minimum additional data — in order

1. **Complete one outcome chain for affected and comparison councils.** Retrieve original adopted budget and capital/maintenance schedules, September/December/March QBRS attachments with approval dates, final budget and same-scope actuals. Start with Lismore and Richmond Valley FY2021–22 plus a provisionally screened comparison such as Wagga Wagga; its suitability must still be checked. Obtain earlier years too, since February 2022 was not the first relevant shock. For the Black Summer set, use Eurobodalla FY2019–20 with Griffith/Kiama only after local exposure checks.
2. **A small classification/code bridge.** Stable program/project IDs; ordinary capital versus operating maintenance versus disaster response/reconstruction; fund, asset, cash/accrual and GST basis; transfers/carryovers and scope changes. If public schedules cannot supply it, request this targeted administrative extract. This is the critical bridge from broad capital numbers to the actual research outcome.
3. **Local event and baseline clocks.** Check event onset/impact/end and prior/overlapping disasters for every selected council, plus baseline budget adoption and capacity measurement/publication dates. Reuse existing data wherever verified. Do not request an entirely new statewide fiscal panel as the first step.
4. **Expand symmetrically after the measurement pilot works.** Obtain comparable pre-event years, event year and follow-up for affected and comparison municipalities. A planning window of three pre-years, event year and two post-years is sensible for auditing recurring revisions/carryovers, not a sufficient-sample guarantee. Re-screen controls across the entire window and add independent councils/events with fiscal-capacity variation. No fixed council count can be certified adequate before seeing coverage and dependence.
5. **Project register for the deferral mechanism.** Baseline funded portfolio and original milestones, each revised due date/budget, approval date, reasons, actual completion and damage/access status. Include projects that did not defer. Detailed grant receipts and staffing/procurement records are a second-stage mechanism need, not a prerequisite for the first budget-revision measurement check.

Exact minimum fields and priorities are in [minimum_additional_data.csv](minimum_additional_data.csv). This is an acquisition specification only; no requests were sent. Cached council index links may help find documents, but an index link is not a downloaded/verified QBRS.

## Audit scope and checks

All 187 existing CSV paths were inventoried; 183 parsed. Four supposed NEMA CSV downloads contain HTML and fail parsing; they are acquisition failures, not data tables. Key fiscal, exposure, event, documentary and E3 tables were profiled for counts, columns, missingness, dates and duplicate keys. Twenty cached E3 PDF text extractions were searched after whitespace normalisation; relevant primary financial/budget pages were read, and five newly transcribed pages were visually checked. Spreadsheet/ZIP files and generated graph indexes were inventoried; their mere presence is not treated as independent quarterly evidence. This is not exhaustive manual transcription of every PDF or workbook.

The new notebook runs only the audit, descriptive differences and coverage checks. It does not execute previous forecasting scripts or fit any model. Earlier E3 exclusions remain intact: the broader outcomes are documented separately rather than retroactively relabelling E3 as successful.

**Decision:** existing data support a concrete document/ledger collection pilot and some descriptive examples. They do not yet support the quarterly/annual causal comparison or the fiscal-capacity interaction in the research question.
