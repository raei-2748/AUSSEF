from pathlib import Path
import json,hashlib,shutil
import pandas as pd
ROOT=Path('/Users/ray/Research/AUSSEF'); O=ROOT/'outputs/fiscal_panel_v2'
s=json.loads((O/'validation_summary.json').read_text())
profile='https://www.olg.nsw.gov.au/sites/default/files/2026-02/your-council-june-2015-profile-and-performance-of-the-nsw-local-government-sector.pdf'
comp='https://www.olg.nsw.gov.au/sites/default/files/2026-02/comparative-information-on-nsw-local-government-measuring-local-government-performance-2012-2013.pdf'
albury='https://eservice.alburycity.nsw.gov.au/ACCPublicDocs/DocumentViewer.aspx?DocID=1072745'
(O/'README.md').write_text(f'''# NSW fiscal panel — Version 2 candidate

**Verdict: NO-GO for immediately rerunning the persistence–ridge–tree experiment.** The historical extension is useful, but it is not yet a verified as-of forecasting dataset. No new models were fitted.

Built 18 September 2026. Start with [GO_NO_GO.md](GO_NO_GO.md), then the [definition audit](definition_changes.md) and [availability audit](temporal_availability_audit.md).

## What was delivered

- **103 continuing councils**, identified by `council_key`; 1,339 council-year rows from 2012–13 to 2024–25.
- **515 additional historical rows**, covering five earlier financial years. Numeric operating-ratio observations: 1,232. The 2024–25 primary target was not collected in the source and remains missing.
- Detailed audited income-statement components for **9 council-years**, including two newly transcribed historical Albury observations. This is a sparse supplementary layer, not statewide component coverage.
- Eight dated statewide advance-grant announcements for target years 2017–18 to 2024–25. Seven have years with observed primary outcomes. Repeating an announcement across councils does not create independent policy variation.
- Seven unresolved maintenance arithmetic conflicts; two documented Albury archive/comparative discrepancies. Earlier cash cover and broader road lengths are retained as raw values but withheld from their common-definition columns.

## Main files

| File | Purpose |
|---|---|
| [NSW_Fiscal_Panel_V2_candidate.csv](NSW_Fiscal_Panel_V2_candidate.csv) | Annual candidate observations; NOT an approved predictor matrix |
| [variable_dictionary.csv](variable_dictionary.csv) | Units, definitions, caveats and roles for every panel column |
| [coverage_by_year_variable.csv](coverage_by_year_variable.csv) | Observed and missing counts, each year and variable |
| [coverage_by_council.csv](coverage_by_council.csv) | Council coverage |
| [coverage_by_forecast_year.csv](coverage_by_forecast_year.csv) | Available fiscal pairs and exposure combinations |
| [council_selection.csv](council_selection.csv) / [council_crosswalk.csv](council_crosswalk.csv) | Included/excluded entities and historical source names |
| [cell_lineage.csv](cell_lineage.csv) / [detailed_component_lineage.csv](detailed_component_lineage.csv) | Workbook cells, units, sources and statement transcriptions |
| [temporal_availability_audit.csv](temporal_availability_audit.csv) | Predictor-by-council-by-target availability decisions |
| [publication_date_audit.csv](publication_date_audit.csv) | Verified release months versus unresolved archive vintages |
| [dated_ex_ante_policy.csv](dated_ex_ante_policy.csv) / [verified_ex_ante_features.csv](verified_ex_ante_features.csv) | Dated announcements, separately from realised fiscal results |
| [potential_forward_folds.csv](potential_forward_folds.csv) | Structural fold counts only; no fitted models |
| [validation_summary.json](validation_summary.json) | Counts and preservation checks |

## Timing and interpretation

For an event financial year **t**, use council characteristics from **t−1** and event exposure during **t** to predict fiscal outcomes in **t+1**. The operational forecast cutoff used here is the start of the target year, **1 July of t+1**. This preserves the previous two-year fiscal lag. It does not presume that a fire map was available merely because the fire had occurred.

The existing expanding-window rule is retained for the eligibility count: training target years must be earlier than `test_target_year − 1`, with at least 100 training rows and two test rows. Fiscal-only history permits eight potential folds; retaining available event exposure permits four, compared with three in the original-period subset. These are optimistic structural counts, not certified backtests.

Any later authorised rerun should compare persistence, ridge and the shallow tree on identical target rows using MAE, RMSE and out-of-sample R², retaining negative R². Fit all preprocessing within training folds. No score or claim of improved accuracy is produced here.

## Reproduction and preservation

Run `python build_panel_v2.py`, then `python write_v2_reports.py`, with pandas, NumPy, matplotlib, xlrd and openpyxl installed. Scripts read the frozen original CSV and the previously cached official OLG workbooks in `../operating_ratio_audit/sources/`; new report sources are cached in `sources/`. Absolute project root is declared near the top of each script. No downloads are needed for this rebuild. Source manifests retain failed retrievals as well as successes; a failed download is not a missing council observation.

All writes are confined to this folder. SHA-256 checks verify **252 prior files unchanged**, including `NSW Data Panel.csv` and prior experiments. The output does not create a composite health index, fill missing exposure with zeros, or splice predecessor councils into amalgamated councils.

![Coverage](coverage_heatmap.png)
''')
(O/'definition_changes.md').write_text(f'''# Definition, unit and measurement audit

This is a candidate harmonisation, not a claim that every historical ratio has an invariant definition. Original values, headers, cell addresses and multiplication factors remain in the lineage files. Missing values are never imputed.

## Fiscal measures

| Measure | Common unit and handling | Unresolved issue |
|---|---|---|
| Operating performance | Percentage points; published ratio retained after explicit fraction-to-percent conversion | Adjusted numerator and revenue exclusions vary across report vintages; not reconstructed from broad income totals |
| Cash expense cover | Months; common column begins 2013–14 | 2012–13 uses an incompatible numerator/denominator; raw value retained separately |
| Unrestricted current ratio | Times; never multiplied by 100 | Restricted assets and excluded liabilities require consistent note definitions |
| Own-source revenue | Percent; continuing-revenue denominator can include capital grants | Adjusted exclusions differ; not automatically `100 − grants_pct` |
| Debt service cover | Times; zero values flagged for denominator review | Debt-free/zero-service cases must not be interpreted as ordinary low cover |
| Debt service ratio | Percent; separate from cover, not its reciprocal | Missing in 2012–13 source; keep distinct denominator definition |
| Maintenance adequacy | 100 × actual/required, positive required denominator only | Council-assessed required spending is not a uniform engineering standard |
| Monetary components | Nominal AUD; multiply only headers explicitly stated in thousands by 1,000 | No inflation deflation or reporting-vintage repair is implied |
| Road length | km; common column restricted to local/regional scope | Early series also includes state roads, so common measure is missing in those years |

### Cash cover: a verified definition break

The [2013–14 OLG profile]({profile}), PDF p17 (printed p15), explicitly describes the addition of term deposits that were excluded previously. Its cash-flow-based denominator also differs from the expense-based description in the [2012–13 comparative report]({comp}), PDF p346. No universal conversion is defensible without cash, deposit and payment components. Consequently `cash_cover_reported_months` retains 2012 values while `cash_cover_months` withholds them. Numeric availability in 2012 is not comparability.

### Operating ratio and statement components

The early comparative report describes revaluation exclusions (PDF pp346 and348). Albury's [2013–14 statements]({albury}), PDF p50, also exclude specified fair-value, disposal and joint-venture effects. Do not divide unadjusted before-capital surplus by an unadjusted income total and label the result the official operating ratio.

The Albury example supplies an explicit vintage check: its later 2012–13 comparative operating ratio is −0.94%, whereas the OLG archive candidate is −1.12%; own-source revenue is 82.52% versus 78.97%. These differences remain unresolved in `vintage_discrepancies.csv`. They are not silently overwritten or attributed to a particular cause without reconciliation.

Albury PDF p4 contains current 2013–14 and comparative 2012–13 consolidated income statements in $000. Revenue and expense sums, and the before-capital result, reconcile exactly. Depreciation plus separately reported impairment is labelled as a derived sum in lineage. `operating_revenue_ex_capital_aud` uses revenue and capital grants from the **same audited statement**, not mixed vintages. Other detailed observations are inherited from the earlier documented statement audit. Report-vintage and source-location fields remain attached.

### Accounting regimes

Potential breaks include AASB13/119 changes around 2013–14; AASB9 from 2018–19; revenue standards AASB15/1058 and leases AASB16 from 2019–20; and service-concession standard AASB1059 from 2020–21. These are review flags, not numerical adjustments and not proof that every council was materially affected. The [Audit Office 2019 report](https://www.audit.nsw.gov.au/our-work/reports/report-on-local-government-2019), section2.3, and [2020 report](https://www.audit.nsw.gov.au/sites/default/files/documents/Report%20on%20Local%20Government%202020.pdf) discuss the later transitions. Individual restatements and transition amounts remain unquantified.

### Maintenance

The 2015 profile, PDF p27 (printed p25), identifies the early Special Schedule7 figures as unaudited. Required spending depends on council asset-management estimates. Recalculation checks internal arithmetic only; it cannot harmonise the underlying engineering requirement.

Seven rows differ by more than one percentage point between reported and recomputed adequacy. Raw amounts, reported ratios and recomputed ratios remain available; the common eligible ratio is withheld. The fixed 1pp tolerance accommodates integer reporting in older years and is not selected by model performance. Four of these rows occur in the V1 overlap; `v1_overlap_differences.csv` records their changed eligibility. Other compared nonmissing overlap values agree within the stated rounding tolerance. No extreme fiscal outcomes were removed simply for being extreme.

### Source-specific scaling

`unit_conversion_rules.csv` records every source-year variable rule. Examples: 2012 maintenance fractions ×100; 2023 operating, own-source, grants and maintenance fractions ×100; debt-service ratio is already a percentage and receives no such conversion. In 2024 grants are fractional but maintenance is already a percentage. Currency scaling is per column, not per workbook. The 2024–25 source omits six fiscal ratios; those cells are missing, not zero.

Read `coverage_by_year_variable.csv` for target-specific missingness. The presence of a complete annual identity row does not imply complete measurements, a clean audit opinion, or ex-ante availability.
''')
(O/'council_and_period_audit.md').write_text('''# Council identity and reporting-period audit

The official OLG 2015–16 workbook identifies 108 councils operating for the full July2015–June2016 financial year. This is the starting continuing-entity list. Names are matched to the frozen panel's `council_key`, using reviewed legal-name token normalisation and explicit aliases. All extension years must contain the same matched key. Names are display/provenance fields, not identifiers.

Twenty present-day councils absent from that continuing list are excluded; no predecessor totals are added together. Of the 108 continuing entities, five further exclusions leave **103**:

| Council key | Reason |
|---|---|
| hills | 2016 boundary transfer to Parramatta |
| hornsby | 2016 boundary transfer to Parramatta |
| cobar | Existing boundary-change flag; conservatively excluded pending reconciliation |
| inverell | Existing boundary-change flag; conservatively excluded pending reconciliation |
| lachlan | Existing boundary-change flag; conservatively excluded pending reconciliation |

Evidence includes the [2016 proclamation](https://legislation.nsw.gov.au/view/pdf/asmade/sl-2016-241), [Audit Office amalgamation appendix](https://www.audit.nsw.gov.au/sites/default/files/auditoffice/2018-Reports/Local%20Government%202017/Appendix%20four%20-%20Councils%20amalgamated%20in%202016.pdf), [Hornsby boundaries](https://www.hornsby.nsw.gov.au/Council/About-Council/Wards-and-boundaries), [The Hills boundaries](https://www.thehills.nsw.gov.au/Council/Mayor-Councillors-Elections/Ward-Boundary-Maps), and [Parramatta harmonisation records](https://participate.cityofparramatta.nsw.gov.au/harmonisation-dcp). Original flags are conservative evidence, not independent confirmation of the date or extent of each transfer.

This screen is defensible for a candidate panel but is not a certification of unchanged cadastral geometry. Minor boundary adjustments and source-boundary vintages require further checking before causal/geographic interpretation. Inclusion depends on entity continuity, not predictive success or fiscal outcomes.

Each candidate row represents 1July to30June and is labelled with the **starting year**. `reporting_months=12` reflects source annual headers and the continuing-entity screen. Individual auditor opinions and reporting-period exceptions have not been read for every council-year; `reporting_period_evidence` states that limit. Consolidated Albury statements are not mixed with its separate general/water/sewer indicator tables.

There are 13 identity rows per council, 2012–13 through2024–25. Missing fiscal values remain missing within these rows. All 515 pre2017 rows are new; later source cells are re-extracted rather than changing the frozen input. See `council_selection.csv` for all128 original councils and `council_crosswalk.csv` for historical names, source rows and unmatched predecessors.
''')
(O/'temporal_availability_audit.md').write_text('''# Temporal availability audit

## Forecast contract

For target financial year starting Y, prior council measurements come from Y−2 and disaster exposure from Y−1. The cutoff is **1July Y**, immediately before the target year's observations begin. A value must both refer to an eligible period and be demonstrably available by that cutoff. Publication delays, restated comparatives and later geographic mapping can violate the second condition despite a correct year label.

The CSV audit covers every selected council, each target year2014–2024, the candidate fiscal/scale/component variables, three exposure variables, and the dated policy feature. It records numeric presence separately from verified availability. Missing does not mean zero; unknown publication does not prove late publication.

## Findings

| Evidence | Finding | Eligibility |
|---|---|---|
| FY2012–13 comparative report | Cover says June2014 | Release-month upper bound is before July2014; current spreadsheet vintage not yet matched to original report cells |
| FY2013–14 profile | Cover says June2015; OLG2014–15 annual report PDF p17 corroborates release | Same distinction: report timing verified, archived numeric vintage unverified |
| Later annual OLG workbooks | Current official downloads recovered | Original release dates and revision histories not certified |
| Albury2013–14 statements | Authorised27October2014, PDF p2 | This retrieved report could not supply its 2012–13 comparative before July2014; for later cutoffs authorisation alone does not prove public release |
| Remaining granular statements | Source/report vintage retained | No certified first-publication dates in this audit |
| Prior-year disaster data | Occurrence periods known in frozen data | Mapped-product/declaration publication vintages not certified; pre2017 exposures not extended |
| Target-entitlement FAG advance policy | Dated circulars before target starts | Verified announcement feature; final council entitlement and realised revenue are different quantities |

`verified_ex_ante_features.csv` contains only the verified policy announcements: approximately50%,50%,52%,50%,50%,75%,100%,85% for targets2017–18 through2024–25. The seven first years have observed primary outcomes; 2024–25 does not. There are eight statewide announcements, not824 independent financial shocks. See the dated-policy CSV for exact dates, original links, page references and caveats. The 2022 circular is GC151 despite the archive filename saying GC150.

Advance payments against the **target year's entitlement**, announced during the preceding year, are eligible timing information. Advance payments against the *following* year's entitlement announced near the end of the target year are not known at this cutoff. Actual target-year grant revenue, reconstruction spending, realised losses, audited target balances and retrospective revised ratios cannot be predictors.

The genuine new information is limited: a statewide announcement can capture a policy regime but supplies no within-year council differentiation. Older detailed operating/capital grants were recovered for only two new council-years. Historical rating-category revenue is much broader, but residential rates are not total rates plus annual charges, and numeric presence does not certify original availability.

## Decision rule and remaining work

**Zero complete predictor bundles are presently certified as ex ante.** This is an evidence-completeness finding, not a claim that councils lacked financial information at the time. No fitted performance conclusion follows from it.

To unlock a forecast rerun, obtain original released annual reports or archived workbook vintages, match candidate cells, and attach a dated public-release record to each retained predictor source. For a pre2017 disaster experiment, also extend comparable exposure and verify product availability. A retrospective explanatory experiment using later mapping would answer a different question and must be labelled separately.

Current upload paths (including2026 folders), HTTP modification dates, accounting year-ends, audit-signing dates and statutory deadlines are not silently used as publication dates. Failed source downloads remain in acquisition manifests and do not become numeric missingness claims.
''')
(O/'GO_NO_GO.md').write_text('''# Decision: NO-GO for an immediate predictive rerun

The historical extension provides useful additional measurements, but the combination of historical exposure, consistent financial definitions and demonstrably pre-target financial information is not yet sufficient to justify rerunning the existing persistence–ridge–tree experiment as an ex-ante forecast.

| Gate | Evidence | Result |
|---|---|---|
| Continuing-council extension | 103 councils; five earlier financial years;515 additional rows | Candidate construction achieved |
| Common definitions | Cash-cover break in2013–14; road-scope change; operating-vintage discrepancies; maintenance measurement conflicts | Partial; explicit exclusions/flags needed |
| Broad new financial mechanisms | Historical aggregate revenue/expenses and rating categories; only two new detailed statement council-years | Insufficient broad operating/capital-grant component coverage |
| Dated ex-ante information | Eight statewide advance-grant announcements, seven with primary outcomes | Useful but limited independent variation and no council-specific payment coverage |
| Same disaster design gains | At most four potential folds versus three on the same V1-period subset | One extra potential test year, not five |
| Financial-only design gains | Eight potential folds under existing embargo/minimum training rule | Upper bound; would omit the original disaster requirement and still needs vintage checks |
| Verified complete as-of bundles | Zero certified by this audit | Fails current forecast-readiness gate |

Potential fold counts use observed primary-target/prior-value pairs; train targets precede test target−1, and training must contain at least100 rows. They do not assume imputation creates absent outcomes or certify source availability. `potential_forward_folds.csv` retains every candidate test year, including invalid/empty years. There was no model fit or performance-based year selection.

The data do **not** establish that fiscal prediction is impossible. They show that this extension alone has not solved the weak design's information limitations. More rows of related ratios can increase training size without adding the timing and mechanisms needed to predict abrupt fiscal changes.

## Smallest useful next data task

1. Validate original publication vintages for a bounded set of prior-year financial predictors and target years, with explicit as-of dates and matched values. Resolve the Albury discrepancy as a worked example rather than assuming all archived ratios are first releases.
2. Extend disaster exposure before2017 on the same definition and audit when mapped products/declarations became available. Without this, the original question cannot use most of the extra fiscal history.
3. Build comparable council-specific prior operating/capital grants, total rates/charges, cash payments and material expense components from released statements. Prioritise broad target-year coverage over a few isolated examples; do not substitute realised target-year grants.

Only after these checks should the existing small-model comparison be rerun on a declared common sample, with unchanged forward-validation rules and all preprocessing confined to training folds. A claim of improved prediction requires held-out performance against persistence; no such claim is made by this audit.

All earlier data and outputs remain unchanged. The V2 panel is a separate candidate research artefact, not a replacement certified training set.
''')
# More precise units for inherited numeric fields and identifiers.
d=pd.read_csv(O/'variable_dictionary.csv').fillna('')
units={'council_key':'stable text identifier','council_name':'display text','year_start':'calendar year of financial-year start','financial_year':'financial-year label','reporting_months':'months','population':'persons','area_km2':'square kilometres','maintenance_difference_pp':'percentage points','fesm_burned_pct_raw':'percent; inherited source definition','source_excel_row':'1-based Excel row','fesm_excel_total_row':'1-based Excel row'}
for v in d.variable:
 if v.endswith('_ha') or v=='fesm_min_fire_size_ha_exclusive':units[v]='hectares'
 if v.endswith('_count'):units[v]='event/record count; see inherited source definition'
 if v.endswith('_flag') or v in ['historical_extension','maintenance_conflict','candidate_only','strict_asof_predictor_panel','verified_zero_all_disaster_exposure','direct_infrastructure_damage_documented','debt_service_cover_requires_review']:units[v]='boolean; missing is unknown'
for v,u in units.items():d.loc[d.variable==v,'unit']=u
d.to_csv(O/'variable_dictionary.csv',index=False)
# Unified inventory without copying or changing prior cached data.
inv=[]
for mf in [ROOT/'outputs/operating_ratio_audit/source_downloads.json',*O.glob('source_manifest*.json')]:
 for r in json.loads(mf.read_text()):
  z=dict(r);z['manifest_file']=str(mf.relative_to(ROOT));inv.append(z)
(O/'source_inventory.json').write_text(json.dumps(inv,indent=2))
# Save exact rebuild scripts inside the new output area.
for src,name in [('/private/tmp/build_panel_v2.py','build_panel_v2.py'),('/private/tmp/write_v2_reports.py','write_v2_reports.py')]:
 if Path(src).exists() and Path(src).resolve()!=(O/name).resolve():shutil.copyfile(src,O/name)
frozen=json.loads((O/'frozen_before.json').read_text());assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in frozen.items())
print('Reports written; all',len(frozen),'prior files unchanged.')
