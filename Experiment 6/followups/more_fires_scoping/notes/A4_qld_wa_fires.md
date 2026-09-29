# A4. Queensland and Western Australia fires: scoping notes

Prepared 2026-09-29 for Experiment 6 (real large fires beyond NSW). Scope: QLD and WA bushfires 2003-2023.

Labels used throughout: **reported** = a source I opened states it; **estimated** = I derived it (arithmetic shown); **judgement** = my call, not a sourced fact.
No data files were downloaded. Reports and web pages were read as text only (PDFs streamed into memory, nothing saved). Sizes of data files were taken from HEAD requests or catalogue metadata.

## 0. Limits of this pass (read first)

- The session web-search budget ran out part-way through. From that point I could only fetch pages by direct URL. Anything I could not reach is listed in section 9 and is NOT filled with guesses.
- Wikipedia and ACM mastheads were not used. Where a search result offered a number only from such a page I left it out.
- I did not read the on-disk data (GA outlines, ICA catastrophe file, house_loss folder). Cross-check those against the events below; they may already hold some of these numbers.
- Council areas: QLD areas come from QRA recovery plans. WA areas come from the DFES tenure tables quoted in the AFAC Wooroloo review, or from council websites. Areas I could not source are marked "not sourced". For final shares, intersect the GA outline with the ABS LGA boundary already on disk.

## 1. Headline findings

1. **Only a handful of QLD/WA events add real variation in "share of a council burned".** In WA: Waroona-Yarloop (Jan 2016), Wooroloo (Feb 2021), Esperance (Nov 2015), the Feb 2022 Wheatbelt fires. In QLD: the Sep-Dec 2019 event (Noosa, Lockyer Valley, Southern Downs, Somerset) and Nov 2018 Central Queensland (Mackay). Most other events burned <5% of any council (judgement).
2. **Waroona-Yarloop is the one WA event that plausibly puts a council at >=20% burned**, and it is a small shire (Shire of Waroona, 835 km2). Loss was concentrated in Yarloop, which sits in the Shire of Harvey, so burned share and loss land in different councils.
3. **Wooroloo (2021) has the cleanest per-council loss split in either state**: 80 properties destroyed in City of Swan and 6 in Shire of Mundaring, with DFES tenure areas for both councils, and a DRFA activation for exactly those two LGAs (AGRN 950). The worst-hit council is at least 6.4% burned (even if the fire is split so both councils burn in equal proportion) and at most 16.7%, so it never reaches 20% (estimated).
4. **QLD 2019 has per-council dwelling counts in the QRA local recovery plans** (Livingstone 14, Scenic Rim 11, Gladstone 8, Somerset 4, Toowoomba 1 plus reported Ravensbourne losses, Noosa 2). Total 49 homes statewide, so a large share of the fire footprint had almost no housing loss. That is useful as a "big burn, little loss" contrast to Black Summer.
5. **QLD Nov 2018 is a big-burn/low-loss event**: 1.4 million ha statewide, 9 dwellings destroyed, 8 DRFA LGAs. Mackay's local plan implies roughly 8-22% of that council burned (estimated, section 4).
6. **Data-window problem (judgement, matters a lot):** ABS CABEE business counts start June 2013 and DSS payments start Mar 2016. Any fire before 2016 has no DSS pre-fire baseline (Esperance Nov 2015 and Waroona Jan 2016 fall just before it). Pre-2013 fires (Toodyay 2009, Roleystone 2011, Margaret River 2011) have no CABEE baseline either. So the social-loss pillar only works for events from about mid-2016 onward. SALM starts Dec 2010, so unemployment is fine for all events below.
7. **Census 2016/2021 profile files on disk are NSW only.** Dwelling denominators for QLD/WA councils will need another source (ABS Census, or ERP with household size).

## 2. Western Australia candidates

### WA-1. Waroona-Yarloop fire, January 2016

| Item | Value | Source / label |
|---|---|---|
| Dates | Ignited by lightning 5 Jan (first detected 6 Jan 0630); Yarloop impacted evening 7 Jan; all-clear 23 Jan | DBCA reconstruction PDF p3; Ferguson report p19; ABC 2016-01-23 (reported) |
| Area burned | 69,165 ha (31,180 ha private, 37,985 ha public; 3,300 ha FPC plantation) | Ferguson Special Inquiry, pp19, 86 (reported). AIDR says 69,000 ha; ABC says >69,000 ha |
| Homes destroyed | 181, but the same report counts three ways: "buildings 181 (166 dwellings in Yarloop)" (p86 table); "181 dwellings" (p12); "181 properties" (p19) | Ferguson (reported; counting basis is inconsistent within the report). ABC 2026 says "more than 160" |
| Homes damaged | Not found in what I read | not verified |
| Deaths | 2 (Yarloop residents, civilians). No firefighter death mentioned in text I read | Ferguson pp12, 19 (reported) |
| Councils | Shire of Harvey (Yarloop: the report refers to Shire of Harvey reserves in the Yarloop townsite, pp17, 38) and Shire of Waroona (Waroona townsite). Preston Beach: p18 groups it with "the Shires of Harvey and Waroona" without saying which; I did not confirm its council. Emergency declared for the Shires of Waroona and Harvey (p86). The origin in Lane Poole Reserve is described as in the Shires of Waroona and Boddington (p164) | Ferguson pp17-18, 38, 86, 164 (reported) |
| Council costs | Shire of Harvey: $12.84m total, of which $9.28m building and contents; Shire of Waroona: $0.85m | Ferguson Table 6.2, p88 (reported) |
| Insured loss | $71m (ICA estimate cited by Ferguson, Table 6.2). AIDR: $70m. Total cost of fire $155m (Ferguson p19) | reported |
| Natural-disaster declaration | Not confirmed from a page I opened. The DRFA activation dataset (section 6) would settle it | not verified |
| Reported burned area per LGA | None found | - |
| GA outline on disk | Murray Road / Waroona-Yarloop Jan 2016, 68,246 ha (from brief) | - |

**Burned-share arithmetic (estimated):**
- Shire of Waroona area: 835 km2 = 83,500 ha (Shire of Waroona statistics page, reported).
- Shire of Harvey area: about 1,734 km2 (estimated: council page gives 2024 ERP 31,495 and density 18.16 per km2; 31,495 / 18.16). Not stated directly.
- If ALL 69,165 ha lay inside these two shires, the smallest possible "worst-shire" share is when both shires are burned in equal proportion: 69,165 x 83,500 / (83,500 + 173,400) = 22,481 ha = **26.9% of each**. So at least one would be >=26.9%.
- That assumes no burn in Shire of Murray or Boddington. The origin lies near those boundaries, so the assumption may not hold.
- **Judgement:** Waroona very likely >=5%; >=20% likely for Waroona (and/or Harvey) but must be confirmed by intersecting the GA outline with the ABS LGA polygons.

**Per-council loss data exists?** Partly. Yarloop's 166 dwellings belong to Shire of Harvey (reported). The other 15 (181 minus 166, estimated) are unallocated between Waroona, Harvey and any other shire. Denominators: Shire of Waroona says about 2,000 residential dwellings and about 4,650 people (Shire statistics page, reported). Harvey dwellings not sourced.

**Verdict:** Best WA candidate for a small-shire, high-burn-share case; needs the per-shire loss split from a recovery or insurer source and has no DSS pre-fire baseline.

### WA-2. Esperance fires, November 2015

| Item | Value | Source / label |
|---|---|---|
| Dates | Lightning ignitions 15 Nov; catastrophic run and deaths 17 Nov | DFES feature story; ABC 2019-12-07 (reported) |
| Area burned | "300,000+" ha (DFES). Component split 128,000 (Cascades) + 18,000 (Merivale) + 164,000 (Cape Arid complex) = 310,000 came from a search summary I could not trace to a primary page; treat the split as unverified | DFES (reported); split not verified |
| Homes destroyed | 2 (DFES). A figure of 3 houses plus 16 non-residential buildings circulates in secondary listings; I could not trace it to a primary page | DFES (reported); alternative not verified |
| Deaths | 4 civilians, in two vehicles on Griggs Road, Scaddan, 17 Nov (Kym Curnow, Thomas Butcher, Julia Kohrs-Lichte, Anna Winther) | ABC coroner article 2019-12-07 (reported). Coroner: Sarah Linton |
| Council | Shire of Esperance | DFES; ABC (reported) |
| Declaration / insured loss | Not confirmed / not found | not verified |

**Burned-share arithmetic (estimated):** Shire of Esperance area is reported three different ways: 44,000 km2 (Shire "About the area" page), "over 53,700 km2" (Shire "General information" page, which also says about 5,900 km2 is national parks and reserves), and 42,547 km2 (ABS figure quoted in a secondary summary, not opened). 300,000 to 310,000 ha over those areas gives **5.8% (5.37m ha) to 7.3% (4.25m ha)**. Some of the 310,000 ha may lie outside the shire (Cape Arid). **Judgement:** >=5% probable but borderline; >=20% no.
**Per-council loss data?** Only the shire-level story; no per-property list found.
**Verdict:** Useful for the deaths component (4 deaths in a shire of about 14,000 people: 13,883 at 2021 Census per the Shire page) but very few homes; no DSS baseline (Nov 2015 precedes Mar 2016).

### WA-3. Wooroloo bushfire, February 2021

| Item | Value | Source / label |
|---|---|---|
| Dates | 1 Feb 2021 (about midday) to contained 6 Feb | AFAC Independent Operational Review, pp4, 8-9 (reported) |
| Area burned | About 10,750 ha (AFAC); "over 10,500 ha" (DFES annual report, AIDR); 154 km perimeter | reported |
| Homes destroyed | 86 properties destroyed: **80 in City of Swan, 6 in Shire of Mundaring**. AFAC also says 110 dwellings impacted, 86 destroyed. Tilden Park had the majority of losses | AFAC review p4 and p8 (reported) |
| Homes damaged | "more than 100" structures destroyed or damaged (AIDR); 137 properties registered in clean-up | AIDR; WA joint media statement Aug 2021 (reported) |
| Deaths | None | DFES 2020/21 annual report (reported) |
| Councils | City of Swan, Shire of Mundaring. The AFAC review text places the burned area in these two councils only (p4). Its map (p8) also labels Shires of Toodyay and Northam, and one search summary I could not open mentions Chittering and Northam in the emergency area; treat those as adjacent, not burned | AFAC pp4, 8 (reported); other mentions not verified |
| Declaration | DRFA activated for **Mundaring and Swan**; AGRN 950; AGDRP and DRA. Category C community recovery package $18.1m | DisasterAssist page; Home Affairs release 3 Feb 2021; DFES (reported) |
| Insured loss | $93m (AFAC p4); $92m (AIDR) | reported |
| Reported burned area per LGA | None found | - |

**Burned-share arithmetic (estimated):** DFES tenure tables quoted in the AFAC review (p17) give Shire of Mundaring 64,409 ha and City of Swan 104,210 ha.
- Worst case all in Mundaring: 10,750 / 64,409 = 16.7%. All in Swan: 10.3%.
- Smallest possible worst-council share (fire split so both are equally burned): 4,106 ha in each, i.e. **6.4%** of the more affected council.
- **Judgement:** at least one council >=5% is certain if the review is right that only these two councils burned; >=20% is not possible.

**Per-council loss data exists?** Yes (Swan 80, Mundaring 6 destroyed; AFAC review p4). Dwelling denominators not sourced.
**Verdict:** Strong add. Full data window (SALM, CABEE, DSS, PIA all cover 2021). Caveat: City of Swan is a large metropolitan council, so per-1,000-dwelling loss is small.

### WA-4. February 2022 Wheatbelt and South West fires (four Level 3 incidents, 4-6 Feb 2022)

Source for all rows: AIDR Major Incidents Report 2021-22, pp43-46 (reported).

| Incident | Council(s) | Area | Loss reported |
|---|---|---|---|
| Shackleton Complex (two fires) | Shires of Bruce Rock, Quairading, Corrigin | 44,600 ha | 15 houses and 54 other structures; significant breeding livestock and feed losses |
| Narrogin East | Shire of Narrogin | 17,851 ha | 31 "buildings"; a commercial piggery with 5,000 livestock |
| Bridgetown | Shire of Bridgetown-Greenbushes | 2,206 ha | 8 houses and 15 other structures; timber treatment facility |
| Bayview Rise | Shire of Denmark | 2,200 ha | 4 houses and 9 other structures |

- Deaths: none stated in the report pages I read.
- Declaration: not found (the AIDR report does not say). Not verified whether DRFA was activated.
- Burned-share (judgement, areas not sourced this session): Wheatbelt shires are typically a few thousand km2. If all 44,600 ha of Shackleton lay in ONE shire of area under 8,920 km2, that shire would be at least 5%. Split across three shires the worst-hit shire is very likely still >=5%. Confirm with the GA outline and ABS areas.
- **Per-council loss data?** Incident-level counts only; per-shire split for Shackleton (three shires) not published in the report.
- **Verdict:** Worth adding. Small rural shires with a few hundred to a couple of thousand dwellings, so per-1,000 loss could be large. Full data window. Needs DRFA/activation check and per-shire loss breakdown.

### WA-5. Parkerville, Stoneville and Mt Helena fire, January 2014

- Date: 12 Jan 2014 (AIDR; Bushfire and Natural Hazards CRC report p8).
- Area: 650 ha (AIDR). Other figures in circulation are about 386-400 ha (secondary). Sources disagree; I use AIDR as reported.
- Homes destroyed: **57** (CRC report pp6, 8, 9: majority in Stoneville). AIDR quotes 52. Sources disagree.
- Deaths: none from this fire. AIDR notes 1 death of a man preparing for a separate blaze in John Forrest National Park (civilian).
- Council: Shire of Mundaring (CRC report p8; AIDR).
- Insured loss: early ICA estimate $15m (AIDR).
- Declaration: AIDR lists State grants ($3,000 per destroyed house) and joint funding for clean-up, and Australian Government disaster recovery payments; a formal WANDRRA declaration page was not opened. Not verified.
- Burned share (estimated): 650 ha / 64,409 ha (Mundaring, DFES via AFAC) = **1.0%**; at 386 ha, 0.6%. Judgement: <5%.
- Per-council loss data: single council, so yes trivially (57 or 52 in Mundaring).
- **Verdict:** High loss, tiny burn share; useful as an interface-fire contrast but only one full year of CABEE baseline (June 2013) and no DSS. Weak for the SL pillar.

### WA-6. Perth Hills fires (Roleystone-Kelmscott and Red Hill), 5-6 February 2011

- Area: Roleystone about 440 ha; Red Hill about 1,100 ha (AIDR).
- Homes destroyed: 71 (AIDR; one line says 72); damaged about 39. Deaths: none. Injuries: at least 12 hospitalised.
- Councils named: Roleystone and Kelmscott (City of Armadale); Red Hill, Herne Hill, Millendon, Baskerville, Gidgegannup (north-east; council names not stated in the AIDR text).
- Declaration: Premier declared Roleystone, Kelmscott and Red Hill natural disaster zones on 7 Feb 2011 (AIDR, reported).
- Insured loss: $35m preliminary ICA estimate (AIDR).
- City of Armadale area: not sourced. Judgement: 440 ha is well under 5% of any metropolitan council.
- **Verdict:** Pre-window (no CABEE, no DSS); low burn share. Not recommended except as a reference.

### WA-7. Margaret River (23-26 Nov 2011) and Nannup (from 2 Dec 2011)

- Margaret River: 3,400 ha; AIDR lists 32 houses plus 5 sheds, 9 chalets, 1 shop, and states "total homes destroyed 39"; another summary says 39 homes destroyed and 14 damaged. I treat 32 houses / 39 as unresolved. No deaths. Insured loss $53.5-54m preliminary. Premier declared an eligible natural disaster (AIDR, reported).
- Nannup fire: about 55,150 ha, small property loss (AIDR, reported).
- Councils: Shire of Augusta-Margaret River; Shire of Nannup (also Molloy Island, Augusta in AIDR text). Areas not sourced.
- Judgement: Nannup fire may exceed 5% of Shire of Nannup, but area not sourced and losses were small. Margaret River <5% (3,400 ha would exceed 5% only in a shire under 68,000 ha, and this shire is much larger; judgement).
- **Verdict:** Pre-window. Skip for modelling; note Nannup as a large-burn/low-loss example only.

### WA-8. Toodyay fire, 29 December 2009

- 38 homes destroyed, about 3,000 ha, more than $50m damage, no deaths (ABC 2009-12-31; AIDR AJEM Apr 2013 article; reported). Early ABC reports said "at least eight homes" on 29 Dec.
- Council: Shire of Toodyay (the AIDR article does not name the council; the FESA Major Incident Review, which I could not open, is the primary source).
- Area of Shire of Toodyay: not sourced. Judgement: 3,000 ha is <5% of any WA shire of Toodyay's size.
- **Verdict:** Pre-window; low share. Not recommended.

### WA-9. Large fires with no household loss (not household events)

- **Esperance complex, Jan-Mar 2019:** about 315,000 ha, perimeter 1,500 km, no lives lost, only outbuildings and sheds destroyed (AIDR Major Incidents Report 2018-19, p36; reported). Council: Goldfields-Esperance region; Shire of Esperance and others. A high-burn, near-zero-loss event: a natural "placebo" for a burned-share design.
- **Kimberley and pastoral fires:** no source opened (search budget ran out). Treat as no-household-impact by expectation, not fact.

### WA-10. Mariginiup fire, November 2023 (outside GA WA coverage)

- Started about 1pm 22 Nov 2023; about 2,000 ha and 60 km perimeter by the morning of 24 Nov; "some residential and non-residential properties" confirmed destroyed (WA joint media statement 25 Nov 2023; number not given). DRFA activated for **Swan and Wanneroo** (DisasterAssist; WA statement).
- Homes destroyed: not verified. GA WA outlines end mid-2023, so no outline on disk. Judgement: <5%. Also the outcome window (post-2023) is too short for most pillars.

### WA leads I could not verify

Boddington 2012, Northcliffe/Bunbury-region fires Dec 2019 and Dec 2020, Boorabbin Dec 2007: nothing found. The AIDR Major Incidents Reports 2016-17 to 2023-24 (which I grepped) list no other WA bushfire with household loss beyond those above (2019-20 and 2023-24: none; 2023-24: no Level 3 bushfire in WA). Those reports only cover "major incidents", so smaller events could be missing.

## 3. Council areas and vintages: WA

- Reported: Shire of Waroona 835 km2; Shire of Mundaring 64,409 ha; City of Swan 104,210 ha; Shire of Esperance 44,000 / over 53,700 / 42,547 km2 (sources differ). Harvey about 1,734 km2 (estimated).
- The AFAC review notes only 85 WA local governments are subject to bushfire risk management planning (54 with endorsed plans at the time). I did not find a source for the total of WA local governments (brief says about 139) or for WA amalgamations since 2003. Use `boundary_changes.html` and the ABS crosswalks on disk to check WA LGAs across vintages 2015 to 2023.

## 4. Queensland candidates

### QLD-1. Queensland Bushfires, September to December 2019 (AGRN 909; related AGRNs 870, 876, 879)

| Item | Value | Source / label |
|---|---|---|
| Dates | 6 Sep to about 7 Dec 2019 (AIDR); DRFA event window 1 Sep to 31 Dec 2019 | AIDR; DisasterAssist (reported) |
| Area burned | QRA: "more than 7.5 million ha" (p9) and "over 7.7 million ha" (p5). AIDR (QFES source): 6.6 million ha | reported; sources disagree |
| Homes destroyed | **49** homes across the state, 100 further damaged; also 68 sheds and 5 commercial buildings | QRA State Recovery Plan pp5, 14, 29 (reported); AIDR |
| Deaths | None stated in the QRA plan text (I searched for deaths/fatalities) | not found |
| Insured loss | $69.6m for Queensland | AIDR (reported) |
| DRFA / disaster declaration | DRFA activated for **23 LGAs** (Counter Disaster Operations): Brisbane, Bundaberg, Gold Coast, Cook, Fraser Coast, Gladstone, Gympie, Ipswich, Livingstone, Lockyer Valley, Mareeba, Noosa, North Burnett, Redland, Rockhampton, Scenic Rim, Somerset, South Burnett, Southern Downs, Sunshine Coast, Toowoomba, Townsville, Whitsunday. Personal Hardship Assistance in 9 (Bundaberg, Gladstone, Livingstone, Noosa, Scenic Rim, Somerset, Southern Downs, Sunshine Coast, Toowoomba). Primary-producer loans in 13. State of fire emergency for 42 LGAs from 9 Nov | DisasterAssist page; QRA State Recovery Plan pp9, 11-12 (reported) |

**Per-council figures from the QRA plan and local recovery plans (reported unless marked estimated):**

| Council | Area (km2, QRA) | Dwellings destroyed | Burned/affected area reported | Share estimated |
|---|---|---|---|---|
| Livingstone (Cobraball fire, 9 Nov) | 11,776 | 14 (plus 37 other structures per local plan; state plan says 47) | about 11,500 ha (local plan); over 13,000 ha (state plan p36) | 1.0% to 1.1% |
| Scenic Rim (Binna Burra, Sarabah, Nov fires) | 4,256 | 11 destroyed/uninhabitable, 18 properties damaged | not stated | - |
| Gladstone (Mount Maria fire, from 15 Dec) | 10,506 | 8 | 32,425 ha burnt | 3.1% |
| Somerset | 5,382 | 4 | about 25,500 ha "impacted" | 4.7% (just under 5%) |
| Toowoomba (Pechey/Ravensbourne; Cypress Gardens/Forest Ridge) | 12,973 | 1 (local plan, Cypress Gardens/Forest Ridge); ABC reported 4 homes at Ravensbourne | Pechey fire nearly 20,000 ha (ABC 2019-11-22) | about 1.5% |
| Noosa | 871 | 2 houses (1 at Peregian in Sep; 1 in the Nov Cooroibah/North Shore fires) plus 2 unapproved dwellings destroyed in Nov (QRA plan pp82-83). ABC's first-day report said 10 homes at Peregian; the QRA figure is the later one | **13,700 ha burnt** in the shire (Sep and Nov fires); 366 ha at Peregian | **15.7%** |
| Lockyer Valley | 2,272 | none stated in plan | about 22,000 ha "impacted" | 9.7% |
| Southern Downs | 7,122 | not stated (Sep fires: "damage to houses") | over 3,000 ha (Sep); estimated 50,000 ha agricultural land "destroyed/damaged" (Nov) | up to 7.4% (upper bound: not all is burnt area) |
| Mareeba / Cook / Fraser Coast / North Burnett / Redland | - | Mareeba: at least one home; Cook: one house (ignition point); Fraser Coast, North Burnett, Redland: no property damage | - | - |

Sum of the named councils' dwellings destroyed: 40 of the 49 statewide (14 + 11 + 8 + 4 + 1 + 2, estimated; Toowoomba's 1 and Noosa's 2 as in the table). The remaining 9 are not itemised in what I read, and the ABC's 4 at Ravensbourne may overlap with the plan's Toowoomba figure.

**Judgement on burned share:** Noosa (15.7%) and Lockyer Valley (9.7%, "impacted") are >=5%; Southern Downs may be. None of these reaches 20% on the figures reported. Noosa is a small shire with only 2 houses lost: an extreme "big burn, almost no loss" case.
**Per-council loss data exists?** Yes for the main councils (QRA local recovery plans: Scenic Rim, Somerset, Southern Downs, Toowoomba PDFs; Livingstone, Noosa, Gladstone, Lockyer Valley summaries inside the state plan). Not exhaustive: absence of a number is not proof of zero.
**Verdict:** Best QLD candidate; many councils, sourced counts, full data window. Confound: same season as NSW/Vic Black Summer and a severe drought (QRA lists drought declarations for most of these LGAs).

### QLD-2. Central Queensland Bushfires, 22 Nov to 6 Dec 2018

| Item | Value | Source / label |
|---|---|---|
| Area burned | 1.4 million ha statewide; 140,000 ha of national park and state forest; 82% of Deepwater National Park | QRA Central Queensland Bushfires Recovery Plan (Aug 2019) pp5, 9 (reported) |
| Homes | **9 dwellings destroyed, 17 damaged**; 27 sheds destroyed; 479 damage assessments in 35 localities across 8 LGAs | QRA plan p5, p9; AIDR Major Incidents Report 2018-19 p18 (reported) |
| Deaths | "one life was lost" (QRA plan p9); civilian vs firefighter not stated | reported |
| DRFA LGAs | 8: Banana, Bundaberg, Central Highlands, Gladstone, Isaac, Livingstone, Mackay, Rockhampton | QRA plan p5; QRA event page (reported) |
| Funding | $12.042m Category C and D package | QRA event page (reported) |
| Insured loss | not found | - |

**Per-council (reported):** Gladstone 3 dwellings destroyed/uninhabitable, 64 properties impacted; Mackay 3 households destroyed (1 Netherdale/Finch Hatton, 2 Dalrymple Heights); Rockhampton 1 (Kabra); Livingstone none stated. That is 7 of 9; the other 2 are not itemised.
**Mackay burned share (estimated):** Mackay Regional Council area 7,622 km2 (QRA CQ plan p8). Its local plan reports 63,194 ha of bush reserve and state national park "lost", 101,339 ha of cropping, forestry and mining land "lost", and 3,458 ha of parkland in the fire scar. Land in the two large categories may not all be inside the council or all burnt. Adding 63,194 + 101,339 = 164,533 ha gives **21.6%**; national park/bush reserve alone gives **8.3%**. **Judgement:** Mackay is >=5% almost certainly and may reach 20%.
**Verdict:** Valuable for the "burned share high, loss low" end of the design. Only 9 dwellings, so DL is near zero; DL per 1,000 dwellings meaningless. Other pillars (IL, FP, SL) could still be tested. Full data window.

### QLD-3. Other Queensland fire activations (from QRA activations list, 150 activations over 3 pages)

Dates and LGA only; I did not find loss figures for these.

| Event | Dates | Councils / notes |
|---|---|---|
| Queensland Bushfires (grass and scrub, mostly western/central) | Aug-Nov 2011 | NDRRA (Minister-activated). More than 40 LGAs listed, mostly western and central (Longreach, Barcaldine, Diamantina, Boulia, Winton, etc.) |
| Far Northern Queensland Bushfires | late Oct-Dec 2012 | NDRRA |
| South Western Queensland wildfires | Dec 2012 | NDRRA |
| North Stradbroke Island fires | from 29 Dec 2013 | Redland City Council (Counter Disaster Operations, 8 Jan 2014) |
| Cape Cleveland bushfires | 6 Oct 2015 | Townsville City Council; State Disaster Relief Arrangements (SDRA), not NDRRA |
| Gympie bushfires | 19-27 Sep 2018 | Gympie Regional Council |
| Mareeba Tablelands bushfires | 17 Sep-9 Oct 2018 | Mareeba, Tablelands |
| Redland bushfires | 28 Nov-13 Dec 2018 | Redland City Council |
| Wallangarra bushfires | 12-21 Feb 2019 | Southern Downs |
| Kooralbyn, Gumlow, K'gari (Fraser Island) | Oct 2020, Nov 2020, Nov-Dec 2020 | Scenic Rim; Townsville and others; Fraser Coast |
| Sept-Oct 2009 Queensland bushfires | Sept-Oct 2009 | in the Qld Open Data NDRRA activations dataset; not opened |
| 2023 events: Southern Queensland (8 Sep-7 Nov), Nome and Julago (16-24 Sep), Mount Isa (23 Oct-1 Nov), Northern Queensland (18 Oct-8 Dec), The Pines and Condamine Farms (19 Nov-1 Dec) | 2023 | listed with fact sheets; loss figures not read |

Judgement: none of these is likely to add household loss variation (activation summaries do not carry loss counts). The Aug-Nov 2011 and 2012 events are savanna/grassland and pastoral fires: **not household-impact events**. Also pre-2013 for the outcome data.

## 5. Consolidated arithmetic table (burned share; estimated unless noted)

| Event / council | Burned (ha) | Council area (ha) | Share |
|---|---|---|---|
| Waroona-Yarloop, two shires (min worst-shire) | 69,165 in total | Waroona 83,500; Harvey about 173,400 | >=26.9% (only if no burn outside these two shires) |
| Wooroloo, worst council minimum | 10,750 in total | Mundaring 64,409; Swan 104,210 | >=6.4%; max 16.7% (Mundaring) |
| Esperance 2015 | 300,000-310,000 | 4.25m-5.37m | 5.6-7.3% (sources for area differ) |
| Noosa 2019 | 13,700 | 87,100 | 15.7% |
| Lockyer Valley 2019 | 22,000 (impacted) | 227,200 | 9.7% |
| Southern Downs 2019 | up to 53,000 (agricultural land) | 712,200 | up to 7.4% |
| Somerset 2019 | 25,500 (impacted) | 538,200 | 4.7% |
| Gladstone Dec 2019 | 32,425 | 1,050,600 | 3.1% |
| Toowoomba Pechey 2019 | about 20,000 | 1,297,300 | 1.5% |
| Livingstone Cobraball 2019 | 11,500-13,000 | 1,177,600 | 1.0-1.1% |
| Mackay Nov 2018 | 63,194 to 164,533 | 762,200 | 8.3% to 21.6% |
| Parkerville 2014 | 650 (or 386) | 64,409 | 1.0% (0.6%) |

## 6. Where to get the declarations by LGA (data catalogue findings)

- **DRFA Activation History by LGA**, data.gov.au (NEMA), CC-BY, covers 2006 to current (as at 11 Aug 2026), by LGA, all states. One CSV, 367,919 bytes (HEAD Content-Length; catalogue also lists 367,919). URL: https://data.gov.au/data/dataset/10ba7303-e3af-41b4-98b5-e04db77caea8/resource/ada7908b-afe6-48f3-966b-789aa26c1391/download/drfa_activation_history_by_location_2026_august_11.csv . This would settle "natural-disaster declaration" status for every event above in one small file. Not downloaded. (The data.gov.au dataset page itself refused a plain fetch; the catalogue API answered.)
- **QRA activations** (150 items, 3 pages): https://www.qra.qld.gov.au/disaster-funding-activations/activations . Each event has a PDF summary listing activated councils. Queensland Open Data also hosts NDRRA activations for Aug 2007 to Mar 2014 (47 resources, last updated 25 July 2016).
- **DFES WA recovery funding page** lists only recent activations (2023 onward) in the page I read; the DisasterAssist site holds older WA pages (Wooroloo: AGRN 950, Mundaring and Swan).
- **ICA catastrophe list:** `ica_catastrophes.xlsx` is already on disk. Cross-check WA/QLD bushfire rows there against the insured figures I quote: Waroona $71m, Wooroloo $93m, Perth Hills 2011 $35m preliminary, Margaret River $53.5-54m preliminary, Parkerville $15m early estimate, Qld 2019 $69.6m; Qld Nov 2018 not found.

## 7. Council changes since 2003 and comparability with ABS vintages 2015-2021

**Queensland**
- 2008 amalgamations (from brief). QRA confirms Southern Downs was created in 2008 by merging Warwick and Stanthorpe shires (State Recovery Plan p61) and Redland attained city status in March 2008 (p58).
- 2013 de-amalgamations of Cook, Douglas, Livingstone, Mareeba (from brief; QRA lists Cook, Livingstone, Mareeba separately in 2019). Noosa Shire was also re-created around 1 Jan 2014: this is from my own recollection, not a page I opened; Noosa appears as its own LGA (871 km2) with Sunshine Coast (about 2,290 km2) in the 2019 QRA plan, which is consistent. Verify the date.
- QRA states Queensland has 77 LGAs (CQ plan p5; State plan p11). All ABS vintages you hold (2015 to 2023) post-date the splits, so QLD LGA geography is stable for fires from 2015. Pre-2014 baseline years (for example Noosa within Sunshine Coast) only matter if ABS series are not back-cast to the current vintage (judgement: ABS regional series are normally published on the current ASGS edition).
- Southern Downs: the QRA local plan lists "de-amalgamation process" as a community dynamic (State plan pp94-95). Its outcome is not confirmed here; check against the ABS crosswalks on disk.

**Western Australia:** I found no source on amalgamations or boundary changes since 2003 and will not assert any. Check `boundary_changes.html` and the ABS crosswalks (2015-2016, 2016-2018, 2018-2020, 2020-2021, 2021-2023).

## 8. Is the comparison group large enough for the "excess change" design? (judgement)

- **QLD (77 LGAs):** the criterion is "no fire >=100 ha in the same period". In northern and western QLD, savanna and pastoral fires of that size are routine every year (the Aug-Nov 2011 activation alone lists more than 40 LGAs). The eligible controls are then mostly south-east metropolitan and coastal councils (Brisbane, Logan, Moreton Bay, Gold Coast, Redland and similar), which are structurally different from the rural councils that burned. Expect the control set to be thin or unrepresentative in most years; a higher area threshold, or region-stratified controls, would be needed. This must be checked with the GA outlines.
- **WA (about 139 LGAs per brief):** metropolitan and many Wheatbelt/South West councils often have no fire >=100 ha in a year, so a control set exists in most years. But Pilbara, Kimberley, Goldfields, Murchison and Gascoyne councils burn routinely, and mining councils have very different income and finance patterns. Match controls by region type or use mining-excluded controls.
- Both states: because "excess" nets out the state-wide shock, a state-wide drought and a concurrent season (QLD 2019 sits inside Black Summer and drought) can still leak into the control group. Stated as judgement, not tested.

## 9. Not verified / open items

- Per-shire homes lost for Waroona-Yarloop beyond "166 dwellings in Yarloop (Harvey)"; per-shire burned hectares for any WA event.
- DRFA/WANDRRA activation for Waroona 2016, Esperance 2015, Parkerville 2014 (partial), Feb 2022 WA fires.
- Council areas not sourced: Armadale, Augusta-Margaret River, Nannup, Toodyay, Corrigin, Quairading, Bruce Rock, Narrogin, Bridgetown-Greenbushes, Denmark, Wanneroo.
- Total number of WA local governments and any WA boundary changes.
- Insured loss for Qld Nov 2018.
- Deaths (firefighter vs civilian) for QLD 2018 (one life lost, not classified).
- Kimberley/pastoral mega-fires; Boddington 2012; Northcliffe 2019/2020; Boorabbin 2007.
- WA and QLD council finance data availability (MyCouncil for WA; QLD council financial statements) was not scoped here.

## 10. Final table

| Candidate | Homes destroyed (reported) | Deaths | Councils with >=5% burned (judgement) | Per-council loss data exists? | One-line verdict |
|---|---|---|---|---|---|
| WA Waroona-Yarloop, Jan 2016 | 181 (buildings/dwellings/properties, inconsistent); 166 dwellings in Yarloop | 2 civilians | Waroona very likely; Harvey possible; >=20% plausible for Waroona | Partly: Y (Yarloop = Harvey, Ferguson report); rest unallocated | Best WA small-shire case; no DSS baseline; needs per-shire split |
| WA Esperance, Nov 2015 | 2 (DFES) | 4 civilians | Esperance, borderline (5.6-7.3%) | N (shire-level only) | Deaths test in a giant shire; no DSS baseline; almost no homes |
| WA Wooroloo, Feb 2021 | 86 | 0 | At least one of Swan/Mundaring >=6.4%; none >=20% | Y: Swan 80, Mundaring 6 (AFAC review) | Strong add: clean split, full data window, DRFA on both LGAs |
| WA Wheatbelt/SW fires, Feb 2022 | 15 (Shackleton) + 8 (Bridgetown) + 4 (Denmark); Narrogin East 31 "buildings" | none stated | Shackleton shires likely; areas not sourced | Incident-level only | Add; small shires; check DRFA and per-shire counts |
| WA Parkerville, Jan 2014 | 57 (CRC); 52 (AIDR) | 0 from this fire | None (about 1% of Mundaring) | Y (single council) | Interface fire; tiny burn share; thin baseline |
| WA Roleystone-Red Hill, Feb 2011 | 71 | 0 | None | N | Pre-window; skip |
| WA Margaret River, Nov 2011 (and Nannup) | 32 houses or 39 (sources differ); Nannup "small" | 0 | Margaret River no; Nannup possibly (area not sourced) | N | Pre-window; skip |
| WA Toodyay, Dec 2009 | 38 | 0 | None | N | Pre-window; skip |
| WA Esperance complex, Feb 2019 | 0 (outbuildings only) | 0 | Probable in Esperance/Dundas (315,000 ha) | N | Big burn, no loss; usable as a placebo only |
| WA Mariginiup, Nov 2023 | "some" (number not verified) | not verified | No (about 2,000 ha) | N | Too recent; no GA outline; skip |
| QLD Sep-Dec 2019 (AGRN 909) | 49 statewide (100 damaged) | none stated | Noosa (15.7%), Lockyer Valley (9.7% impacted), Southern Downs (up to 7.4%); Somerset 4.7% | Y for main councils (QRA plans): Livingstone 14, Scenic Rim 11, Gladstone 8, Somerset 4, Toowoomba 1 (plus 4 reported at Ravensbourne), Noosa 2 | Best QLD add; 23 DRFA LGAs; drought/Black Summer confound |
| QLD Nov-Dec 2018 Central QLD | 9 (17 damaged) | 1 (type not stated) | Mackay (8-22%) | Y: Gladstone 3, Mackay 3, Rockhampton 1 | Big burn, almost no loss; test for other pillars |
| QLD Aug-Nov 2011, 2012 grass/wild fires | not stated | not stated | pastoral LGAs (not household) | N | Not household events; pre-window |
| QLD other activations 2013-2023 (Stradbroke, Gympie, Mareeba, Wallangarra, Kooralbyn, K'gari, 2023 events) | not retrieved | not retrieved | unlikely | N | Activation only; no loss data; skip |

## 11. Sources opened

- Ferguson, Reframing Rural Fire Management: Special Inquiry into the January 2016 Waroona Fire (WA Government, 10.99 MB PDF; read as text): https://www.wa.gov.au/system/files/2020-02/Reframing%20Rural%20Fire%20Management%20-%20Report%20of%20the%20Special%20Inquiry%20into%20the%20January%202016%20Waroona%20Fire.pdf (pp12, 17-19, 38, 86, 88, 164)
- DBCA, Reconstruction of the Waroona bushfire (Perth Hills 68): https://library.dbca.wa.gov.au/FullTextFiles/072096.pdf
- AIDR Knowledge Hub: Waroona-Yarloop https://knowledge.aidr.org.au/resources/bushfire-waroona-yarloop-fire-2016/ ; Wooroloo https://knowledge.aidr.org.au/resources/bushfire-wooroloo-perth-hills-western-australia-2021/ ; Parkerville https://knowledge.aidr.org.au/resources/bushfire-parkerville-and-perth-hills-western-australia-2014/ ; Perth Hills 2011 https://knowledge.aidr.org.au/resources/bushfire-perth-hills-western-australia-2011/ ; Margaret River https://knowledge.aidr.org.au/resources/bushfire-margaret-river-wa/ ; Esperance 2019 https://knowledge.aidr.org.au/resources/2019-bushfire-wa-esperance-complex-bushfires/ ; Black Summer QLD https://knowledge.aidr.org.au/resources/black-summer-bushfires-qld-2019/ ; Toodyay AJEM article https://knowledge.aidr.org.au/resources/ajem-apr-2013-practical-stories-the-toodyay-experience-connecting-with-men-in-disaster-recovery/
- AIDR Major Incidents Reports 2016-17, 2017-18, 2018-19 (https://www.aidr.org.au/media/7087/aidr_major-incidents-report_web_2019-08-22.pdf), 2019-20, 2020-21, 2021-22 (https://knowledge.aidr.org.au/media/10654/aidr_major-incidents-report_2021-2022.pdf), 2022-23, 2023-24 (index: https://knowledge.aidr.org.au/resources/major-incidents-report/)
- AFAC Independent Operational Review, Wooroloo fire: https://www.wa.gov.au/system/files/2022-09/Wooroloo-Bushfire-Review-2021.pdf (pp4, 8-9, 17)
- DFES 2020/21 annual report, Wooroloo: https://www.dfes.wa.gov.au/annualreport2021/wooroloo-bushfire/ ; WA joint media statement, Wooroloo six months on: https://www.wa.gov.au/government/media-statements/McGowan-Labor-Government/Joint-media-statement---Wooroloo-bushfire-recovery-six-months-on-20210804
- DisasterAssist: Wooroloo https://www.disasterassist.gov.au/Pages/disasters/current-disasters/Western-Australia/bushfires-1-february-2021-onwards.aspx ; Qld 2019 https://www.disasterassist.gov.au/Pages/disasters/current-disasters/Queensland/queensland-bushfires-september-december-2019.aspx ; Mariginiup https://www.disasterassist.gov.au/Pages/disasters/current-disasters/Western-Australia/mariginiup-bushfire-22-november-2023-onwards.aspx
- Home Affairs release 3 Feb 2021 (Wooroloo AGDRP/DRA): https://minister.homeaffairs.gov.au/davidlittleproud/Pages/government-assistance-for-bushfire-affected-communities-WA.aspx ; WA statement 25 Nov 2023 (Mariginiup): https://www.wa.gov.au/government/media-statements/Cook-Labor-Government/Joint-media-statement---Disaster-assistance-available-for-Western-Australia's-Mariginiup-bushfire--20231125
- DFES Esperance story: https://news.dfes.wa.gov.au/media-releases-feature-stories/bumper-crops-catastrophic-conditions-made-esperance-fires-unstoppable/ ; ABC coroner report 2019-12-07 https://www.abc.net.au/news/2019-12-07/esperance-bushfires-2015-inquest-fire-coronial-report-coroner/11767300 ; Shire of Esperance pages https://www.esperance.wa.gov.au/residents/welcome-to-esperance/about-the-area.aspx and .../general-information.aspx
- Shire of Waroona statistics https://www.waroona.wa.gov.au/shire/about-waroona/statistics.aspx ; Shire of Harvey community page https://www.harvey.wa.gov.au/shire/about-the-shire-and-maps/shire-of-harvey-community
- Bushfire and Natural Hazards CRC, Parkerville fire experiences: https://www.naturalhazards.com.au/crc-collection/downloads/capturing_community_members_bushfire_experiences_12_january_2014_parkerville_fire_web.pdf
- ABC: Waroona all-clear https://www.abc.net.au/news/2016-01-23/all-clear-given-for-devastating-western-australian-bushfire/7109708 ; Yarloop decade https://www.abc.net.au/news/2026-01-06/yarloop-bushfire-10-year-anniversary-marked/106155544 ; Toodyay https://www.abc.net.au/news/2009-12-31/power-lines-blamed-for-toodyay-bushfire/1194258 ; Qld Sept 2019 https://www.abc.net.au/news/2019-09-09/queensland-fires-sunshine-coast-stanthorpe-beechmont-binna-burra/11490356 ; Ravensbourne/Pechey https://www.abc.net.au/news/2019-11-22/queensland-bushfires-emergency-destroys-homes-ravensbourne/11718954
- QRA: 2019 Queensland Bushfires State Recovery Plan https://www.qra.qld.gov.au/sites/default/files/2020-08/2019_qld_bushfires_recplan_2019-20_lr.pdf (pp5, 9, 11-14, 29, 36, 52-63, 70, 76, 80-83, 92-95, 110); Central Queensland Bushfires Recovery Plan (updated Aug 2019) https://www.qra.qld.gov.au/sites/default/files/2019-08/Central_Queensland_Bushfires_Recovery_Plan_2018-21_Updated_August_2019.pdf (pp5, 8-9, 17, 26-29); local plans for Scenic Rim, Southern Downs, Somerset, Toowoomba, Livingstone (https://www.qra.qld.gov.au/sites/default/files/2020-08/Scenic_Rim_bushfires_recovery_plan.pdf and siblings); QRA event pages for 2018 and 2019; QRA activations list pages 1-3; activation summary PDFs 2011-2020.
- DRFA activation history dataset (catalogue metadata and HEAD only): data.gov.au link in section 6; Qld Open Data NDRRA activations: https://www.data.qld.gov.au/dataset/https-www-qra-qld-gov-au-activations
