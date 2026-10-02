# A7 - National (all-state) data series: coverage, years, gaps

Scoping note for Experiment 6 (more real fires, other years and states). Written 2026-09-29.
Author: scoping agent A7. Nothing was downloaded except web pages and JSON catalogue metadata; sizes below are from HTTP HEAD requests (`Content-Length`) unless marked "size unknown". Local files were only read.

Conventions
- "on disk" = a file I inspected under `/Users/ray/Research/AUSSEF - Local/fire_event_dataset/data/` (call it DATA) or `/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0/dataset_phase1/raw/` (call it P1).
- FY = July-June. "Fire FY" = the FY containing the ignition month; "pre-fire FY" = the FY before it.
- "Source states" = what a page or file says. "Inference" = my reading. "Unverified" = I could not open the evidence (the shared WebSearch budget ran out part-way, so some follow-up checks were impossible; each such case is listed in section 12).

---------------------------------------------------------------------

## 0. Bottom line

1. The four national LGA series the NSW build uses (PIA, CABEE, SALM, DSS) plus ERP and SEIFA 2016/2021 are already on disk as national raw files, but the derived parquet files (`cabee_lga_year.parquet`, `dss_lga_quarter.parquet`) are NSW-only (130 and ~130 LGAs). The Census GCP packs on disk (`abs/gcp2016`, `abs/gcp2021`) are NSW-only.
2. Post-2015 non-NSW fires (2015-16, 2019-20, WA 2016 and 2021, Qld 2018-19) can be rebuilt almost entirely from files already on disk. The only missing input is the national Census LGA pack (dwellings, industry shares) and, for Jan 2016 fires, one DSS quarter (Dec 2015).
3. Pre-2015 fires are patchy because each series has a different start:
   - Income at LGA: continuous back to FY2001-02 through two ABS products (EPISA 2001-02 to 2010-11, PIA 2011-12 onwards). One break at 2010-11/2011-12.
   - Business counts at LGA: CABEE LGA cubes only start June 2015. Earlier LGA-level counts exist in the ABS National Regional Profile (NRP, Jun 2008-2014, LGA 2012/2013 boundaries) and, as Statistical Local Area cubes, for Jun 2007-2009. None is on disk.
   - Unemployment (SALM): LGA smoothed series starts Dec quarter 2010. Nothing earlier is publicly downloadable that I could find.
   - Income support (DSS): LGA level starts September 2013. So Black Saturday (2009), Wangary (2005), WA Feb 2011 and Jan 2013 fires have no DSS pre-fire baseline. Oct 2013 fires can use Sep 2013 as baseline.
   - SEIFA: LGA files exist for 2001 (unverified content), 2006, 2011, 2016, 2021.
   - ERP: one file, 2001-2025, single boundary vintage (2025), already on disk. Solves all denominators.
4. Event registers: the NEMA "DRFA Activation History by LGA" CSV is exactly the declared-event x LGA unit, but although its title says "2006 to current" the rows start in Sep 2017 (AGRN 776), are very thin before 2020 (text-match counts by year, 2017 to 2026: 3, 21, 16, 107, 442, 584, 344, 419, 502, 250) and contain zero SA bushfire rows. In practice it is a 2020-onward table. DisasterAssist has the older NDRRA-era declarations but as a JavaScript table over an undocumented endpoint (not machine-readable in a supported way). ICA has every candidate event but at event level (state + sometimes postcode list), not LGA.
5. Geoscience Australia polygons (v2.0 on disk) cover ACT, NSW, Qld, SA, Tas, Vic, WA (no NT), last year 2022 (Tas, Vic) or 2023 (others). All candidate large fires are present except that I could not find the Jan 2016 Waroona/Yarloop WA fire. Qld polygons come from Queensland Parks and Wildlife Service only (protected estate).

---------------------------------------------------------------------

## 1. What is already on disk (national vs NSW-only)

| Item | Path | Geography and states | Time coverage | LGA vintage(s) | Verified how |
|---|---|---|---|---|---|
| CABEE raw workbooks (8165.0) | DATA/cabee/*.xls, *.xlsx (18 files) | National, all 8 states/territories in every release | June 2015 to June 2025 (11 June-years). Each release holds only 3-4 June tables (e.g. "Jun 2013 to Jun 2017" release contains June 2015, 2016, 2017 sheets only) | Repo labels: LGA 2016 (Feb-2018 release), 2018, 2018/19, 2020, 2021, 2022, 2023, 2024, 2025. Within the Feb-2018 release the June 2015 sheet lists 150 NSW LGAs (pre-amalgamation) but the June 2017 sheet lists 130 (post) | pandas over every sheet; state names counted |
| CABEE parquet | DATA/cabee/cabee_lga_year.parquet | NSW only (130 LGAs x 11 years = 1,430 rows) | 2015-2025 | mixed, labelled per row | pandas |
| SALM | DATA/salm/salm_lga.csv | National: 544 LGAs (NSW 129, Vic 80, Qld 77, SA 71, WA 137, Tas 29, NT 20, ACT 1). Three items: unemployment, labour force, rate | Dec-10 to Mar-26 (61 quarters) | 2025 ASGS LGAs only. Dashes where no estimate | pandas |
| DSS | DATA/dss/*.csv (5 files) + dss_lga_quarter.parquet | CSV national (all 8 states + 'Other'); parquet NSW only (5,706 rows) | Mar 2016 to Jun 2026 (files: Mar-16..Dec-18; Mar-19..Dec-20; Mar-21..Mar-23; Jun-23..Sep-24; Dec-24..Jun-26) | 2014 LGA (NSW 153), 2018, 2020, 2022, 2024 | pandas |
| PIA (ABS Personal Income in Australia) | P1/pia_2020.xls; P1/pia_2024.xlsx; P1/project_inputs/pia_old_total.xlsx; P1/project_inputs/pia_total.xlsx (+ P1/pia_*_method.html) | National LGA table (Table 1.5). 539-546 LGAs, all 8 states/territories | pia_2020: FY2011-12 to 2017-18. pia_old_total: 2015-16 to 2019-20. pia_2024: 2017-18 to 2021-22. pia_total: 2018-19 to 2022-23 | pia_2020: "LGA boundaries at 2018". pia_old_total: concorded to 2020 edition. pia_2024: method page says 2021 edition in one place and 2020 edition in another. pia_total: file note says ASGS Edition 3, 2023 LGA boundaries | pandas; method HTML read |
| ABS Data by Region (LGA tables) | DATA/raw/il/dbr*.xlsx (15 files: 14100DO0003 economy, DO0004 income, DO0005 education/employment) | National LGA (Table 2) | Releases 2015-20, 2011-22, 2011-23, 2011-24, 2011-25. Business counts only carry a rolling 5 June-years per release (e.g. 2016-2020 in the 2015-20 file; 2021-2025 in the 2011-25 file). Business entries/exits from 2017. Income (PIA) 2015-2023. DSS/DVA payment counts at 30 June from 2015 (Age pension, DSP, Carer payment, Newstart/JobSeeker, Parenting payment, Youth Allowance, FTB; JobSeeker only 2020) | LGA 2011 + successive editions | pandas |
| ERP by LGA | DATA/abs/32180DS0004_2001-25.xlsx (Regional population 2024-25, released 31 Mar 2026); P1/population_lga.xlsx (2022-23 release, 2001-2023); P1/population_lga_2020*.xls (2019-20 release, only 2019-2020 by state) | National, 548 LGA codes in the 2025 file | 30 June 2001 to 2025 (2022-24 revised, 2025 preliminary) | File footnote: based on 2025 LGA boundaries. 2022-23 file: 2023 boundaries | pandas; footnotes read |
| SEIFA | P1/seifa_2016.xls (released 27 Mar 2018); P1/seifa_2021.xlsx (released 27 Apr 2023) | National LGA, IRSD is Table 2 of each. 2016: 544 codes; 2021: 547 codes | Census 2016; Census 2021 | LGA 2016 (NSW 130+); LGA 2021 (ASGS Ed 3) | pandas |
| ABS LGA boundaries | P1/lga_2015, lga_2016, lga_2018, lga_2020, lga_2021 (GDA94), lga_2023 (GDA94) (unzipped shapefiles + zips) | National | 2015 (581 features; NSW 154), 2016 (563; NSW 132), 2018 (562; NSW 131), 2020 (562), 2021 (566), 2023 (566) | as named | pyogrio attribute read |
| LGA crosswalks | P1/crosswalk_2015_2016, 2016_2018, 2018_2020, 2018_2023, 2020_2021, 2020_2023, 2021_2023 (.csv) | National | n/a | Custom spatial-intersection tables from an earlier session (columns from_code, to_code, percent_from, percent_to, mapping_status), not official ABS correspondences | header read |
| Census GCP | DATA/abs/gcp2016, gcp2021 | NSW ONLY (zips 6,817,415 B and 7,019,787 B match the ABS NSW packs) | 2016, 2021 | LGA 2016, 2021 | HEAD size match |
| Remoteness Areas | DATA/abs/RA_2021 | National (not my slice) | 2021 | | ls |
| Geoscience Australia (GA) Historical Bushfire Boundaries | P1/ga_original.zip (458,831,604 B) + P1/ga_original/Bushfire_Boundaries_Historical.gdb | ACT, NSW, Qld, SA, Tas, Vic, WA. No NT | see section 9 | n/a | pyogrio attribute read (no geometry) |
| ICA Historical Catastrophe List | DATA/ica/ica_catastrophes.xlsx ("As at June-2024") | National, event level | 1967-2024 (737 events) | n/a | pandas |

---------------------------------------------------------------------

## 2. (a) SEIFA IRSD by LGA

Publisher: ABS, Socio-Economic Indexes for Areas (cat. 2033.0.55.001). IRSD = Index of Relative Socio-economic Disadvantage.

| Vintage (Census date) | Release date | Publication page (opened) | LGA file | Size (HEAD) | On disk | LGA boundary |
|---|---|---|---|---|---|---|
| 2001 | data cube reissued 05/10/2006; cube 22/08/2007 | https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/2033.0.55.0012001?OpenDocument= | single zip `AUS.zip` (LGA content UNVERIFIED) https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&AUS.zip&2033.0.55.001&Data%20Cubes&9C5AD93C41B4FB69CA25715B007AA9C5&0&2001&22.08.2007&Latest | 9,229,178 B | no | ASGC 2001 (inference) |
| 2006 | 26/03/2008 | https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/2033.0.55.0012006?OpenDocument= | `2033055001_ seifa, local government areas, data cube only, 2006.xls` https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&2033055001_%20seifa,%20local%20government%20areas,%20data%20cube%20only,%202006.xls&2033.0.55.001&Data%20Cubes&D51E2B1E6FB35F1ACA25741700117816&0&2006&26.03.2008&Latest | 697,856 B | no | ASGC 2006 LGA |
| 2011 | data cubes released between 28/03/2013 and 12/11/2014; LGA indexes cube 18/07/2013 | https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/2033.0.55.0012011?OpenDocument= | `2033.0.55.001 lga indexes.xls` https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&2033.0.55.001%20lga%20indexes.xls&2033.0.55.001&Data%20Cubes&28EF8569335AC7CDCA257BAB00136B0F&0&2011&18.07.2013&Latest (also .zip; and per-index zips e.g. irsd lga.zip 2,421,796 B) | 667,136 B | no | ASGS 2011 LGA |
| 2016 | 27/03/2018 | https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/2033.0.55.0012016?OpenDocument= | `2033055001 - lga indexes.xls` https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&2033055001%20-%20lga%20indexes.xls&2033.0.55.001&Data%20Cubes&5604C75C214CD3D0CA25825D000F91AE&0&2016&27.03.2018&Latest | 656,896 B (matches disk) | YES P1/seifa_2016.xls | LGA 2016 |
| 2021 | 27/04/2023 | https://www.abs.gov.au/statistics/people/people-and-communities/socio-economic-indexes-areas-seifa-australia/latest-release | `Local Government Area, Indexes, SEIFA 2021.xlsx` https://www.abs.gov.au/statistics/people/people-and-communities/socio-economic-indexes-areas-seifa-australia/2021/Local%20Government%20Area%2C%20Indexes%2C%20SEIFA%202021.xlsx | 384.13 KB per page (HEAD gave no length; disk copy 393,344 B) | YES P1/seifa_2021.xlsx | LGA 2021, ASGS Ed 3 |

Method note 2016 vs 2021 (source: https://www.abs.gov.au/methodologies/socio-economic-indexes-areas-seifa-australia-methodology/2021, opened; paraphrased): the 2021 version drops the dwelling internet-connection variable (not collected) and updates occupation and income cut-offs. Scores are re-standardised to mean 1,000 and SD 100 at each census, so a score means different things in different years; the ABS states the indexes compare areas at a point in time, not over time, and recommends deciles or percentiles for any cross-year use.

Which vintage is "pre-fire"? Two conventions:
- Strict (latest Census before the fire): 2001 for Wangary (Jan 2005); 2006 for Black Saturday (Feb 2009), WA Feb 2011; 2011 for Jan and Oct 2013, WA Jan 2014, Vic Feb 2014, SA Jan 2015, and (strictly) all of 2015-16; 2016 for Qld Nov 2018 and 2019-20; 2016 for WA Feb 2021 (2021 Census was Aug 2021).
- Repo rule today (`fire_event_dataset/src/affected_pop.py`, line 20: "2016 Census for fires starting up to 2020, 2021 after"): nearest Census, which puts 2015-16 fires on 2016. Under that rule 2009 and 2013 fires would need a new rule; I recommend using strict pre-fire for the added fires, and 2016 for 2015-16 only if consistency with the NSW rows matters more than strict timing.
- Availability at the time (inference): SEIFA 2011 was not published until 2013, so for Jan 2013 fires only SEIFA 2006 was public. If "information available to a planner" matters, use 2006 for 2009-2013 fires.

---------------------------------------------------------------------

## 3. (b) ABS Personal Income by LGA (all releases)

Release list (ABS page https://www.abs.gov.au/statistics/labour/earnings-and-working-conditions/personal-income-australia, opened, "Previous releases" block):

| Product | Reference period | Release | LGA level? | Boundary | On disk | Size / URL |
|---|---|---|---|---|---|---|
| Estimates of Personal Income for Small Areas (EPISA, cat. 6524.0.55.002) | 2001-02 to 2005-06 | 17/12/2008 | Yes; one LGA workbook per year (`6524055002do001/003/005/007/009_200102200506.xls`) | ASGC-era LGAs (inference) | no | 2001-02 772,608 B; 2002-03 955,392; 2003-04 934,912; 2004-05 947,200; 2005-06 974,848. Page https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/6524.0.55.0022001-02%20to%202005-06?OpenDocument= ; example file https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&6524055002do007_200102200506.xls&6524.0.55.002&Data%20Cubes&DE95CA5AAF7856CBCA257521000D6544&0&2001-02%20to%202005-06&17.12.2008&Latest |
| EPISA time series | 2003-04 to 2006-07; 2003-04 to 2007-08; 2003-04 to 2008-09; 2009-10 | 2009-2010 | not opened | | no | listed only |
| EPISA time series | 2005-06 to 2010-11 | 29/10/2013 | Yes: `6524055002do003_200506201011.xls` (LGA) and `do004` (SA2-4) | Source says ASGS July 2011 is used, LGA series built directly from postcode; 2005-06 to 2009-10 LGA numbers revised vs an earlier issue. For 2010-11 the "region unknown" split is Australia-only | no | 1,019,904 B. https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&6524055002do003_200506201011.xls&6524.0.55.002&Data%20Cubes&7E5B1952AA505ECDCA257C12000CA87B&0&2005-06%20to%202010-11&29.10.2013&Latest . Page https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/6524.0.55.0022005-06%20to%202010-11?OpenDocument= |
| EPISA | 2011-2015 (2010-11 to 2014-15), released 28/04/2017; 2011-2016 (2010-11 to 2015-16), 19/06/2018; 2012-13, 28/01/2016 | | 2011-2015 page says LGA included; others not stated | | no | (superseded by PIA) |
| PIA (LEED-based) | 2011-12 to 2016-17; 2011-12 to 2017-18 (16/12/2020); 2014-15 to 2018-19; 2015-16 to 2019-20 (8/11/2022); 2020-21; 2021-22 (8/11/2024); 2022-23 (14/11/2025) | | Yes, Table 1 LGA (all states; ACT is reported as one LGA-like unit 89399, ABS notes ACT has no LGAs) | 2011-12-2017-18: LGA 2018; 2015-16-2019-20: LGA 2020; 2017-18-2021-22: Ed 3 (2020/2021 edition, wording differs on the page); 2018-19-2022-23: 2023 LGAs | YES (four workbooks, see section 1) | 2022-23 Table 1: 803.34 KB per page. Pages: .../personal-income-australia/2011-12-2017-18, /2014-15-2018-19, /2011-12-2016-17, /2015-16-2019-20, /2020-21, /2021-22, /2022-23 |

Key facts
- The 2011-12 to 2017-18 workbook on disk starts at FY2011-12, so FY2012-13 and FY2013-14 fires (NSW/Tas Jan 2013, NSW Oct 2013, WA/Vic Jan-Feb 2014) have their pre-fire year (2011-12 or 2012-13) but for Jan 2013 the pre-fire FY is 2011-12, the first column. Fine, but no earlier year is available in this product.
- For 2009 and 2005 fires use EPISA: Black Saturday needs FY2007-08 and 2008-09 (both in `do003_200506201011.xls`); Wangary needs FY2003-04 and 2004-05 (`do005` and `do007`); WA Feb 2011 needs FY2009-10 and 2010-11 (both in `do003`).
- Series break (inference from the two method pages): EPISA counts tax-return lodgers processed by 31 October; PIA from LEED and, in the 2024 release, adds non-lodgers for 2017-18 to 2020-21 (file note on disk). So never compute a "change" that straddles EPISA 2010-11 and PIA 2011-12; the "excess % change" (council minus control councils) is safe if both years and the controls come from one product.
- ATO postcode-level Taxation Statistics exist on data.gov.au (e.g. "Taxation Statistics 2009-10", "Taxation Statistics 1994-95 to 2008-09" appeared in a catalogue search) but are postcode level; I did not open them and do not recommend them because EPISA already gives LGA.

---------------------------------------------------------------------

## 4. (c) CABEE business counts by LGA (ABS cat. 8165.0)

Earliest June year at LGA level, nationally, in the 8165.0 data cubes: June 2015. Evidence: I opened every archived release page (Jun 2003-Jun 2007 through Jun 2013-Jun 2017). The first release with an "LGA by industry division by employment/turnover size" cube is "Jun 2013 to Jun 2017" (released 20/02/2018, cubes 8165010 and 8165011, June 2015, 2016, 2017 sheets); the on-disk copy confirms this. Page: https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/8165.0Jun%202013%20to%20Jun%202017?OpenDocument=

What exists before that (all read from ABS archive pages):

| Release | Released | Geography of cubes | Notes |
|---|---|---|---|
| Jun 2003 to Jun 2007 | 14/12/2007 (cubes 21/12/2007) | Statistical Local Area (SLA), employment and turnover: `8165009.zip` (1,303,081 B), `8165010.zip` (1,570,975 B) | SLAs replaced an earlier postcode-based release (Feb 2007). Which June years the SLA cube holds: UNVERIFIED |
| Jun 2007 to Jun 2009 | 16/02/2011 (SLA cubes 02/05/2011) | Statistical Division (`sd_emp.xls` 907,776 B; `sd_turn.xls` 1,577,984 B) and SLA (`SLA_EMP.xls` 3,170,304 B; `SLA_TURN.xls` 4,386,304 B) | ABS notes multi-location businesses are attributed to one SLA only. SLAs are built from LGAs where these exist, so SLA-to-LGA aggregation is possible (inference; check the concordance). URL example: https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&SLA_EMP.xls&8165.0&Data%20Cubes&CBA875AA5B3291F6CA2577FF00114A7E&0&Jun%202007%20to%20Jun%202009&02.05.2011&Previous |
| Jun 2007 to Jun 2011 | 31/01/2012 | SA2 (`sa2_emp.xls`, `sa2_turn.xls`) and industry class by state only | no LGA cube |
| Jun 2008 to Jun 2012; Jun 2009 to Jun 2013; Jun 2010 to Jun 2014; Jun 2011 to Jun 2015; Jun 2012 to Jun 2016 | 2013-2017 | SA2 (`816507`, `816508`) and state; no LGA cubes | SA2 to LGA needs an ABS SA2-LGA correspondence (population-weighted) |
| Jun 2013 to Jun 2017 | 20/02/2018 | LGA (`8165010` employment, `8165011` turnover), Jun 2015-2017 | on disk |
| Later releases to Jul 2021-Jun 2025 | to 16/12/2025 | LGA | on disk (18 files) |

Better alternative for 2008-2014: ABS National Regional Profile (NRP, cat. 1379.0.55.001) is an LGA-level compendium built on ABS 8165.0. Its 2008-2012 explanatory notes (opened, https://www.abs.gov.au/AUSSTATS/abs@.nsf/Lookup/1379.0.55.001Explanatory+Notes12008+to+2012) state: LGAs are presented on 2012 boundaries within ASGS 2011; business counts by employment size and by industry and business entries and exits by employment size are given for 2008, 2009, 2010, 2011, 2012 (June snapshots) for LGAs; personal income (EPISA) 2008-2012; DVA age pension, service pension, income support supplement and DSS family tax benefit 2008-2012. See section 12 for the DSS payment items, whose year coverage is shorter.

NRP releases (pages opened): 2002-2006 (28/07/2008, SuperTABLE .srd), 2004-2008, 2005-2009 (22/11/2010; SuperTABLE plus a CSV), 2006-2010 (21/11/2011; SuperTABLE, CSV, LGA comparison xls), 2007-2011 (27/05/2013), 2008-2012 (04/07/2014), 2009-13 (29/06/2015; LGA 2013 boundaries per a search summary), 2010-14 (30/06/2016, marked "Ceased"). LGA economy zips (HEAD): 2007-2011 472,504 B; 2008-2012 488,524 B; 2009-13 448,264 B; 2010-14 784,749 B. CSVs: `nrp 2004-2009 csv file.csv` 13,234,831 B; `nrp 2004-2010 csv file.csv` 14,083,979 B; `nrp 2006-2010 lga comparison file.xls` 7,207,424 B. Cube contents by year were not opened.

The on-disk Data by Region files do not help before 2016 for business counts (rolling 5-year window; earliest June 2016 in the 2015-20 file).

---------------------------------------------------------------------

## 5. (d) SALM (DEWR Small Area Labour Markets)

- Publisher/dataset: Department of Employment and Workplace Relations, "SALM Smoothed LGA Datafiles (ASGS 2025) - March quarter 2026". Page https://www.dewr.gov.au/employment-research/resources/salm-smoothed-lga-datafiles-asgs-2025 ; methodology https://www.dewr.gov.au/employment-research/small-area-labour-markets/methodology (opened).
- Files: XLSX 576.18 KB and CSV 586.24 KB (page). The on-disk CSV is 600,309 B (= 586.24 KiB, so it is this file).
- Range: smoothed LGA estimates from the December quarter 2010 (methodology page). Smoothing is a four-quarter average (ABS 1367.2 note on the earlier DEEWR series).
- ASGS breaks (methodology page, paraphrased): SALM moved from the 2011 to the 2016 ASGS in the June quarter 2019 and from 2016 to 2021 in the September quarter 2023; the first smoothed estimate after a break comes three quarters later; regions with a break have a partial series. The ASGS-2025 LGA file dashes those.
- What the on-disk file shows (my calculation, Smoothed unemployment rate rows):

| State | LGAs | from Dec-10 | from Mar-20 (2011 to 2016 break) | from Jun-24 (2016 to 2021 break) |
|---|---|---|---|---|
| NSW | 129 | 122 | 2 | 5 |
| Vic | 80 | 78 | 1 | 1 |
| Qld | 77 | 52 | 9 | 16 |
| SA | 71 | 63 | 4 | 4 |
| WA | 137 | 84 | 17 | 36 |
| Tas | 29 | 28 | 1 | 0 |
| NT | 20 | 8 | 6 | 6 |
| ACT | 1 | 1 | 0 | 0 |
| All | 544 | 436 | 40 | 68 |

  No LGA has a gap after its first value. Consequence: for WA (84/137) and Qld (52/77) about a third to a half of LGAs have no pre-fire value for any 2010-2019 fire in this file; the missing LGAs are mostly small or remote.
- Earlier editions: DEWR says users can email SALM@dewr.gov.au for revised estimates on the 2011 or 2016 ASGS for past quarters (methodology page). The archived quarterly releases at docs.jobs.gov.au did not respond (connection failed).
- Pre-Dec-2010: ABS 1367.2 State and Regional Indicators Victoria (Dec 2009 issue, https://abs.gov.au/ausstats/abs@.nsf/Previousproducts/9A479914B1D43E57CA2576CE001B9543?opendocument=) says DEEWR published SLA-level estimates and an Excel workbook "Estimates of unemployment rate, By Local Government Area: Smoothed series", on the 2006 ASGC from March quarter 2008 (2001 benchmarks before). I could not find a live download for those files. UNVERIFIED that they still exist; ask DEWR or use the Census 2006/2011 unemployment rate by LGA (2011/2016 Census values are in Data by Region 14100DO0005 on disk) as the pre-fire unemployment proxy for 2005-2011 fires.
- data.gov.au also hosts AURIN copies "DJSB Small Area Labour Market - Unemployment Rate LGA 2010-2018 (LGA 2018)" (JavaScript download manager; not opened).

---------------------------------------------------------------------

## 6. (e) DSS payment recipients by LGA

- Publisher/dataset: Department of Social Services, "DSS Benefit and Payment Recipient Demographics - quarterly data" (data.gov.au, CKAN id `dss-payment-demographic-data`, metadata opened via API https://data.gov.au/data/api/3/action/package_show?id=dss-payment-demographic-data ) plus the machine-readable companion "DSS Payments by Local Government Area" (id 3c45b53c-c6c3-4fcb-9023-f05d95ab42a9).
- Earliest LGA-level quarter: September 2013. The dataset lists CSVs "Payment recipients by LGA and payment type" for Sep 2013, Dec 2013 (2013 LGA) and Mar 2014 (2014 LGA), then quarterly workbooks from Jun 2014. The dataset notes say geography includes LGA and SA2 "for 2015 onwards". Whether each quarterly workbook from Jun 2014 has an LGA tab: UNVERIFIED.
- On disk: Mar 2016 onward (all states), five LGA-vintage files (2014, 2018, 2020, 2022, 2024).

Files not on disk (HEAD sizes):

| Quarter | File | Size |
|---|---|---|
| Sep 2013 | CSV Payment recipients by LGA and payment type https://data.gov.au/data/dataset/cff2ae8a-55e4-47db-a66d-e177fe0ac6a0/resource/22801f16-c709-4e4b-9426-ba943bf7aaf7/download/september2013paymentrecipientsby2013localgovernmentarealgaandpaymenttype.csv | 149,042 B |
| Dec 2013 | CSV .../resource/b78f0c63-d6c9-463f-8ec3-338c2f6a4be0/download/december2013paymentrecipientsby2013localgovernmentarealgaandpaymenttype.csv | 151,918 B |
| Mar 2014 | CSV .../resource/e5232153-d057-4a58-9583-78f5e7a21d9c/download/march2104paymentrecipientsby2014localgovernmentarealgaandpaymenttype.csv | 151,913 B |
| Jun 2014 | xlsx .../resource/f0615bb3-463f-4352-902c-0b6bb0e22e7d/download/dss-demographics-june-2014-jan-2020-edit.xlsx | 1,100,863 B |
| Sep 2014, Dec 2014, Mar 2015, Jun 2015 | xlsx | 1,257,402; 1,233,147; 1,726,694; 1,719,096 B |
| Sep 2015 | xlsx .../resource/1cfde617-da6b-444a-9e97-584c596adb78/download/201509-dssdemographics.xlsx | 1,561,529 B |
| Dec 2015 | xlsx .../resource/6b3fba11-2f71-4df9-963d-fce31a7e59e3/download/demographics-december-2015-conf.xlsx | 1,591,530 B |
| Mar 2016 | xlsx | 1,713,206 B (already covered by the on-disk LGA csv) |

What a 2009 or Jan-2013 fire could use instead (none is a like-for-like replacement):
1. ABS NRP 2008-2012 pensions and allowances by LGA: DVA and FTB items 2008-2012; DSS Newstart, youth allowance, single parenting payment items are only available for fewer (later) years (section 12).
2. ABS Data by Region 14100DO0004 (on disk): "Selected Government pensions and allowances - at 30 June" by LGA from 2015 (e.g. Newstart 2015-2019, JobSeeker 2020). Gives a June-2015 baseline for Jan 2016 fires without the Dec 2015 quarterly workbook.
3. SALM unemployment (from Dec 2010) or Census unemployment (2006, 2011) as a labour-market stress proxy for the SL pillar.
4. I did not find any earlier LGA or postcode DSS/Centrelink series on data.gov.au (searches returned only annual "Income Support Customers" overview reports and ATO tax statistics).

---------------------------------------------------------------------

## 7. (f) Census DataPacks at LGA level

ABS DataPacks page (opened, JavaScript page; file list extracted from its source): https://www.abs.gov.au/census/find-census-data/datapacks . Base for downloads: `https://www.abs.gov.au/census/find-census-data/datapacks/download/<name>`.

| Census | Pack | Table with private dwellings | National LGA file | Size (HEAD) | On disk | LGA vintage |
|---|---|---|---|---|---|---|
| 2021 | GCP | G36 (your repo) | `2021_GCP_LGA_for_AUS_short-header.zip` | 13,827,380 B | NSW only (`2021_GCP_LGA_for_NSW...` 7,019,787 B) | LGA 2021 |
| 2016 | GCP | G32 (your repo) | `2016_GCP_LGA_for_AUS_short-header.zip` | 12,823,638 B | NSW only (6,817,415 B) | LGA 2016 |
| 2011 | BCP (Basic Community Profile) | B31 "Dwelling Structure" (ABS 2011.0.55.001 page, opened: https://www.abs.gov.au/ausstats/abs@.nsf/lookup/2011.0.55.001main+features1042011 ) | `2011_BCP_LGA_for_AUST_short-header.zip` | 9,445,666 B | no | LGA 2011 |
| 2011 | TSP (Time Series Profile) | not checked | `2011_TSP_LGA_for_AUST_short-header.zip` | 14,073,533 B | no | presumably 2006 and 2011 on 2011 LGAs (inference; verify) |
| 2016, 2021 | TSP | not checked | `2016_TSP_LGA_for_AUS_short-header.zip` 14,332,352 B; `2021_TSP_LGA_for_AUS_short-header.zip` 14,858,649 B | | no | |
| 2006 | Community Profile Series: BCP (45 tables), XCP (has dwelling structures) | Table number for BCP dwellings NOT verified | No national DataPack found. ABS page https://www.abs.gov.au/census/find-census-data/community-profiles/2006/0 offers one Excel per region (~1 MB each) for six profile types | size per region ~1 MB | no | ASGC 2006 |

Notes
- 2011 B31: "Total private dwellings" counted as occupied plus unoccupied private dwellings (search-result summary; the ABS page I opened confirms the table title B31 Dwelling Structure only).
- Census 2001 and earlier were not checked.

---------------------------------------------------------------------

## 8. (g) ABS ERP by LGA

- Product: ABS Regional population (cat. 3218.0 lineage; current cube names 32180DS000x). Latest release page https://www.abs.gov.au/statistics/people/population/regional-population/latest-release : reference period 2024-25 financial year, released 31/03/2026, next 25/03/2027; previous 2023-24, 2022-23, 2021-22.
- `32180DS0004_2001-25.xlsx` https://www.abs.gov.au/statistics/people/population/regional-population/2024-25/32180DS0004_2001-25.xlsx : 300,045 B, on disk. ERP at 30 June for 2001 to 2025 for 548 LGA codes on 2025 LGA boundaries (footnote), 2022-2024 revised, 2025 preliminary.
- `32180DS0004_2001-23.xlsx` (2022-23 release, 2023 boundaries) is on disk as P1/population_lga.xlsx.
- Vintage consequence: one file covers every candidate fire year (2005 to 2025) for every state on one boundary set. It is the natural denominator and the natural target boundary for crosswalking every other series.
- The 2019-20 release files on disk (P1/population_lga_2020*.xls) hold only 2019-2020 by state; not needed.

---------------------------------------------------------------------

## 9. (h) ASGS/ASGC LGA digital boundaries

Files opened/HEAD-checked (all national):

| Edition | Product | File | Size | On disk |
|---|---|---|---|---|
| LGA 2006 (ASGC) | 1259.0.30.002 | `1259030002_lga06aaust_shape.zip` (shape released 06/12/2011; original 14/07/2006) https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&1259030002_lga06aaust_shape.zip&1259.0.30.002&Data%20Cubes&5B3D3825D195847BCA25795D0024804A&0&2006&06.12.2011&Previous | 41,403,801 B | no |
| LGA 2007 | 1259.0.30.001 (Intercensal) | `1259030001lga07 aust.zip` | 41,602,062 B | no |
| LGA 2008 | same | `1259030001_lga08aaust_shape.zip` | 40,517,424 B | no |
| LGA 2009 | same (released 16/07/2009) | `1259030001_lga09aaust_shape.zip` https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&1259030001_lga09aaust_shape.zip&1259.0.30.001&Data%20Cubes&794C356BF1ABEF18CA2575F400174776&0&July%202009&16.07.2009&Latest | 41,290,643 B | no |
| LGA 2010 | same | `1259030001_lga10aaust_shape.zip` | 41,424,475 B | no |
| LGA 2011 (ASGC) | 1259.0.30.001 (14/07/2011) | `1259030001_lga11aaust_shape.zip` | 38,845,715 B | no |
| LGA 2011 (ASGS) | 1270.0.55.003 July 2011 (31/10/2011) | `1270055003_lga_2011_aust_shape.zip` https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&1270055003_lga_2011_aust_shape.zip&1270.0.55.003&Data%20Cubes&4A320EE17A293459CA257937000CC967&0&July%202011&31.10.2011&Previous | 37,724,971 B | no |
| LGA 2012 | 1270.0.55.003 July 2012 | page did not resolve; NRP uses "2012 boundaries" | unknown | no |
| LGA 2013 | July 2013 (23/07/2013) | `1270055003_lga_2013_aust_shape.zip` | 38,767,064 B | no |
| LGA 2014 | July 2014 (17/07/2014) | `1270055003_lga_2014_aust_shape.zip` | 38,873,853 B | no |
| LGA 2015 | July 2015 (17/07/2015) | `1270055003_lga_2015_aust_shape.zip` | 38,873,853 B (identical size to 2014; may be identical content, unverified) | YES P1/lga_2015 (581 features, LGA_CODE15) |
| LGA 2016 | July 2016 (07/11/2018) | `1270055003_lga_2016_aust_shape.zip` | 40,410,494 B | YES P1/lga_2016 |
| Correspondence LGA 2011 to LGA 2016 | 1270.0.55.003 July 2016 | `1270055003_cg_lga_2011_lga_2016.002.zip` | 60,154 B | no |
| LGA 2018, 2020, 2021, 2023 | | | | YES (P1/lga_2018, 2020, 2021, 2023) |
| Ed 3 correspondences | https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/correspondences | `CG_LGA_2016_LGA_2021.csv`, `CG_LGA_2020_LGA_2021.csv`, `CG_LGA_2021_LGA_2022.csv`, `CG_2022_LGA_2023_LGA.csv` (28,806 B), `CG_LGA_2023_LGA_2024.csv`, `CG_LGA_2024_LGA_2025.csv` | mostly size unknown (HEAD returned 200 without length) | no (custom crosswalks on disk instead) |
| LGA 2025 | Ed 3 boundary page | `LGA_2025_AUST_GDA94.zip`, `LGA_2025_AUST_GDA2020.zip` | size unknown | no |

Which boundary for which fire (my recommendation; polygons are for overlaying fire footprints):
- 2005 (Wangary Jan 2005): LGA 2006 ASGC (the 2005 edition is not listed; SA LGAs changed little). SA has 68-71 LGAs so risk is small.
- 2009 (Black Saturday): ASGC LGA 2009.
- 2011 (WA Feb 2011): ASGC LGA 2011 or ASGS LGA 2011.
- Jan/Oct 2013: LGA 2013. Jan 2014, Feb 2014: LGA 2014.
- SA Jan 2015, SA Nov 2015, Vic Dec 2015, Tas/WA Jan 2016: LGA 2015 (on disk) or 2016 (on disk). NSW amalgamations (12 May 2016) do not matter for these non-NSW fires.
- Qld Nov 2018, 2019-20: LGA 2018 or 2020 (on disk).
- WA Feb 2021: LGA 2021 (on disk).
Recommendation: overlay on the boundary edition matching the fire year, then aggregate every LGA-level series to a single target boundary set (suggest 2025, the ERP edition) with the correspondences above. Pre-2016 to modern needs the ABS 2011-to-2016 correspondence plus the Ed 3 chain, or the existing custom intersection crosswalks.

---------------------------------------------------------------------

## 10. (i) Geoscience Australia national historical bushfire boundaries

- Product: "Historical Bushfire Boundaries - Version 2.0" (data.gov.au id `historical-bushfire-boundaries-version-2-0`, metadata modified 2026-01-09; opened via CKAN API). Download https://d28rz98at9flks.cloudfront.net/149017/149017_00_0.zip = 458,831,604 B, exactly the on-disk `ga_original.zip`.
- Source states: aggregation of jurisdiction-supplied burnt-area polygons from the early 1900s to 2023, excluding the Northern Territory; includes bushfires and prescribed burns; "may, or may not, represent all fire history" per jurisdiction; produced under the National Bushfire Intelligence Capability. Temporal coverage metadata 1899-12-30 to 2023-10-15. Version 1.0 (427.6 MB) also listed.
- My read of the on-disk attribute table (310,640 polygons, 157,496 prescribed burns, 61,060 bushfires, 92,083 "Unknown"):

| State | Polygons | First year | Last year | Note |
|---|---|---|---|---|
| ACT | 1,903 | 1920 | 2023 | agency ACT PSC |
| NSW | 35,366 | 1899 | 2023 | 44.8% have no ignition date; agency field is NSW PWS for all rows |
| Qld | 15,227 | 1930 | 2023 | agency is QPWS for 15,197 rows and DAF for 30: protected estate and Parks-managed land only. Qld fires outside parks (Qld Fire and Emergency Services) are not visible |
| SA | 6,375 | 1931 | 2023 | agency SA DEW |
| Tas | 8,412 | 1961 | 2022 | 2023 has no rows |
| Vic | 77,463 | 1903 | 2022 | 2023 has no rows |
| WA | 165,894 | 1922 | 2023 | 447 polygons in 2023 vs 1,000s in earlier years |
| NT | 0 | none | none | absent |

- Candidate events found (ignition date, area): Black Saturday Vic 7 Feb 2009 (116,586 ha, 68,931 ha, 54,553 ha, 32,300 ha etc.; polygons mostly unnamed); Wangary SA 10 Jan 2005 (77,170 ha); Tas 3 Jan 2013 (Inala Road-Forcett 23,378 ha; Giblin River 40,488 ha); NSW Wambelong 12 Jan 2013 (55,204 ha) and State Mine Oct 2013 (54,429 ha); WA Feb 2011 Banovich 7,356 ha; WA Jan 2014 large unnamed polygons on 12 Jan 2014; SA Sampson Flat Jan 2015 (11,530 ha) and Pinery Nov 2015 (78,505 ha); Vic Wye River Dec 2015 (2,523 ha); Tas Jan 2016 (Pipeline Rd & Rulla Rd 61,830 ha); SA Ravine/Cudlee Creek/KI Complex Dec 2019; Vic 2019-20 Snowy Complex etc.; WA Wooroloo Feb 2021 (10,750 ha); Qld Nov 2018 only via QPWS national-park fires (e.g. Deepwater NP 28,657 ha).
- Known omissions / risks: (1) NT absent. (2) Qld coverage is QPWS estate only. (3) I could not find the WA Waroona/Yarloop fire (6 Jan 2016) by name (Waroona, Yarloop, Preston, Harvey) or as a large polygon in 5-10 Jan 2016; the largest 8 Jan 2016 record is 14,382 ha "Telegraph/Warrenup Rd"; treat as possibly missing (unverified). (4) Tas and Vic end in 2022. (5) Many WA/Vic polygons have no name.
- Related: NRRA "2019-20 Financial Year Bushfire Boundaries" (data.gov.au, ~0.9 GB gdb, ~1.5 GB shapefile) is a separate national product for FY2019-20 only (not needed).

---------------------------------------------------------------------

## 11. (j) Event registers: can they reproduce "declared event x council"?

| Register | Publisher | URL (opened) | Years | Unit / fields | Machine-readable? | Reproduces declared event x council? |
|---|---|---|---|---|---|---|
| DRFA Activation History by LGA | National Emergency Management Agency (NEMA), data.gov.au | https://data.gov.au/data/dataset/drfa-activation-history-by-lga ; CSV https://data.gov.au/data/dataset/10ba7303-e3af-41b4-98b5-e04db77caea8/resource/ada7908b-afe6-48f3-966b-789aa26c1391/download/drfa_activation_history_by_location_2026_august_11.csv (367,919 B, HEAD) | Title says "2006 to current". In the catalogue's datastore (2,475 rows) the earliest row is 2017-09-08 (AGRN 776, Tenterfield bushfires); a search for "2009" finds 0 rows; rows whose text matches "2017-" to "2026-": 3, 21, 16, 107, 442, 584, 344, 419, 502, 250 | Columns: Location_Name, Location_Type, Location_code, STATE, event_name, agrn, cat_A, cat_B, cat_C, cat_D, highest_drfa_category_group, AGDRP, DRA, hazard_type, disaster_start_date | Yes (CSV, plus CKAN datastore API) | YES for events from Sep 2017 with LGA codes. Bushfire rows by state: NSW 139, Vic 52, Qld 71, WA 7, Tas 11, NT 19, SA 0, ACT 0. Wooroloo (WA, 1 Feb 2021, AGRN 950) present; no rows matching Oct 2019 or Dec 2019 (0 each; Sep 2019 has 7, Nov 2019 has 4, Jan 2020 has 13 mostly NT) so Black Summer is essentially absent, and no SA rows for Cudlee Creek/Kangaroo Island; a Qld Nov 2018 search for "Gracemere"/"Eungella" returns 0. So 2019-20 needs a separate list (below). NO for 2005-2016 |
| NRRA "Disaster Recovery Data for Local Government Areas" (Black Summer) | National Recovery and Resilience Agency, data.gov.au | https://data.gov.au/data/dataset/2020-local-government-interactive-map-dataset | FY2019-20 Black Summer | CSV "Black Summer Bushfire Recovery Data" 402,848 B (catalogue size) | Yes | Likely for 2019-20 by LGA across states (content unopened) |
| DisasterAssist | Home Affairs, moved toward NEMA (site notes a new National Emergency Management Agency; list page last updated 22/09/2024; home page 20/01/2026) | https://www.disasterassist.gov.au/find-a-disaster/australian-disasters | Not stated on the static page. Its NDRRA page covers "eligible events up to and including 31 October 2018"; DRFA covers events from 1 Nov 2018 (https://www.disasterassist.gov.au/disaster-arrangements/natural-disaster-relief-and-recovery-arrangements ; .../disaster-recovery-funding-arrangements). The homepage says it lists Local Government Areas declared natural disasters | Table columns (from the page script): start month-year, end, state, disaster types, name (link), AGRN. Filled by an undocumented POST to `/_layouts/15/api/Data.aspx/FilterDisasters` (my one probe with a guessed payload returned HTTP 500; I stopped) | Not in a supported way | Possible only by opening event pages (per-event LGA lists not verified) or scraping; not a clean table. Depth of history unknown (I could not enumerate events without running the page's JavaScript) |
| ICA Historical Catastrophe List | Insurance Council of Australia | Data hub https://insurancecouncil.com.au/resources/data-hub/ (via WebFetch; direct HTTP gets 403). On disk edition: `ICA-Historical-Normalised-Catastrophe-June-2024.xlsx` https://insurancecouncil.com.au/wp-content/uploads/2024/07/ICA-Historical-Normalised-Catastrophe-June-2024.xlsx (229,642 B). Newer: `ICA-Historical-Normalised-Catastrophe-Master-Updated-2026_07.xlsx` https://insurancecouncil.com.au/wp-content/uploads/2026/08/ICA-Historical-Normalised-Catastrophe-Master-Updated-2026_07.xlsx (273,626 B) | 1967 to Apr 2024 (June-2024 file): 737 events, 50 typed Bushfire | Fields: CAT Name, Event Name, Event Start/Finish, FY, State, Town, Description, Location, Type, Year, Postcode (list), Original and Normalised (2022) loss, Claims Count, six domestic and four commercial claim counts | Yes (xlsx) | Event yes, council no. Postcode list is filled for only 7.6% of events (56); for bushfires it is present from 2013 (Tasman Peninsula 12 postcodes, Warrumbungle 4, Blue Mountains 12, Perth Hills Jan 2014 18, Sampson Flat 11, Pinery 25, Great Ocean Rd 1, Yarloop 13, Tathra 24, Bunyip 35, CAT195 159, Perth Hills 2021 4). No postcode list for Wangary CAT051, Black Saturday CAT093 (loss $1.07bn), WA CAT116 |
| AIDR Knowledge Hub "Australian disasters | Disaster Mapper" | Australian Institute for Disaster Resilience | https://knowledge.aidr.org.au/disasters/ | Page offers a year filter 1876-2026 and hazard categories (script driven) | Not found | No download or LGA field found on the page | Unlikely to reproduce the unit; useful only to cross-check event dates and names |

ICA bushfire CATs that match the candidate list (from the June-2024 file): CAT051 SA 10 Jan 2005 ($27.7m); CAT093 Black Saturday 7 Feb 2009 ($1,070m); CAT116 WA 5 Feb 2011; CAT131 Tas Tasman Peninsula 3 Jan 2013; CAT132 Warrumbungle 7 Jan 2013; CAT135 Blue Mountains 17 Oct 2013; CAT141 Perth Hills 12 Jan 2014; CAT151 Sampson Flat 2 Feb 2015; CAT156 Pinery 26 Nov 2015; CAT158 Great Ocean Rd 24 Dec 2015; CAT161 Yarloop 6 Jan 2016; CAT195 2019/20 (NSW, Qld, SA, Vic); CAT211 Perth Hills 1 Feb 2021. No separate ICA CAT for the Qld Nov 2018 fires (an "Undeclared" or absent). Undeclared Tasmania Jan 2016 exists.

---------------------------------------------------------------------

## 12. Things I could not verify

- SEIFA 2001 zip contents (LGA level or not); ABS 2001 LGA vintage.
- The 2006 Census Basic Community Profile table number for private dwellings, and a national 2006 LGA file (none found; per-region Excel only).
- Whether each DSS quarterly workbook Jun 2014 to Dec 2015 has an LGA tab.
- NRP contents: which items exist for which years for LGAs (the availability grid in the 2008-2012 notes suggests DSS Newstart, youth allowance and parenting payment items cover fewer years than business counts and income). NRP 2004-2009/2004-2010 CSV contents unopened.
- EPISA 2005-06 to 2010-11 LGA cube: state completeness and LGA edition.
- Which June years the 2003-2007 and 2007-2009 SLA business cubes hold.
- Pre-Dec-2010 SALM LGA files: existence and URL.
- DisasterAssist: earliest event, whether every old event has an LGA list.
- NRRA Black Summer recovery CSV fields.
- Waroona/Yarloop 2016 polygon in GA.
- WebSearch was capped mid-task, so a few planned lookups (2006 dwelling table, older DSS/Centrelink series) were not possible.

---------------------------------------------------------------------

## 13. Per-pillar table: can it be rebuilt for a non-NSW / earlier fire?

Legend: Y = yes from files on disk; Y* = yes after a listed download; P = partial or proxy; N = no LGA series found. Fires: 2009 = Black Saturday (Vic); 2013 = Tas/NSW Jan 2013 and NSW Oct 2013; 2015-16 = SA Jan 2015, SA/Vic Nov-Dec 2015, Tas/WA Jan 2016; 2019-20 = Vic/SA/Qld/WA.

| Pillar / input | NSW indicator | Source | Year range at LGA, all states | Rebuild 2009? | 2013? | 2015-16? | 2019-20? | State-specific gaps |
|---|---|---|---|---|---|---|---|---|
| DL denominator | Private dwellings, G32 (2016), G36 (2021) | ABS Census GCP / BCP | 2011 (B31), 2016, 2021 national packs; 2006 per-region xls | P (2006 xls per LGA, or 2011 B31 with time-mismatch) | Y* (2011 B31, 9.4 MB) | Y* (2016 G32 national, 12.8 MB; GCP on disk is NSW-only) | Y* (2016 G32 national) | WA/Qld/NT remote LGAs have suppressed cells; LGA vintage 2011/2016/2021 |
| DL numerator | Homes destroyed (per-council reports) | not this slice | | | | | | |
| IL income | Excess % change in PIA total income | PIA (2011-12+), EPISA (2001-02 to 2010-11) | FY2001-02 to 2022-23 | Y* (`do003_200506201011.xls`) | Y (pia_2020.xls, FY2011-12 onward) | Y | Y (pia_old_total, pia_2024, pia_total) | EPISA to PIA break at 2010-11/2011-12; ACT has no LGAs (one unit) |
| IL business counts | Excess % change in CABEE LGA counts | CABEE (LGA from Jun 2015); NRP 2008-2014; SLA cubes 2007-2009 | Jun 2007-2014 via NRP/SLA; Jun 2015-2025 CABEE | Y*/P (NRP 2008-2012 LGA 2012; or SLA_EMP aggregated) | Y* (NRP 2008-12/2009-13) | Y (CABEE Jun 2015, 2016 on disk) | Y (CABEE) | Jun 2015/2016 sheets use pre-amalgamation NSW LGAs (irrelevant outside NSW); NT/WA have unincorporated areas coded as separate units |
| IL entries/exits | (if used) | DBR 2017+, NRP 2008-2012 | | Y* (NRP) | Y* (NRP) | P (none 2014-16 at LGA; CABEE entries/exits cubes are not LGA) | Y (DBR 2017+) | |
| FP | OLG council finance | other agent | | | | | | |
| SL income support | Excess rise in recipients per 1,000 | DSS quarterly by LGA | Sep 2013 to Jun 2026 | N (no pre-2013 LGA series; NRP DVA/FTB or SALM as proxies) | N for Jan 2013 (no baseline); Y* for Oct 2013 (Sep 2013 CSV) | Y* for Nov 2015-Jan 2016 (Sep and Dec 2015 workbooks) and for Jan 2015 (Dec 2014); Y for anything from Mar 2016 | Y (on disk) | 2013-14 quarters are on 2013/2014 LGAs; pre-2016 NSW has 153 LGAs |
| SL deaths | | not this slice | | | | | | |
| X SEIFA IRSD | IRSD score/decile | ABS SEIFA | 2001 (unv), 2006, 2011, 2016, 2021 | Y* (2006 LGA, 697,856 B) | Y* (2011 LGA, 667,136 B; or 2006) | Y (2016 on disk; strict pre-fire 2011 Y*) | Y (2016 on disk) | Different scaling per census; use decile |
| X income | PIA median income | PIA/EPISA | as above | Y* | Y | Y | Y | as above |
| X unemployment | SALM smoothed rate | DEWR SALM | Dec-10 to Mar-26 | N (pre-Dec-10; Census 2006 unemployment proxy) | Y (Dec-10 onward, 436/544 LGAs) | Y (same) | P: 436 LGAs; 40 LGAs first estimate Mar-20 (after Dec-19 fires); 68 LGAs first estimate Jun-24 | WA has only 84/137, Qld 52/77, NT 8/20 with a pre-2020 value |
| X population | ERP | ABS 32180DS0004 | 2001-2025 | Y | Y | Y | Y | 2025 boundaries; back-cast |
| X remoteness, industry shares | | ABS RA; Census | | not this slice / Y* for industry (Census) | | | | |

---------------------------------------------------------------------

## 14. Files to download that are NOT already on disk

### A. Needed for pre-2015 fires (Wangary 2005, Black Saturday 2009, WA 2011, NSW/Tas Jan 2013, NSW Oct 2013, WA/Vic 2014)

| # | Purpose | File | URL | Size |
|---|---|---|---|---|
| A1 | Income FY2003-04 (Wangary pre-fire) | EPISA `6524055002do005_200102200506.xls` | https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&6524055002do005_200102200506.xls&6524.0.55.002&Data%20Cubes&0AFFEAA09BFF4C6ACA257521000D6348&0&2001-02%20to%202005-06&17.12.2008&Latest | 934,912 B |
| A2 | Income FY2004-05 (Wangary fire year) | EPISA `do007_200102200506.xls` | https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&6524055002do007_200102200506.xls&6524.0.55.002&Data%20Cubes&DE95CA5AAF7856CBCA257521000D6544&0&2001-02%20to%202005-06&17.12.2008&Latest | 947,200 B |
| A3 | Income FY2005-06 to 2010-11 (Black Saturday, WA 2011) | EPISA `6524055002do003_200506201011.xls` | https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&6524055002do003_200506201011.xls&6524.0.55.002&Data%20Cubes&7E5B1952AA505ECDCA257C12000CA87B&0&2005-06%20to%202010-11&29.10.2013&Latest | 1,019,904 B |
| A4 | Business counts Jun 2008-2012 by LGA (2012 LGAs) plus income, DVA/FTB payments | NRP `national regional profile, economy, lga, 2008-2012.zip` | https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&national%20regional%20profile,%20economy,%20lga,%202008-2012.zip&1379.0.55.001&Data%20Cubes&8F23880EEA1C57A1CA257D0A0011782D&0&2008%20to%202012&04.07.2014&Latest | 488,524 B |
| A5 | Same for Jun 2007-2011 (older LGA edition) | NRP `national regional profile, economy, lga, 2007-2011.zip` | https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&national%20regional%20profile,%20economy,%20lga,%202007-2011.zip&1379.0.55.001&Data%20Cubes&A9647037ED70FAE8CA257B75001B118B&0&2007%20to%202011&27.05.2013&Previous | 472,504 B |
| A6 | Jun 2013 and 2014 business counts | NRP economy LGA 2009-13 and 2010-14 zips | https://www.abs.gov.au/AUSSTATS/SUBSCRIBER.NSF/log?openagent&1379055001_economy_2009-2013_lga_201506.zip&1379.0.55.001&Data%20Cubes&DC45B9F767450EB4CA257E70001519A8&0&2009-13&29.06.2015&Latest ; https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&1379055001_economy_2010-2014_lga_201606.zip&1379.0.55.001&Data%20Cubes&5622F64E4A0E1742CA2580360016C571&0&2010-14&23.09.2016&Latest | 448,264 B; 784,749 B |
| A7 | Optional: NRP population and industry LGA 2008-2012 | `national regional profile, population, lga, 2008-2012.zip`; `... industry, lga, 2008-2012.zip` | pages https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/1379.0.55.0012008+to+2012 | 449,734 B; 160,182 B |
| A8 | Optional 2004-2010 all-region LGA CSV (2005-2009 release) and (2006-2010 release) | `nrp 2004-2009 csv file.csv`; `nrp 2004-2010 csv file.csv` | https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&nrp%202004-2009%20csv%20file.csv&1379.0.55.001&Data%20Cubes&545FE21CB8A1A642CA25785D000DE95F&0&2005%20to%202009&25.03.2011&Latest ; https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&nrp%202004-2010%20csv%20file.csv&1379.0.55.001&Data%20Cubes&72FA2883275E0F35CA25793D000CAC8B&0&2006%20to%202010&04.11.2011&Previous | 13,234,831 B; 14,083,979 B |
| A9 | Business counts Jun 2007-2009 by SLA (Black Saturday) | 8165.0 `SLA_EMP.xls` | https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&SLA_EMP.xls&8165.0&Data%20Cubes&CBA875AA5B3291F6CA2577FF00114A7E&0&Jun%202007%20to%20Jun%202009&02.05.2011&Previous | 3,170,304 B |
| A10 | Business counts near Wangary (SLA 2003-2007) | 8165.0 `8165009.zip` | https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&8165009.zip&8165.0&Data%20Cubes&E530CAB1491CE443CA2573B70011AD1A&0&Jun%202003%20to%20Jun%202007&21.12.2007&Latest | 1,303,081 B |
| A11 | SEIFA 2006 LGA | `2033055001_ seifa, local government areas, data cube only, 2006.xls` | URL in section 2 | 697,856 B |
| A12 | SEIFA 2011 LGA | `2033.0.55.001 lga indexes.xls` | URL in section 2 | 667,136 B |
| A13 | SEIFA 2001 (Wangary) | `AUS.zip` | URL in section 2 | 9,229,178 B (contents unverified) |
| A14 | DSS Oct-2013 baseline and 2014 fires | Sep 2013, Dec 2013, Mar 2014 LGA CSVs | URLs in section 6 | 149,042; 151,918; 151,913 B |
| A15 | Census dwellings and industry | 2011 BCP LGA national (`2011_BCP_LGA_for_AUST_short-header.zip`); optional 2011 TSP LGA (`2011_TSP_LGA_for_AUST_short-header.zip`) | https://www.abs.gov.au/census/find-census-data/datapacks/download/2011_BCP_LGA_for_AUST_short-header.zip | 9,445,666 B; 14,073,533 B |
| A16 | LGA boundaries for overlay | ASGC LGA 2006, 2009; ASGS LGA 2011, 2013, 2014; correspondence LGA 2011 to 2016 | URLs in section 9 | 41,403,801; 41,290,643; 37,724,971; 38,767,064; 38,873,853; 60,154 B |
| A17 | Event names/dates | ICA July-2026 list (optional; June-2024 already on disk) | section 11 | 273,626 B |
| A18 | SALM Dec 2008 to Sep 2010 LGA | no public file found | ask salm@dewr.gov.au | n/a |

### B. Needed for post-2015 non-NSW fires (2015-16, 2019-20, WA 2016/2021, Qld 2018-19)

Already national and on disk: CABEE (Jun 2015-2025), PIA (FY2011-12 to 2022-23), DSS (Mar 2016 on), SALM (Dec-10 on), ERP (2001-2025), SEIFA 2016 and 2021, LGA boundaries 2015-2023, DBR.

| # | Purpose | File | URL | Size |
|---|---|---|---|---|
| B1 | Dwellings and industry, national | `2016_GCP_LGA_for_AUS_short-header.zip`; `2021_GCP_LGA_for_AUS_short-header.zip` | https://www.abs.gov.au/census/find-census-data/datapacks/download/2016_GCP_LGA_for_AUS_short-header.zip ; .../2021_GCP_LGA_for_AUS_short-header.zip | 12,823,638 B; 13,827,380 B |
| B2 | DSS baseline before Jan 2016 fires (Dec 2015; Sep 2015 for Nov-Dec 2015 fires; Dec 2014 for Jan 2015) | DSS Demographics Dec 2015, Sep 2015, Dec 2014 workbooks (LGA tab unverified) | URLs in section 6 | 1,591,530; 1,561,529; 1,233,147 B |
| B3 | Declared LGAs, events from Sep 2017 (Qld 2018, WA 2021, Vic/Qld 2019-20 where present) | NEMA DRFA Activation History CSV | section 11 | 367,919 B |
| B4 | Declared LGAs, Black Summer | NRRA "Black Summer Bushfire Recovery Data" CSV | https://data.gov.au/data/dataset/2020-local-government-interactive-map-dataset | 402,848 B (catalogue) |
| B5 | Missing SALM pre-2020 values for 108 LGAs (40 + 68) | request from DEWR (SALM on 2011 and 2016 ASGS) | salm@dewr.gov.au | n/a |
| B6 | Qld fire polygons outside parks | not in GA v2.0; other agent | | |

---------------------------------------------------------------------

## 15. Source URLs actually opened (index)

ABS SEIFA: 2033.0.55.0012001, 2006, 2011, 2016 DetailsPages; SEIFA 2021 latest-release page; 2021 methodology page. ABS PIA: personal-income-australia (all-releases page), latest-release (2022-23), EPISA DetailsPages 2001-02 to 2005-06 and 2005-06 to 2010-11, EPISA 2005-06 to 2010-11 Explanatory Notes, EPISA 2011-2016 and 2012-13 pages. ABS 8165.0: DetailsPages Jun 2003-Jun 2007, Jun 2007-Jun 2009, Jun 2007-Jun 2011, Jun 2008-2012 through Jun 2013-Jun 2017, and latest-release page (Jul 2022-Jun 2026, released 18/08/2026, national/state only); ABS 8165.0 Explanatory Notes Jun 2007 to Jun 2009. ABS NRP 1379.0.55.001: DetailsPages 2002-2006, 2005 to 2009, 2006 to 2010, 2007 to 2011, 2008 to 2012, 2009-13, 2010-14; Explanatory Notes 2008 to 2012. ABS ASGC/ASGS boundaries: 1259.0.30.001 (2007-2011), 1259.0.30.002 (2006), 1270.0.55.003 (2011, 2013-2016), ASGS Ed 3 correspondence and boundary-file pages. ABS Census: DataPacks page, 2011.0.55.001, 2006 community-profile pages. ABS Regional population latest-release. DEWR SALM pages and resource page. data.gov.au CKAN API: DSS (both datasets), GA v2.0, DRFA Activation History (schema and a few count queries only), NRRA datasets. DisasterAssist pages (home, list, NDRRA, DRFA) and its `disasterSearch.js`. ICA data hub (WebFetch) and ICA workbook on disk. AIDR Knowledge Hub disasters page. ABS 1367.2 Victoria Dec 2009.
