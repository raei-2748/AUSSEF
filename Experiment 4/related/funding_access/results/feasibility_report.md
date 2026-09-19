# Candidate Experiment 4 — extraordinary disaster-funding access

**Verdict: NO-GO for the proposed pooled LGA × disaster Category C need-versus-capacity study with these data. A measure-specific redesign would require new decision and eligibility records.** This is a feasibility result, not evidence that council capacity does or does not affect assistance access. No models were fitted.

Audit completed 19 September 2026. The supplied 11 August 2026 CSV is byte-identical to the current official resource. Newer webpages were used to audit meaning; they were not silently substituted for the snapshot. Experiments 1–3 and all **737** pre-existing files are hash-protected and unchanged.

## Verified backbone

| Quantity | Verified count |
|---|---:|
| All rows | 2,475 |
| LGA rows | 2,305 |
| SAL rows, excluded from LGA analysis | 170 |
| Distinct AGRNs, including those with SAL records | 378 |
| Recorded C-positive rows | 687 |
| Recorded D-positive rows | 993 |
| Events with any C | 30 |
| No-C / all-C / mixed-C events | 348 / 22 / 8 |
| Events with any D | 42 |
| No-D / all-D / mixed-D events | 336 / 31 / 11 |
| LGA rows in the 30 C-positive events | 739 |
| Natural-disaster, ordinary-council candidate rows after explicit exclusions | 733 |
| Verified eligible negatives / usable positive-negative contrasts | **0 / 0** |

There are no exact duplicate rows or duplicate LGA-event keys. One hazard label is missing. Onsets range from **8 September 2017 to 29 June 2026**. The metadata describes history from 2006, which the actual file does not provide. No C/D flags occur before 2021. These are coverage warnings, not proof that earlier disasters had no extraordinary assistance. All 170 SAL rows have C=D=0; mixing them into the negative class would be particularly misleading. The 172 `highest_drfa_category_group=unknown` rows comprise those SAL records plus Orange and Yarra. The dataset is not a census of every disaster-affected location, every applicant or every funding decision. See [publisher metadata](https://data.gov.au/data/api/3/action/package_show?id=10ba7303-e3af-41b4-98b5-e04db77caea8) and `activation_backbone_audit.csv`.

## A. What do cat_C and cat_D represent?

The defensible description is **recorded category activation indicators in a location-event assistance inventory**. Category C is a collection of community/sector recovery measures; Category D is exceptional relief/recovery beyond A–C. States request C/D assistance and Commonwealth agreement is required. The flags contain no amount, payee, measure ID, application, refusal or payment date. Activation is not receipt. AGDRP and DRA are separate individual assistance schemes. [NEMA overview](https://www.nema.gov.au/our-work/disaster-recovery/disaster-recovery-funding-arrangements); [DRFA 2018, clauses 4.4–4.5](https://www.nema.gov.au/sites/default/files/2024-08/disaster-recovery-funding-arrangements-2018.pdf).

The official export schema supplies column IDs and types **without field-level definitions or an explanation of zero coding**. Consequently, `cat_C=0` means only that the supplied row has no C flag. It cannot establish denial, consideration, ineligibility, absence of a relevant measure, or absence of funding. The same limitation applies to D. `activation_backbone_audit.csv` separates verified policy meanings from undocumented export semantics; it does not claim to have obtained definitions that the publisher did not supply.

## B. Is LGA × disaster the right outcome unit?

**Not for a generic pooled C indicator.** The formal assessment framework allows requests for a community, region or sector, not only an LGA. It also permits adjacent buffer areas subject to conditions. One event can have several measures with different eligible locations and beneficiaries. The relevant documentation unit is at least **event × state × named measure × geographic scope**, with applicant/provider records where the decision is actually made below or above LGA level. [Category C assessment framework, paragraphs 2–7](https://www.nema.gov.au/sites/default/files/2024-08/drfa-2018-guideline-3-category-c-assessment-framework.pdf).

A practical counterexample is AGRN 1046. The official category table identifies three C measures: mental health, recovery officers and tourism. Their named eligible council lists contain **5, 3 and 6 councils**, respectively. The union is seven councils, while the CSV records only five C-positive LGAs. **Cloncurry and Mornington are C-zero in the CSV but explicitly eligible for the Category C tourism program.** The category table is dated 17 January 2024 and the tourism page was updated 3 December 2024, before the supplied snapshot. This is a reconciliation failure for an “any C measure available” interpretation; do not overwrite the CSV or assume why it happened. [Official matrix, p6](https://www.qra.qld.gov.au/sites/default/files/2024-01/v16_activation_summary_northern_and_central_queensland_monsoon_and_flooding_20_december_2022_-_30_april_2023.pdf); [tourism eligibility](https://www.qra.qld.gov.au/tourism-recovery-and-resilience-program-115-million); [mental-health eligibility](https://www.qra.qld.gov.au/funding-programs/event-specific-exceptional-circumstances-assistance/2022-23-monsoon-and-flooding-exceptional-circumstances-package/community-mental-health-package-1-million); [officer-program eligibility](https://www.qra.qld.gov.au/funding-programs/event-specific-exceptional-circumstances-assistance/2022-23-monsoon-and-flooding-exceptional-circumstances-package/community-recovery-and-resilience-officers).

There is also direct council-targeted assistance: the Jasper matrix names Wujal Wujal's targeted package as C, alongside other regional programs. An all-C event therefore does **not** mean every LGA receives that council-specific package. [Jasper matrix, p3](https://www.qra.qld.gov.au/sites/default/files/2025-01/Version_18_Activation_Summary_for_Tropical_Cyclone_Jasper_associated_rainfall_and_flooding_13_28_December_2023.pdf).

## C. Can genuine positives and negatives be identified?

Some **specific-measure geographic positives** can be verified, but no eligible-but-unselected negatives were recovered. `positive_negative_case_audit.csv` records 16 positive measure-location entries across three events; this includes multiple programs for the same council and one unincorporated area. It is not 16 independent decisions or 16 payments. Rows outside a published program scope are `OUTSIDE_MEASURE_SCOPE`, not rejected eligible applicants.

All **30** C-positive events have an explicit review in `risk_set_validation.csv`. The measure ledger contains **63 review records**, including **42 category-verified C program components across 10 events**, one D comparator and 20 records whose exact C mapping remains unresolved. These are recovered lower bounds, not complete measure inventories. Searches that returned only a program description or blocked local downloads remain labelled as such. For the remaining events, formal eligibility and the C flag's measure aggregation could not be reconstructed fully from the reviewed public sources.

The eight mixed-C events warrant separate treatment:

| AGRN | C / LGA rows | Zero-case diagnosis |
|---|---:|---|
| 960 | 78 / 79 | Orange has A=B=C=D=0, AGDRP=DRA=1; recorded C prerequisite A/B absent |
| 1037 | 64 / 65 | Yarra likewise has no DRFA category flags, only individual AGDRP/DRA |
| 1038 | 17 / 18 | Glamorgan-Spring Bay is named on the producer grant page; exact category mapping unresolved |
| 1046 | 5 / 45 | Multiple C scopes; Cloncurry/Mornington zero conflicts; other zeros lack eligible-denial evidence |
| 1174 | 38 / 40 | Mackay and Torres Strait Island: basic activations recorded; eligibility for each extraordinary program unresolved |
| 1202 | 40 / 41 | North Burnett: basic activation does not prove eligibility for the same C measure |
| 1243 | 62 / 65 | Balonne, Murweh, Paroo: activation timing/program scopes vary; no refusal denominator |
| 1269 | 10 / 13 | Darwin, East Arnhem, Palmerston: scope of NFP assistance not reconciled to C flag; includes unincorporated geography elsewhere |

The CSV gives Orange and Yarra only individual-assistance flags. The corresponding [NSW](https://www.disasterassist.gov.au/Pages/disasters/current-disasters/New-South-Wales/storms-floods-10-March-2021-onwards.aspx) and [Victorian](https://www.disasterassist.gov.au/Pages/disasters/current-disasters/Victoria/victoria-floods-06102022.aspx) event pages do not establish them as C-eligible controls. The [Tasmanian producer page](https://alert.tas.gov.au/recovery/financial-support-small-business-primary-producer) lists 18 LGAs but does not by itself prove their Category C mapping. `mixed_event_case_review.csv` preserves each raw flag, so these distinctions are inspectable.

## D. How much independent information remains?

- **378 AGRN registrations**, not certified independent weather systems or policy decisions.
- **30 C-positive registrations**; removing the terrorist event and the SA event consisting only of an unincorporated area leaves at most **28 candidate ordinary-council natural-disaster events** before other gates.
- **42 recovered C program components in 10 events**, not 42 proven independent approvals. Some are monitoring/evaluation or service-delivery programs, and multiple components may share an approval.
- **Unknown number of independent funding decisions**, because application/approval IDs, scope versions and joint package links are missing.
- **Zero certified eligible positive-negative contrasts** for the proposed capacity question.

Cross-state registrations can share a storm, and a package can span several registrations: the [Queensland 2021–22 package](https://www.qra.qld.gov.au/funding-programs/event-specific-exceptional-circumstances-assistance/2021-22-queensland-rainfall-and-flooding-exceptional-circumstances-package) covers multiple rainfall/flood events. Alfred spans NSW and Queensland; 2025 inland floodwater crossed from Queensland into South Australia. Treating all affected LGAs or all AGRNs as independent would inflate information. No numerical effective sample size is manufactured.

## E. Is there sufficient variation?

No. Twenty-two of the thirty C-positive events flag every listed LGA. The eight apparent mixed events do not produce eight certified contrasts: two lone zeros have no DRFA categories, one has a possible program-scope discrepancy, and the others lack a common eligible-but-unselected risk set. Comparing against no-C events would require independently observed need and proof those events were considered under comparable measures. Conditioning only on activated locations may itself select on the policy process.

## F. Can legitimate need be measured independently?

Potential sources exist, but **no complete, pre-decision event × LGA need bundle is certified here**. `need_data_availability.csv` audits 16 separate variables for each of 30 events (480 rows); it deliberately does not fabricate a merged need dataset or a need index.

DEA satellite water observations are independent of grants but have cloud, revisit and peak-capture limitations and do not measure water depth. NSW FESM can support fire exposure, with state/season/event restrictions. BoM cyclone best tracks are reanalysed after events, so original observation and publication dates matter. [DEA water documentation](https://knowledge.dea.ga.gov.au/data/product/dea-water-observations-landsat/); [NSW FESM](https://www.environment.nsw.gov.au/topics/animals-and-plants/native-vegetation/landcover-science/fire-extent-and-severity-maps); [BoM cyclone database](https://www.bom.gov.au/cyclone/tropical-cyclone-knowledge-centre/databases/).

Houses damaged, displacement, infrastructure loss and agricultural/business impacts require dated assessment records covering both included and excluded areas. Wooroloo's official annual report documents 86 destroyed properties across the event, but an annual two-council total cannot supply a pre-decision LGA vector. [DFES Wooroloo report](https://dfes.wa.gov.au/annualreport2021/wooroloo-bushfire/).

ABS population, remoteness and disadvantage are baseline characteristics, not substitutes for event damage. Census 2021 reference time, first release and SEIFA release differ: SEIFA 2021 was released **27 April 2023**. It must not be treated as publicly known before then. No funding amount, recipient count, reconstruction spending or later recovery is used as a need proxy. [Census release guide](https://www.abs.gov.au/census/guide-census-data/2021-census-product-release-guide); [SEIFA technical paper](https://www.abs.gov.au/statistics/detailed-methodology-information/concepts-sources-methods/socio-economic-indexes-areas-seifa-technical-paper/2021).

## G. Can pre-disaster capacity be linked?

Partly, retrospectively, within NSW. An explicit state-constrained name/key crosswalk links **157 / 739 candidate rows (21.2%)** to the frozen 103-council fiscal panel. This includes the excluded Waverley terrorist-event row; linkage is not study eligibility. Financial periods are selected only when **period end < disaster onset**. No current disaster-year annual value is used if its period ends after onset.

Numeric pre-onset coverage: cash cover 155, current ratio 155, operating performance 155, own-source ratio 155, grant share 156, debt-service cover 153 after quality exclusions, debt-service ratio 155, population 157 and road length 157. Exact original value, source year, workbook/sheet/row and lag days are retained. Unmatched councils remain missing; no fuzzy match or national extrapolation is performed. Geography vintage remains a join-certification gap.

These are **prior-period economic measurements, not certified real-time predictors**: first publication and revision vintages are unresolved. Earlier event-onset counts are retained as descriptive history only. A past onset does not prove its C/D decision was made before the next disaster; the 2026 snapshot can backfill history. Staffing/FTE, remoteness and actual prior grant receipt are not present in the backbone and remain missing. See `capacity_linkage_audit.csv`, `capacity_coverage.csv`, `council_crosswalk_audit.csv` and `temporal_leakage_audit.csv`.

## H. Are policy periods and states comparable?

Not on the category letter alone. DRFA replaced NDRRA on **1 November 2018**. Queensland identifies distinct guideline periods: November 2018–June 2021, July 2021–November 2024, and December 2024–June 2026. These are Queensland implementation periods, not universal national causal cutoffs. The current NEMA page also describes standardised packages without proving a single effective date for every measure. [DRFA commencement](https://www.qra.qld.gov.au/funding/drfa); [Queensland guideline versions](https://www.qra.qld.gov.au/qdfg).

Program composition also changes: the 1046 matrix labels the large primary-producer recovery grants D, while the 1202 matrix labels its producer recovery grants C. This is an observed classification/composition difference, not proof that a single legal definition changed on one date. State and measure-specific rules must be reconciled before pooling. [1046 matrix p6](https://www.qra.qld.gov.au/sites/default/files/2024-01/v16_activation_summary_northern_and_central_queensland_monsoon_and_flooding_20_december_2022_-_30_april_2023.pdf); [1202 matrix p4](https://www.qra.qld.gov.au/sites/default/files/2025-07/V24_Activation_Summary_Western_Queensland_Surface_Trough_Associated_Rainfall_and_Flooding_21_March_to_19_May_2025.PDF). `policy_era_audit.csv` keeps known periods separate from unresolved transitions.

## I. Overall verdict

**NO-GO with the supplied activation flags as Y.** The decisive failures are an unverified negative class, inconsistent mapping from C flags to actual measures, repeated policy decisions across locations, unknown independent decision counts, incomplete need evidence and geographically limited capacity data. Category D does not repair these failures.

## J. Is an eventual modelling design justified?

Because the gates fail, no substantive model specification or train/test experiment is adopted. A **major redesign** could first investigate one named, stable assistance measure within one state. The administrative data contract would require: all impact assessments and geographic consideration records; approved, declined, not-requested and out-of-scope cases; dated measure/decision IDs; eligibility rules and scope revisions; independent damage measures recorded before each decision; and pre-onset fiscal/administrative data. For an applicant-level grant, obtain all eligible applications and outcomes; the resulting question concerns applicant access and may not support a council-capacity interpretation. Assess this before choosing models.

## K. Why NO-GO, and is another outcome more defensible?

No other column in this CSV is presently a defensible substitute for **extraordinary council funding receipt**. C/D, AGDRP and DRA can support a narrower descriptive inventory of recorded assistance availability, subject to scope reconciliation. They cannot establish amounts paid, denials or fairness after need. Do not relabel higher classification accuracy as evidence for the thesis.

The output does not include `statistical_results.csv`, because this phase permits no substantive modelling. Figures report descriptive flags, geographic-scope verification and certification gaps only. All 30 candidate events remain visible; unresolved cases were not discarded to manufacture a favourable result.
