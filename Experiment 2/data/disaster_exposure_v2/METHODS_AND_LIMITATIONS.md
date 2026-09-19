# Methods and limitations

## 1. Fixed population and reference years

Membership is inherited exactly from `../fiscal_panel_v2/council_selection.csv`: 103 continuing councils, with stable `council_key`. No predecessor councils are added to a merged entity. `Nambucca` maps to the existing key `nambuccavalley`. Explicit spelling/short-name aliases include Bega → Bega Valley, Moree → Moree Plains, Port Macquarie → Port Macquarie-Hastings, Eurobodala → Eurobodalla and Sellharbour → Shellharbour. Raw names remain in the ledger; every non-agricultural table name either matches the fixed subset or an explicitly reviewed excluded council.

A row is one council and one July–June year. Disaster declarations are assigned to the financial year containing the reported **onset**, including events printed in a later annual report. This measures new event onsets, not ongoing exposure or recovery. Exact dates are not invented where only a month is stated. `onset_date_lower_bound` and `onset_date_upper_bound` bracket uncertainty; known ranges have a separate reported end date. Open-ended events remain flagged by date precision. No complete duration/carryover inventory is claimed.

The 824 original exposure rows for 2017–18 onward are copied unchanged for the selected councils into `original_exposure_snapshot_2017_2024.csv`. Existing quality flags remain there. The combined candidate preserves original shared measures and adds explicit provenance; it does not silently recertify their completeness or publication timing.

## 2. Historical fire mapping

Primary inputs are the NSW Government SEED **statewide** historical wildfire mosaics, not the geographically restricted historical NPWS products. [2012–13 catalogue](https://datasets.seed.nsw.gov.au/dataset/historical-fire-extent-and-severity-mapping-fesm-statewide-201213) and [2016–17 catalogue](https://datasets.seed.nsw.gov.au/dataset/fire-extent-and-severity-mapping-fesm-2016-2017) describe the input scope. Exact resource URLs and hashes are in `source_register.csv`.

For all five extension years:

1. Use the wildfire package only; do not combine hazard-reduction burns.
2. Transform the fixed ABS 2023 LGA polygons to EPSG:3308 and match the 103 stable keys.
3. Assign each raster pixel by its centre. Count classes 2–5 as burned and 4–5 as high/extreme. Sum unique mosaic pixels rather than overlapping fire perimeters.
4. Multiply pixel counts by `abs(pixel_width × pixel_height) / 10,000`. Actual dimensions are close to, but not exactly, 30 metres. Areas are projected-grid approximations, not surveyed land areas.
5. Divide mapped hectares by the **same polygon's area** to obtain percentage. Do not use a changing population, a fiscal workbook area or a rounded reported percentage as the denominator.

The [FESMv3 factsheet](https://datasets.seed.nsw.gov.au/dataset/eeaf2006-db96-4218-a124-43b19cd15765/resource/43c71151-d790-423a-8436-457036c470cb/download/fireextentandseveritymapping_fesmv3_factsheet_december2020.docx.pdf), PDF p2, defines 0 as unburnt, 1 as reserved, and 2–5 as low/moderate/high/extreme. The global raster audit found no class-1 pixels in these five products. Class-0 counts are diagnostic only: they are **not** labelled area inside an independently verified fire perimeter. NoData 255 is never relabelled unburnt. A zero is supported only as no class-2–5 pixel in this published statewide inventory, not comprehensive physical absence. The 2016 raster bounding box differs from a few polygon edges by tiny slivers; all positive/zero results independently agree with the published council table.

`historical_fire_zonal_statistics.csv` records source members, actual pixel dimensions, methods and extra class summaries. `raster_audit.json` records global and selected-council class counts. These products map vegetation effects; agricultural/grassland burning, small fires and infrastructure impacts are not exhaustively measured.

## 3. Area-unit discrepancy and measurement breaks

The 2016–17 published workbook's labelled hectare totals fail an independent area/percentage check. Across its 49 positive selected councils, the raster/workbook hectare ratio has median 8.993584 and range about 8.970–9.007. This is consistent with applying a 10-metre-cell area to approximately 30-metre pixels, with small boundary/rounding differences. **That explanation is an inference, not a verified statement about the publisher's code.** Direct raster extraction supplies the candidate values. The untouched downloaded workbook, every source cell and a council-level reconciliation remain available for inspection. No source workbook or original panel was corrected in place.

The [May 2022 report](https://www.environment.nsw.gov.au/sites/default/files/2025-01/fire-extent-severity-mapping-2020-21-2016-17-220206.pdf), Appendix A, explicitly assigns Landsat to 2016–17 and earlier and Sentinel 2 to 2017–18 onward. This year-specific evidence overrides the generic historical-catalogue sentence implying Sentinel begins in 2016–17. Historical pixels are approximately 30 m; later Sentinel pixels are approximately 10 m. Sensor/algorithm differences can alter measured burn and severity. The minimum-fire threshold and broader scope also change in later original years; retain the original row flags and thresholds.

All five added years use ABS2023 geometry, avoiding a changing denominator within the extension. Continuing legal identity is not proof of identical historical polygons. `boundary_sensitivity.csv` compares ABS2015 with ABS2023: maximum relative symmetric difference is about 1.17%, and this includes coastline/generalisation changes. It is a geometry diagnostic, not cadastral certification or a re-extraction sensitivity test. The original later-year workbook boundary vintage has not been revalidated.

## 4. Declaration reconstruction and zeros

The **Ministry for Police & Emergency Services Annual Report 2012–13**, PDF pp23–24 (printed pp21–22), supplies 29 listed events and 181 council–event links across NSW. Parsing reproduces those source records before subset selection: 23 bushfire, four explicitly flood-labelled and two other events. A zero means no new event in **that complete published list**. It does not guarantee no later declaration extension, no ongoing prior-year event or no physical disaster.

The **Rural Assistance Authority annual reports** supply later council lists: 2013–14 PDF pp10–11; 2014–15 pp14–15; 2015–16 pp15–16; 2016–17 pp12–13. All accepted sources and page locators appear in the event ledger. We extracted 111 source event records in total; excluded 24 agricultural-only records and one corroborating duplicate of the June 2013 MPES event, leaving 86 event entries for the five historical years. Agricultural-only assistance has a different scope and is retained as excluded evidence, not pooled with the primary measures.

Reports include some prior-year onsets. They are reassigned to their onset year, not counted in report year. The 2017–18 RAA report was additionally checked for late 2016–17 rows; none appeared in its event tables. An out-of-period date `21/12/2014` in the 2013–14 agricultural table is preserved and flagged, not silently repaired. Grant-recipient subsets beneath an event are not extra events. Same-day entries naming disjoint regions are retained as separate source entries; without AGRNs they cannot be claimed to represent independent meteorological events.

Only explicit flood/flooding labels enter the flood measure. Storm-only, severe-weather and tornado records remain other hazards; some may physically involve flooding, which cannot be inferred from their title alone. Declarations measure administrative assistance eligibility, not inundation, damage, expenditure or event severity. Absence from the later assistance-oriented lists cannot certify absence from the full declaration register: hence unknown cells and lower-bound observed counts. This deliberate asymmetry prevents fabricated control observations.

The [national dataset](https://data.gov.au/data/dataset/drfa-activation-history-by-lga) was checked against its downloaded contents. The retrieved current file begins on 8 September 2017, despite broader catalogue coverage claims. Older resource URLs returned failures, and current NSW year pages did not yield the missing historical registers. A successful download of an archive viewer or redirected homepage was not mistaken for a recovered table. Failures are retained in the source-access audit.

## 5. Timing and future use

Reference year, event onset, declaration announcement, report publication and download date are different dates. The 2012–16 fire-catalogue records were created in February 2025; the 2016–17 catalogue in June 2022 and its report in May 2022. These retrieved vintages do not certify information available at the historical forecast cutoff. Catalogue creation is evidence about the current product, not proof of the first-ever availability of every underlying fire observation.

The temporal audit uses the existing design: fiscal characteristics from t−1, exposure in t, and outcome in t+1; the illustrative forecast cutoff is July 1 at the start of t+1. Declaration announcement and revision dates were not verified, so an event's earlier onset alone cannot certify an ex-ante predictor. `ex_ante_certified=False` means certification has **not** been achieved, not that every declaration was necessarily unknown then. Original later-year availability is expressly unreviewed, rather than implicitly approved.

This candidate panel adds retrospective fire information and documented declaration positives. It does not supply a complete, publication-dated historical flood/declaration panel. **NO-GO for treating the extension as an immediately ready, historically ex-ante forecasting dataset.** A later model rerun would need either verified publication vintages and declaration completeness, or an explicitly retrospective research question with these limitations and the existing fiscal-definition restrictions. No claim about improved forecast accuracy follows from this data extension, and no model has been fitted here.
