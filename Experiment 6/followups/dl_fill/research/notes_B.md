# Notes for slice B_2023 (53 missing council rows, 29 declarations)

Scan date: 2026-09-29. Companion file: `findings_B.csv` (23 rows). Two extra pseudo-agrn rows (`ALL_2022-23`, `ALL_2023-24`) hold the RFS state season totals.

## Headline answers to the four priorities in the task

1. **NSW Reconstruction Authority declarations pages (FY2022-23, FY2023-24) and Disaster Assist.** The declaration pages give LGA lists only. FY2022-23 page: "This pages lists Local Government Areas (LGAs) that have been severely impacted by a natural disaster." The FY2023-24 page has the same wording and lists AGRN, name, dates and LGAs, with no damage figure. The NSW Government/NEMA disaster-assistance releases I could open (Dec 2023) also give LGAs only. Disaster Assist event pages returned HTTP 403 to the fetch tool (they are LGA/assistance pages; I expect no damage figures but could not confirm). **Neither source can fill a DL cell.**
2. **RFS season totals (confirmed, official).** 2022/23 = **8 homes** and 15 outbuildings (RFS media release 30 Apr 2023). 2023/24 = **29 homes** and 142 outbuildings (RFS media release 31 Mar 2024, repeated in Bush Fire Bulletin 46(1) foreword). RFS does not break the 8 down; my reconciliation is Hill End/Tambaroora 6 (RFS Bulletin 45(1): "at least six") + Craigs Rd Curraweela 1 (Upper Lachlan Shire Council: "Houses lost: 1") + Conimbla Rd Cowra 1 (ABC: "A house has been destroyed"). Note the RFS Bulletin does not call the Cowra house destroyed; it says the roof was blown off and two internal walls collapsed.
3. **Which council held the six Hill End/Tambaroora homes: NOT resolved.** No source I could open places any individual home in a council. Evidence for the caller: (a) ABC 15 Mar 2023 says the fire burned "primarily through parts of Mid-Western regional council and Bathurst regional council areas"; (b) ABC 9 Mar 2023 says "A structure on Hill End Road at Hargraves was destroyed" (Hargraves is Mid-Western); (c) ABC 8 Mar 2023 has a farmer 9 km outside Hill End (Bathurst side) who lost everything except shearing shed and house; (d) Wikipedia places Tambaroora locality in Bathurst Regional; (e) a search-result title for an RFS Facebook post reads "Alpha Rd Fire, Tambaroora (Mid-Western LGA) Three ..." (post could not be opened, so unverified), and the incident was run by RFS Cudgegong District (Mudgee-based); (f) the dataset's own burned areas are 17,130 ha Mid-Western vs 1,830 ha Bathurst. I recorded scope=multi_council on one combined row rather than pick. If you must allocate, a burned-area or population weighting is a modelling decision, not a sourced fact.
4. **Individual 2023 fires.** Positive figures found: Cowra/Conimbla 1, Craigs Rd 1, Glens Creek Rd 2, Booral Rd 1, Willi Willi 7 (later count; 4 was interim), Section 44 Inverell/Tenterfield/Glen Innes 1 (RFS final table), Hudson 24 "properties" / 3 residences. No "no homes were lost" statement from RFS for any small fire. Two weak zeros (Wee Jasper Rd, Ulan Rd). Everything else: nothing findable online.

## (i) Table of every agrn in the slice

"Fill" = a row in `findings_B.csv` tied to that council row. "Firm" = usable as is with the stated scope. "Tentative" = a figure exists but assignment to the row is uncertain, the unit is not homes, or it is a weak/partial zero.

| agrn | event | rows_missing | rows_you_could_fill | main source / comment |
|---|---|---|---|---|
| 1052 | NSW Bushfires 6 Mar 2023 | 11 | 3 (1 firm: Cowra; 2 multi-council: Bathurst + Mid-Western share one figure of 6) | RFS Bulletin 45(1) p.3; ABC 15 Mar 2023; ABC 17 Feb 2023 (Cowra). Other 8 rows (Bogan, Brewarrina, Cabonne, Coonamble, Dubbo Regional, Upper Hunter, Walgett, Warren): nothing found; season-total arithmetic implies 0 (inference only). |
| 1053 | Gwydir/Narrabri 18 Jan 2023 | 2 | 0 | nothing found (Maules Creek/Bundarra). RFS names Narrabri LGA among 2022/23 "significant fires" but gives no losses. |
| 1054 | Gwydir/Moree/Narrabri 1 Mar 2023 | 3 | 0 | nothing found |
| 1055 | Western/North West 17 Feb 2023 | 4 | 0 | Conimbla Rd fire (Cowra) belongs to the Cowra row, which is not missing. Blayney, Cabonne, Liverpool Plains, Upper Hunter: nothing found. |
| 1056 | Upper Lachlan 16 Mar 2023 | 1 (Cobar) | 0 (cross-check row for Upper Lachlan added, row not missing) | Cobar / Mount Hope fire: nothing found. Upper Lachlan Shire Council tally for Craigs Rd: houses lost 1, minor damage 3, saved 45, outbuildings 17. |
| 1065 | Cootamundra-Gundagai 25 Jan 2023 | 1 | 0 | nothing found |
| 1066 | Upper Lachlan/Yass Valley 11 Feb 2023 | 2 | 1 tentative (Yass Valley weak zero) | ABC 12 Feb 2023, Wee Jasper Rd: only an uninhabited cottage lost, as at 12 Feb. Upper Lachlan (Bigga/Breadalbane): nothing found; Craigs Rd is not in this row's footprint. |
| 1071 | North Eastern 21 Aug 2023 | 4 | 2 tentative (Clarence Valley 2 homes, Kempsey 7 homes; both probably belong to rows of 1075/1076) | RFS Bulletin 46(1) p.9; ABC/AAP Oct 2023. Armidale, Nambucca Valley: nothing found. |
| 1075 | Far North 13 Oct 2023 | 2 | 1 tentative (Inverell within multi-council total of 1 home) | RFS Bulletin 46(1) p.3 Section 44 table. Kyogle (Bean Creek): nothing found. |
| 1076 | Mid North 16 Oct 2023 | 1 (Port Macquarie-Hastings) | 0 (Kempsey cross-check rows added, row not missing) | PMH (Costigans Rd, Yarras): nothing found. |
| 1081 | North Western 14 Nov 2023 (Hudson) | 1 | 1 tentative (unit is properties) | AIDR 2023-24 (24 destroyed / 20 damaged "properties"); ABC 15 Jan 2024 (about 3 residences + 16 camps). |
| 1083 | Mid-Western 2 Oct 2023 | 1 | 1 tentative (weak zero for the Ulan Rd fire only) | RFS Bulletin 46(1) p.11. |
| 1084 | Snowy Monaro 2 Oct 2023 | 1 | 0 | nothing found |
| 1089 | Mid Coast 20 Sep 2023 | 1 | 1 firm lower bound (Booral Rd: 1 home) | ABC 21 Oct 2023. Possible double count with 1076 Mid-Coast row. |
| 1090 | Lower Hunter 20 Sep 2023 | 3 | 0 | nothing found (Kearsley/Cessnock, Upper Allyn/Dungog, Port Stephens). |
| 1091 | Hunter 22 Oct-5 Nov 2023 | 1 | 0 | nothing found (Baerami Creek, Muswellbrook). |
| 1099 | Singleton 11 Sep-18 Oct 2023 | 1 | 0 | nothing found (Broke Rd Pokolbin). |
| 1112 | Armidale 9-24 Dec 2023 | 1 | 0 | nothing found |
| 1114 | Inverell/Tenterfield 7-24 Dec 2023 | 2 | 0 | nothing found (Dthinna Dthinnawan). |
| 1131 | Upper Hunter 10-17 Aug 2023 | 1 | 0 | nothing found (Stewarts Brook). |
| 1132 | Snowy Monaro 20 Sep-4 Oct 2023 | 1 | 0 | nothing found |
| 1133 | Lake Macquarie 1-18 Oct 2023 | 1 | 0 | not searched (search quota exhausted). |
| 1134 | Tamworth 26 Oct-4 Nov 2023 | 1 | 0 | not searched (quota exhausted). |
| 1135 | Byron 14 Oct-5 Nov 2023 | 1 | 1 tentative (ambiguous "at least one property destroyed") | ABC 17 Oct 2023 key points. |
| 1136 | Lithgow 11-17 Nov 2023 | 1 | 0 | not searched (quota exhausted). |
| 1137 | Parkes 19-27 Nov 2023 | 1 | 0 | not searched (quota exhausted). |
| 1138 | Richmond Valley 4-15 Dec 2023 | 1 | 0 | not searched (quota exhausted). |
| 1139 | Mid-Western 6-16 Dec 2023 | 1 | 0 | not searched (quota exhausted). |
| 1140 | Singleton 8-18 Dec 2023 | 1 | 0 | not searched (quota exhausted). |
| **Total** | | **53** | **firm 2, multi-council 2, tentative 8** | |

Realistic yield: 2 firm rows (Cowra 1052, Mid-Coast 1089), one multi-council figure covering 2 rows, and about 8 tentative rows. About 40 rows have no online figure at all.

## (ii) Sources searched with no result (coverage of each source)

- **NSW RA declarations pages FY22-23 and FY23-24:** LGA lists only (see above).
- **Disaster Assist (disasterassist.gov.au) event pages** (NSW Bushfires 6 March 2023; Mid-Western 2-10 Oct 2023; Lower Hunter 20 Sep-9 Oct 2023): fetch returned 403. NEMA DRFA page for March 2023 timed out. NSW Government release "Disaster assistance following severe bushfires": LGAs only.
- **RFS Bush Fire Bulletin:** Vol 45(1) (2023) and 46(1) (2024) read in full text. Only 45(1) p.3 (Hill End), 45(1) p.4 (Conimbla) and 46(1) pp.1, 3, 9, 11, 18 carry home counts. Vol 45(2): too large to fetch (over 10 MB) and its Issuu page has only a description. Vol 46(2): over 10 MB / Issuu description only. Vol 47(1): URL 404. Vol 47(2): not opened. The RFS bulletin index shows two issues a year (44(1), 44(2), 45(1), 45(2), 46(1), 46(2), 47(x)); I found no "45(3)" or "46(3)".
- **RFS Annual Report 2023/24** (read): season box only (9,596 fires, 507,318 ha, 22 Section 44 declarations, first Clarence Valley 21 Aug 2023, last revoked 3 Jan 2024); no fire-by-fire homes. 2022/23 report over 10 MB, not read.
- **RFS media releases:** only the two end-of-season releases contain home totals. "Major Fire Update" incident pages (`/fire-information/major-fire-updates/mfu?id=...`) return only navigation text to the fetch tool, so archived incident updates could not be read. RFS Facebook is blocked.
- **AIDR:** Major Incidents Report 2023-24 read (Hudson entry, NSW). 2022-23 report over 10 MB, not read. AIDR Knowledge Hub Hudson page read. No AIDR Knowledge Hub page for the Alpha Rd/Hill End fire was found.
- **Hansard / questions on notice:** nothing found for the Tambaroora fire or the 2023 season (only ministers' media coverage).
- **Council sites:** Bathurst Regional (Mayor's column, disaster dashboard redirected to a maintenance page): nothing. Mid-Western Regional: nothing found. Kempsey: fire pages give road closures, no losses. Byron: generic bushfire page. Kyogle: page 404. MidCoast: page HTTP 526. Walgett: nothing found. Upper Lachlan: found (Craigs Rd tally).
- **Fire-by-fire searches with no home-loss result at all** (ABC, RFS, council domains): Girilambone/Booramugga Rd (Bogan); Dripstone/Burrendong (Dubbo Regional); Lightning Ridge Castlereagh Hwy and Bangate Rd (Walgett); Maules Creek/Narrabri; Currabubula/Piallaway; Mount Hope/Cobar; Foggs Crossing Rd/Bigga; Bredbo/Shannons Flat/Anembo/Taskers (Snowy Monaro); Upper Allyn/Dungog; Kearsley/Cessnock; Pokolbin; Thunderbolts Way/Bretti; Costigans Rd/Yarras; Bean Creek/Kyogle; Wallangra/Bonshaw Rd (Inverell); Stewarts Brook/Merriwa; Dthinna Dthinnawan; Weston/Baerami Creek/Scone (Barton St fire, threat only).
- **Not searched at all because the session WebSearch quota (200) ran out:** Tamworth (Woolomin/Moonbi), Parkes (Staircase Rd), Lake Macquarie (Congewai), Richmond Valley (Busbys Flat), Lithgow (Capertee), Singleton Dec 2023, Mid-Western Dec 2023 (Murrumbo/Lue), Cootamundra-Gundagai (Bundarbo Rd). If you want these covered, the quota needs raising.

## (iii) New datasets / portals that list building damage

I found **no dataset or portal that lists building damage per fire or per LGA for 2023**. Things that come closest:

- **RFS Bush Fire Bulletin PDFs** (https://www.rfs.nsw.gov.au/resources/bush-fire-bulletin ; archive back to 2001): narrative incident stories with "fire facts" boxes carrying "Property loss" / "Losses" lines (e.g. Vol 46(1) p.9: "Two homes and 15 sheds lost") and one Section 44 assessment table (Vol 46(1) p.3). Free to read, text-extractable, but the fetch tool cannot parse them (text was recovered by reading the harness-cached copy with pypdf). Not a systematic list; only fires the editors chose to feature. Vol 46(1) also has a list of historical fires with "Losses:" lines (e.g. "Five homes destroyed and one damaged") and the 2013 Blue Mountains "195 homes destroyed and 145 buildings damaged".
- **Council recovery/news pages with impact tallies**, e.g. Upper Lachlan Shire Council's Craigs Rd summary (houses lost, minor damage, saved, outbuildings, fences). Other councils probably publish similar tallies at recovery meetings (Kempsey "Readiness & Recovery News", Snowy Monaro "Bushfire Recovery Updates", Tenterfield, Walgett) but I could not open most.
- **AIDR Major Incidents Reports:** one line per major incident with "properties destroyed/damaged"; NSW bushfire coverage in 2023-24 is Hudson only.
- **RFS Building Impact Assessment (BIA) program:** data collected for every fire that destroys or damages habitable structures, but only one-off PDF reports were published (Sep/Oct 2019, already used). No open dataset on data.nsw.gov.au or the Natural Hazards Science Hub bushfire dataset list (that list is vegetation, extent/severity, koala, erosion, bush fire prone land only). Requesting BIA data from RFS (GIPA or a research request) would be the systematic route.
- **NPWS "Fire extent and severity mapping report 2023-24"** (environment.nsw.gov.au) gives area burnt only.

## (iv) Candid reliability comment

- **Strongest facts:** the two RFS season totals (8 and 29 homes) and RFS Bulletin 45(1) "at least six" homes at Hill End; the Upper Lachlan council tally; the RFS Glens Creek fire-facts box. All read directly in the source text.
- **Fetch-tool caveat:** WebFetch answers come from a small model. Quotes marked `yes` were returned inside quotation marks or read by me directly from PDF text; ABC quotes rely on the tool's reproduction. The Booral Rd quote has the article's own grammar slip ("was been"), which suggests it was reproduced, not paraphrased. Text from four RFS/AIDR PDFs was extracted locally with pypdf from copies the fetch tool cached on its own; I saved no files into the project. Scratch text files I made in the session scratchpad were deleted at the end.
- **Definition risks for DL:** (1) RFS counts "homes" and "outbuildings" separately, ABC counts "properties", "buildings", "structures", "bush shacks" and sometimes revises them (Rocky River Rd: ABC on 21 Oct said "three in the Rocky River Road blaze" while also calling them "three smaller bush shacks", and the RFS final Section 44 table has only 1 home for the three LGAs, so a reclassification is likely but not stated; Willi Willi: 4 then 7). Use RFS final counts where they exist. (2) AIDR's 24 "properties" at Hudson cannot all be homes: the RFS state total for 2023/24 is 29, and Willi Willi (7), Glens Creek (2), Coolagolite (2), Booral Rd (1), Tabulam (1+) already account for 13+. (3) Opal-field "camps" at Grawin/Glengarry are a genuine dwelling-definition question.
- **Inference not in the CSV:** season arithmetic suggests all other 2022/23 fires in this slice lost 0 homes (8 = 6 + 1 + 1). It depends on "at least six" being exactly six and on Cowra being counted, so I did not encode it as zero rows. If you want to use it, mark those cells "derived zero" and treat them as such in the model.
- **Leads I could not confirm (not in CSV):** Wikipedia (2023-24 season page) says one home destroyed at Home Rule (Mid-Western, 3 Oct 2023), citing ABC 2 Oct and 9News 3 Oct; the ABC 2 Oct pages I opened do not say so. Wikipedia also says the Hudson fire destroyed "6 properties" in Glengarry on 15 Nov, citing ABC 15/16 Nov; the ABC pages I opened give no counts. Wikipedia says two homes destroyed in Cessnock-area fires on 14 Dec 2023 (AGRN 1092, not in this slice; ABC 15 Dec has "Weston home and tyre shop destroyed"). RFS Bulletin 46(1) p.18 gives Coolagolite (Bega Valley, not in this slice) as "Approximately 7,300ha burnt and two houses lost", matching ABC 6 Oct 2023.
- **Rule compliance notes:** (a) One Tenterfield Star (ACM) page was fetched by mistake and its content was not used anywhere. (b) Several WebSearch result lists included ACM mastheads; none was used. (c) The session WebSearch budget (200) was exhausted part-way through, so the low-coverage rows above are "not searched", not "searched and empty".
