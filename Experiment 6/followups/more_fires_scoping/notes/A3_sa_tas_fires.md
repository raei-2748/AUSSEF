# A3. South Australia and Tasmania fires, 2003-2021 (scoping notes)

Written 2026-09-29. Scope: real fires only. Nothing downloaded; only web pages and report PDFs were read (some PDFs were streamed into memory and text-searched, none saved).

Labels: **R** = reported (a source states it). **E** = estimated (I derived it; arithmetic shown). **J** = judgement.

## 0. How to read this / limits of this pass

- The session's WebSearch budget ran out part-way through (200 calls, shared). Tasmania 2016 / 2018-19 / 2019-20 were therefore covered through direct fetches of AIDR, AFAC and TFS documents, not further searching.
- Blocked or walled sources (not read, so figures from them are absent): the Tasmanian Bushfires Inquiry report (dpac.tas.gov.au: Cloudflare, then a login redirect), the SA Recovery site (recovery.sa.gov.au: sign-in wall; holds the Cudlee Creek and Kangaroo Island recovery plans), pressreader/Guardian (Cloudflare challenge; I did not try to bypass), several council sites for WebFetch (I read those through the browser pane instead).
- ICA Historical Catastrophe List is a data file: https://insurancecouncil.com.au/wp-content/uploads/2022/05/ICA-Historical-Catastrophe-List-April-2022.xlsx, HEAD Content-Length 224,645 bytes. **Not opened** (rule 1). Insured-loss figures below come from AIDR/ABC text instead.
- SA Pinery per-council statistics file: https://data.sa.gov.au/data/dataset/2bada993-8377-49ef-b0f4-c9cffadc02b6/resource/b8274025-6535-4641-b1d0-a66a75c81f2c/download/state-recovery-pinery-fire-statistics.xlsx, HEAD Content-Length 66,501 bytes. **Not opened.** A per-LGA table from it is already reproduced in section 3 (via AIDR).
- Sources avoided: Wikipedia and ACM mastheads. One caution: the AIDR Knowledge Hub Tasmanian pages list The Examiner (an ACM masthead) among AIDR's own underlying sources. I used only AIDR's text, not the masthead.
- Council areas: taken from SA Government "Local Councils" pages, ESCOSA advice PDFs, council sites and annual reports. The SA council-area sources disagree by 0-3% (e.g. Barossa 893.5 vs 912 km2; Adelaide Plains 926 vs 935; Lower Eyre 4,754 vs 4,771). This does not change any >=5% / >=20% call. **Tasmanian council areas were only verified for Sorell (583 km2). Tasman (659.3 km2) is from a search-result snippet of tasman.tas.gov.au whose page returned 404 when I opened it: treat as unverified.** All other Tasmanian council areas are unverified; compute them from the ABS LGA boundary attribute table on your disk.
- Best sources by strength: SA CFS bushfire history (primary), SA Deputy Coroner's Wangary findings (primary), Pinery Recovery Final Report table (via AIDR evaluation), TFS Fireground magazine with the DPIPWE fire-area map (primary), DisasterAssist pages (primary), council annual reports/financial statements (primary).

## 1. Candidate list (2003-2021) that meets the inclusion rule

Inclusion rule: >=10 homes destroyed, or any death, or a bushfire natural-disaster declaration, or one fire >=20,000 ha reaching populated or farmed land.

### South Australia

| # | Event (dates) | Ha (source) | Homes destroyed (source; what is counted) | Deaths | Councils (names of the time) |
|---|---|---|---|---|---|
| S1 | **Wangary / Lower Eyre Peninsula** 10-20 Jan 2005 (main run 11 Jan) | 77,964 (Deputy Coroner) [R]; ~78,000 (CFS); ~82,000 (AIDR) | 93 "houses destroyed or significantly damaged" (Coroner); 93 houses (CFS); 79 houses destroyed + 26 extensively damaged (AIDR) | 9 civilian; 115 injured (Coroner) | District Council of Lower Eyre Peninsula (main); fire ran to outskirts of City of Port Lincoln. Any Tumby Bay share unverified |
| S2 | **Kangaroo Island** 6-16 Dec 2007 (lightning; 6 major fires) | 90,982 (CFS) [R] | none reported (CFS lists ~3,000 ha agri/forestry assets destroyed) | 1 | Kangaroo Island Council (single council) |
| S3 | **Eden Valley** 17-20 Jan 2014 | ~25,000 (CFS) | 4 houses lost of 371 in the scar (CFS) | 0 | Barossa and/or Mid Murray (both in the declaration); split unknown |
| S4 | **Bangor** 1 Jan-14 Feb 2014 (note: not Nov 2014) | >35,000 (CFS) | 5 houses (CFS) | 0 (24 minor injuries) | Mount Remarkable (declared); possibly Port Pirie Regional / Northern Areas. Unverified |
| S5 | **Sampson Flat** 2-9 Jan 2015 (Adelaide Hills) | 12,569 (CFS research page); 12,600 (CFS history); 12,500 (AIDR); "more than 13,000" (Adelaide Hills Council) | ~24 houses, 103 sheds (CFS); 24 homes "in the Council area" (AHC); 27 homes (AIDR) | 0 (134 injured, mostly firefighters) | Adelaide Hills (dominant); declared also Playford, Tea Tree Gully, Barossa |
| S6 | **Pinery** 25 Nov-2 Dec 2015 | 82,500 (CFS); 82,600 (Pinery Recovery Final Report) | ~91 (CFS, ABC 19 Dec); **97 private dwellings destroyed** (Recovery Final Report, via AIDR); 87 (ABC 30 Nov, early) | 2 | Light, Wakefield, Mallala/Adelaide Plains, Clare & Gilbert Valleys |
| S7 | **Yorketown / Edithburgh** 20-29 Nov 2019 | >5,000 (AIDR MIR) | 8 dwellings (CFS); 7 homes (AIDR MIR) | 0 | Yorke Peninsula (declared; borderline candidate) |
| S8 | **Cudlee Creek** 20 Dec 2019-3 Jan 2020 | 23,295 (CFS); ~23,000 (AIDR MIR) | 85 homes (CFS); 84 (AIDR MIR); 86 (ABC, 23 Dec 2019 headline) | 1 (elderly man at Charleston); 51 firefighter injuries (CFS) | Adelaide Hills (dominant; AHC says ~30% of its district directly impacted); declared also Mount Barker, Mid Murray |
| S9 | **Kangaroo Island complex** (Menzies, Duncan, Ravine) 20 Dec 2019-21 Jan 2020 (safe 7 Feb) | 211,474 (CFS); 211,228 (independent After-Action Review) | **87 "dwellings" (CFS)**; 87 "homes and other significant built assets, incl. Southern Ocean Lodge" (AAR); 87 homes (ESCOSA); **56 homes** (AIDR MIR + Black Summer page) | 2 | Kangaroo Island Council (single council) |
| S10 | **Keilira** 30 Dec 2019-9 Jan 2020 | 26,000 (CFS); >25,000 (Kingston DC) | 3 homes (only 1 occupied; 2 unused farmhouses) (Kingston DC; CFS) | 0 | District Council of Kingston |

Minor SA events that meet only the declaration rule (all small; not recommended): Tulka (11 Nov 2012) and Coomunga (20 Nov 2012), both Lower Eyre Peninsula, counter-disaster/asset assistance; Bundaleer (16 Jan 2013), Northern Areas; Cherryville (9-12 May 2013), Adelaide Hills; Tantanoola (2 Jan 2015), Wattle Range. Large conservation-park fires in Jan 2014 (Ngarkat complex >90,000 ha; Ceduna complex 46,000 ha; Billiatt) are declared for counter-disaster costs but reached no populated land and destroyed no homes (CFS): excluded. Also below threshold and undeclared as far as I can tell: Proper Bay 13 Jan 2009 (4 houses), Port Lincoln 23 Dec 2009 (6 houses, 650 ha), Blackford/Lucindale 11 Jan 2021 (14,074 ha, 27 structures), Cherry Gardens Jan 2021 (2 houses), Duck Ponds 11 Nov 2019 (2 homes, 228 ha). [CFS bushfire history]

### Tasmania

| # | Event (dates) | Ha (source) | Homes destroyed (source; what is counted) | Deaths | Councils |
|---|---|---|---|---|---|
| T1 | **Forcett-Dunalley ("Inala Road-Forcett")** 3-18 Jan 2013 | 25,197 (DPIPWE Emergency Services GIS map printed in TFS Fireground Spring 2013) [R]; 25,000 (TFS Regional Chief); ~24,000 (AIDR); 20,200 at containment (NHESS-cited figure, not opened) | Whole Jan-2013 fire complex: **203 homes** + >201 outbuildings/caravans + several businesses, a school, a police station (TFS Deputy Chief Officer; AIDR). TFS "facts and figures" box: >170 properties destroyed. ABC (Oct 2013, on the Inquiry): 4 fires, >400 properties, ~200 residential. Forcett fire alone: ABC reports 63-65 homes at Dunalley, ~15 Boomer Bay, ~20 Murdunna | 0 in affected communities; 1 interstate firefighter died of natural causes (TFS). AIDR says a Victorian firefighter was killed during back-burning: **conflict, unresolved** | Sorell and Tasman (Tas Govt review: "Sorell and Tasman Municipal Areas"); Dunalley itself straddles both |
| T2 | **Lake Repulse** 3-22 Jan 2013 | >10,000 (TFS Regional Chief); >12,000 (AIDR) | TFS district officer lists losses: 1 caravan, outbuildings, fencing, stock; no dwellings listed. (TFS regional summary also says "destroying homes"; count not given) | 0 | Central Highlands, Derwent Valley |
| T3 | **Bicheno / Apsley River** 3-Jan 2013 | 4,938 (DPIPWE map) | "up to 19 structures" (AIDR); a search snippet of the Inquiry said 10 dwellings + 9 outbuildings (not opened) | 0 | Glamorgan-Spring Bay |
| T4 | Giblin River (South-West wilderness) 3 Jan 2013 | 44,471 (DPIPWE map) | none | 0 | remote; wilderness |
| T5 | Molesworth 6 Feb 2013 | 2,678 (TFS) | no dwellings lost (TFS) | 0 | Derwent Valley, Glenorchy (declared) |
| T6 | **North-West / lightning fires** 13 Jan-15 Mar 2016 | 124,742 across 229 fires (AFAC review) [R] | Review: loss of life avoided, built-asset damage "only at low levels"; no home count given | 0 | Circular Head, Kentish, West Coast, Meander Valley, Waratah-Wynyard (declared) |
| T7 | St Helens bushfire, from 17 Oct 2017 | not opened | not opened | not opened | Break O'Day (declared); details not checked |
| T8 | **Dec 2018-Mar 2019** (Gell River, Riveaux Road, Great Pine Tier, Moore's Valley) | >200,000 total (2.9% of Tasmania): Riveaux Road 64,000; Great Pine Tier 51,000; Moore's Valley 36,000; Gell River 35,000 (AIDR MIR 2018-19) | AIDR pages give no home losses. A Guardian headline from 30 Jan 2019 mentions 3 homes destroyed in southern Tasmania; could not open, so unverified | 0 | Huon Valley, Central Highlands, West Coast, Derwent Valley (declared) |
| T9 | **Pelham** (30 Dec 2019) | >2,100 (AIDR) | 1 dwelling | 0 | Central Highlands, Southern Midlands |
| T10 | **Fingal / Mangana** (29 Dec 2019) | ~22,000 (AIDR) | 1 dwelling | 0 | Break O'Day |

Tasmanian events from 2003-2011 were not systematically covered: the Inquiry's "history of bushfire in Tasmania" (Part B) was inaccessible and searching stopped. Nothing I saw suggests a home-loss event in that gap, but this is unverified.

## 2. Declarations (DisasterAssist pages actually opened)

| Event | AGRN | Declared / assisted LGAs (as named on the page) | URL |
|---|---|---|---|
| Tas Bushfires Jan 2013 | 537 | AGDRP: Central Highlands, Glamorgan-Spring Bay, Sorell, Tasman (+ Ellendale district). DIRS: Sorell, Tasman. NDRRA personal hardship/counter-disaster/assets: Central Highlands, Circular Head, Derwent Valley, Glamorgan-Spring Bay, Sorell, Tasman. Clean-up grants: Glamorgan-Spring Bay, Sorell, Tasman; Lake Repulse primary-producer grants: Central Highlands, Derwent Valley | https://www.disasterassist.gov.au/Pages/disasters/current-disasters/Tasmania/Bushfires-January-2013.aspx |
| Molesworth Feb 2013 | 548 | Derwent Valley, Glenorchy | .../Tasmania/Molesworth-bushfire-6-February-2013.aspx |
| NW Tas Jan 2016 | 709 | Circular Head, Kentish, West Coast, Meander Valley, Waratah-Wynyard (also Cat D World Heritage package) | .../Tasmania/North-West-Tasmanian-Bushfires-January-2016.aspx |
| St Helens Oct 2017 | 779 | Break O'Day | .../Tasmania/St-helens-bushfire-commencing-17-october-2017.aspx |
| Tas Dec 2018-Jan 2019 | 838 | DRA: Central Highlands, Derwent Valley, Huon Valley, West Coast | .../Tasmania/tasmanian-bushfires-december-2018-january-2019.aspx |
| Tas 16 Nov 2019 onwards | 913 | Break O'Day, Central Highlands, Flinders, Glamorgan-Spring Bay, Southern Midlands | .../Tasmania/tasmanian-bushfires-16112019-onwards.aspx |
| Pelham 30 Dec 2019 | 885 | AGDRP: Central Highlands, Southern Midlands | .../Tasmania/pelham-bushfire-30122019-onwards.aspx |
| Fingal 29 Dec 2019 | 883 | AGDRP: Break O'Day | .../Tasmania/fingal-bushfire-december-2019-onwards.aspx |
| SA Bushfires Jan 2014 | 603 | Personal hardship: Barossa, Loxton Waikerie, Mid Murray, Mount Remarkable, Southern Mallee, Tatiara. Counter-disaster adds Berri Barmera, Ceduna, Coorong, Karoonda East Murray, Murray Bridge, Renmark Paringa, Gawler Ranges (unincorporated) | .../South-Australia/Bushfires-January-2014.aspx |
| SA Bushfires Jan 2015 (Sampson Flat + Tantanoola) | 641 | AGDRP/DRA: Adelaide Hills, Barossa, Playford, Tea Tree Gully. NDRRA: Adelaide Hills, Playford, Tea Tree Gully (Sampson Flat); Wattle Range (Tantanoola) | .../South-Australia/Bushfires-January-2015.aspx |
| SA Pinery 25 Nov 2015 | 682 | AGDRP/DRA: Light and Mallala (Barossa region), Clare and Gilbert Valleys and Wakefield | .../South-Australia/Lower-Mid-North-Bushfire-25-November-2015.aspx |
| SA Nov 2019 onwards (Yorketown, Cudlee Creek, Kangaroo Island, Keilira, Duck Ponds) | 877 | DRFA in 11 LGAs: Adelaide Hills, Coorong, Kangaroo Island, Kingston, Lower Eyre Peninsula, Mid Murray, Mount Barker, Murray Bridge, Southern Mallee, Playford, Yorke Peninsula. AGDRP in 7: Adelaide Hills, Kangaroo Island, Kingston, Lower Eyre Peninsula, Mount Barker, Playford, Yorke Peninsula. Community Recovery Fund: Mount Barker, Adelaide Hills, Murray Bridge, Mid Murray, Kangaroo Island | .../South-Australia/Yorketown-bushfire-112019-onwards.aspx |
| Tulka 11 Nov 2012 / Coomunga 20 Nov 2012 / Bundaleer 16 Jan 2013 / Cherryville 9-12 May 2013 | 518 / 519 / 541 / 562 | Lower Eyre Peninsula / Lower Eyre Peninsula / Northern Areas / Adelaide Hills | .../South-Australia/... (same folder) |

- DisasterAssist's SA listing (paged through in a browser) reaches back only to Dec 2010. I found no declaration page for Wangary (2005) or Kangaroo Island (2007): **status unverified**. AIDR says a "major incident" was declared on 11 Jan 2005 (an emergency-management declaration, not an NDRRA one).
- Keilira: the Kingston council page says the Australian Government Disaster Recovery Payment and Allowance were activated for Kingston. Kingston is in the Nov 2019 AGRN 877 list.
- ICA: national bushfire catastrophe declared 8 Nov 2019; at 28 May 2020 the national insured value was about $2.32b from 38,181 claims, SA about $186m from 3,054 claims (8%) [AIDR Major Incidents Report 2019-20, https://knowledge.aidr.org.au/media/8049/aidr_major-incidents-report_2019-20.pdf]. This SA figure covers Cudlee Creek + Kangaroo Island + others; no per-fire split found.
- Insured losses otherwise: Wangary $27.7m in 2005, $41m normalised to 2011 (AIDR). Tas Jan 2013: ICA preliminary $89m (AIDR; TFS box says damage ~$50m; ABC says >$70m). Sampson Flat: $24.9m claims (AIDR). Pinery: ICA declared a catastrophe; $75m from 525 claims on 30 Nov 2015 (ABC), $61m (AIDR).

## 3. Per-council loss data that exists

- **Pinery (S6): yes.** Pinery Fire Recovery Final Report (July 2017), reproduced in the AIDR evaluation, table 4, private dwellings destroyed: Light 41, Wakefield 36, Adelaide Plains 15, Clare & Gilbert Valleys 5 (total 97). Source: https://knowledge.aidr.org.au/media/12446/bushfire-evaluation-report-pinery-fire-recovery-program-south-australia-2015.pdf. Same report: 82,600 ha; 10 houses with major damage, 39 minor; 546 sheds/outbuildings destroyed or highly damaged. A per-LGA impact-statistics file also exists at data.sa.gov.au (link in section 0, not opened).
- **Sampson Flat (S5): partial.** Adelaide Hills Council's 2014-15 annual report says 24 homes lost "in the Council area", almost 200 outbuildings, and about $700k council cost (https://www.ahc.sa.gov.au/assets/downloads/council/Reports/Annual-Reports/COUNCIL-Annual-Report-2014-2015.pdf). So essentially all 24 homes are in one council.
- **Cudlee Creek (S8): council share not found.** AHC's audited statements (Note 16, 2019-20 annual report) say the fire directly impacted "some 30 per cent" of the district, about $3.0m roadside tree clean-up, about $2.15m net hit to the 2019-20 result (https://www.ahc.sa.gov.au/assets/downloads/council/Reports/Annual-Reports/COUNCIL-Annual-Report-2019-2020.pdf). No home count by LGA (Adelaide Hills vs Mount Barker vs Mid Murray) found; the walled SA Recovery plan likely has it.
- **Kangaroo Island (S9), Keilira (S10): trivially per-council** (single council).
- **Wangary (S1):** the Coroner's totals are not split by council; the fire scar lies almost wholly in Lower Eyre Peninsula DC (J).
- **Tas Jan 2013 (T1): locality level only.** ABC 5 Jan 2013 (https://www.abc.net.au/news/2013-01-05/tragic-scenes-as-fires-destroy-homes/4453980): Dunalley ~65 properties, Boomer Bay ~15 homes, Murdunna ~20 homes, ~40% of properties at Connelly's Marsh. Mapping localities to Sorell vs Tasman needs ABS localities / cadastre. The Inquiry report almost certainly has a fuller breakdown (inaccessible). The Tasmanian Government's own Review of Recovery (https://knowledge.aidr.org.au/media/3999/bru_-_review_of_recovery_arrangements.pdf) says impact on Central Highlands, Sorell and Tasman was far greater than in other declared councils, which sought minimal assistance.

## 4. Share of council burned (arithmetic; council areas and sources)

Council areas used (km2): Kangaroo Island 4,400.9 (ESCOSA Local Government Advice, Feb 2026, https://www.escosa.sa.gov.au/ArticleDocuments/21863/20260212-LocalGovernmentAdvice-2025-26-KangarooIslandCouncil.pdf.aspx?Embed=Y); Adelaide Hills 795 / 795.08 (AHC annual reports 2019-20 and 2014-15); Lower Eyre 4,771 (localcouncils.sa.gov.au) or 4,754 (council history page); Light 1,277; Adelaide Plains 926 (localcouncils) or 935 (council site); Clare & Gilbert Valleys 1,840; Wakefield 3,468.5 (ESCOSA); Barossa 893.5 (ESCOSA) or 912; Mid Murray 7,957; Mount Remarkable 3,422.8 (ESCOSA); Kingston 3,337; Port Pirie 1,760; Yorke Peninsula 5,830; City of Port Lincoln 30.4 (all localcouncils.sa.gov.au unless stated). Sorell 583 (Sorell Council strategic plan, https://assets.sorell.tas.gov.au/uploads/2023/05/Strategic-Plan-2019-2029-Review-2023.pdf); Tasman 659.3 (snippet only, unverified).

| Event | Burned area used | Council | Arithmetic | Share | Call |
|---|---|---|---|---|---|
| S9 Kangaroo Island 2019-20 | 211,474 ha = 2,114.7 km2 (CFS) | Kangaroo Island | 2,114.7 / 4,400.9 | **48.0% (E)**; ESCOSA says "almost 50 percent" (R); AAR says 3 Jan run alone ~150,000 ha, ~38% of island (R) | >=5% yes, **>=20% yes (J: certain)** |
| S2 Kangaroo Island 2007 | 90,982 ha = 909.8 km2 (CFS) | Kangaroo Island | 909.8 / 4,400.9 | 20.7% (E); CFS says 22% (R) | >=5% yes, >=20% yes (borderline). Pre-data era |
| S8 Cudlee Creek | 23,295 ha = 233.0 km2 | Adelaide Hills | 233.0 / 795 | 29.3% if all inside (E); council says ~30% "directly impacted" (R) | >=5% yes, **>=20% yes (J)**; some scar may lie in Mount Barker/Mid Murray, but the council's own 30% supports it |
| S5 Sampson Flat | 12,569-13,000 ha | Adelaide Hills | 125.7-130 / 795.08 | 15.8-16.4% if all inside (E); some in Playford/Barossa/Tea Tree Gully | >=5% yes (J); >=20% no |
| S1 Wangary | 77,964 ha = 779.6 km2 | Lower Eyre Peninsula | 779.6 / 4,771 (or 4,754) | 16.3-16.4% if all inside (E; an upper bound because a slice is in Port Lincoln) | >=5% yes; >=20% no (J) |
| S6 Pinery | 82,600 ha = 826 km2 over 4 LGAs | Light / Wakefield / Adelaide Plains / Clare & Gilbert | 826 / (1,277+3,468.5+926+1,840) | 11.0% of the four councils' combined area (E). Crude split by share of homes destroyed (41/36/15/5 of 97), for illustration only: Light ~27%, Adelaide Plains ~14%, Wakefield ~9%, Clare & Gilbert ~2% | >=5%: Light, Adelaide Plains, Wakefield probably. **>=20%: Light plausible (J, low confidence)**. Needs overlay |
| S10 Keilira | 25,000-26,000 ha | Kingston | 250-260 / 3,337 | 7.5-7.8% if all inside (E) | >=5% yes; >=20% no |
| S4 Bangor | 35,000 ha = 350 km2 | Mount Remarkable (declared) | 350 / 3,422.8 | 10.2% if all inside (E); if it were all in Port Pirie: 19.9% (E, unlikely) | >=5% likely yes (J), >=20% no |
| S3 Eden Valley | 25,000 ha = 250 km2 | Barossa; Mid Murray | 250 / 893.5 = 28.0% if all Barossa; 250 / 7,957 = 3.1% if all Mid Murray | unknown split | Undetermined; needs overlay. Only 4 homes lost, so low DL value |
| S7 Yorketown | >5,000 ha | Yorke Peninsula | 50 / 5,830 | ~0.9% (E) | no |
| **T1 Forcett-Dunalley** | 25,197 ha = 252.0 km2 (DPIPWE); GA outline 23,378 ha = 233.8 km2 | Sorell + Tasman (combined 583 + 659.3 = 1,242.3 km2) | 252.0 / 1,242.3; 233.8 / 1,242.3 | **20.3% (E) / 18.8% (E)** of the two councils' combined area. If the scar sits inside those two councils, the more-burned of the pair is at least that share (pigeonhole). One council alone would be at most 43.2% (Sorell) or 38.2% (Tasman) | Both >=5% very likely (J). **>=20% for at least one of Sorell/Tasman: likely (J)**, borderline until overlaid. Tasman area unverified |
| T2 Lake Repulse | >10,000-12,000 ha | Central Highlands / Derwent Valley | areas unverified | not computed | probably <5% each (J) |
| T3 Bicheno | 4,938 ha = 49.4 km2 | Glamorgan-Spring Bay | area unverified | not computed | probably <5% (J) |
| T8 Riveaux Road etc. | 64,000 / 51,000 / 36,000 / 35,000 ha | Huon Valley; Central Highlands; West Coast | areas unverified | not computed | Huon Valley and Central Highlands plausibly >=5% (J, unverified); >=20% unlikely. Wilderness, almost no homes |

Kangaroo Island and Sorell/Tasman, as asked:
- **Kangaroo Island Council:** 48% of the council area burned (E, 211,474 ha on 4,400.9 km2), corroborated by ESCOSA's "almost 50 percent". 56-87 homes lost (see discrepancy below) against about 5,740 rateable properties in 2024-25 (ESCOSA) = roughly 10-15 homes per 1,000 rateable properties (E; rateable properties are not ABS dwellings, so redo with Census dwellings). Two deaths. This is the largest burn fraction in my slice and larger than any single NSW council.
- **Sorell / Tasman:** no source states the burned share of either council. Combined arithmetic says ~19-20% of the two councils together (E). Sorell is 583 km2 (verified); Tasman 659.3 km2 is unverified.

Data-availability note (from your brief; not re-verified): CABEE business counts start June 2013 and DSS payments start Mar 2016. So Tasmania 2013 has no pre-fire business-count baseline (fire was Jan 2013), and Sampson Flat / Pinery have no pre-fire DSS baseline; Wangary (2005), Kangaroo Island 2007 fall before SALM (Dec 2010) as well. Full four-pillar data exist only for 2019-20 events (Cudlee Creek, Kangaroo Island, Keilira) and, with the SL pillar limited, for 2016-2019 Tasmanian events. The Dec 2019 SA events sit in the same season as NSW Black Summer and are followed by the COVID-19 shock (Mar 2020 onward), which hits tourism-heavy Kangaroo Island harder than comparators. Flag this as a confound.

## 5. Discrepancies to carry forward (each figure with its source)

| Item | Values |
|---|---|
| Wangary homes | 93 destroyed or significantly damaged (Coroner); 93 houses (CFS); 79 destroyed + 26 extensively damaged (AIDR) |
| Wangary area | 77,964 ha (Coroner); ~78,000 (CFS); ~82,000 (AIDR). GA fieldwork note says >145,000 ha for the whole 10-11 Jan 2005 Eyre Peninsula fires and 48,000 ha around the named townships: ambiguous, do not use |
| Sampson Flat homes | 24 (CFS, AHC); 27 (AIDR) |
| Pinery homes | 87 (ABC 30 Nov 2015); ~91 (CFS, ABC 19 Dec); 97 (Recovery Final Report) |
| Pinery insured loss | $75m at 30 Nov 2015 (ABC); $61m (AIDR) |
| Cudlee Creek homes | 84 (AIDR MIR); 85 (CFS); 86 (ABC headline) |
| Kangaroo Island homes | 87 (CFS "dwellings"; AAR "homes and other significant built assets"; ESCOSA "homes"); 56 (AIDR MIR: "56 homes"). Best reading: 56 residential homes within ~87 lost dwellings/assets; unresolved |
| Kangaroo Island area | 211,474 ha (CFS); 211,228 ha (AAR); GA outline for Ravine alone is 184,941 ha (from your brief), so it omits about 26,500 ha (12.5%) of the complex |
| Tas Jan 2013 homes | 203 (TFS Deputy Chief Officer, AIDR); >170 properties (TFS box); ~200 residential of >400 properties (ABC); 93 dwellings + 186 other buildings for Forcett fire (ABC/Inquiry per search result) |
| Tas Jan 2013 deaths | 0 in communities; TFS: 1 interstate firefighter died of natural causes; AIDR: firefighter "killed" during back-burning |
| Tas Forcett area | 25,197 ha (DPIPWE); GA outline 23,378 ha (your brief); 20,200 ha at containment (NHESS text, not opened) |
| Council areas | See section 0 |

## 6. Council mergers and boundary changes (comparability with ABS LGA 2015-2021)

**South Australia (68 councils):**
- The SA Government "Find your council" list (https://www.localcouncils.sa.gov.au/get-involved/find-your-council) shows 68 councils.
- The big amalgamations happened in 1996-1999, i.e. before 2003. I did not find any post-2003 merger affecting my candidates (J; a Government Gazette search was not possible). Renames only, so the entity is continuous:
  - District Council of Mallala renamed **Adelaide Plains Council in 2016** (Adelaide Plains site: https://www.apc.sa.gov.au/our-council/about-adelaide-plains-council). DisasterAssist's Pinery page still says "Mallala". ABS LGA 2015 vintage vs 2016+ will carry different names for the same area.
  - District Council of Lower Eyre Peninsula renamed **Lower Eyre Council on 19 June 2024**; its history page lists no boundary change after 1982 (https://www.lowereyrepeninsula.sa.gov.au/council/council-history).
  - District Council of Grant now appears as **Southern Limestone Coast Council** on the SA council list (rename date not checked).
- The declaration lists use older names ("Lower Eyre Peninsula", "Mallala", "Grant"): match on code, not name.
- "Unincorporated South Australia" (Gawler Ranges etc.) is a separate area in DisasterAssist and in ABS LGAs: large pastoral fires land there with no population.
- Kangaroo Island Council was formed in 1996 (ESCOSA-derived search result, not directly verified); one council for the whole island, so island-wide fire = council-wide fire.

**Tasmania (29 councils):**
- LGAT: "Tasmania is made up of 29 municipalities" (https://www.lgat.tas.gov.au/tasmanian-councils). The 2022-24 Local Government Review considered boundary consolidation, but the LGAT page describes it as options and government response, not enacted change (https://www.lgat.tas.gov.au/tasmanian-councils/lg-reform). I found no boundary change in 2013-2021 (J).
- Name variants: "Glamorgan-Spring Bay" (DisasterAssist) vs ABS "Glamorgan/Spring Bay"; "Break O'Day", "Flinders" (Island).

## 7. Is the comparison group big enough for an excess-change design? (J)

- **South Australia:** 68 councils. About 18 are metropolitan or peri-urban (City of Adelaide, Burnside, Campbelltown, Charles Sturt, Holdfast Bay, Marion, Mitcham, Norwood Payneham & St Peters, Onkaparinga, Port Adelaide Enfield, Prospect, Salisbury, Tea Tree Gully, Unley, Walkerville, West Torrens, Playford, Gawler; count from the list) and about 50 are regional. In most years dozens of regional councils will have no >=100 ha fire, so the "median of no-fire councils" is estimable. Weaknesses: (a) urban comparators poorly match rural burned councils, (b) many pastoral councils have tiny populations and noisy income/unemployment, (c) tourism-exposed Kangaroo Island has no close comparator. Adequate for Cudlee Creek (Adelaide Hills, peri-urban) and Kangaroo Island with matched sub-groups (e.g. non-metro councils only).
- **Tasmania:** 29 councils. Big fire seasons touch many councils: 2012-13 saw more than 110,000 ha burned (Forestry Tasmania in TFS Fireground), 2015-16 229 vegetation fires, 2018-19 over 200,000 ha, so the "no fire >=100 ha" filter can strip out many rural councils. What remains is plausibly a dozen or so mostly urban or small councils (my estimate; count needs the GA outlines). The median over a handful of dissimilar councils is noisy, and small-LGA suppression in ABS/DSS tables is likely. **Marginal**: workable for Sorell/Tasman 2013 only with a loosened rule (e.g. exclude only councils with >=1% burned) or a multi-year pooled reference.
- Council finance data (FP pillar) leads, not opened: SA: ESCOSA advice PDFs give asset renewal funding ratios etc. for a rotating subset of councils (list at https://www.escosa.sa.gov.au/advice/advice-to-local-government); the SA Local Government Grants Commission database is the full set (not checked). Tasmania: Audit Tasmania "Local Government Authorities" annual reports (e.g. https://audit.tas.gov.au/publication/local-government-authorities-2017-18/, seen in a search result, not opened).

## 8. Suggested next steps for the parent (no experiments proposed)

1. Overlay GA outlines (already on disk) with ABS LGA 2016/2021 boundaries for: Kangaroo Island 2019-20 (add Menzies and Duncan to Ravine to reach ~211,000 ha), Cudlee Creek, Sampson Flat, Pinery (Light, Wakefield, Adelaide Plains, Clare & Gilbert), Keilira, Bangor, Eden Valley, Wangary, Kangaroo Island 2007, Forcett/Inala Road (Sorell vs Tasman), and the four 2019 Tasmanian fires. This resolves every "unverified" cell in section 4 and gives the actual >=5% / >=20% counts.
2. Download the data.sa.gov.au Pinery statistics file (66 KB) if per-LGA damage is wanted beyond the Recovery Final Report table.
3. Ask for the Tasmanian Bushfires Inquiry Volume 1 (Part D) and the SA Recovery plans for Cudlee Creek and Kangaroo Island from a person with access; they likely hold per-LGA dwelling counts.

## 9. Summary table

| Candidate | Homes destroyed (reported) | Deaths | Councils with >=5% burned (J) | Per-council loss data exists? | Verdict |
|---|---|---|---|---|---|
| Kangaroo Island Dec 2019-Jan 2020 | 87 dwellings/assets (CFS, AAR, ESCOSA); 56 homes (AIDR) | 2 | Kangaroo Island (48%, E) | Y trivially (single council) | **Best add.** Only >=20% case with full 2019-20 data; COVID/tourism confound |
| Cudlee Creek Dec 2019 | 85 (CFS); 84 (AIDR) | 1 | Adelaide Hills (~29-30%; council-reported) | Partly: total known, LGA split not found (Recovery site walled) | **Strong add.** >=20% by the council's own statement; whole-season overlap with NSW Black Summer, different state comparators |
| Tas Forcett-Dunalley Jan 2013 | 203 (whole Jan-2013 complex); ~93-100+ Forcett | 0 civilian; 1 firefighter (natural causes per TFS) | Sorell and Tasman (combined ~19-20%; at least one likely >=20%) | Locality level only (ABC); Inquiry has more (walled) | **Strong add for Sorell/Tasman.** Business-count and DSS baselines missing (2013) |
| Pinery Nov 2015 | 97 (Recovery Final Report; ~91 elsewhere) | 2 | Light (plausibly >=20%), Adelaide Plains, Wakefield | **Y**: Light 41, Wakefield 36, Adelaide Plains 15, C&GV 5 | **Good add**; 4 councils in one fire; DSS baseline missing (starts Mar 2016) |
| Sampson Flat Jan 2015 | 24 (CFS/AHC); 27 (AIDR) | 0 | Adelaide Hills (~16% if all inside) | Y: 24 in Adelaide Hills (AHC) | Modest; near the 20% line, fewer homes; DSS baseline missing |
| Wangary Jan 2005 | 93 destroyed or significantly damaged (Coroner) | 9 | Lower Eyre Peninsula (~16%) | Not split; almost all one council | Large real event but pre-data (no SALM, CABEE, DSS, PIA baselines): DL-only |
| Kangaroo Island Dec 2007 | none reported | 1 | Kangaroo Island (20.7%; CFS 22%) | Y (single council) | Real >=20% burn but no homes and pre-data: not usable |
| Keilira Dec 2019-Jan 2020 | 3 (1 occupied) | 0 | Kingston (~7.5-7.8%) | Y (single council) | Small DL, useful only as a moderate-burn, low-loss row |
| Bangor Jan-Feb 2014 | 5 | 0 | Mount Remarkable (~10%, unverified split) | Not needed | Low-DL moderate-burn row; pre-DSS |
| Eden Valley Jan 2014 | 4 | 0 | Barossa and/or Mid Murray (unresolved) | N | Low value unless overlay shows a big Barossa share |
| Yorketown Nov 2019 | 7-8 | 0 | none (~1%) | Y (Yorke Peninsula) | Not useful |
| Tas Dec 2018-Mar 2019 (Riveaux Rd etc.) | none confirmed (3 homes headline unverified) | 0 | Huon Valley, Central Highlands plausibly (unverified) | N | Large area, almost no homes; wilderness; not useful for DL, weak for the rest |
| Tas Jan 2016 lightning fires | none significant (AFAC) | 0 | unverified | N | Not useful |
| Tas Nov 2019-Jan 2020 (Pelham, Fingal) | 1 + 1 | 0 | unverified | N | Not useful |
| Tas Lake Repulse / Bicheno / Molesworth 2013 | none / up to 19 structures / none | 0 | probably none | N | Minor; comparators for T1 only |
