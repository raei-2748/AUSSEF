# Notes for slice C_2015-16_2024-25 (22 missing council rows)

Files: `findings_C.csv` (20 rows: 12 rows keyed to RAA agrns, of which 9 are slice rows, 1 is the extra r22 cross-check and 3 are other-council rows for the same Feb 2017 event; plus 8 rows whose agrn starts `CONTEXT_`). The `CONTEXT_` rows are not slice rows; they are there so the 2016/17 season box can be reconciled. Filter them out before merging, and check the r22, Port Macquarie-Hastings, Kempsey and Narrabri rows against what the dataset already has.

Bottom line: only 4 of the 22 rows got a usable single-council value (Penrith high; Mid-Western lower bound; Cessnock and Mid-Coast low). One more (Upper Hunter) got only a multi-council total. The 2024-25 rows (14 of the 22) got nothing that states a home count or an explicit "no homes lost"; the evidence there is indirect (see section 4).

## (i) Table of every agrn in the slice

| agrn | rows_missing | rows_you_could_fill | main source / status |
|---|---|---|---|
| 1121 Clarence Valley Jan-Feb 2024 | 1 | 0 | No event-level source. Context only: RFS 31 Mar 2024 release, 29 homes lost statewide in 2023/24 (CONTEXT_SEASON_2023-24). |
| 1156 Tenterfield Sep 2024 | 1 | 0 | Nothing found. NSW RA declaration page lists only "Counter disaster operations". |
| 1189 Singleton + Muswellbrook Dec 2024-Jan 2025 | 2 | 0 | Nothing explicit. Indirect only (section 4). |
| 1190 Yass Valley | 1 | 0 | Nothing. RFS AR 2024/25 p.27 lists Yass among December s44 fires. |
| 1191 Singleton Dec 2024 | 1 | 0 | Nothing explicit (as 1189). |
| 1192 Tamworth + Uralla | 2 | 0 | Nothing. |
| 1193 Bathurst + Lithgow | 2 | 0 | Nothing explicit. |
| 1196 Mid-Western Dec 2024 | 1 | 0 | Nothing. RFS AR 2024/25 p.27 lists Mid Western among December s44 fires. |
| 1197 Hawkesbury Jan 2025 | 1 | 0 | Nothing explicit. |
| 1199 Narrabri + Gwydir | 2 | 0 | Nothing. |
| RAA r09 Shoalhaven (26 Nov 2015) | 1 | 0 | Only confirmation that RAA declared it (RAA Annual Report 2015-16 p.15: "26/11/2015 Bushfire Shoalhaven"). No impact information found. |
| RAA r07 Tenterfield (Nov 2016) | 1 | 0 | Nothing. Residual bound only (section 2). |
| RAA r12 Penrith (Nov 2016) | 1 | 1 (high) | RFS 5 Nov 2016: "No homes have been destroyed." 4 houses damaged. |
| RAA r16 Cessnock (Dec 2016-Jan 2017) | 1 | 1 (low) | ABC 18 Jan 2017: Kurri Kurri fires, "no homes were destroyed". Match to r16's named fires is indirect. |
| RAA r17 Mid-Western (Jan-Feb 2017) | 1 | 1 (medium, lower bound) | RFS 18 Feb 2017: White Cedars Rd fire, 1 uninhabited home destroyed. Sir Ivan 35 is multi-council. |
| RAA r23 Mid-Coast + Upper Hunter (Feb 2017) | 2 | 1 (low) + 1 multi-council | Mid-Coast: inferred zero by accounting (low). Upper Hunter: only the Sir Ivan multi-council total (35). |
| RAA r26 Singleton (Feb 2017, Brinawa/Carrowbrook) | 1 | 0 | Nothing found. Fire started 19 Feb 2017, after RFS closed its 18 Feb assessment. |

## 1. Priority 1: the 2016/17 season loss box (65 destroyed, 38 damaged)

Official statements (all read in full, not paraphrased):
- RFS media release 31 Mar 2017: "Total number of properties destroyed - 65", "Total number of properties damaged - 38".
- RFS Annual Report 2016/17 p.28 loss box: 65 habitable structures destroyed, 38 damaged; 243 sheds/outbuildings destroyed, 103 damaged.
- RFS Annual Report 2016/17 p.29: "a total of 56 homes were destroyed with another 26 damaged" in the February 2017 fires (Sir Ivan, White Cedars Rd, Pappinbarra, Binalong Rd Boggabri, Dondingalong, then Carwoola).

Allocation by fire (RFS "Assessment of last week's fire affected areas completed", 18 Feb 2017, plus Carwoola release 18 Feb 2017):

| Fire (LGA as labelled by RFS) | Destroyed | Damaged |
|---|---|---|
| Sir Ivan (Warrumbungle) | 35 | 11 |
| Pappinbarra (Port Macquarie-Hastings) | 6 | 3 |
| Spring Hill Rd, Dondingalong (Kempsey) | 2 (1 uninhabited) | 0 listed |
| Binalong Rd, Boggabri (Narrabri) | 1 | 0 listed |
| White Cedars Rd, Kains Flat (Mid-Western) | 1 (uninhabited) | 0 listed |
| Subtotal, 11-12 Feb weekend | 45 | 14 |
| Carwoola (Queanbeyan-Palerang), 17 Feb | 11 | 12 |
| Feb 2017 total | 56 (ties to AR p.29) | 26 (ties to AR p.29) |
| Currandooley (Queanbeyan-Palerang), Jan 2017 | 1 (RFS 31 Mar 2017 release; ABC 17-19 Jan) | not given |
| Llandilo/Londonderry (Penrith), 4 Nov 2016 | 0 | 4 |
| Kurri Kurri (Cessnock), 18 Jan 2017 | 0 (ABC) | not given |
| **Season total** | **65** | **38** |
| **Unallocated residual** | **8** (65 - 56 - 1) | **8** (38 - 26 - 4) |

The RFS progressive updates show how the count moved: 19 homes (13 Feb), 32 (14 Feb), 42 (Update 7, 16 Feb), 44 (Update 9, 17 Feb), 45 (final, 18 Feb). White Cedars Rd's "1 home (uninhabited)" is inside the total from Update 7 on.

What this means for "other 2016/17 fires can be shown to be zero": partly. The February event is fully allocated (56 = 45 + 11), so any fire burning 11-18 Feb that is not in the table (Barnards Rd Gloucester, Howes Creek, Wardells Rd, Mount Pleasant Rd) has no assessed loss. The Brinawa/Carrowbrook fire started on 19 Feb, after the window, so it is not covered. But 8 destroyed and 8 damaged across Jul 2016 - Jun 2017 are unattributed, and I could not find which fires they belong to. So a zero for any single non-February fire (Tenterfield, Shoalhaven, Singleton, Cessnock Dec) cannot be proven from the season box alone; the cap is 8 homes per fire, shared. Candidate fires named in the RFS AR 2016/17 p.28 (no loss figures given there): Fortis Creek (Oct), Beecroft Peninsula/Callala Bay (Shoalhaven, Nov), Racecourse Rd/Lone Pine (Cessnock/Port Stephens s44, Nov), Ravenswood (Kempsey s44, Nov), Paynes Rd (West Wyalong; RFS says crops, sheep, fencing lost, no houses mentioned), Clear Hills Rd (Urana, Dec), Wuuluman (Dubbo s44), Sutton/Mulligans Flat (ABC: livestock and outbuildings only), Camberwell/Singleton (ABC: two sheds unconfirmed), Kurri Kurri, Tenterfield.

Two definitional points: the media release says "properties", the annual report says "habitable structures", and the RFS itemised list counts uninhabited buildings (White Cedars 1, Dondingalong 1) inside "homes". If the dataset's DL numerator is occupied dwellings, subtract those 2 uninhabited buildings: the 11-12 Feb weekend list becomes 43 and the Feb total 54.

Other 2016/17 evidence:
- Penrith (Llandilo/Londonderry) fire was 4 Nov 2016, not 13 Nov: RFS 5 Nov 2016 "No homes have been destroyed"; 4 houses, 1 care facility damaged; 1 shed destroyed. The dataset's 2016-11-13 start looks like the RAA declaration date.
- Cessnock: only the Jan 2017 Kurri Kurri fires have a loss statement (ABC: sheds and outbuildings damaged, no homes destroyed). The RFS AR 2016/17 says December 2016 had "only one significant fire event" (Urana), which fits but is not a loss statement.
- Shoalhaven: RAA declared a bushfire on 26 Nov 2015 (RAA AR 2015-16 p.15). I found no description of it. RFS AR 2016/17 mentions a different Shoalhaven fire (Beecroft Peninsula/Callala Bay) in November 2016; if the dataset's year is wrong that could be the event, but I could not confirm either way. RFS 31 Mar 2016 end-of-season release has no property-loss figure ("relatively quiet fire season", 6,912 fires, 64,572 ha).
- Tenterfield (Demon Creek/Nightshade/Boorook, Nov 2016): nothing found. RFS AR 2016/17 p.28 lists "major fires at Kurri Kurri, Singleton and Tenterfield" in January 2017 without loss numbers.

## 2. Priority 2: 2024-25 season (and Clarence Valley Jan 2024)

What official sources say:
- RFS Bush Fire Bulletin Vol 47 No 1 (2025), Foreword, p.1 (read in full): "Despite seven section 44 declarations for fires (mostly in the northwest of the state), only one fire reached emergency warning level and property losses across the season were minimal." Not a count and not zero.
- RFS Annual Report 2024/25 pp.8, 26-27 (read): seven s44 declarations (Bathurst/Lithgow, Singleton/Muswellbrook, Tamworth part Uralla, Hawkesbury, Walgett/Coonamble, Narrabri/Gwydir, Warrumbungle); December list also names Yass and Mid Western. No loss box, no home count (the "2,476 homes" in that report is Black Summer 2019/20).
- RFS release 31 Mar 2025: 4,100+ fires, 61,000+ ha; no property-loss figure. (Compare 2024 release: 29 homes, 142 outbuildings; 2023 release: 8 homes, 15 outbuildings.) RFS stopped putting a loss count in the end-of-season release for 2024-25.
- NSW Reconstruction Authority natural disaster declarations FY2024-25 page: AGRN 1156, 1189, 1190, 1192, 1193, 1196, 1197, 1199 each list only "Counter disaster operations" as assistance. FY2023-24 page: AGRN 1121 (Clarence Valley) the same. No property counts on those pages. Weak indicator only: events with many lost homes usually carry more measures (concessional loans, asset restoration, etc.), but I would not enter zeros on this alone.
- Independent Bushfire Group, "Remote fires December-January", 5 Feb 2025 (non-official commentary, `other`): the Yengo-Wollemi complex (Singleton-Muswellbrook, Lithgow, Hawkesbury s44s) "received little to no mainstream media coverage, probably because no property was under imminent threat". This is about threat, not losses, so I did NOT enter it as a finding.
- ABC Emergency incident pages (Sandon River, Devils Hole, Hill End, Copeton/Upper Bingara) show size and alert level only; none mention property loss. ABC 26 Jan 2024 article on Sandon River/Wooli reports evacuations and the threat but no losses.

Not entered in the CSV, by rule 5 (zero only if a source says no homes lost): all 2024-25 rows. My judgement, for the caller to accept or not: the evidence (RFS "minimal" season losses, counter-disaster-operations-only declarations, remote lightning fires, small burned areas, no media reports of lost homes surfaced in any search) makes "no reported home losses" the reasonable working assumption for 1156-1199 and 1121, but it is an absence-of-evidence call, not a sourced zero.

Clarence Valley (1121): the 2023/24 season total of 29 homes (RFS 31 Mar 2024) is in the CSV as `CONTEXT_SEASON_2023-24`. Test: sum the dataset's homes destroyed for all 2023-24 events; if it is about 29, the Jan 2024 Clarence Valley fires have about zero residual.

## 3. Priority 3: any per-fire or per-LGA publication

Found and useful (all free, no download needed, HTML or PDF text layer):
- RFS media releases "Initial assessment of fire affected areas" (Updates 1-9 and final, 13-18 Feb 2017): per fire, with LGA, destroyed/damaged homes and outbuildings. URL pattern: `rfs.nsw.gov.au/news-and-media/media-releases/initial-assessment-of-fire-affected-areas-update-N` and `.../initial-assessment-of-carwoola-fire-affected-area2`; final at `rfs.nsw.gov.au/__data/assets/pdf_file/0016/52144/170218-Final-damage-assessment-from-weekend-bush-fires.pdf`. RFS also issued one for Llandilo (5 Nov 2016). Goes back to at least Nov 2016.
- RFS annual reports: only the 2016/17 report has a per-season loss box with habitable structures (p.28). The 2023/24 and 2024/25 reports have none (checked). Earlier reports (2015/16, 2017/18) not checked in this pass.
- RFS end-of-season media releases (31 Mar): 2017 gives 65/38, 2023 gives 8, 2024 gives 29. 2016 and 2025 give none.
- NSW Coroner findings for the Sir Ivan fire: 35 houses destroyed, 11 damaged (state-level whole-fire number, agrees with RFS).

Checked and NOT holding building damage:
- NSW Reconstruction Authority declarations pages (nsw.gov.au/emergency/recovery/natural-disaster-declarations/fy-2024-25 and the FY2023-24 page): per-AGRN dates, LGAs, assistance measures only.
- Disaster Assist event pages (disasterassist.gov.au): WebFetch returns HTTP 403; search snippets show only assistance-measure text.
- NSW Natural Hazards Science hub bushfire dataset list (naturalhazardsscience-hub.seed.nsw.gov.au/bushfire-related-datasets): 19 datasets, all vegetation/fire-extent/bush-fire-prone-land; none records buildings destroyed.
- data.nsw.gov.au searches: no Building Impact Assessment dataset found.
- NSW DPI primary industries damage survey (dpi.nsw.gov.au/.../primary-industries-natural-disaster-damage-survey): LGA-by-event summaries per search snippets, but livestock/fencing/crops, not dwellings; WebFetch got HTTP 403, so not read.
- RFS "Major Fire Update" pages (`mfu?id=...`): JavaScript-rendered, WebFetch sees only the site template.

## (ii) Sources searched with no result

- RFS Bush Fire Bulletin Vol 38(3) (Dec 2016) and Vol 39(1) (2017): both over WebFetch's 10 MB cap, could not be read. Vol 39(2) does not appear in the RFS archive listing (listing goes 38(3), 39(1), 40(1)). Vol 46(3) is not in the archive listing; Vol 46(2) (Nov 2024) predates the events and was not read; Vol 47(2) (late 2025) not read. Vol 38(2) (Tasmanian fires issue) was read and has no NSW home-loss content. Vol 47(1) was read in full (the foreword sentence above is the only relevant text; the Hunter fires article is about bulk water carrying, no losses).
- Web searches (all returned nothing usable on losses): Shoalhaven Nov/Dec 2015 and Bomaderry Creek; Tenterfield Nov 2016 / Demon Creek / Jan 2017; Carrowbrook/Brinawa Feb 2017; Barnards Rd/Gloucester Feb 2017; Cessnock Forbes Street Dec 2016; Sandon River outcome Jan 2024; Tenterfield/Tabulam/Legume Sep 2024; Hunter/Martindale/Howes Valley/Broke Dec 2024; Attunga/Kingstown/Tamworth Dec 2024; Hill End/Dingo Creek; Devils Hole (Colo Heights); Binalong/Yass Valley; Copeton/Upper Bingara; Charbon/Yarrawonga (Mid-Western); ministerial releases and Hansard for the Hunter fires.
- The WebSearch quota for the session (200 calls) ran out near the end, so a few follow-ups were not run (Kempsey Ravenswood Nov 2016, Callala Bay Nov 2016, further Shoalhaven 2015).
- ACM domains appeared in results (Newcastle Herald, Cessnock Advertiser, Lithgow Mercury, Western Advocate, Tenterfield Star, Singleton Argus, etc.) and were skipped, not opened. Note that the Kurri Kurri "no homes destroyed" result was confirmed on ABC, not ACM.
- Ideas for a follow-up pass: Trove full text of Bush Fire Bulletin 38(3), 39(1), 39(2) (Trove hosts the whole series); Tenterfield, Singleton and Shoalhaven council annual reports/minutes for 2016-17 and 2015-16; RAA 2016-17 annual report event descriptions; NSW Parliament questions on notice on the 2016/17 fire season losses.

## (iii) New datasets/portals

None that hold building damage per fire or LGA beyond the RFS media-release series and the annual-report loss boxes listed in section 3. The one structural finding: RFS published per-fire, per-LGA building counts in 2016-17 (media releases) but appears to have stopped putting season-level loss counts in its annual report after that era, and did not publish one in the 2025 end-of-season release. The NSW RA and Disaster Assist pages carry no property counts.

## (iv) Reliability

- Solid: every 2016/17 number in the CSV was read from the RFS PDFs' text layer (the harness cached the PDFs when WebFetch fetched them; I extracted the text locally with pypdf). The 56 = 45 + 11 and 26 = 14 + 12 checks close exactly, which is a good sign the fire-level figures are right.
- Medium: the ABC Kurri Kurri quote and the ABC Carwoola quote came through WebFetch's small-model summary in quotation marks; treat as `yes` per the rule but re-check if the number is decisive. The Penrith damaged count is preliminary (the day after the fire) and moved from 1 to 4 within a day.
- Weak: the Mid-Coast zero is inference by accounting; the Cessnock zero is for a neighbouring declaration's fire; both are labelled low. The Mid-Western 1 is a lower bound for an uninhabited building. Fire-to-row matching for RAA declarations is uncertain in general: the dataset's fire start dates for r12 and r16 do not match the fires I found, so the "onset" dates in the RAA rows are probably declaration dates.
- The web-search summaries repeatedly returned wrong figures (for example "2,476 homes destroyed" attributed to 2024-25, which is the 2019/20 Black Summer figure quoted in the annual reports). Nothing from a search summary went into the CSV unless I opened the source page or PDF.
- Files outside `research/`: none written by me. WebFetch saved fetched PDFs into the session's tool-results cache (outside the repo) as a side effect; I only read those.
