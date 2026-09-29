# A6. Queensland, Tasmania, Western Australia: council finance (FP pillar, X finance ratios) and hazard layers

Scoping only. Nothing downloaded (no xlsx/xls/csv/zip/gdb/shp/geojson/gpkg/raster/parquet). Sizes come from HEAD requests, or from the publisher's own catalogue metadata where HEAD was refused (stated each time). Date of scoping: 2026-09-29.

Legend used below
- **[V]** = I opened the page/document/API and the source states it.
- **[I]** = my inference from what I opened (reason given).
- **[U]** = could not verify (reason given).
- Where sources disagree, each is listed.

Working notes on method and blockers (useful for whoever downloads later)
- Queensland Government department sites (`dlgwv.qld.gov.au`, `statedevelopment.qld.gov.au`, `localgovernment.qld.gov.au`) return HTTP 403 to curl and to the WebFetch tool. They do load in a real browser session, and same-origin HEAD requests from that browser worked, which is how the Queensland file sizes were obtained. Navigating a browser tab straight to one of their file URLs triggers a "save file" prompt (this happened once with a PDF; nothing was saved).
- The WebSearch budget for the session ran out mid-task (200 of 200 used, shared). Items I could not verify for that reason are marked [U].
- The Audit Office NSW appendix (opened) was used for the NSW ratio definitions. The NSW OLG Code of Accounting Practice PDFs are behind bot protection and could not be opened, so NSW definitions for the infrastructure backlog ratio and the buildings and infrastructure renewals ratio come only from a search-result summary [U].

---------------------------------------------------------------------------------------------------

## 1. QUEENSLAND

### 1A. Council finance sources

| # | Source | Publisher | Financial years | Statements / ratios | Councils | Format, URL | Licence | Size |
|---|---|---|---|---|---|---|---|---|
| Q1 | **Queensland local government comparative information** (annual, one release per year; "Financial input" + "Financial PIs (1)" + "Financial PIs (2)" workbooks, plus rates, roads, waste, water, personnel) | Dept of Local Government, Water and Volunteers (earlier names: DLGPSR, DLGRMA, DSDILGP). Source is the council "Consolidated Data Collection", completed each November [V] | 2002-03 to 2024-25 (23 releases listed; page last updated 17 Apr 2026) [V]. 2002-03 to 2005-06 are PDFs, 2006-07 to 2012-13 are XLS, 2013-14 to 2024-25 are XLSX [V]. Each 2005-06-vintage ratio table shows a 5-year history (2001-02 to 2005-06) [V] | **Both**: "Financial input" = raw inputs (revenue, expenditure, borrowing, asset management data per the department's description [V]); "Financial PIs" = a fixed set of ratios. The F1-F10 ratio list is verified for the 2005-06 vintage only (see 1B). Field list of the 2013+ "Financial input" workbook not verified [U] (workbook not opened) | All reporting councils. From 2013-14 all councils incl. Indigenous and the four de-amalgamated councils; for earlier years Indigenous councils are absent except Aurukun and Mornington [V, department page] | XLSX/XLS. Index page: https://www.dlgwv.qld.gov.au/local-government/for-councils/resources/local-government-comparative-reports (same content also under localgovernment.qld.gov.au and statedevelopment.qld.gov.au). File paths are in the Appendix at the end | Not stated on the page; a "Copyright and glossary" workbook accompanies each release [V, unopened]. Licence for the workbooks therefore [U] | "Financial input" 25,956 B (2013-14) to 40,520 B (2024-25); "Financial PIs (1)" 24,793-33,160 B; XLS versions 35-59 KB (HEAD, see Appendix). Pre-2013 combined XLS files are 4-6 MB (page labels: 2009-10 4 MB, 2010-11 4 MB, 2006-07 6 MB) [V] |
| Q2 | **Queensland local government comparative information report** (open-data CSV extract) | Local Government, Water and Volunteers, on data.qld.gov.au | Description states 2010-11 to 2016-17 [V]. Resource last updated 25 Nov 2022; package modified 12 Jun 2025 [V] | "Financial Inputs" CSV (inputs, not ratios). Explanatory notes name items such as total operating expenses before interest, expenses before interest excluding depreciation, and councillor remuneration; they say the first two excluded unfunded depreciation before 2013-14 [V] | As per Q1 (Indigenous councils first in 2013-14; 8 councils affected by 2014 de-amalgamation) [V] | CSV. https://www.data.qld.gov.au/dataset/queensland-local-government-comparative-information-report ; file https://www.data.qld.gov.au/dataset/c7c0c31e-a844-480d-bfbe-4b689179a5cf/resource/2dd25c9b-cc5b-4c81-876f-97d277e88889/download/qld-local-government-comparative-information-report-cdc-financial-inputs.csv . Not loaded in the CKAN datastore, so column names unverified [U] | CC BY 4.0 [V] | 82,305 B (HEAD; catalogue says 79 KiB) |
| Q3 | **QAO "Local government" audit-results reports**, appendix tables of council-level sustainability ratios | Queensland Audit Office | Reports found: 2013-14 (Report 16: 2014-15), 2016-17, 2018-19 (Report 13: 2019-20), 2020, 2021, 2022 (Report 15: 2022-23), 2023 (Report 8: 2023-24), 2024 (Report 13: 2024-25), 2025 (Report 12: 2025-26) [V titles]. Council-by-council ratio tables opened for 2018-19 (Appendix I, current-year value + 5-year average) and 2024 (Figure J3, 2023-24 + 5-year average) [V]. The 2022 report page says it gives aggregates and named at-risk councils, not a per-council ratio download [V, via page summary] | **Ratios only** (3 ratios up to 2022-23; 6 audited ratios from 2023-24; see 1B) | 77 councils [V] | PDF appendices. 2024 report: https://www.qao.qld.gov.au/reports-resources/reports-parliament/local-government-2024 ; Appendix J PDF https://www.qao.qld.gov.au/sites/default/files/2025-04/Local%20government%202024%20(Report%2013%20%E2%80%93%202024%E2%80%9325)%20%E2%80%93%20Appendix%20J.pdf (706.85 KB per page); 2018-19 report https://www.parliament.qld.gov.au/Work-of-the-Assembly/Tabled-Papers/docs/5620t302/5620t302.pdf (94 pp) | Not stated [U] | 706.85 KB (App J) |
| Q4 | **QAO interactive "Local government dashboard"** | Queensland Audit Office | Dashboards listed for 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 [V]; each shows one audited financial year (2024 = 1 Jul 2023 to 30 Jun 2024) [V] | Revenue, expenses, operating costs, assets, liabilities, sustainability indicators [V] | All councils | Interactive web tool, e.g. https://www.qao.qld.gov.au/2024-local-government-dashboard . No download option mentioned [V] | [U] | n/a |
| Q5 | **Council annual reports / audited financial statements** (each council) | 77 councils | Every year; includes the "current-year financial sustainability statement" | Full statements + ratios | 77 | PDF per council-year; not aggregated [I] | Varies | n/a |
| Q6 | QTC (Queensland Treasury Corporation) council credit reviews | QTC | none found | none | none | Only found QTC advising on the 2012-13 de-amalgamation impacts; no public council-level review series located. One search only before search budget ended [U] | n/a | n/a |
| Q7 | Local Government National Report (Dept of Infrastructure) | Commonwealth | 2014-15 to 2023-24 editions listed [V] | State-level finance tables (revenue by source, expenditure by purpose, assets, liabilities by jurisdiction; Tables 2-5) and Financial Assistance Grant entitlements per council (Tables 43-48). **No council-level financial statements or ratios** [V, 2023-24 edition contents read] | n/a | PDF 8.73 MB (2023-24) [V]; https://www.infrastructure.gov.au/territories-regions-cities/local-government/publications/national-reports | CC BY 4.0 (report front matter) [V] | 8.73 MB per page |

### 1B. Ratio comparability (NSW measure -> Queensland)

| NSW measure | Queensland | Notes / definitional difference |
|---|---|---|
| Cash expense cover (months) | **Close analogue, only from 2023-24**: "unrestricted cash expense cover ratio" = (cash + current investments + available ongoing QTC working-capital facility - external restricted cash) x 12 / (total operating expenditure - depreciation - finance costs). Benchmarks: >2 months (tiers 1-2), >3 (tier 3), >4 (tiers 4-8) [V, QAO 2023 App L and 2024 App J]. Before 2023-24: nothing published as a ratio | NSW numerator is not net of restrictions and the denominator is cash payments (operating + financing), whereas Queensland's denominator is accrual expenses net of depreciation and finance costs; also adds the QTC facility. Cash balances are in each council's balance sheet but I could not confirm they are a stand-alone field in the Financial input workbook [U] |
| Own-source revenue % | **Close analogue**: PI F1 "revenue ratio" = net rates and utility charges income / total operating income [V, 2005-06 vintage]. From 2023-24 a "council-controlled revenue" ratio is reported for context only and is not audited [V]; its formula not opened [U] | F1 counts only rates and utility charges as own-source, so fees and charges are excluded (NSW own-source includes fees and charges) |
| Debt service ratio | **Close analogue**: PI F8 "debt servicing ratio" = (repayment of borrowings and finance leases + borrowing costs) / total operating income [V, 2005-06]. From 2023-24: "leverage ratio" = book value of debt / (operating result + depreciation + finance costs), in times [V] | F8 is the cost-of-debt-service over revenue form; it is not the NSW "debt service cover ratio" (which is a cover multiple). The leverage ratio is the inverse-type measure |
| Operating ratio | **Same measure**: operating surplus ratio = net operating result / total operating revenue, capital items excluded [V, QAO 2018-19 Fig I1]. Older PI F2 "operating efficiency ratio" = total operating income / total operating expenses [V, 2005-06] | **Sources disagree on the denominator**: QAO 2018-19 (Fig I1) and QAO 2024 (Fig J2) use operating revenue; QAO 2023 (Fig L2) prints "operating expenses". Treat as an error in the 2023 appendix [I]. Also "operating cash ratio" added from 2023-24, and its formula differs between the 2023 and 2024 appendices (2024 adds finance costs to the numerator) |
| Infrastructure backlog ratio | **Nothing**. Nearest: asset consumption ratio (written-down / gross replacement cost of depreciable infrastructure assets; >60%), audited from 2023-24 [V] | Consumption is a condition measure of the stock, not an estimated cost to reach a satisfactory standard |
| Unrestricted current ratio | **Close analogue**: PI F3 "working capital ratio" = (current assets - constrained works reserve - unspent loan monies) / current liabilities [V, 2005-06] | Removes fewer restrictions than NSW's "less all external restrictions" / "less specific-purpose liabilities". Not in the 2023-24 audited set |
| Buildings and infrastructure renewals ratio | **Close analogue**: asset sustainability ratio = capital expenses on replacement of assets (renewals) / depreciation expenses; benchmark >90% (2018-19) [V]. Since 2023-24 the denominator is depreciation on infrastructure assets and the target is tiered (>50% to >90%) [V]. Also PI F5 "capital expenditure ratio" (additions / depreciation) in the older series [V] | Concept identical; NSW restricts to buildings and infrastructure |
| Net financial liabilities ratio (extra) | Yes: (total liabilities - current assets) / total operating revenue; target <=60%; used up to 2022-23 [V] | Not one of the NSW list but is the third of Queensland's three legacy ratios |
| Services share of spending (expenditure by function) | **Not established.** The comparative reports cover selected services (roads, waste, water, sewerage, parks, personnel) [V] but I found no complete function split. Council statements are by nature (employee, materials, depreciation, finance costs) [I, not opened] | Crowd-out needs a complete function split; probably not available for Queensland without hand-extraction [I] |
| Cash and investment balances (to compute cash cover myself) | Council balance sheets have them (Q5). Inside Q1 "Financial input": unknown [U]. PI F10 "net debt per capita" nets cash against borrowings, so cash is an input in the collection [V], but it is not published stand-alone as far as I could see [U] | For fire years 2018-19 and 2019-20, computing cash cover means hand-extracting 77 x 3 balance sheets, unless the Financial input workbook carries it [U] |

Ratio-set breaks to plan for [V]: three legacy ratios (operating surplus, net financial liabilities, asset sustainability) with targets 0-10%, <=60%, >90% up to 2022-23 (QAO 2018-19 Fig I1). From 2023-24 a nine-ratio set (six audited: operating surplus, operating cash, unrestricted cash expense cover, asset sustainability, asset consumption, leverage; three contextual: council-controlled revenue, population growth, asset renewal funding), with tiers by remoteness and population (Guideline 2024 v1, in force for 2023-24 onwards).

### 1C. Year coverage

| Era | Queensland availability |
|---|---|
| FY2007-08 to 2012-13 | Comparative information exists for every year (2007-08 "Continuing councils" Vol 2 A/B; 2008-09 shows Vol 1 Regional councils and Vol 2 Continuing councils [I from page order]; 2009-10, 2010-11 large XLS; 2011-12 and 2012-13 with Financial input + PIs XLS). Indigenous councils largely absent. 2008 amalgamation is a series break (see 1D). No council-level QAO ratio tables opened for this era [U] |
| FY2013-14 to 2018-19 | Comparative information every year, XLSX. 2013-14 is a partial-year year for 8 councils (see 1D). QAO 2018-19 report gives council ratios with 5-year averages (so 2014-15 to 2018-19 annual values exist in each council's statements) [I] |
| FY2018-19 to 2023-24 | Comparative information every year (file names listed in Appendix). QAO dashboards for 2018 onward. 2023-24 brings the new nine-ratio set (definition break) |

Candidate Queensland fire years (fire year, prior year, year after all needed):
- **2018-19**: needs 2017-18, 2018-19, 2019-20. Comparative information Financial input + Financial PIs exist for all three [V]. Legacy 3-ratio set applies throughout. Buildable.
- **2019-20**: needs 2018-19, 2019-20, 2020-21. All exist [V]. Legacy 3-ratio set applies throughout. Buildable.
- Earliest full triple with all councils and no partial-year problem: fire year 2014-15 (prior year 2013-14 is partial for the eight affected councils and is the first year for Indigenous councils) [I]. Earlier fire years would use continuing councils only.
- Mapping of file IDs to release years for 2019-20 onward is my reading of link order and of the pairing with next-year rate files [I]; 2018-19 and earlier are labelled in the file names.

### 1D. Boundary / name changes

- 2008 amalgamations: series break between 2007-08 and 2008-09 (the department published separate "Continuing councils" and "Regional councils" volumes) [V page]. The count "157 councils to 73" is widely quoted but I did not open a permitted source for it [U].
- De-amalgamation from 1 Jan 2014: Douglas, Livingstone, Mareeba and Noosa were re-created. For 2013-14 the four continuing shires supplied data for 1 Jan to 30 Jun 2014 only; Cairns, Rockhampton, Sunshine Coast and Tablelands supplied 2013-14 excluding the four new councils for the half-year [V, dataset explanatory notes]. Result: 77 councils (QAO reports 77) [V].
- Indigenous councils (except Aurukun and Mornington) first appear in the collection in 2013-14 [V].
- Name variants seen: "Council of the City of Gold Coast" in QAO tables [V]. For 2017-18 to 2020-21 (fire years 2018-19 and 2019-20) no boundary change exists, so no breaks inside the needed triples [I].

### 1E. Hazard layer (Queensland)

| Item | Finding |
|---|---|
| Layer | "Bushfire prone area - Queensland series" (state-wide Bushfire Hazard Area / Bushfire Prone Area) [V] |
| Custodian | Queensland Fire Department (renamed from QFES 1 Jul 2024); owner listed as Rural Fire Service Queensland; built by CSIRO with QFES [V, qldspatial metadata] |
| First designation / versions | Methodology written for the State Planning Policy that took effect 2 Dec 2013 (CSIRO report Jan 2014, replaces the SPP 1/03 method) [V]. Metadata: temporal extent 2014-07-30, publication 2015-07-15, update frequency "as needed"; inputs span 1986-2014, vegetation 1988-2012 [V]. data.qld.gov.au record created 2015-03-25; the regional resources are dated 2020-11-12 [V]. **One vintage; no evidence of later re-runs** [I from metadata; not confirmed]. It pre-dates every candidate Queensland fire year (2018-19, 2019-20), so no historical version is needed |
| Category structure | Three potential bushfire intensity classes (Very High, High, Medium, from a fire-line-intensity model = fuel load x fire-weather severity x maximum slope, 25 m raster) plus a 100 m Potential Impact Buffer around the three classes; also mapped: Grassfire Prone Areas and Low Hazard Areas [V]. Reliability judged 85% on average by expert appraisal [V] |
| Fit to NSW BFPL Cat 1/2/3 | Good. Graded classes let you compute a council share in Very High + High vs Medium vs buffer, the same shape of input as "Cat 1 and Cat 2 shares". Difference: Queensland classes are modelled fire-line intensity, NSW categories are vegetation-type classes. NSW category definitions here are background knowledge, not re-verified [U] |
| Format | Shapefiles by region (12 regions) [V]. Smoothed vector by LGA and raster on request [V] |
| Access | data.qld.gov.au page https://www.data.qld.gov.au/dataset/bushfire-prone-area-queensland-series ; qldspatial catalogue record https://qldspatial.information.qld.gov.au/catalogueadmin/rest/document?id=%7B676500B2-5468-4626-B1C2-02A92501ACC4%7D . **Sources disagree** on access: the CKAN abstract says to email for a copy; the qldspatial metadata says unsmoothed vector is downloadable. Contact in the metadata: brc@fire.qld.gov.au |
| Size | Sum of the 12 regional resources listed in the catalogue = 1,637 MiB (about 1.6 GiB): SEQ 423, Darling Downs 188, N-W 159, Central Qld 159, S Gulf 142, C West 112, Cape York 108, Mackay-Isaac-Whitsunday 106, S West 96, Far North 77, Wide Bay Burnett 37, North Qld 30 MiB (publisher's figures; HEAD not possible because there is no direct file URL) |
| Licence | CC BY 4.0 [V] |

---------------------------------------------------------------------------------------------------

## 2. TASMANIA

### 2A. Council finance sources

| # | Source | Publisher | Financial years | Statements / ratios | Councils | Format, URL | Licence | Size |
|---|---|---|---|---|---|---|---|---|
| T1 | **Tasmanian Local Government Consolidated Data Collection (CDC)** (annual council returns; open data on the LIST) | Office of Local Government (Dept of Premier and Cabinet, now shown on justice.tas.gov.au); custodian "Director of Local Government" [V] | 2000-01 to the present. Two statewide repositories: "2000 to 2015" and "2015 to 2025" [V] | Raw returns covering finances, infrastructure, roads, bridges, planning, HR, disability access [V]. Financial section externally validated; from 2017-18 the financial data is audited council data consistent with the Auditor-General's reports [V, LIST/DPAC text]. The dashboards draw **operating and capital expenditure by function** and rate/grant splits from the CDC [V]. Exact column list of the returns not opened (files not downloaded) [U] | All 29 councils, every year since 2000 [V] | Excel workbooks in zips. https://listdata.thelist.tas.gov.au/opendata/ (CDC accordion). Files: `.../opendata/data/LGA_CDC_Data_Repository_2000-2015.zip` and `.../opendata/data/LGA_CDC_Data_Repository_2015-2025.zip`; also one zip per council (`LGA_CDCS_<COUNCIL>.zip`). Metadata https://www.thelist.tas.gov.au/app/content/data/geo-meta-data-record?detailRecordUID=d8e9d3f1-25a2-4db7-a8d0-c88984e9956a | CC BY 3.0 Australia [V] | 16,835,035 B (2000-2015 zip, last modified 17 Jan 2018) and 13,432,951 B (2015-2025 zip, last modified 10 Feb 2026) (HEAD) |
| T2 | **Tasmanian council data dashboards** (Dashboard 1 "council profile", Dashboard 2 "financial trends"; Power BI) | Future of Local Government Review / Local Government Board; now linked from the Office of Local Government | Dashboard 2 = "10 years"; Dashboard 1 = 5 years [V]. Exact first and last year not stated in the pages I opened [U]. The unrestricted-cash method is stated to apply to all councils in all years since 2013-14 [V] | **Both**. Ratios: underlying surplus ratio, asset consumption, asset renewal funding, asset sustainability, cash expense cover, current ratio, debt service cover, net financial liabilities ratio, own-source revenue coverage [V]. Inputs: total, operating and own-source revenue, rates, grants, fees, employee costs, depreciation, finance costs, unrestricted cash, expenditure by function [V]. Data are from audited statements with Tasmanian Audit Office (TAO) adjustments plus the CDC | 29 | Interactive; data can be exported from visuals ("show as table"/export data) [V]. Definitions PDF https://www.futurelocal.tas.gov.au/wp-content/uploads/2022/08/Dashboard-2.0-Information-Sheet-FoLGR-Final-web.pdf ; https://www.futurelocal.tas.gov.au/council-data/ | Not stated [U] | n/a |
| T3 | **Auditor-General's reports on local government authorities** (council-by-council financial summaries and ratio trends) | Tasmanian Audit Office | Reports found: 2007-08; June and December 2009; 2011-12 (Report 4 of 2012-13, Vol 4 Part II, Nov 2012, 304 pp); 2012-13 (Vol 3 Parts I and II, Dec 2013); 2015-16; 2016-17 (Report 6 of 2017-18); 2017-18; 2018-19; then Vol 2 carries the local government analysis for 2019-20 to 2022-23 and Vol 3 for 2023-24 [V, Office of Local Government page]; a 2024-25 volume set exists (Vol 4 shown on the publications page) but I did not confirm which volume holds local government [U]. 2010-11, 2013-14 and 2014-15 report locations, and council-level ratio pages for 2019-20 onward, not individually confirmed [U] | **Both**: per council a 4-year ratio trend (operating result, net financial liabilities, asset sustainability, asset consumption), balance sheet (incl. cash and financial assets) and cash flow statement (2011-12 volume opened) [V] | 29 councils (2016-17 report: 29 councils, 10 urban with own chapters, 19 rural in a summary) [V] | PDF. e.g. https://audit.tas.gov.au/wp-content/uploads/Volume-4-II.pdf (2011-12); https://audit.tas.gov.au/publication/report-of-the-auditor-general-2013-14/ (2012-13 volumes); https://audit.tas.gov.au/publication/local-government-authorities-2016-17/ (has a "Summary Tables" PDF) | Not stated [U] | 304 pp (2011-12 volume) |
| T4 | State Grants Commission "Financial Assistance Grants Data Tables" | Tasmanian State Grants Commission | 2023-24 edition holds "council revenues 2021-22" (standardised for grant purposes), assessed expenditure requirements, roads, population [V] | Derived grant-model tables, **not** council statements. Confirms the CDC is the base data and that CDC returns go back to 2000-01 [V] | 29 | PDF, 34 pp; https://www.treasury.tas.gov.au/Documents/State%20Grants%20Commission%202023-24%20Financial%20Assistance%20Grants%20Data%20Tables.pdf | [U] | 1.6 MB (fetch note) |
| T5 | Local Government National Report | Commonwealth | as Q7 | State-level only | n/a | as Q7 | CC BY 4.0 | as Q7 |
| T6 | LGAT (Local Government Association of Tasmania) data | LGAT | not checked | [U] | | | | |

### 2B. Ratio comparability (NSW measure -> Tasmania)

| NSW measure | Tasmania | Notes |
|---|---|---|
| Cash expense cover (months) | **Close analogue, published**: cash expense cover ratio = total unrestricted cash / (cash payments to suppliers, employees and financing costs) x 12; benchmark 3-6 months. Unrestricted cash = cash + financial assets - financial assistance grants received in advance - trust funds and deposits - aged-person tenancy bonds (TAO method) [V] | NSW numerator = cash + term deposits (no restriction adjustment); Tasmania nets the listed items. TAO method applied from 2013-14; for 2011-12 and 2012-13 I would compute it from balance sheet + cash flow (both in the TAO PDFs) [I] |
| Own-source revenue % | Dashboards give operating revenue, own-source revenue (= operating revenue less grants), grant revenue and total revenue, so the NSW-form share can be computed [V]. The published "own source revenue coverage ratio" = own-source operating revenue / operating expense (benchmarks 40-60% basic, 60-90% intermediate, >90% advanced) | The published Tasmanian ratio is the coverage form, not the NSW share form (NSW divides by total revenue incl. grants; benchmark >60%) |
| Debt service ratio | **Debt service cover ratio** = annual operating surplus before interest and depreciation / principal and interest (>2 basic, >5 advanced) [V] | Same formula and benchmarks as WA. NSW's DSCR (op result before capital excl. interest and depreciation / principal + borrowing costs; >2 times) is the same idea [V, Audit Office NSW App 9] |
| Operating ratio | **Underlying surplus ratio** = (operating revenue - operating expenses) / operating revenue [V]; mandatory under the Local Government (Management Indicators) Order 2014 [V] | Same concept. TAO adjusts for prepaid financial assistance grants and capital income recognition |
| Infrastructure backlog ratio | **Nothing**. Nearest: asset consumption ratio (depreciated replacement cost / current replacement cost; >60%) and asset renewal funding ratio (planned vs required renewals from long-term plans; 90-100%) [V] | Both are condition or plan-based, not a backlog cost |
| Unrestricted current ratio | Current ratio = current assets / current liabilities (>1) [V] | Not adjusted for restrictions, so it is a weaker analogue |
| Buildings and infrastructure renewals ratio | Asset sustainability ratio = payments for PPE on existing assets / depreciation (benchmark 100%) [V] | Close; all PPE, not only buildings and infrastructure |
| Services share of spending | **Yes**: CDC operating and capital expenditure by function, grouped in the dashboards as Arts and Culture; Community and Regional Development; Environment and Parks; General Administration; Social Support; Sport and Recreation; Transport and Energy; Waste Management [V] | Underlying CDC line items are COFOG-style (e.g. Legislative/Executive/Financial Affairs, Aged Services, Road Bridge Street Infrastructure) [V]. Can be rebuilt to match NSW groupings |
| Cash and investment balances | Yes in TAO PDFs (balance sheet, cash flow per council) [V]; dashboards hold unrestricted cash from 2013-14 [V] | Enough to compute cash cover ourselves |

### 2C. Year coverage

| Fire year | Prior year | Fire year | Year after | Status |
|---|---|---|---|---|
| 2012-13 (Dunalley, Jan 2013) | 2011-12: CDC Vol 1; TAO Vol 4 Pt II (Nov 2012) with 4-year council ratios [V] | 2012-13: CDC Vol 1; TAO Vol 3 Pt I and II (Dec 2013) [V] | 2013-14: CDC Vol 1 (covers to 2015) [V]; TAO 2013-14 volume exists as "Auditor-General's Report on the Financial Statements of State entities 2013-14" [V title, not opened] | **Buildable**. TAO-adjusted unrestricted cash only from 2013-14, so cash cover for 2011-12 and 2012-13 must be self-computed |
| 2015-16 | 2014-15 [V CDC] | 2015-16 [V CDC; TAO 2015-16 report] | 2016-17 [V CDC; TAO 2016-17] | **Buildable** |
| 2018-19 | 2017-18 [V CDC audited; TAO 2017-18] | 2018-19 [V] | 2019-20 [V CDC; TAO Vol 2] | **Buildable**, financial data audited from 2017-18 |

Era view: 2007-08 to 2012-13 covered by CDC (2000-2015) and TAO reports; 2013-14 to 2018-19 covered; 2018-19 to 2023-24 covered (CDC 2015-2025 repository; latest year in it not verified [U]). Earliest triple: CDC starts 2000-01, so the earliest buildable fire year is 2001-02 on CDC alone; TAO statements from 2007-08 [I].

### 2D. Boundary / name changes
- 29 councils each year of the CDC since 2000 [V, Office of Local Government page]. No amalgamation or split found in 2000-2025 [I]. The Future of Local Government Review reported in Oct 2023; I found no implemented mergers [I].
- Name in Grants Commission tables: "Glamorgan Spring Bay" [V]. Whether ABS boundary files spell it differently (e.g. with a slash) I did not check [U]; join on codes.

### 2E. Hazard layer (Tasmania)

| Item | Finding |
|---|---|
| Layer | Bushfire-Prone Areas overlay. Statewide it is one of the "Tasmanian Planning Scheme - Code Overlay" layers (LIST). I could not open the attribute list to confirm the exact overlay name in the file [U] |
| Custodian | Tasmanian Planning Commission (GIS Officer) for the statewide Code Overlay layer [V]. The overlay content originates from the Tasmania Fire Service methodology [V, TFS FAQ via Flinders Council] |
| First designation / current version | Creation 26 Jun 2020, publication 22 Jul 2020, revision 20 Mar 2024. Lineage: council data assessed 2017-2021; layer "under construction" [V]. Earlier council-level overlays: Clarence (2015), Hobart (2017) [V]. Since 2012 the planning/building rules already applied to "bushfire-prone areas" but without a map [V] |
| Historical (pre-fire) versions | **No statewide pre-2020 layer**. So nothing exists for the 2013 (Dunalley) or 2016 fires and only patchy council coverage for 2018-19. A post-2020 layer used for 2013 or 2016 would be a comparability problem (and Tasmanian rules apply to land near vegetation regardless of the overlay) |
| Category structure | **Single class**. The overlay does not separate high, medium and low; land within 100 m of bushfire-prone vegetation (AS 3959 distance) [V, TFS FAQ]. Fit to NSW Cat 1/2/3: weak (binary only) |
| Format and endpoint | ESRI shapefile and TAB in zip; https://listdata.thelist.tas.gov.au/opendata/data/TASMANIAN_PLANNING_SCHEME_CODE_OVERLAY_STATEWIDE.zip [V, HEAD] |
| Size | 1,319,248,472 B (1.32 GB) (HEAD; last modified 20 Aug 2026). It bundles all code overlays, not just bushfire |
| Licence | CC BY 3.0 Australia [V] |
| Fall-back within Tasmania | TASVEG (state vegetation map; TASVEG 5.0 statewide zip 1,785,214,638 B (1.79 GB), modified 4 Dec 2025; TASVEG 4.0 Fire Attributes per council also on the LIST) [V sizes]. Which TASVEG version was current at each fire, and version history, not verified [U] |

---------------------------------------------------------------------------------------------------

## 3. WESTERN AUSTRALIA

### 3A. Council finance sources

| # | Source | Publisher | Financial years | Statements / ratios | Councils | Format, URL | Licence | Size |
|---|---|---|---|---|---|---|---|---|
| W1 | **MyCouncil data** (open OData web service behind the MyCouncil website) | Dept of Local Government, Sport and Cultural Industries (data.wa.gov.au publisher). The MyCouncil FAQ now names the department "Local Government, Industry Regulation and Safety" [V] | See table below: finance/ratio view 2012/13 to 2023/24; expenditure by program 2010/11 to 2023/24; 2024-25 expected later in 2026 [V] | **Both** (see below) | 139 distinct council names every year (139-140 rows per year; see 3D) | OData service (XML default; `$format=json` works): https://prod-mycouncil-services.azurewebsites.net/data.svc/ ; catalogue page https://catalogue.data.wa.gov.au/dataset/mycouncil (resource page https://catalogue.data.wa.gov.au/dataset/mycouncil/resource/73098951-68aa-4d37-8d8d-d956d339e3a7). Site: https://mycouncil.wa.gov.au/ | CC BY 4.0, "open" [V] | No file. Rows: FinanceActuals 1,674; Expenditure (by program) 22,564; ExpenditureType 11,839; Snapshot 1,676; GrantData 4,682 [V, `$count`] |
| W2 | **Council annual financial reports** (statutory ratios note; two prior years shown) | Each of 139 councils | Regulation 50 ratios first reported in 2012/13 with comparatives for 2010/11 and 2011/12 (comparatives for asset consumption and asset renewal funding not required) [V, Operational Guideline 18, June 2013] | Full statements + 7 ratios | 139 | PDF per council-year; not aggregated [I] | Varies | n/a |
| W3 | **Auditor General WA "Local Government ... Financial Audit Results"** | Office of the Auditor General | Latest: Local Government 2025 (Report 13: 2025-26, 15 Apr 2026) [V]. Earliest edition in this series not established [U] | Appendix 9 gives each council's current ratio for the last two years; 138 entities audited in 2025 [V] | 138 (**sources disagree**: MyCouncil has 139 councils, OAG 2025 says 138 entities audited [V both]) | PDF; https://audit.wa.gov.au/reports-and-publications/reports/local-government-2025-financial-audit-results/ | [U] | n/a |
| W4 | Local Government National Report | Commonwealth | as Q7 | State-level only | | | | |

MyCouncil entities and coverage (counts via `$count`; sample rows read for one council to see categories) [V]:

| Entity | What it holds | Years present (rows per year) |
|---|---|---|
| `vw_LG_FinanceActuals` | Seven Reg-50 ratios (CurrentRatio, AssetConsumptionRatio, AssetRenewalFundingRatio, AssetSustainabilityRatio, DebtServiceCoverRatio, OperatingSurplusRatio, OwnSourceRevenueCoverageRatio) with benchmarks and scores; FSSScore (the earlier Financial Health Indicator score, [I] from the field name and the 2025 news item); LGFI (4 ratios: current ratio, debt service coverage, operating surplus, net financial liabilities, plus weighted score); RateRevenue, FeesCharges, OtherRevenue, FinancialGrants, TotalRevenue, EmployeeCost, CashBackedReserves (current and previous period), TotalAssets (current and previous), NonCurrentLiabilities (current and previous) | 2012/13 to 2023/24 (139-140 per year). Seven old ratios populated 2012/13 to 2020/21 (2020/21: about 121-129 of 139, so some councils missing); zero rows for 2021/22 and later. LGFI columns populated 2018/19 to 2023/24 (2018/19 DSCR: 128 of 139). FSSScore 2012/13 to 2022/23 full, 53 rows in 2023/24 |
| `vw_LG_Expenditure` | Expenditure by **program**: Governance; General Purpose Funding; Law, Order, Public Safety; Health; Education and Welfare; Housing; Community Amenities; Recreation and Culture; Transport; Economic Services; Other Property and Services; Total Expenditure | 2010/11 (103 councils only), 2011/12 to 2023/24 (135-140) |
| `vw_LG_ExpenditureType` | Expenditure by nature: Utilities, Depreciation, Employee Costs, Material and Contracts, Other, Total | 2010/11 (103 councils), 2011/12 to 2023/24 |
| `vw_LG_GrantData` | Grants by category | 2011/12 to 2023/24 |
| Not held | Any 2005/06 to 2009/10 finance record (counts = 0); total cash or investment balances (only cash-backed reserves) | |

### 3B. Ratio comparability (NSW measure -> WA)

WA's ratios are set by Regulation 50 (Local Government (Financial Management) Regulations 1996), explained in Operational Guideline 18 (June 2013), which says they complement the national criteria endorsed by the Local Government and Planning Ministers' Council [V].

| NSW measure | WA | Definitional note |
|---|---|---|
| Cash expense cover (months) | **Nothing.** MyCouncil holds cash-backed reserves (a restricted subset) but no cash or investments total and no cash-cover ratio. The LGFI net financial liabilities ratio is a solvency proxy only [V field list] | Cash balances must come from annual financial reports (W2), which are not aggregated |
| Own-source revenue % | `OwnSourceRevenueCoverageRatio` = own-source operating revenue (rates and service charges, fees and user charges, reimbursements and recoveries, interest, profit on disposal) / operating expense [V]. **Not identical to NSW**: NSW = revenue excluding all grants and contributions / total continuing operating revenue including all grants (benchmark >60%) [V, Audit Office NSW App 9] | WA divides by expense (a coverage multiple), NSW by total revenue (a share). An NSW-style share might be built from RateRevenue + FeesCharges + OtherRevenue over TotalRevenue, but whether MyCouncil's OtherRevenue and FinancialGrants match the NSW own-source scope is [U] |
| Debt service ratio | `DebtServiceCoverRatio` = annual operating surplus before interest and depreciation / principal and interest (standards: >=2 basic, >5 advanced) [V]. **Near-identical in concept to NSW's debt service cover ratio** (operating result before capital excluding interest, impairment, depreciation and amortisation / principal repayments + borrowing costs; >2 times) [V]. Not word-for-word identical (WA counts all borrowings and leases under s6.20; NSW takes principal from the cash flow statement) | Same national framework origin [I from matching benchmark and structure]. The LGFI DSCR (2018/19 on) may be defined differently [U] |
| Operating ratio | `OperatingSurplusRatio` = (operating revenue - operating expense) / **own-source** operating revenue (Basic 1-15%, Advanced >15%) [V] | Different denominator from NSW's operating performance ratio (÷ total operating revenue excl. capital grants). LGFI version's definition not opened [U] |
| Infrastructure backlog ratio | **Nothing.** `AssetConsumptionRatio` (written-down / current replacement cost of depreciable assets; >=50%) and `AssetRenewalFundingRatio` (NPV of planned 10-year renewals / NPV of required renewals; 75-95%; only about 125-135 of 139 councils populated in 2012/13-2019/20) [V] | Condition and plan measures, not backlog cost |
| Unrestricted current ratio | `CurrentRatio` = (current assets - restricted assets) / (current liabilities - liabilities associated with restricted assets), standard >=1 [V]. **Near-identical concept to NSW's unrestricted current ratio** (current assets less external restrictions / current liabilities less specific-purpose liabilities; >1.5) [V] | WA treats all s6.11 cash reserves (including council-chosen ones) as restricted [V], so it is stricter than NSW's "external" restrictions only |
| Buildings and infrastructure renewals ratio | `AssetSustainabilityRatio` = capital renewal and replacement expenditure / depreciation (standard 90%) [V] | Same concept; all non-financial assets, not only buildings and infrastructure |
| Services share of spending | **Yes**: expenditure by program (11 programs, 2010/11 to 2023/24) and by nature (2011/12 to 2023/24) [V]. Rough map to NSW groups: Governance; Transport (roads); Recreation and Culture; Community Amenities (waste, planning, cemeteries); Health + Education and Welfare + Housing (community services); Law, Order, Public Safety (bushfire brigades, rangers) [I] | Good for a crowd-out test |
| Cash and investment balances | **No** (see row 1) | |

### 3C. Year coverage

| Fire year | Prior year | Fire year | Year after | Status |
|---|---|---|---|---|
| 2010-11 (Roleystone, Jan 2011) | 2009-10: **nothing in MyCouncil** (0 rows) | 2010-11: program and nature expenditure only, for 103 councils (Armadale, Kalamunda, Mundaring, Esperance, Waroona, Harvey all present) [V]; no ratios | 2011-12: expenditure only; ratios not in MyCouncil until 2012/13 | **Not buildable from MyCouncil.** Would need council annual reports (2012-13 reports carry 2010/11 and 2011/12 comparatives for five ratios [V]; nothing for 2009-10 [I]) |
| 2013-14 (Perth Hills, Jan 2014) | 2012-13 (first ratio year) [V] | 2013-14 [V] | 2014-15 [V] | **Buildable** (7 ratios), cash cover excluded |
| 2015-16 (Esperance Nov 2015; Waroona/Yarloop Jan 2016) | 2014-15 [V] | 2015-16 [V] | 2016-17 [V] | **Buildable** |
| 2020-21 (Wooroloo, Feb 2021) | 2019-20 [V] | 2020-21: old seven ratios for about 121-129 councils, LGFI for all 139 [V] | 2021-22: old seven ratios absent, LGFI present [V] | **Buildable on the LGFI four ratios only** (current ratio, DSCR, operating surplus ratio, NFL ratio) for all three years; the asset and own-source ratios drop out in 2021-22 |

Era view: 2007-08 to 2012-13: ratios only 2012-13; expenditure from 2010-11. 2013-14 to 2018-19: fully covered. 2018-19 to 2023-24: seven old ratios to 2020/21, LGFI to 2023/24 (note the LGFI replaced the earlier Financial Health Indicator [V, May 2025 news item]; DLGSC states the four LGFI metrics were designed to reflect changes in reporting requirements [V]).

### 3D. Boundary / name changes
- MyCouncil (my API check): 139 identical council names in every year 2012/13 to 2023/24, no additions or drops [V]. So no boundary-driven break inside 2012/13-2023/24 in the MyCouncil naming [I; MyCouncil may have harmonised names].
- **Key on LGId, not name**: "Narrogin" exists twice (Town, LGId 95; Shire, LGId 176) in 2012/13 and 2019/20, and "Coolgardie" (LGId 30) has a duplicated row in 2016/17 [V]. That explains 140 rows in some years.
- 2010/11 covers only 103 councils in the expenditure views [V].
- WA boundary changes 2005-2010 and structural events in 2005-2012: not verified [U].

### 3E. Hazard layer (Western Australia)

| Item | Finding |
|---|---|
| Layer | Map of Bush Fire Prone Areas [V] |
| Custodian | DFES Office of Bushfire Risk Management (OBRM). Areas are designated by the Fire and Emergency Services Commissioner under section 18P of the Fire and Emergency Services Act 1998, by Gazette order; Landgate builds the dataset [V] |
| First designation / versions | Mapping Standard V1.0 May 2014; V2.0 Nov 2015 [V]. Map launched by the State Government in Dec 2015 [V, DFES 2017 release]. In the current layer the earliest polygon designation date is **2015-12-08** [V, ArcGIS REST]. Reviewed regularly (annual review in the 2014 Standard [V, V2.0 amendment note]); 2017 edition released 31 May 2017 [V]; latest designated 13 Dec 2025 [V]; another dataset OBRM-026 created 2026-09-01 [V, catalogue] |
| Historical versions | DFES Standard (2023) says previously designated data "will continue to be publicly available" on data.wa.gov.au identified by designation date [V]. Reality today: the data.wa.gov.au catalogue lists OBRM-001 (copy of current), OBRM-006 (display only), OBRM-023, OBRM-024 (2025), OBRM-025 (designated 13-12-2025), OBRM-026 [V]. Record pages for OBRM-008 (2017) and OBRM-018 (28-09-2019) that a search engine had indexed now return 404 [V]. HEAD requests to `data-downloads.slip.wa.gov.au/OBRM-0xx/...` all end in HTTP 403 [V] so size is unknown |
| **Reconstruction trick** | The 2025 layer (OBRM-024, ArcGIS layer 22, 469 polygons; also OBRM-001 layer 17, 469) carries `lga` and `designationdate` per polygon. Polygon counts by designation date: 2015-12-08: 136; 2016-05-21: 79; 2017-06-01: 63; 2017-07-12: 1; 2018-06-01: 15; 2019-06-01: 14; 2021-12-11: 9; 2024-09-24: 42; 2025-12-13: 110 [V]. Each LGA has one polygon per designation date it was touched (e.g. ARMADALE 2015-12-08, 2016-05-21, 2017-06-01, 2019-06-01, 2024-09-24, 2025-12-13) [V]. **Inference [I]:** the layer is cumulative by increments, so filtering `designationdate <= fire date` reproduces the additive extent in force at that date; areas removed at later reviews would be missing. This needs a sanity check against an archived version before use |
| Pre-2015 | **No official statewide map before 8 Dec 2015.** So Roleystone (2011), Perth Hills (2014) and Esperance (Nov 2015) have no pre-fire designated layer. Waroona/Yarloop (Jan 2016) can use the 8 Dec 2015 polygons; Wooroloo (Feb 2021) can use polygons dated up to 2019-06-01 [I] |
| Category structure | Binary "bush fire prone area" = bush-fire-prone vegetation (AS 3959 classes; managed grassland and low-threat vegetation excluded) plus a 100 m buffer [V]. From the Sept 2023 Standard the map labels BPA 1 (suburbs on the Swan Coastal Plain within the Perth, Peel and Greater Bunbury region schemes) and BPA 2 (rest of the state), a location split rather than a hazard grade [V]. The REST layers' `type` field has one value "BPA" [V]. Fit to NSW Cat 1/2/3: weak (binary) |
| Inputs | Vegetation data from DPIRD, Forest Products Commission and PF Olsen, updated with high-resolution imagery (Perth/Peel/Bunbury) [V, 2023 Standard] (a search summary said NVIS; the document text does not say that, so I trust the document) |
| Format and endpoints | ArcGIS REST: https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Bush_Fire_Prone_Areas/MapServer (layers 17, 20, 21, 22, 23); WFS https://public-services.slip.wa.gov.au/public/services/SLIP_Public_Services/Bush_Fire_Prone_Areas_FS/MapServer/WFSServer ; downloads listed as GeoJSON, SHP, FGDB, GeoPackage at https://data-downloads.slip.wa.gov.au/OBRM-024/ [V, catalogue] |
| Size | 469 polygons in OBRM-024/-001; 148 in OBRM-026 (`returnCountOnly`) [V]; file size unknown (HEAD returned 403) |
| Licence | CC BY 4.0 (OBRM-001, -024) [V]. The DFES page itself states no licence [V] |

---------------------------------------------------------------------------------------------------

## 4. Is NVIS 6.0 enough as a fall-back forest-share hazard?

- The DCCEEW NVIS page (updated 13 Nov 2025) now serves **Version 7.0** (100 m rasters; 33 Major Vegetation Groups, 85 subgroups) and says cross-version comparison is not possible [V]. The 6.0 product used by the existing pipeline is therefore a superseded, static snapshot; its release date and reference year I could not verify (search budget ended) [U].
- NVIS is a national compilation of state sources of differing age and scale (the "Key Layers" products exist to show this) [V]. It has no time dimension, no ignition or slope logic and no 100 m buffers.
- Verdict [I]: adequate as a **consistent, time-invariant forest/woodland/shrub/grass share** across NSW, Queensland, Tasmania and WA, and the only option for WA 2011 and 2014 and Tasmania 2013 and 2016 where no pre-fire bushfire-prone layer exists. It is a weaker hazard measure than the state layers (no graded intensity, no buffers), so a NSW model calibrated on BFPL Cat 1/2 shares will not transfer one-for-one. Best design: use the NVIS share as the common cross-state hazard input and the state layers only as within-state robustness checks.

---------------------------------------------------------------------------------------------------

## 5. Final tables

### Table 1. Finance sources

| Source | State | FY range | Ratios or statements | Closest NSW analogue | Verdict |
|---|---|---|---|---|---|
| Comparative information workbooks (Financial input + Financial PIs) | QLD | 2002-03 to 2024-25 (all councils from 2013-14) | Both (inputs + F1-F10 PIs) | OLG Time Series (inputs and older ratios) | **Use** for 2018-19 and 2019-20 fires. Field list of 2013+ workbook unverified; no cash-cover or function split verified |
| Comparative information open-data CSV (Financial Inputs) | QLD | 2010-11 to 2016-17 | Inputs only | OLG Time Series inputs | Small (82 KB); useful only for pre-2018 fires, of which the candidate list has none |
| QAO local government reports and dashboards | QLD | 2013-14 to 2024-25 (dashboards 2018-2025) | Ratios (3 legacy, then 6 audited from 2023-24) | Operating ratio, renewals ratio | **Use as a cross-check** and for operating ratio, net financial liabilities, asset sustainability |
| Council annual reports (audited statements) | QLD | all | Full statements | Cash cover, function split | Manual extraction only (77 x 3 per event) |
| Sustainability ratio set from 2023-24 (unrestricted cash expense cover etc.) | QLD | 2023-24 on | Ratios | Cash expense cover | Too late for any candidate fire year |
| Tasmanian CDC (LIST open data, 2 zips 16.8 MB and 13.4 MB) | TAS | 2000-01 to 2025 | Raw returns incl. expenditure by function; audited from 2017-18 | OLG Time Series (function spend) | **Use.** Column list unverified until opened |
| Tasmanian dashboards (Power BI, exportable) | TAS | about 10 years (from 2013-14 for unrestricted cash) | Both: 9 ratios + inputs | All eight NSW measures (cash cover, own-source, DSCR, underlying surplus, etc.) | **Use** for ratios that match NSW best; range must be confirmed |
| Auditor-General local government reports | TAS | 2007-08 to 2024-25 | Both, per council, PDF | Statements for cash cover | **Use** for 2011-12 to 2013-14 (Dunalley) and cash inputs |
| State Grants Commission data tables | TAS | 2021-22 revenue | Derived | none | Not needed |
| MyCouncil OData (FinanceActuals) | WA | 2012/13 to 2023/24 | Both: 7 ratios (to 2020/21), LGFI 4 ratios (2018/19 on), revenue splits | Own-source, DSCR, unrestricted current ratio, renewals ratio (partly) | **Use** for 2013-14, 2015-16, 2020-21 fires |
| MyCouncil OData (Expenditure by program / nature) | WA | 2010/11 to 2023/24 | Statements (function) | Function spend | **Use** (needed for crowd-out); 2010/11 only 103 councils |
| Council annual financial reports | WA | all | Full statements, 7 ratios with 2 prior years | Cash cover | Only route to cash balances and to 2010-11 ratios; manual |
| OAG WA local government audit results | WA | to 2025 | Ratios (current ratio per council, 2 years) | Current ratio | Cross-check only |
| Local Government National Report | All | 2014-15 to 2023-24 | State-level tables, FAG per council | none | Not usable for council finance |

### Table 2. Hazard layers

| Hazard layer | State | First version | Custodian | Fit to NSW BFPL | Size | Verdict |
|---|---|---|---|---|---|---|
| Bushfire prone area - Queensland series (CSIRO/QFES method) | QLD | SPP effective 2 Dec 2013; mapped 2014, published 2015-07-15 | Queensland Fire Department (owner Rural Fire Service Queensland) | Good: graded Very High/High/Medium classes plus 100 m buffer; classes are modelled intensity rather than vegetation type | about 1.6 GiB (12 regional shapefile sets, catalogue figures) | **Use** for 2018-19 and 2019-20 (single 2014 vintage, pre-fire). Access route conflicting (email vs download) |
| Bushfire-Prone Areas overlay in Tasmanian Planning Scheme Code Overlay (statewide) | TAS | Layer created 26 Jun 2020 (council overlays from 2015 Clarence, 2017 Hobart) | Tasmanian Planning Commission (method from Tasmania Fire Service) | Weak: single class, 100 m from bushfire-prone vegetation | 1.32 GB zip (all code overlays) | **Not pre-fire** for 2013 and 2016 (and patchy for 2018-19). Use only as post-hoc robustness; use NVIS or TASVEG as main input |
| TASVEG 5.0 (fall-back vegetation) | TAS | version history not verified | NRE Tasmania | Vegetation only | 1.79 GB zip | Optional finer fall-back |
| Map of Bush Fire Prone Areas (OBRM-024/-001 etc.) | WA | Standard May 2014; first designation 8 Dec 2015 | DFES Office of Bushfire Risk Management | Weak: binary BPA (+ BPA1/BPA2 location labels from 2023) | 469 polygons; file size unknown (403) | **Use** for 2015-16 (Waroona) and 2020-21 via `designationdate <= fire date` (inference to verify). **Nothing** for 2011, 2014 and Nov 2015 |
| NVIS (national) | All | v6.0 used by pipeline; DCCEEW now serves v7.0 | DCCEEW | Vegetation share only, time-invariant, no buffers | not measured | **Use as the common fall-back**, with state layers as within-state checks |

---------------------------------------------------------------------------------------------------

## 6. Five-line summary

1. **Queensland**: FP and X-finance can be rebuilt for the 2018-19 and 2019-20 fires from the comparative-information workbooks (2017-18 to 2020-21 present) and QAO ratios; missing or unverified are cash expense cover before 2023-24 (needs hand extraction), and a complete spending-by-function split. Hazard: one 2014 CSIRO/QFD layer with graded classes, pre-fire and usable.
2. **Tasmania**: the best-served state for FP. The CDC (2000-01 to 2025) plus the TAO reports and dashboards give all NSW-type ratios (cash cover, DSCR, underlying surplus, asset ratios, own-source) and expenditure by function for 2012-13, 2015-16 and 2018-19; only the TAO-adjusted cash measure starts in 2013-14. Hazard: no pre-2020 statewide overlay and it is binary, so use TASVEG or NVIS.
3. **Western Australia**: MyCouncil OData supplies seven Reg-50 ratios (2012/13-2020/21), the four LGFI ratios (2018/19-2023/24), revenue splits and expenditure by program (2010/11 on): 2013-14, 2015-16 and 2020-21 fires are buildable (2020-21 on LGFI ratios only). The 2010-11 Roleystone fire is not (no 2009-10, no ratios before 2012/13). No total cash balances anywhere in MyCouncil, so no cash cover without annual reports.
4. **Comparability**: same or close analogues exist for operating ratio, renewals ratio, unrestricted current ratio and debt service (WA and Tasmania DSCR match NSW's DSCR concept); own-source revenue is different in WA and Tasmania (coverage of expenses, not share of revenue); the infrastructure backlog ratio has no equivalent in any of the three.
5. **Hazard**: only Queensland has a usable graded pre-fire layer; WA's first map is 8 Dec 2015 (with polygon designation dates allowing reconstruction), Tasmania's statewide overlay dates from 2020; NVIS is the only consistent cross-state fall-back and is time-invariant (and the current release is 7.0).

---------------------------------------------------------------------------------------------------

## 7. Not verified, and open items

- Field lists of the Queensland "Financial input" workbooks (2013-14 on), the Queensland CSV, and the Tasmanian CDC returns (files not opened). Whether Queensland or Tasmanian returns carry cash and investment balances as fields.
- Whether the Queensland F1-F10 ratio set (verified in the 2005-06 report) is unchanged in 2013-14 to 2024-25.
- Licence of the Queensland Excel workbooks, the QAO and TAO PDFs, and the Tasmanian dashboards.
- Queensland 2008 amalgamation counts; WA council boundary changes 2005-2010; whether ABS spellings differ for Tasmanian councils.
- The exact first and last year of the Tasmanian dashboards and of the "2015-2025" CDC zip.
- WA: why MyCouncil has no classic ratios from 2021/22 (my count shows zero; likely a regulation change, not confirmed); whether MyCouncil's LGFI definitions equal the classic ones; whether `OtherRevenue`/`FinancialGrants` allow an NSW-style own-source share.
- WA hazard: whether archived versions (OBRM-008 2017, OBRM-018 28-09-2019 and others) can still be obtained (record pages 404, downloads 403); whether the cumulative-designation-date reading is right.
- Tasmania: exact overlay name inside the Code Overlay zip; TASVEG version history.
- NVIS 6.0 release date and reference year.
- NSW definitions for the infrastructure backlog ratio and the buildings and infrastructure renewals ratio (OLG Code PDFs blocked).

---------------------------------------------------------------------------------------------------

## Appendix. Queensland comparative-information file paths and HEAD sizes

Base: `https://www.dlgwv.qld.gov.au/__data/assets/excel_doc/`. Size = Content-Length (bytes) from same-origin HEAD in a browser session. Year assignment: 2018-19 and earlier from the file names; 2019-20 onward from the link order and the "next-year rate" companion files [I].

| Release | Financial input | Size | Financial PIs (1) | Size |
|---|---|---|---|---|
| 2024-25 | `0003/2171964/2-financial-input.xlsx` | 40,520 | not listed in this pass | |
| 2023-24 | `0008/2098907/2-financial-input.xlsx` | 30,902 | | |
| 2022-23 | `0009/2104002/2-financial-input-932.xlsx` | 32,042 | `0010/2104003/3-financial-pis-1-intro-and-pis-1-933.xlsx` | 31,005 |
| 2021-22 | `0010/2103949/2-financial-input-879.xlsx` | 34,554 | `0020/2103950/3-financial-pis-1-intro-pis-1-880.xlsx` | 32,466 |
| 2020-21 | `0016/2103820/2-financial-input-751.xlsx` | 32,210 | `0017/2103821/3-financial-pis-1-intro-and-pis-1-752.xlsx` | 33,160 |
| 2019-20 | `0019/2103670/2-financial-input.xlsx` | 31,382 | `0020/2103671/3-financial-pis-1-intro-and-pis-1.xlsx` | 32,686 |
| 2018-19 | `0013/2103610/lg-comparative-18-19-2-financial-input.xlsx.xls` | 27,549 | `0016/2103640/lg-comparative-18-19-3-financial-pis-1-intro-and-pis-1.xlsx.xls` | 26,586 |
| 2017-18 | `0014/2103611/lg-comparative-17-18-2-financial-input.xlsx` | 27,203 | `0019/2103616/lg-comparative-17-18-3-financial-pis-part1.xlsx` | 27,109 |
| 2016-17 | `0003/2103465/lg-comparative-16-17-02-financial-input.xlsx` | 26,632 | `0008/2103488/lg-comparative-16-17-03-financial-pis-part1.xlsx` | 26,542 |
| 2015-16 | `0017/2103461/lg-comparative-15-16-02-financial-input.xlsx` | 28,554 | `0008/2103497/lg-comparative-15-16-03-financial-pis-part1.xlsx` | 26,083 |
| 2014-15 | `0004/2103448/lg-comparative-14-15-02-financial-input.xlsx` | 27,753 | `0004/2103493/lg-comparative-14-15-03-financial-pis-part1.xlsx` | 25,253 |
| 2013-14 | `0018/2103426/lg-comparative-13-14-financial-input.xlsx` | 25,956 | `0003/2103474/lg-comparative-13-14-financial-pis-part1.xlsx` | 24,793 |
| 2012-13 (XLS) | `0013/2103412/lg-comparative-12-13-financial-input.xls` | 49,152 | `0019/2103463/lg-comparative-12-13-financial-pis-part1.xls` | 59,392 |
| 2011-12 (XLS) | `0017/2103362/comparitive-information-2011-12-02.xls` | 41,472 | `0003/2103366/comparitive-information-2011-12-03.xls` | 35,328 |

Other year files (2002-03 to 2010-11) are PDFs or large XLS on the same index page; not sized here.

Verified 2005-06 ratio definitions used in 1B (PDF, 349 pp, read in memory, not saved): F1 revenue ratio; F2 operating efficiency ratio; F3 working capital ratio; F4 rates arrears ratio; F5 capital expenditure ratio; F6 unfunded depreciation ratio; F7 change in community equity ratio; F8 debt servicing ratio; F9 borrowing ratio; F10 net debt per capita.

## Appendix. Primary pages opened (all fetched or read, none downloaded as data)

- QLD: https://www.dlgwv.qld.gov.au/local-government/for-councils/resources/local-government-comparative-reports ; https://www.data.qld.gov.au/dataset/queensland-local-government-comparative-information-report (and CKAN API metadata) ; https://www.qao.qld.gov.au/reports-resources/reports-parliament/local-government-2024 ; QAO 2024 Appendix J, QAO 2023 Appendix L, QAO 2018-19 report (tabled paper 5620t302) ; https://www.qao.qld.gov.au/2024-local-government-dashboard ; https://www.qao.qld.gov.au/reports-resources/interactive-dashboards ; https://www.qao.qld.gov.au/reports-resources/reports-parliament/local-government-2022 ; CSIRO methodology report (data.qld.gov.au resource fc6ec388-...) ; qldspatial metadata record ; https://www.data.qld.gov.au/dataset/bushfire-prone-area-queensland-series
- TAS: https://www.justice.tas.gov.au/local-government/council-performance ; https://listdata.thelist.tas.gov.au/opendata/ ; LIST metadata records d8e9d3f1-... (CDC) and d4c9d9cd-... (Code Overlay) ; futurelocal.tas.gov.au dashboard information sheets (Apr and Aug 2022) ; TAO Report 4 of 2012-13 (Vol 4 Pt II) and Report 11 of 2020-21 (Vol 2) ; audit.tas.gov.au publication pages (2012-13 volumes, 2016-17) ; State Grants Commission data tables 2023-24 ; Flinders Council overlay FAQ (TFS)
- WA: https://prod-mycouncil-services.azurewebsites.net/data.svc/ (service document, `$metadata`, `$count`, single-council sample rows) ; https://catalogue.data.wa.gov.au (MyCouncil, OBRM records via CKAN API) ; Operational Guideline 18 (June 2013) ; https://www.cits.wa.gov.au/department/news/2025/05/14/new-local-government-financial-indicator-on-mycouncil-website ; https://mycouncil.wa.gov.au/Home/faqs ; DFES Mapping Standard for Bush Fire Prone Areas 2023 ; https://news.dfes.wa.gov.au/media-releases-feature-stories/updated-map-of-bush-fire-prone-areas-released-tomorrow/ ; SLIP ArcGIS REST `Bush_Fire_Prone_Areas/MapServer` (layer schema, counts, grouped statistics only) ; OAG WA Local Government 2025 report page
- National/NSW: https://www.infrastructure.gov.au/territories-regions-cities/local-government/publications/national-reports and the 2023-24 National Report PDF ; Audit Office NSW, Report on Local Government 2018, Appendix nine (OLG indicator formulas) ; https://www.dcceew.gov.au/environment/environment-information-australia/national-vegetation-information-system/data-products
