# Experiment 4: budget-reallocation pilot
**Verdict: NO-GO for scaling directly into a causal study with the reconstructed public data.**
**GO for a descriptive documentary pilot and a targeted administrative-data request. No model fitted.**

Research question: Do disasters cause abnormal downward revisions to pre-planned ordinary infrastructure spending, and are revisions larger for councils with weaker pre-disaster fiscal capacity?

The pilot covers Lismore and Richmond Valley in FY2021–22, Eurobodalla in FY2019–20, and two screened comparison candidates: Griffith in FY2019–20 and Wagga Wagga in FY2021–22. These are five council-years, not 79 independent treated observations. Earlier experiments, original data and outputs were preserved.

## Reconstruction
79 council/category budget chains, 312 observed stage values and 83 explicit missing stage values; 32 selected project/program revision records; five audited original-to-actual cash-IPPE pairs. All five councils have Q1/Q2/Q3 records. Wagga's original capital-program total remains unverified. Every category's same-scope year-end actual remains missing; annual cash totals are supplied separately.

Nominal AUD million, **different source scopes**, not an ordinary-infrastructure comparison:
| Council        |   Original |      Q1 |      Q2 |      Q3 |
|:---------------|-----------:|--------:|--------:|--------:|
| richmondvalley |     46.881 |  49.34  |  45.706 |  38.585 |
| eurobodalla    |     75.418 |  65.695 |  47.122 |  43.394 |
| lismore        |     66.17  |  67.8   |  70.436 |  49.932 |
| griffith       |     40.932 |  48.536 |  49.469 |  34.701 |
| waggawagga     |    nan     | 158.777 | 132.453 | 128.414 |

Lismore figures are quarantined because the capital table prints 2020/21 and $000 headings inside its 2021–22 review. Context suggests dollar amounts, but this pilot does not certify that correction. Q3 has problematic allocations and a negative “Renewal Other” balance. The adopted May resolution also adds a $5m reserve transfer. Eurobodalla Q3 remains proposed: adoption minutes could not be retrieved, and index date and minutes filename differ. Griffith reports cash-flow purchases; Richmond and Eurobodalla report capital programs; Wagga includes pending works. Do not pool these as one outcome.

Separate annual cash comparison:
| Council        |   Original cash IPPE $m |   Actual cash IPPE $m |   Deviation % |
|:---------------|------------------------:|----------------------:|--------------:|
| richmondvalley |                  43.69  |                26.431 |         -39.5 |
| lismore        |                  64.888 |                32.656 |         -49.7 |
| griffith       |                  40.933 |                22.21  |         -45.7 |
| eurobodalla    |                  75.418 |                39.541 |         -47.6 |
| waggawagga     |                 133.279 |                82.534 |         -38.1 |

These measure all-capital IPPE cash expenditure. They do **not** complete the category chains above. A similar original cash budget magnitude is not proof of identical scope or accounting basis. Large underspends in the screened comparisons show why an annual negative deviation alone cannot establish a disaster effect.

## Project evidence
- Richmond Valley approved a $7,121,799 net capital reduction on **17 May 2022**, reported against March31. Its roads decrease contains **$1,245,243 of old AGRN960 reconstruction** removed after roads were damaged again and funding was to be reassessed under AGRN1012. That is not ordinary-work displacement. [Q3 statement, PDF pp11–15](https://richmondvalley.nsw.gov.au/wp-content/uploads/2022/11/Quarterly-Budget-Review-Statement-for-the-quarter-ended-31-March-2022.pdf); [adoption, p10](https://richmondvalley.nsw.gov.au/wp-content/uploads/2022/05/Unconfirmed-Minutes-Ordinary-Meeting-17-May-2022.pdf).
- Richmond's ordinary-work candidates include a $1.6m pool deferral, $1m Cell6 construction rephasing and $70,418 depot pavement deferral. Reasons include rain, flood disruption and resources. Damage/access and project actuals remain unverified. Cell6 has a $3m original allocation, but phase-level ID continuity is unresolved. A Q4 action marked completed concerns the pool masterplan while construction had commenced; it is not completion of the pool.
- Lismore documents flood-related deferrals and a transfer from capital to operating roads work. These are distinct changes. Its $20,503,800 reported Q3 reduction is a provisional descriptive figure, not a certified ordinary-spending reduction. [Q3 attachments, pp164–168](https://lismore.infocouncil.biz/Open/2022/05/OC_10052022_ATT_EXCLUDED.PDF); [minutes, p12](https://lismore.infocouncil.biz/Open/2022/05/OC_10052022_MIN.PDF).
- Eurobodalla's September review records **$13,740,180 downward revisions**, partly offset by carryovers, before the main December31 fire impact. Its largest September category reduction is Strategic Planning ($16.57m). Later reviews mix fire, flooding, project timing and COVID effects. [Q3 capital history, PDF p3](https://www.esc.nsw.gov.au/__data/assets/pdf_file/0020/160418/Quarterly-Budget-Review-attachment.pdf).
- Wagga provides source job numbers: **45049** moves $358,985 to FY2023–24, and **45109** moves $133,766 to FY2022–23. Total project budgets are unchanged. These are rephasing examples; WiFi also needs infrastructure-scope screening. [December financial review](https://meetings.wagga.nsw.gov.au/Open/2022/01/OC_31012022_AGN_4855_AT.htm).

The register is a selected evidence sample, not the full ordinary-work universe. Do not add its rows to category totals, or count bundled programs as independent projects. “Ordinary candidate” does not certify an undamaged asset or a complete original-to-actual match.

## Timing and comparisons
Northern Rivers DRFA event start is **22 February 2022**; Lismore gauge peak is **28 February**. These are different date types. Casino's extreme rainfall is documented on February28, but project damage timing across Richmond Valley remains unknown. Both councils also have a November2021 declaration: Q2 is before the February event but not necessarily disaster-free. Lismore's December review was adopted at the **16 February reconvened meeting**, despite the minutes' February8 running header. Q3 approvals occurred in May.

Currowan ignition was **26 November 2019**, the date of Eurobodalla's Q1 adoption; major local fire impact was **31 December**. February2020 flooding and COVID complicate Q3. Do not date a May revision to March31 or treat Q2 as wholly pre-fire. Exact reference/decision dates and sources are in decision_dates.csv and event_timeline.csv. [Lismore peak](https://www.lismore.nsw.gov.au/Community/Natural-hazards-and-emergency-information/Flood-information-for-Lismore1/Flood-history); [Eurobodalla annual report](https://www.esc.nsw.gov.au/__data/assets/pdf_file/0011/163001/E.ANNUAL-REPORT-2019-2020-FINAL.pdf); [Richmond rainfall](https://richmondvalley.nsw.gov.au/wp-content/uploads/2022/04/RV-Flooding-EIS-PUBLIC-REPORT-April-2022.pdf).

Griffith and Wagga retain verified zero **mapped burn within the product scope** and zero bushfire/flood declarations in the inherited V2 event-year inventory. That does not certify zero physical exposure, indirect disruption or complete flood coverage. The later activation snapshot has no index-year records for these candidates; absence alone is not zero. Both have later disasters. Geography, drought, contractors and COVID remain unresolved. They are measurement comparisons, not validated causal controls. No ordinary-budget parallel-trend check is currently possible.

## Cleaning and modelling suitability
Amounts normalised to nominal AUD; signed revisions retained; no missing-value imputation. Category keys are unique within council/year, source project IDs preserved where present, analyst labels distinguished. Original plans, carryovers, revised annual forecasts, YTD actuals and year-end cash actuals remain separate.

Category totals reconcile exactly for Richmond, Griffith, Wagga and the retained Lismore category set. Eurobodalla has $1 residuals retained as rounding flags. Wagga's September one-off change has a **$1m source arithmetic discrepancy**. Griffith's QBR original differs from the rounded annual original by **$545**, unresolved. OCR was checked against page images for retained Lismore/Griffith numbers; Eurobodalla uses public web PDF text because direct download returned403 and page-image retrieval failed. These verification limits remain explicit.

The data are suitable for checking **reported revisions**, subject to flags. They are **not suitable for the causal model**:
1. No certified fixed pre-event ordinary portfolio with same-scope annual actuals.
2. No asset-level damage/access screen separating direct destruction from displaced undamaged works.
3. No multi-year ordinary-budget baseline establishing abnormal revisions.
4. No validated comparisons or sufficient independent event/council contrasts.
5. Fiscal measurements precede the event economically, but exact publication vintage is incompletely certified. All three treated councils have cash cover above three months; two weaker operating positions share one event. That does not identify a capacity interaction.
6. Disaster damage, COVID, grant timing, inflation and supply constraints compete as explanations. Post-event grants/damage estimates cannot become pre-event capacity predictors.

**The model-ready ordinary panel intentionally contains zero rows.** This means the audited reconstruction fails the outcome gate, not that all public documents have been exhausted or a future administrative-data study is impossible.

## Minimum next step and scale gate
minimum_additional_data.csv specifies the request. Priority: versioned project ledger with original/quarterly/final budgets, actuals, project/asset IDs, recodes, deferral/completion dates, disaster job codes and dated damage/access status. Obtain comparable portfolios for at least three pre-event and two post-event years, flagging later disasters. Add grant-payment and workforce/contractor timing for financial-mechanism claims.

Reopen scaling only after joins, pre-event plans, ordinary-budget pretrends, comparison exposure/spillovers and independent council/event variation pass a pre-specified identification/power assessment. Category row counts cannot substitute for these gates. **No outreach sent; no model fitted.**

Validation: 1102 pre-existing files checked; none changed. The notebook/reproduce.py rebuild descriptive outputs offline from curated source-linked records.
