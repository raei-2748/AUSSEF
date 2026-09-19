# Council identity and reporting-period audit

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
