# Fiscal-capacity candidate alignment

Eight recovered council-years have been audited. Seven have inherited fiscal records at both one- and two-year lags; Snowy Valleys has neither in the continuing-council panel. A new typed capacity_candidates table stores 128 council-budget-year/fiscal-year/variable candidates, 112 with values and 16 explicit missing values. Fiscal_annual is preserved unchanged. No values were imputed or borrowed from another council.

Variables: operating performance (percent), cash cover (months), unrestricted current ratio (ratio), own-source revenue and grant shares (percent), debt-service cover (ratio), population (persons), and road length (km). Inclusion reasons and inherited definition flags accompany each observation. These are candidate covariates, not approved modelling inputs. Grant share and own-source share must not be treated as exact complements without checking definitions.

The one-year lag is not automatically ex ante. Ballina FY2020/21 has verified original adoption on 25June2020, but its FY2019/20 fiscal period ends 30June2020. Those annual figures cannot represent information available at that adoption date. This audit marks all eight such candidates not_pre_adoption_period. The two-year lag ends earlier, but its public availability is still unverified. Budget adoption timing is only known for two Ballina projects; the council-year date is the earliest recovered original decision, not a claim about every project.

Pre-adoption and pre-disaster capacity are different estimands. A fiscal year ending after adoption could still precede a later disaster, but may include earlier disasters or revisions. Neither annual period ordering nor a fixed lag proves publication availability. No candidate is certified model eligible. Event-specific measurement/publication cutoffs and overlapping-disaster checks remain required.

Operating ratio definitions cross the 2019/20 accounting regime change. Cash cover retains the detailed-vintage caveat. Debt review flags remain visible. Staffing and asset-specific scale are not supplied by this inherited block. Snowy Valleys requires its own audited records; predecessor values must not be silently joined.

Next evidence: recover contemporaneous audited financial statements and dated council presentation/adoption notices; verify each ratio against its source page and definitions; then link availability to each actual disaster onset and original budget decision. An audit-signature date alone must not be relabelled as public release. Search remains incomplete.

Reproduction: run audit_capacity_alignment.py after screen_disaster_overlap.py. SQLite integrity, foreign keys, finite numeric values and zero eligibility flags were checked. No model fitted.

## Public availability evidence recovered

Ballina resolution 261120/12 (26November2020 minutes, PDF7) adopts FY2019/20 annual financial and auditor reports as publicly exhibited. The agenda (PDF94-95, printed90-91) confirms the advertising process was completed and no submissions were received. These establish availability by 26November2020, not the exact first-publication date. This is before the register's regional December10 disaster start, but after June25 original-budget adoption.

Stored in fiscal_availability_evidence, separate from publication_date. No inherited numerical ratio has yet been reconciled to the report itself, so numeric_value_match_verified remains0 and capacity eligibility remains0. Thus report timing is partly resolved while individual-value vintage is still open. Reproduction adds add_capacity_availability.py after audit_capacity_alignment.py.

## Direct numeric validation: material discrepancies

Annual report FY2019/20 PDF267, financial statements page89, Note28(a), visually verified: operating performance2.76% versus inherited3.39%; own-source revenue69.43% versus69.59%; debt service cover2.54 versus2.59. Current ratio2.59 and cash cover9.99months match. fiscal_value_audit preserves all five pairs; the three conflicting capacity candidates are explicitly flagged. No inherited fiscal value was overwritten. Definition or version differences remain unresolved rather than assumed transcription errors.

The same note says its 2019 comparative ratios were restated for prior-period errors. Therefore even matching earlier-year values may represent a later restatement rather than the information available at the earlier event date. The November2020 presentation establishes report-year availability but does not prove the currently hosted annual-report PDF is byte-identical to the originally exhibited version. Individual historical vintage certification remains open.

Reproduction adds audit_ballina_fiscal_values.py after add_capacity_availability.py. All modelling eligibility flags remain zero. Priority: reconcile the original October2020 draft/approved statements and OLG definitions, retain original and restated vintages separately, and repeat numeric verification for other councils before using capacity interactions.

## Contemporaneous statement corroboration

The October22,2020 agenda attachment (draft annual financial statements PDF98, printed89, Note28a) independently reproduces all five checked FY2019/20 ratios in the annual report:2.76%,69.43%,2.59,2.54,9.99months. Page images were compared. These ratios did not change between these two recovered council versions. This narrows, but does not resolve, the discrepancy with the inherited panel: investigate OLG adjustments/definitions or extraction lineage rather than assume annual-report revision caused it.

The five fiscal_value_audit rows now include corroborating_source_id and page. The original annual-report values and inherited values remain separate. The existing audit_ballina_fiscal_values.py reproduction stage incorporates this corroboration; no extra pipeline stage is required. Overall capacity/model eligibility remains unchanged because cross-council harmonisation, event-specific alignment and other project gates remain open.
