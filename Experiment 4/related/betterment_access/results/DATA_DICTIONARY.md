# Data dictionary and interpretation rules

## Shared fields

`source_id` links to `source_provenance.csv`; `source_url` is the official document URL; `source_locator` identifies page/table/row (PDF and printed pages may differ). `accessed_at` is retrieval time, not publication. `document_or_version_date` has an explicit `date_basis`; an audit/reporting-period date is not a public release date. `confidence`/`label_confidence` concern the specific reported observation, not missing eligibility or round identity.

`council_key` is a deterministic local QLD name key, not an ABS code. Only the explicit Gold Coast naming alias is used; no fuzzy matching and no NSW joins. Council keys must be reconciled to official IDs if the registry is obtained. The observed council set is not certified as the full applicant universe.

Blank numeric cells mean unknown/not recovered; blank text means no information recovered. Zero is preserved only when explicitly measured. `usable_eligible_negative=False` means an evidence observation cannot be used as a control; it is not an approval label. No binary training outcome has been created.

## Award list

`public_record_id` identifies a source-table row only. `application_id` and `project_id` are unknown official IDs. `funding_stream` is D/E, and `applicant_type` distinguishes council and state agency. `project_asset_label` preserves source wording. `repeated_label` and `same_label_row_count` flag matching stream/applicant/asset labels without asserting duplication. `status=APPROVED_REPORTED` comes from the official successful list. Eligibility acceptance is inferred from inclusion, not a recovered eligibility file.

`submission_date` and `decision_date` allow coarse strings such as `2022-12` and `early 2023`; do not parse them as exact dates. `amount_requested_aud`/`amount_approved_aud` would be dollars but are unrecovered in the award list. `asset_type` remains unverified rather than inferred from a road name. Supplemental source IDs link to the evidence ledger and provenance.

## Evidence observations

`evidence_id` is an observation ID, not a project ID. `round_scope`, `eligibility_status`, `unit_resolution` and `interpretation` explain inclusion/exclusion. `evidence_date` is the report's observation date, not necessarily when an application was lodged or adjudicated. Monetary fields require `amount_basis`: a REPA request, historical works total or project estimate is not a verified 2022 Betterment request. Do not pool these amounts. Repeated Boulia and Scenic Rim observations must not inflate the number of cases.

## Capacity values (long format)

Each row is a council–feature–measurement observation. `value` must be read with `unit`, `scope`, `measurement_date`, `publication_date`, `audit_date`, `timing_status` and `quality_note`.

| Feature | Definition / unit | Limitation |
|---|---|---|
| operating_surplus_pct | Net operating result / operating revenue excluding capital, % | QAO current audited period, mostly 2020–21; two councils 2019–20 |
| grant_share_5yr_pct | QAO five-year average grant share of total revenue, % | Not current operating-grant share or complement of own-source ratio; older-audit averaging window needs confirmation |
| net_financial_liabilities_pct | (Total liabilities − current assets) / operating revenue, % | Not simple debt; Brisbane concession accounting flagged |
| cash_and_equivalents | AUD thousands | Ipswich only; restricted money included |
| borrowings | AUD thousands | Gross borrowings, not debt-service capacity |
| property_plant_equipment; total_assets | AUD thousands | Book values; council scope, not group |
| rates_levies_charges; fees_charges; sales_revenue; interest_investment_revenue | AUD thousands | Own-source components; no complete harmonised ratio |
| grants_contributions_total | AUD thousands | Includes capital and contributed assets |
| employee_expenses; finance_costs | AUD thousands | Expenses, not FTE/debt-service ratio; refinancing affects finance costs |
| headcount | People at 30 June 2021 | Not FTE or grant-team staff |
| population_council_reported | People at June 2021 | Ipswich council estimate; not harmonised ABS panel |

The 2021 measurement baseline predates the covered disasters. Public availability is a separate test. QAO publication is 11 May 2022; Ipswich audit signature is 12 October 2021 and is not a certified publication date. The temporal audit tests known submission months conservatively against their earliest day; all unknown dates remain uncertified.

## Feasibility and need tables

`complete_two_outcome_coverage=False` means no comparable eligible approved/unsuccessful block has been recovered; it does not assign a zero project score. Need measures are kept separate. Assessor recommendations, final awards, post-approval design changes and completed-project benefits must not enter approval predictors. Counts in the reconciliation table have different units and cannot be combined to create an approval rate.
