# A2 - Victorian bushfires 2003-2021 (plus a few later leads): scoping notes

Compiled 2026-09-29 by scoping agent A2. Scope: real Victorian fire events that could add council x fire rows to Experiment 6. No data files downloaded (HEAD requests only, sizes noted). No Wikipedia and no ACM mastheads used. Where a search-result excerpt showed a figure but I never opened the page, the figure is marked "excerpt only" or "not opened".

Labels: **reported** = a source I opened states it. **estimated** = I derived it (arithmetic shown). **judgement** = my reasoned call, not a source figure.

## 0. Bottom line

1. Best new material is **Black Saturday (7 Feb 2009, with the Delburn fires of 28 Jan)** and **Black Summer in Victoria (Nov 2019 - Feb 2020)**. Both burned whole councils on a scale NSW outside 2019-20 never did.
   - Black Saturday: Murrindindi about 40% of the shire burnt (council, reported); Yarra Ranges 19.6% (council GIS, reported, just under 20%); Nillumbik plausibly about a quarter (excerpt only, unverified).
   - Black Summer Vic: East Gippsland more than half (council, reported), Towong 32.7% (council plan, reported), Alpine 29% (council plan, reported).
2. **Black Summer Victoria is the same season as the NSW Black Summer rows already in the dataset.** It adds councils, not a new independent year. It does add a second state's comparison group (Victoria's no-fire councils).
3. **Black Saturday collides with the disk data windows.** ABS CABEE business counts start June 2013, DSS payments start Mar 2016, SALM unemployment starts Dec 2010 (after the fire). So Black Saturday supports the DL pillar and ERP only, and pre-fire unemployment is missing. All four pillars are computable only for fires from about 2017 onward in Victoria (Mar 2018, Feb-Mar 2019, Black Summer). See section 6.
4. **No official per-LGA "houses destroyed" table was found for Black Saturday.** VBRC gives houses per fire, not per council. Two councils give their own counts (Murrindindi 1,397; Yarra Ranges 304) but those are on a different basis from VBRC (they do not add up to VBRC's per-fire totals; see 2.1). For Black Summer only three councils have a figure: East Gippsland (410 residential properties), Towong (38 primary residences), Alpine (1 primary residence).
5. Every other Victorian event I could source (Wye River 2015, Scotsburn 2015, Terang 2018, Feb 2014) lost 12-116 homes but burnt under about 5% of any council (Bunyip 2019 in Cardinia is borderline). Only Aberfeldy 2013 and the Mar 2019 Licola/Dargo fires probably clear 5% of one council (Wellington), and Aberfeldy is the only one of those with home loss (22 homes, 1 death).
6. Victoria has **79 councils** (VEC). I found no sign of a Victorian merger or split between 2009 and 2021 (section 5).

## 1. Method and limits

- Web search budget ran out part-way (the session cap of 200 searches was reached). The last third of the work used direct page and PDF reads only. Consequences: no DisasterAssist listing pages for 2014, Dec 2015 or 2018 (probed likely URLs; all 404). No IGEM page (HTTP 403). No FFMVic past-bushfires page (403). Cardinia council page (403).
- PDFs were streamed into memory and text-searched; nothing was written to disk except this file. One WebFetch call auto-saved a council PDF into the tool-results folder; I read it and deleted it. Other WebFetch PDFs in that folder belong to other agents and were not touched.
- LGA areas: I verified some from official pages (Know Your Council, council plans). Others I know only from memory and mark "(area not verified)". The disk already holds ABS ERP by LGA and ABS LGA boundaries, plus the Geoscience Australia fire polygons, so the parent can compute exact per-LGA burnt shares by intersection; my judgements below are only a pre-screen.

## 2. Candidate events

### 2.1 Black Saturday and the Delburn fires, Jan-Feb 2009

| Item | Figure | Status / source |
|---|---|---|
| Dates | Delburn fires 28 Jan - 3 Feb 2009 (most destructive 30 Jan); the big day is 7 Feb 2009; Bunyip Ridge Track fire reported 4 Feb, contained 4 Mar; Murrindindi fire contained 5 Mar; Churchill fire controlled 19 Feb | reported, VBRC Vol 1 ch 3, 4, 9, 10 (URLs in section 9) |
| Total houses destroyed | 2,133 "houses destroyed as a result of the January-February 2009 bushfires" | reported, VBRC Summary p.23 (counts **houses**) |
| Same, other counts | 2,029 homes (AIDR); "more than 2,000 homes" (DisasterAssist); 3,500 buildings (CFA); "almost 2,500 properties" (VBRRA three-year report) | reported; definitions differ |
| Sum of VBRC per-fire houses | 2,131 | estimated: 44+31+1,242+13+1+0+145+538+14+7+58+38 |
| Deaths | 173 total: Kilmore East 119, Murrindindi 40, Churchill 11, Bendigo 1, Beechworth-Mudgegonga 2 | reported, VBRC Vol 1 ch 5, 9, 10, 14; CFA page for Bendigo. Two firefighters among the 173 (CFA page). |
| Area burnt | About 430,000 ha statewide (VBRC); 450,000+ ha (AIDR) | reported |
| Declaration | NDRRA assistance in **25 LGAs**: Alpine, Baw Baw, Cardinia, Corangamite, Greater Bendigo, Hepburn, Horsham, Indigo, Latrobe, Macedon Ranges, Mitchell, Mount Alexander, Murrindindi, Nillumbik, Southern Grampians, Wangaratta, Wellington, West Wimmera, Whittlesea, Yarra Ranges, Lake Mountain Alpine Resort, South Gippsland, Knox, Greater Dandenong, Casey | reported, DisasterAssist page for Victorian bushfires Jan-Feb 2009 (AGRN 322) |
| Insurance Council | Listed; cost $1,070m (2009), normalised $1,266m (2011); 61 businesses destroyed | reported, AIDR Black Saturday page |
| Wider economic cost | Deloitte (court report) cites a final estimate of more than $4bn; class actions (Kilmore East, Murrindindi) settled for about $800m (about $500m for economic loss) approved Dec 2014 and May 2015 | reported, Deloitte Access Economics report for the Supreme Court of Victoria. **Confounder:** large compensation inflows to Yarra Ranges, Whittlesea, Murrindindi, Nillumbik, Mitchell in 2015+. |

**Per fire (VBRC Vol 1; "houses" as counted by VBRC):**

| Fire | Houses destroyed | Deaths | Area (ha) | Councils named by the source | Source status |
|---|---|---|---|---|---|
| Kilmore East | 1,242 | 119 | 125,383 | Nillumbik, Mitchell, Yarra Ranges shires; City of Whittlesea (ch 5); Murrindindi shire is also hit (Kinglake, Flowerdale) per Deloitte's five-LGA study region | reported |
| Murrindindi | 538 | 40 | combined Kilmore East + Murrindindi 168,542 | Murrindindi Shire | reported |
| Churchill | 145 | 11 | 25,861 | Latrobe City and Wellington Shire | reported |
| Delburn (Boolarra) | 44 | 0 | 6,534 | Latrobe (Boolarra, Yinnar; ch 3 refers to Latrobe emergency centre) | reported; council assignment is judgement |
| Bunyip Ridge Track | 31 | 0 | 26,200 | Cardinia and Baw Baw shires | reported |
| Bendigo (Maiden Gully) | 58 | 1 | 341 | Greater Bendigo | reported |
| Beechworth-Mudgegonga | 38 | 2 | 33,577 | Indigo Shire | reported |
| Redesdale | 14 | 0 | 7,086 | not stated in what I read (DisasterAssist lists Macedon Ranges, Mount Alexander, Hepburn) | reported / judgement |
| Horsham | 13 | 0 | 2,346 | Horsham Rural City (judgement) | reported |
| Narre Warren / Upper Ferntree Gully | 7 | 0 | Harkaway 147; Lynbrook 12 | Casey / Knox (judgement) | reported |
| Coleraine | 1 | 0 | 713 | Southern Grampians (judgement) | reported |
| Pomborneit-Weerite | 0 | 0 | 1,008 | Corangamite / Colac Otway (judgement) | reported |

**Per-council loss data ("houses destroyed" by LGA): none official found.** What exists:

| Council | Figure | Basis | Source |
|---|---|---|---|
| Murrindindi | 1,397 houses/dwellings/"properties" destroyed; about 40% of shire burnt (154,355 ha = 1,539 km2); 95 deaths in shire (same document also says 106 lives lost) | council's own planning-policy background, Dec 2012 agenda attachment. Reported by council; wording varies inside the document | Murrindindi Shire Council agenda attachment (URL in section 9) |
| Yarra Ranges | 304 homes destroyed or made unliveable; 161 further private dwellings damaged; 13 lives lost (Steels Creek 10, Toolangi 2, Yarra Glen 1); 48,293 ha burnt = 19.6% of 246,846 ha | council building department at 15 May 2009 and council GIS | Yarra Ranges Council evaluation report June 2012 (hosted by AIDR) |
| Nillumbik | shire area 432 km2; 91% Green Wedge. No 2009 loss figure in the council plan I opened. A "quarter of shire burnt, 125 homes" claim appeared in a search excerpt only | not opened, **unverified** | Nillumbik MFMP 2020-23 (area only) |
| Whittlesea, Mitchell | none found | - | - |
| Latrobe, Wellington | none found (only per-fire VBRC) | - | - |

**Caution:** Murrindindi's 1,397 plus Yarra Ranges' 304 is 1,701, out of VBRC's 1,780 for the two fires (1,242 + 538), before any Nillumbik, Mitchell or Whittlesea loss. So the council counts are on a wider basis (damaged plus destroyed, or all "properties") than VBRC's houses. Do not mix them with VBRC per-fire numbers.

**Councils burnt at 5% or 20% (judgement, with arithmetic):** see section 3.

**Data window:** fails for IL, SL and pre-fire unemployment (section 6). Pre-fire SEIFA would be 2006. Useful for DL and exposure tests only.

### 2.2 Black Summer in Victoria, 21 Nov 2019 - Feb 2020

| Item | Figure | Status / source |
|---|---|---|
| Area burnt | More than 1.5 million ha; complexes: Snowy 662,500 ha, Tambo 324,739 ha, Upper Murray (Walwa) 200,442 ha, Abbeyard-Yarrabula South 151,221 ha | reported, CFA 2019-2020 page |
| Homes destroyed statewide | "Over 400" (CFA); "300+" (AIDR); "some 313 primary and 145 non-primary residences destroyed or damaged" (IGEM Phase 1, quoted in search excerpts; the IGEM page returned 403, **not opened**); "at least 200, rising to 300" (ABC, 6 Jan 2020) | reported; **sources disagree** and use different bases (homes, residences, destroyed vs destroyed or damaged) |
| Deaths | 5 statewide (CFA, AIDR). East Gippsland council says 3 died in East Gippsland. Split of the other 2 by council not found | reported |
| Per council: East Gippsland | 410 residential properties and 27 commercial destroyed; more than half of the LGA burnt (1.1 million ha); 3 deaths; Mallacoota 123 houses (CFA) vs "60+" (AIDR) | council media release 15 Jul 2021 (reported); CFA and AIDR pages |
| Per council: Towong | 38 primary residences destroyed; about 600 properties impacted; 218,015 ha (32.7% of the shire) burnt; 59,849 ha of farmland | Towong Municipal Recovery Plan 2019-21 (reported) |
| Per council: Alpine | 1 primary residence lost; 29% of the shire footprint directly impacted (6% of the burnt area on private land) | Alpine Municipal Recovery Plan (reported) |
| Per council: Wellington, Mansfield, Wangaratta, Indigo, Wodonga | no house figures found; Wellington/Mansfield/Wangaratta Rural were named in the state of disaster | not found |
| Declarations | State of disaster 2 Jan 2020: East Gippsland, Mansfield, Wangaratta Rural, Wellington, Towong, Alpine shires plus Mount Buller, Mount Hotham, Falls Creek, Mount Stirling resorts (AIDR Vic page). DisasterAssist AGRN 882 (start 21 Nov 2019): emergency relief in 18 LGAs plus 4 resorts (Alpine, Ararat, Ballarat, East Gippsland, Glenelg, Golden Plains, Greater Bendigo, Indigo, Mansfield, Moyne, Northern Grampians, Pyrenees, Southern Grampians, Strathbogie, Towong, Wangaratta, Wellington, Wodonga); **emergency re-establishment (home loss) only in East Gippsland and Towong**; AGDRP (lost or damaged homes) only in Alpine, East Gippsland, Towong; grants also in Campaspe (primary producers) | reported, DisasterAssist page AGRN 882 |
| Insurance Council | AIDR Vic page prints about $18.6m insured and 3,050 claims, which looks too small against the national figure of $2.32bn (excerpt only) and probably covers one sub-event; treat as unreliable | AIDR page (opened); national figure not opened |
| Repeat burning | Alpine plan says 2003 and 2006 fires covered 69-88% of the 2019-20 fire area in places; nearly 50% of impacted area severely burnt | reported, Alpine plan |

DisasterAssist's re-establishment list is a useful cross-check: the home-loss councils are East Gippsland and Towong, with Alpine token.

**Data window:** all four pillars computable (CABEE from Jun 2013, DSS from Mar 2016, SALM from Dec 2010). DL denominator (dwellings per LGA) is not on disk for Victoria: the disk has Census GCP for NSW only. HEAD sizes for the Victorian LGA GCP packs (not downloaded): 2021 short-header zip 6,225,215 bytes; 2016 short-header zip 6,090,114 bytes (abs.gov.au datapack URLs, section 9).

### 2.3 Other events, in date order

| Event | Dates | Area (ha) | Homes destroyed | Deaths | Councils | Declaration / insurance | Sources and status |
|---|---|---|---|---|---|---|---|
| **2003 Eastern Victorian alpine fires** | Ignited 8 Jan 2003, contained 7 Mar 2003 | 1.19m public + about 90,000 private (Vic) | 41 houses + 213 other structures | not stated by AIDR; "no loss of life attributable to line firefighting" per a forestry-heritage page (not opened) | not stated; Alpine, Mt Buffalo NP 81% burnt | ICA $12m (2003), normalised $24m (2011) | AIDR page (opened). Pre-2010: outside all disk windows. |
| **Jan 2006 fires** (Deep Lead / Stawell, Yea, Moondarra, Grampians, Kinglake, Anakie) | Jan 2006 | about 160,000 | 57 homes, 359 farm buildings | 4 | places named, councils not | insurance costs $22m; no declaration stated | AIDR Victoria 2006 page (opened). Pre-2010. |
| **2006-07 Great Divide Complex** | 1 Dec 2006 - 7 Feb 2007; separate Tawonga Gap 33,500 ha and Tatong 33,000 ha | 1.2-1.3 million | 51 dwellings (21 primary residences) | 1 civilian | not stated | ICA reported no cost for it | AIDR Great Divide page (opened). Pre-2010. |
| **Jan-Feb 2013 fires: Aberfeldy-Donnellys Creek** (17 Jan 2013) | 17 Jan - about 2 months | 87,000 (ABC); 86,000+ (excerpt) | **22** (Seaton, Dawson, Glenmaggie) | **1** (Stanley Hayhurst, civilian) | Wellington (Seaton, Glenmaggie, Heyfield); judgement | DisasterAssist AGRN 550 (Feb 2013): Alpine, Ararat, Baw Baw, Horsham, Mansfield, Mitchell, Northern Grampians, Southern Grampians, Wellington, Whittlesea | ABC 3 Feb 2019 (opened); DisasterAssist page (opened). Harrietville fire (Alpine): about 37,000 ha in an excerpt only, **unverified** |
| **Mar 2013** | 27 Mar 2013 | not found | not found | not found | DisasterAssist AGRN 557: Golden Plains, Corangamite, South Gippsland, West Wimmera | declared | DisasterAssist page (opened). Size unknown; probably minor. |
| **Jan-Feb 2014 fires** (Grampians 15-21 Jan; Mickleham Road Complex 8-9 Feb; Warrandyte; Gisborne; East Gippsland fires) | Jan - Feb 2014 | Grampians 52,000; East Gippsland fires "130,000+" (as printed by AIDR; unclear) | **40 total** as printed by AIDR; the listed parts (Mickleham 13, East Gippsland fires 15, Warrandyte 3, Gisborne 1, Morwell 1) sum to only 33, so 7 are unallocated | none | Mitchell/Hume corridor (Mickleham), Manningham, Macedon Ranges, Latrobe, Grampians area (12 LGAs affected, unnamed) | national recovery payments activated (AIDR); no DisasterAssist page found | AIDR Victoria 2014 and Grampians NP pages (opened). |
| **Hazelwood open-cut mine fire** (Morwell, Latrobe) | 9 Feb - 25 Mar 2014 | not applicable | none | none stated by AIDR | Latrobe | inquiry: damages above $100m | AIDR page (opened). Not a bushfire; 0 DL. Health-effects case only. |
| **Dec 2014 - Jan 2015 fires** | Dec 2014 - Jan 2015 | not found | not found | not found | 11 councils declared: Ararat, Benalla, Hindmarsh, Horsham, Mildura, Moira, Southern Grampians, Strathbogie, Wangaratta, West Wimmera, Wodonga | NDRRA | Premier release (opened). **Lead only.** |
| **Oct 2015 fires** (Lancefield fire etc.) | Oct 2015 | not found | not found | not found | Macedon Ranges, Mitchell, Murrindindi, Surf Coast areas | emergency relief and re-establishment | Premier release 14 Oct 2015 (opened). **Lead only.** |
| **Dec 2015 Scotsburn** (near Ballarat) | 19 Dec 2015 | 4,000 | **12** | none | Ballarat / Golden Plains area (LGA not stated); judgement | class action paid $10.5m to 86 claimants | ABC 29 Jan 2021 (opened). |
| **Dec 2015 Wye River - Jamieson Track** | 19 Dec 2015 - 21 Jan 2016; house loss on 25 Dec | 2,500 | **116** (98 Wye River, 18 Separation Creek) | none | recovery run by **Colac Otway Shire** with the State | AIDR insured loss $120m; a $38m early estimate appeared in an excerpt only (not opened). Declaration not found | AIDR page and EMV recovery review (opened). **Only about 100-200 permanent residents; many holiday homes owned by Melburnians** (EMV review p.13). Poor fit for resident-based indicators. |
| **Mar 2018 south-west fires** (Terang, Camperdown, Gazette, Garvoc) | 17-18 Mar 2018; response to 8 May | 26,254 total (Terang 9,725; Camperdown 6,725; Garvoc 4,031; Gazette 3,666; small others) | **26 residences**, 66 outbuildings | none | Corangamite (Terang, Camperdown, Cobden) and Moyne (Garvoc, Gazette, Hawkesdale); judgement, AIDR names no LGAs | ICA declared a catastrophe; NDRRA category A, B and C activated (AIDR) | AIDR South-west complex page and ABC 19-20 Mar 2018 (opened). |
| **Feb-Mar 2019 Bunyip Complex, Yinnar South, Licola, Dargo** | Lightning 28 Feb and 1 Mar 2019 | Bunyip 15,000+; Licola 80,000+; Mt Darling-Cynthia Range 28,000+ | **31**: Bunyip 29 (Bunyip North, Garfield North, Tonimbuk in Cardinia), Yinnar South 2; plus 67 outbuildings | none | Baw Baw, Cardinia, Latrobe, South Gippsland, Wellington | ICA catastrophe declared 8 Mar 2019; Bunyip insured about $32m by mid-April; DisasterAssist AGRN 846: AGDRP in Baw Baw, Cardinia, Latrobe; DRA in 17 LGAs | AIDR page, ABC 9 Mar 2019 (both opened), DisasterAssist (opened). |

### 2.4 Leads outside the requested window (2003-2021), from DisasterAssist only

Not researched for losses. All fall inside the disk windows for CABEE, DSS and SALM, but recent enough that ABS income and council finance years may not yet exist.

| Event | Start | Councils listed for assistance | Note |
|---|---|---|---|
| Western Victoria bushfires, Feb 2024 (Pomonal area) | 13 Feb 2024 | AGDRP in Ararat, Horsham, Pyrenees | DisasterAssist combined bushfire-and-storm page |
| Western Victoria bushfires, Dec 2024 (Grampians) | 16 Dec 2024 | Disaster Recovery Allowance in Ararat, Hindmarsh, Horsham, Macedon Ranges, Northern Grampians, Southern Grampians, West Wimmera | no loss figures opened |
| Victorian bushfires, Jan 2026 | 7 Jan 2026 (to 28 Feb 2026) | AGDRP in 16 LGAs: Ararat, Colac Otway, Corangamite, Golden Plains, Greater Bendigo, Horsham, Mansfield, Mitchell, Moira, Mount Alexander, Murrindindi, Pyrenees, Strathbogie, Towong, Wellington, West Wimmera | ICA data hub shows a Victoria bushfires catastrophe: 4.85 thousand claims, $598m incurred, $143m outstanding (that entry is almost certainly this event, judgement) |

## 3. Burnt share by council (judgement, with arithmetic)

Thresholds: 5% and 20% of council area.

| Event | Council | Burnt area (source) | Council area (source) | Share | Passes 5%? / 20%? |
|---|---|---|---|---|---|
| Black Saturday | Murrindindi | 154,355 ha (council; Murrindindi Shire Council doc) | 3,879 km2 = 387,900 ha (Know Your Council) | 39.8% (estimated); council says about 40% (reported) | yes / yes |
| Black Saturday | Yarra Ranges | 48,293 ha (council GIS) | 246,846 ha (same table) | 19.6% (reported by council) | yes / just under |
| Black Saturday | Nillumbik | unknown; excerpt claimed about 23% (not opened) | 432 km2 = 43,200 ha (Nillumbik MFMP) | 5% = 2,160 ha; 20% = 8,640 ha | judgement: yes / plausible, unverified |
| Black Saturday | Mitchell | unknown | 2,862 km2 = 286,200 ha (Know Your Council) | 5% = 14,310 ha; 20% = 57,240 ha | judgement: plausibly yes / no. Compute by GIS. |
| Black Saturday | Whittlesea | unknown | area not verified | - | judgement: uncertain; compute |
| Black Saturday | Latrobe | Churchill 25,861 + Delburn 6,534 ha, split with Wellington unknown | area not verified | - | judgement: likely yes for 5%; 20% possible; compute |
| Black Saturday | Indigo | Beechworth-Mudgegonga 33,577 ha, "in Indigo Shire" (VBRC) | area not verified | - | judgement: likely yes / not likely; compute |
| Black Saturday | Baw Baw | Bunyip 26,200 ha shared with Cardinia | 4,027 km2 = 402,700 ha (Know Your Council) | at most 6.5% if all in Baw Baw (estimated) | uncertain / no |
| Black Saturday | Wellington | part of Churchill 25,861 ha | "nearly 11,000 km2" (Know Your Council) | at most about 2.4% | no |
| Black Saturday | Greater Bendigo | 341 ha | - | negligible | no (but 58 houses) |
| Black Summer | East Gippsland | 1.1 million ha (council) | not opened; "more than half" reported by council | over 50% (reported) | yes / yes |
| Black Summer | Towong | 218,015 ha | implied 666,700 ha = 218,015 / 0.327 (estimated) | 32.7% (reported by council) | yes / yes |
| Black Summer | Alpine | "29% of footprint directly impacted" (council) | 4,790 km2 (Know Your Council) so about 139,000 ha (estimated) | 29% (reported) | yes / yes |
| Black Summer | Wellington, Mansfield, Wangaratta, Indigo | no figure found | - | - | judgement: Wellington and Mansfield probably 5%+, unverified |
| Jan 2013 Aberfeldy | Wellington | 87,000 ha (ABC), assuming all in Wellington | "nearly 11,000 km2" = 1,100,000 ha | 7.9% (estimated; upper bound) | judgement: yes / no |
| Feb-Mar 2019 | Wellington | Licola 80,000+ plus Mt Darling-Cynthia Range 28,000+ = 108,000+ ha, assuming all in Wellington | 1,100,000 ha | 9.8% (estimated; upper bound) | judgement: probably yes / no. Zero homes lost there. |
| Feb-Mar 2019 | Cardinia | Bunyip 15,000+ ha shared with Baw Baw | area not verified | - | judgement: borderline for 5% |
| Dec 2015 Wye River | Colac Otway | 2,500 ha | area not verified | under 1% (judgement) | no |
| Mar 2018 | Corangamite, Moyne | Terang 9,725 + Camperdown 6,725 ha, etc. | areas not verified | probably 2-4% each (judgement) | no |
| Dec 2015 Scotsburn | Ballarat / Golden Plains | 4,000 ha | Golden Plains 2,705 km2 (Know Your Council) | at most 1.5% (estimated) | no |

## 4. Per-council loss data: where it exists

- Black Saturday: per fire only (VBRC Vol 1, with Exhibit 980 "Houses Destroyed - Breakdown by Fire" cited as the underlying source; I did not find the exhibit itself). Council-level counts exist for Murrindindi and Yarra Ranges only, on a different basis (section 2.1). VBRRA reports give **rebuilding permits** by council, not destroyed-house counts: Nillumbik 85, Murrindindi 1,023, Alpine 22 (15-month report, permits include sheds and commercial). The three-year report names the six most affected councils: Murrindindi, Latrobe, Yarra Ranges, Nillumbik, Mitchell, Whittlesea (VBRRA three-year report p.9).
- Black Summer: per-council house counts from three councils (section 2.2). A Bushfire Recovery Victoria or EMV damage assessment table by LGA was not found. The vic.gov.au recovery page reports 736 properties cleaned up, 2,500+ structures removed from 742 properties, and names East Gippsland, Towong and Alpine as the most impacted councils. **Lead (not verified):** Victorian government open data may hold a building-impact-assessment point layer for 2019-20; check data.vic.gov.au and HEAD it for size before anything else.
- Other events: per-event only, no per-council split needed because each event sits in one or two councils.

## 5. Victorian councils, boundary changes, comparison group

- **Number of councils:** the Victorian Electoral Commission says there are 79 local councils (VEC "Local councils" page, opened).
- **Boundary changes 2009-2021 relevant to ABS vintages 2015-2021:** I found no merger or split.
  - ABS Non-ABS Structures, LGA edition of June 2020: its update note mentions gazetted changes in NSW only (opened).
  - ABS ASGS Edition 3 (2021) LGA page: no changes listed for 2021; 2022 changed Palmerston (NT); the **2023 edition renamed Moreland to Merri-bek, with a code change**; 2024 unchanged; 2025 split East Arnhem (NT) (opened). All outside 2009-2021 for Victoria except that the 2023 vintage on disk carries the new Merri-bek code.
  - I could not open the ABS notes for the 2015-2019 editions (the guessed URLs returned the ABS homepage), so minor realignments before 2020 are not ruled out. The ABS crosswalks on disk will settle it.
  - All councils burnt in 2009 and 2019-20 (Murrindindi, Nillumbik, Mitchell, Whittlesea, Yarra Ranges, Latrobe, Wellington, Baw Baw, Cardinia, Indigo, Greater Bendigo, Alpine, Towong, East Gippsland) exist under the same names in the 2015-2021 vintages (judgement; names in council documents match).
  - Alpine resorts are outside the councils: DisasterAssist lists Lake Mountain Alpine Resort as "Unincorporated" (Jan 2026 page and the 2009 list) and Falls Creek, Mount Buller, Mount Hotham and Mount Stirling separately (2019-20). In ABS these are, I believe, under "Unincorporated Vic" (not verified). They cannot be scored as councils.
  - Name style: DisasterAssist and the state of disaster use "Wangaratta Rural" and "Wangaratta"; ABS uses "Wangaratta". Council-plan names are plain (Alpine, Towong).
- **No-fire comparison group (judgement, labelled):** the parent's rule is "no fire of at least 100 ha in the same period". Upper bounds from declarations: in 2009 25 of 79 LGAs were declared, in 2019-20 18-19 of 79, so at least about 54-60 councils had no declared bushfire impact. A council can still hold a 100 ha fire without being declared, so the true no-fire group is smaller. My judgement: a typical year leaves roughly 30-50 of the 79 with no fire of 100 ha or more (mostly the metropolitan and small lowland or urban councils; 31 metropolitan is my recollection, not verified), and an extreme year like 2009 or 2019-20 leaves perhaps 30-45. Compute it directly from the Geoscience Australia polygons (Victorian records end April/May 2022) against the ABS LGA layer.
- Caution on the comparison group: state-level shocks (drought, COVID from 2020, the 2019-20 smoke and tourism collapse across Victoria's north-east) hit non-burnt councils too, so "excess" is cleaner in a year without a statewide shock.

## 6. Fit with the data windows on disk

| Data on disk | Starts | Consequence for Victorian events |
|---|---|---|
| ABS CABEE business counts | Jun 2013 | Need pre-fire years: Aberfeldy Jan 2013 has none; Feb 2014 has one; Wye River Dec 2015 has two |
| DSS payments | Mar 2016 | Wye River (Dec 2015) has no pre-fire base; usable events from about 2017: Mar 2018, Feb-Mar 2019, Black Summer |
| DEWR SALM unemployment | Dec 2010 | Black Saturday 2009 and earlier have no pre-fire base |
| ABS personal income (pia_2020, pia_2024) | not checked by me | check year coverage before using any pre-2012 event |
| ABS Census for Victoria | NSW only on disk | dwellings per LGA for the DL denominator need the Victorian GCP packs (sizes in 2.2) |

So a four-pillar Victorian panel is realistic for Black Summer, Mar 2019 and Mar 2018 only. Black Saturday can carry DL and exposure. Victorian council finance ratios were **not researched** in this slice.

## 7. Summary table

| Candidate | Homes destroyed (reported) | Deaths | LGAs with >= 5% burnt (judgement) | Per-LGA loss data? | Verdict |
|---|---|---|---|---|---|
| Black Saturday 7 Feb 2009 (+ Delburn 28 Jan) | 2,133 houses Jan-Feb (VBRC summary); 2,029 (AIDR); per fire in VBRC | 173 (2 firefighters) | Murrindindi 40%, Nillumbik (about a quarter, unverified), Yarra Ranges 19.6%; probably Mitchell, Latrobe, Indigo, Whittlesea; Cardinia/Baw Baw uncertain | Per fire Y (VBRC). Per council: Murrindindi 1,397 and Yarra Ranges 304 from councils, different basis. No official table | Best size and burn share; fails IL/SL/SALM windows. Add for DL and exposure only. |
| Black Summer Vic, Nov 2019 - Feb 2020 | 400+ (CFA); 300+ (AIDR); 313 primary + 145 non-primary destroyed or damaged (IGEM, excerpt) | 5 (3 in East Gippsland) | East Gippsland over 50%, Towong 32.7%, Alpine 29%; probably Wellington, Mansfield | Council figures: East Gippsland 410, Towong 38, Alpine 1. No state table found | Add. Same season as NSW Black Summer, so more councils, not a new year. All windows fit. |
| Jan 2013 Aberfeldy (Wellington) | 22 | 1 | Wellington about 8% (upper bound) | Single event, single council | Maybe. Small loss; no CABEE base. |
| Feb-Mar 2019 (Bunyip, Yinnar South, Licola, Dargo) | 31 (29 Cardinia area, 2 Latrobe) | 0 | Wellington about 10% (no homes lost there); Cardinia borderline | Per event only | Maybe. In all windows. Wellington is a burn-with-no-loss row. |
| Dec 2015 Wye River - Jamieson Track | 116 | 0 | none (Colac Otway under 1%) | Single council (Colac Otway) | Weak. High loss but under 5% burnt, holiday-home town, no DSS base. |
| Mar 2018 Terang / Camperdown / Garvoc / Gazette | 26 residences | 0 | none | Per event only | No. Under 5% of any council. |
| Dec 2015 Scotsburn | 12 | 0 | none | - | No. |
| Feb 2014 (Mickleham, East Gippsland, Warrandyte etc.) | 40 total (AIDR) | 0 | not established | - | No / weak. Region "East Gippsland fires" entry unclear. |
| Jan 2006 | 57 | 4 | not established | - | Outside all data windows. |
| 2006-07 Great Divide | 51 (21 primary) | 1 | Alpine, East Gippsland likely | - | Outside data windows. Big area, few homes. |
| 2003 Alpine | 41 | not stated | Alpine likely | - | Outside data windows. |
| Hazelwood mine fire 2014 | 0 | none stated | not a bushfire | - | Not a candidate (coal-mine fire); Latrobe health case only. |

## 8. Could not verify

- Per-council houses destroyed for Black Saturday from any official source (none found). Nillumbik, Mitchell, Whittlesea, Latrobe, Wellington counts.
- The Nillumbik "quarter burnt / 125 homes" claim (excerpt only).
- Per-council house counts for Black Summer in Wellington, Mansfield, Wangaratta, Indigo, Wodonga; the split of the 5 deaths beyond East Gippsland's 3.
- IGEM Phase 1 report's 313 + 145 figure (excerpt only; page 403).
- Insured losses for Aberfeldy 2013, Feb 2014, Scotsburn, Mar 2018; the ICA catastrophe list itself is an xlsx (HEAD: 273,626 bytes, ICA-Historical-Normalised-Catastrophe-Master-Updated-2026_07.xlsx; not downloaded), and it is the place to confirm catastrophe status and insured loss for every event above.
- Disaster declarations for 2003, Jan 2006, 2006-07, Feb 2014 and Dec 2015 Wye River (DisasterAssist pages not found).
- Areas for Latrobe, Whittlesea, Indigo, Cardinia, Colac Otway, Corangamite, Moyne, East Gippsland (not opened; read from ABS ERP or LGA layer on disk).
- Harrietville 2013 size (excerpt only).
- ABS LGA change notes for the 2015-2019 editions.

## 9. Sources opened

Royal Commission and recovery reports
- VBRC Vol 1 chapters (Ch 3 Delburn, 4 Bunyip, 5 Kilmore East, 6 Horsham, 7 Coleraine, 8 Pomborneit-Weerite, 9 Churchill, 10 Murrindindi, 11 Redesdale, 12 Narre Warren / Upper Ferntree Gully, 13 Bendigo, 14 Beechworth-Mudgegonga): http://royalcommission.vic.gov.au/Finaldocuments/volume-1/HR/VBRC_Vol1_ChapterNN_HR.pdf (NN = 03 to 14)
- VBRC Summary: http://royalcommission.vic.gov.au/finaldocuments/summary/PF/VBRC_Summary_PF.pdf
- VBRC Vol 1 Introduction: http://royalcommission.vic.gov.au/Finaldocuments/volume-1/HR/VBRC_Vol1_Introduction_HR.pdf
- VBRRA 100 Day report: http://royalcommission.vic.gov.au/getdoc/d4fdd202-24b9-4625-996a-288fb655b492/TEN.046.001.0001.pdf ; 15 Month report: https://vgls.sdp.sirsidynix.net.au/client/search/asset/1162341 ; Three Year report: https://vgls.sdp.sirsidynix.net.au/client/search/asset/1290067
- Deloitte Access Economics, Supreme Court of Victoria: https://www.supremecourt.vic.gov.au/sites/default/files/2018-11/deloitte_access_economics_bushfires_report.pdf
- Yarra Ranges Council evaluation report: https://knowledge.aidr.org.au/media/4088/yr_2009_bushfires_evaluation_full_report.pdf
- Murrindindi Shire Council agenda attachment, 17 Dec 2012: https://www.murrindindi.vic.gov.au/files/assets/public/v/1/documents/1-council/council-meetings/agenda-and-minutes/17-december-2012/2012-12-17-ordinary-attachments-part-1.pdf (opened via WebFetch; pypdf on that URL got an HTML block page)
- EMV Review of the Wye River and Separation Creek Fire Recovery: https://files-em.em.vic.gov.au/public/EMV-web/Review_of_the_Wye_River_and_Separation_Creek_Fire_Recovery.pdf

Council documents 2019-20 and later
- Towong Municipal Recovery Plan: https://www.towong.vic.gov.au/repository/libraries/id:2cvu1xfyg1cxby8c14xc/hierarchy/Bushfire%20Recovery/Municipal%20Recovery%20Plan/municipal-recovery-plan.pdf
- Alpine Municipal Recovery Plan: https://www.alpineshire.vic.gov.au/sites/default/files/Alpine%20Municipal%20Recovery%20Plan%20Endorsed%2025%20June%202021.pdf
- East Gippsland Shire media release, 15 Jul 2021: https://www.eastgippsland.vic.gov.au/media-releases/east-gippslanders-dismayed-by-fire-grants-program
- Nillumbik MFMP 2020-23: https://www.nillumbik.vic.gov.au/files/assets/public/living-in/fire-and-other-emergencies/council-role/nillumbik-shire-council-municipal-fire-management-plan-2020-2023.pdf
- Know Your Council pages (vic.gov.au/know-your-council-*): Murrindindi, Mitchell, Alpine, Baw Baw, Golden Plains, Southern Grampians, Wellington, Nillumbik

Agencies and aggregators
- DisasterAssist (AGRN 322, 550, 557, 846, 882, and the 2024-2026 pages): https://www.disasterassist.gov.au/Pages/disasters/previous-disasters/Victoria/Victorian-bushfires-January-to-February-2009.aspx ; .../current-disasters/Victoria/Bushfires-February-2013.aspx ; .../Bushfires-27-March-2013.aspx ; .../south-east-victoria-bushfires-280219.aspx ; .../victorian-bushfires-november-2019-onwards.aspx ; .../victorian-bushfires-storms-commencing-13-february-2024.aspx ; .../western-victoria-bushfires-16-december-2024.aspx ; https://www.disasterassist.gov.au/Pages/disasters/victoria/victorian-bushfires-commencing-7-Jan-2026.aspx
- AIDR Knowledge Hub: Black Saturday https://knowledge.aidr.org.au/resources/bushfire-black-saturday-victoria-2009 ; Black Summer VIC https://knowledge.aidr.org.au/resources/black-summer-bushfires-vic-2019-20/ ; Great Divide https://knowledge.aidr.org.au/resources/bushfire-great-divide-complex-victoria/ ; 2003 https://knowledge.aidr.org.au/resources/bushfire-alpine-region-and-north-eastern-victoria/ ; 2006 https://knowledge.aidr.org.au/resources/bushfire-victoria-2006/ ; 2014 https://knowledge.aidr.org.au/resources/bushfire-victoria-2014/ ; Grampians 2014 https://knowledge.aidr.org.au/resources/bushfire-grampians-national-park-victoria/ ; Hazelwood https://knowledge.aidr.org.au/resources/bushfire-hazelwood-open-cut-mine-fire-victoria-2014/ ; Wye River https://knowledge.aidr.org.au/resources/bushfire-wye-river-jamieson-track-great-ocean-road-victoria-2015-2016/ ; 2018 https://knowledge.aidr.org.au/resources/2018-bushfire-vic-south-west-complex-fires/ ; 2019 https://knowledge.aidr.org.au/resources/2019-bushfire-vic-eastern-victorian-bushfires/
- CFA: http://www.cfa.vic.gov.au/about-us/history-major-fires/major-fires/black-saturday-2009 ; http://www.cfa.vic.gov.au/about-us/history-major-fires/major-fires/2019-2020-bushfires
- vic.gov.au recovery page: https://www.vic.gov.au/2019-20-eastern-victorian-bushfires
- Premier releases: https://www.premier.vic.gov.au/additional-disaster-assistance-victorian-bushfires ; https://www.premier.vic.gov.au/disaster-assistance-bushfire-affected-communities-victoria
- ABC News: 2019-02-03 Aberfeldy coronial https://www.abc.net.au/news/2019-02-03/aberfeldy-fire-coronial-report/10767938 ; 2021-01-29 Scotsburn https://www.abc.net.au/news/2021-01-29/scotsburn-bushfire-victims-get--compensation-five-years-later/13101888 ; 2018-03-19 and 2018-03-20 south-west fires; 2019-03-09 Bunyip https://www.abc.net.au/news/2019-03-09/bunyip-state-park-fire-destroyed-29-houses-authorities-confirm/10884798 and catastrophe https://www.abc.net.au/news/2019-03-09/bunyip-south-yinnar-fires-declared-catastrophe-for-insurance/10886216 ; 2020-01-06 https://www.abc.net.au/news/2020-01-06/bushfires-in-victoria-destroy-at-least-200-homes/11844292
- ICA data hub: https://insurancecouncil.com.au/industry-members/data-hub/ (xlsx link only; HEAD size 273,626 bytes)
- VEC: https://www.vec.vic.gov.au/electoral-boundaries/local-councils ; ABS LGA pages: https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/non-abs-structures/local-government-areas ; https://www.abs.gov.au/ausstats/abs@.nsf/Lookup/by%20Subject/1270.0.55.003~June%202020~Main%20Features~Local%20Government%20Areas%20(LGAs)~3
- ABS Census GCP Vic LGA packs (HEAD only): https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_GCP_LGA_for_VIC_short-header.zip (6,225,215 bytes) ; .../2016_GCP_LGA_for_VIC_short-header.zip (6,090,114 bytes)

Not opened, figures used only as flagged excerpts: IGEM Phase 1 report page (HTTP 403); Community Bushfire Connection Harrietville page; Nillumbik "quarter burnt" claim.
