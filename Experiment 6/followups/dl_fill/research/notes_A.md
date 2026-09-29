# Notes - slice A_2017-2019 (53 missing council rows, 33 declarations)

Companion file: `findings_A.csv` (20 rows). Working date 2026-09-29.

## Headline

- Firm fill: **1 row** (Shoalhaven / agrn 818: 0 homes destroyed, 1 damaged, medium confidence). **1 partial row** (Clarence Valley / agrn 880: Bees Nest fire, at least 9 residences, but the source does not split it between Clarence Valley, Armidale Regional and Bellingen).
- The other 51 rows: no row-specific published figure or explicit "no homes lost" statement found. Most search hits for these small fires were on ACM mastheads (skipped per the rules).
- What does exist is a **season budget** from the RFS annual reports, and it is tight enough to be useful (next section).
- The web-search quota (200 calls) ran out part-way through, so the council-annual-report and Hansard leads listed in section (ii) were not followed.

## Season budget (the most useful inference for the blank rows)

RFS season loss boxes vs homes destroyed already in the dataset, by fire start date (dataset file `out/DL_ROW_STATUS.csv`):

| Season | RFS habitable structures destroyed / damaged | Filled dataset rows: destroyed | Left for ALL other rows in the season |
|---|---|---|---|
| 2017/18 (1 Jul 2017 - 30 Jun 2018) | 74 / 63 (AR 2017/18 p.28) | 71 = Tathra 65 + Port Macquarie-Hastings NSW1718-05 6 (others 0) | **at most 3 destroyed** (at most 13 damaged: 63 minus Tathra 48 and PMH 2) |
| 2018/19 (1 Jul 2018 - 30 Jun 2019) | 37 / 27 (AR 2018/19 p.26 and p.32) | 36 = Bega Valley 4 + Inverell 14 + Tenterfield 18 (others 0) | **at most 1 destroyed** (about 8 damaged) |

So across the 21 missing 2018/19 rows in this slice (818, 819, 820-Eurobodalla, 823, 824, 841, 842, 843-Armidale, 847, 851, 855, 860, 862, 864, 866, 867) plus every other 2018/19 fire, the combined homes destroyed cannot exceed 1, and across the 27 missing 2017/18 rows (771, 772, 776, 792 and NSW1718-*) plus every other 2017/18 fire the combined total cannot exceed 3. (The remaining 5 rows are all agrn 880, 2019/20.) Caveats: RFS counts "habitable structures" for RFS-attended fires; the dataset's filled values come from other sources (if the PMH value of 6 is really 2, the 2017/18 residual is 7). The 32 homes at Tingha + Bruxner Highway are confirmed by the RFS 2018/19 report ("32 homes lost"), matching Inverell 14 + Tenterfield 18.

Where the single 2018/19 residual home might sit: the AR says that in Aug 2018 "A further four fires, within the Shoalhaven, Hawkesbury, Richmond Valley and Clarence Valley LGAs, reached Watch and Act. Property losses were recorded during this time." Type and number are not given. The only same-week damage list I could read (ABC 16 Aug 2018, from RFS BIA teams) covers Bemboka, Kingiman and North Nowra only, so Richmond Valley/Clarence Valley (agrn 823/824) are the open question, but at most one home.

## (i) Table of every agrn in the slice

`rows_you_could_fill`: rows where I hold a defensible figure tied to that row (F = firm, P = partial/multi-council, 0 = none). "Implied 0" means the evidence points to zero but no source says so; I did not enter those as zeros because rule 5 requires an explicit statement.

| agrn | Event (dataset name) | rows_missing | rows_you_could_fill | Main source / status |
|---|---|---|---|---|
| 771 | Kempsey, 27 Aug 2017 (Kempsey) | 1 | 0 | ABC 29 Aug 2017 (Clybucca fire): "at least a dozen homes" threatened, no loss stated. ABC 25 Sep 2017: shed and vehicle lost at South Kempsey, no house. Implied 0 (budget). |
| 772 | Mid-Coast + PMH, 30 Aug 2017 (Mid-Coast, PMH) | 2 | 0 | Nothing row-specific. RFS AR 2017/18 lists Mid Coast S44 fires (Cairncross, Aerodrome Lakes Way, Innes View, Belbora) with no loss narrative. Implied 0 (budget). |
| 776 | Tenterfield, 8 Sep 2017 | 1 | 0 | RFS AR 2017/18 names Rivertree and Cullendore Creek Rd S44 fires, no losses stated. Tenterfield Shire annual report 2017-18 does not mention them. Implied 0 (budget). |
| 792 | Singleton, 18 Dec 2017 | 1 | 0 | RFS AR names Singleton S44 "Apple Tree"; no losses stated. Implied 0. |
| 818 | Shoalhaven, 11 Aug 2018 | 1 | **F** | ABC 16 Aug 2018 x2 (RFS BIA): no home destroyed; 1 house damaged (North Nowra); Kingiman 11 outbuildings. RFS AR: fire is "Croobyar Rd Fire (also known as the Kingiman Fire)". |
| 819 | Cessnock + Port Stephens, 15 Aug 2018 (Cessnock) | 1 | 0 | ABC 19 Aug 2018 covers Salt Ash (Port Stephens, already 0) only. Nothing for Cessnock (Upper Yango Creek/Laguna, Jacobs Rd Corrabare). |
| 820 | Bega Valley + Eurobodalla, 15 Aug 2018 (Eurobodalla) | 1 | 0 (event-level rows only) | Yankees Gap: ABC 16 Aug 2018 "Two houses"; NSW Coroner 2024 "destroyed or damaged at least three homes". All at Bemboka (Bega Valley). Eurobodalla portion (431 ha) is Wadbilliga NP fringe; implied 0, no source. |
| 823 | Richmond Valley, Lismore, Kyogle, 12 Aug 2018 (Kyogle, Richmond Valley) | 2 | 0 | RFS AR names Mothersoles Rd, Ellangowan as the S44 fire; "property losses were recorded" for Richmond Valley/Clarence Valley Watch-and-Act fires (unspecified). Open: at most 1 home (budget). |
| 824 | Clarence Valley + Glen Innes Severn, 14 Aug 2018 | 2 | 0 | RFS AR names Bristol Arms Rd, Ramornie as the S44 fire. No figure. At most 1 home (budget). |
| 841 | Tamworth (Rockview), 30 Oct 2018 | 1 | 0 | Nothing found (non-ACM). Implied 0 (budget). |
| 842 | Port Stephens + Cessnock, 22 Nov 2018 (Cessnock, Port Stephens) | 2 | 0 | ABC 22-23 Nov 2018: "homes threatened at Salt Ash", no loss statement. Ministerial release 26 Feb 2019 (RFS site) has assistance text only. Richardson Rd (Campvale) is the S44 fire. Implied 0 (budget). |
| 843 | Northern NSW, 11 Feb 2019 (Armidale Regional, 7 ha) | 1 | 0 | Tingha Plateau: 14 homes destroyed (AIDR MIR 2018-19) all near Tingha (Inverell). Armidale row is a 7 ha edge; 0 very likely, not stated. |
| 847 | Armidale (Melrose), 1 Dec 2018 | 1 | 0 | RFS AR lists an Armidale/Walcha S44 for "Moona Plains Rd Fire" in Nov-Dec 2018 (possibly the same fire as "Melrose"; unverified), no losses mentioned. Implied 0 (budget). |
| 851 | Glen Innes Severn (Highland Creek), 25 Dec 2018 | 1 | 0 | Nothing found. Implied 0 (budget). |
| 855 | Tamworth (Halls Creek Rd), 3 Jan 2019 | 1 | 0 | RFS AR: Halls Creek Rd S44 was a pre-emptive declaration on 12 Feb 2019; no losses mentioned. Implied 0. |
| 860 | Snowy Valleys, 17 Jan 2019 | 1 | 0 | RFS AR: Little Talbingo Mountain Road pre-emptive S44 (12 Feb 2019); no losses mentioned. Implied 0. |
| 862 | Tamworth + Upper Hunter, 11 Feb 2019 | 2 | 0 | Pretty Gully/Warrabah, Crawney Rd Nundle etc.; nothing found. RFS AR: Tingha Plateau S44 covered Gunnedah, Liverpool Plains, Upper Hunter, Tamworth; losses were in Inverell. Implied 0. |
| 864 | Tenterfield, 9 Mar 2019 | 1 | 0 | Silent Grove Rd, Torrington S44 (pre-emptive, 12 Feb); the only Tenterfield LGA losses the AR names are from the Bruxner Highway fire (already in 843). Implied 0 (budget). |
| 866 | Newcastle (Kooragang), 5 Jan 2019 | 1 | 0 | AIDR MIR 2018-19 p.32: 100 ha Ash Island bushfire "quickly brought under control"; site is a waste emplacement facility beside a conservation reserve; no dwellings or losses mentioned. Implied 0. |
| 867 | Singleton + Muswellbrook, 11 Feb 2019 | 2 | 0 | Monundilla Range 49 ha, Three Poles 4 ha; nothing found. Implied 0. |
| 880 | NSW North Coast, 18 Jul 2019 (Clarence Valley, Kyogle, Mid-Coast, Nambucca Valley, PMH) | 5 | **P** (Clarence Valley, multi-council) | Bees Nest fire: NSW Coroner Vol 1 "At least 9 residences were destroyed". Weekend of 10-11 Aug 2019: 4 homes, all in Richmond Valley (2, Rappville) and Kempsey area (2), none in the five missing councils (ABC 14 Aug 2019 + RFS Bulletin 41(2)). Implied 0 for Kyogle, Mid-Coast, Nambucca Valley, PMH (Lindfield Park Rd peat fire discussed in Bulletin with no home loss) through mid-Aug; not explicit. |
| NSW1718-05 | Mid-Coast, PMH, Dungog, Upper Hunter, 23 Sep 2017 (Dungog, Mid-Coast, Upper Hunter) | 3 | 0 | Comboyne fire, 24 Sep 2017: 2 homes lost (ABC 25-26 Sep 2017), council not named (PMH row already filled with 6). Nothing for the three missing councils. |
| NSW1718-06 | Kempsey + PMH, 5 Dec 2017 | 2 | 0 | Big Hill Trail fire (Crescent Head): ABC 7 Dec 2017 says only "no immediate threat to homes". Implied 0 (budget). |
| NSW1718-08 | Tamworth, 25 Dec 2017 | 1 | 0 | Non-ACM: NBN News 8 Jan 2018 "no homes under threat" (Roseneath/Watsons Creek fire). Weak. Implied 0. |
| NSW1718-09 | Tamworth, Uralla, Gwydir, 2 Jan 2018 | 3 | 0 | Bonnay / Scrub Creek / Bald Rock: only ACM coverage found. Implied 0 (budget). |
| NSW1718-11 | Singleton, Cessnock, Muswellbrook, 13 Jan 2018 | 3 | 0 | Fire 695 (Putty/Wollemi): ABC 14-15 Feb 2018 "properties are still at risk", no losses stated. Implied 0. |
| NSW1718-12 | Narrabri + Warrumbungle, 17 Jan 2018 | 2 | 0 | Dipper Rd (Pilliga) S44: nothing non-ACM found. Implied 0. |
| NSW1718-13 | Upper Lachlan (Long Gully), 19 Jan 2018 | 1 | 0 | RFS AR lists S44 Long Gully, Taralga; no losses. Implied 0. |
| NSW1718-15 | Upper Hunter, 23 Jan 2018 | 1 | 0 | Nothing found. Implied 0. |
| NSW1718-16 | Muswellbrook + Mid-Western, 23 Jan 2018 | 2 | 0 | RFS AR: Mid-Western S44 "multiple remote fires"; no losses. Implied 0. |
| NSW1718-17 | Central West, 9 Feb 2018 (Bathurst) | 1 | 0 | Mt Canobolas S44 (Cabonne/Orange, Cabonne already 0). Nothing for Bathurst. Implied 0. |
| NSW1718-18 | Lithgow, 12 Feb 2018 | 1 | 0 | Nothing found. Implied 0. |
| NSW1718-19 | Narrabri + Gwydir (Bobbiwaa), 12 Feb 2018 | 2 | 0 | Bobbiwaa S44 in RFS AR; no losses stated. Implied 0. |

Totals: rows_missing 53; firm 1; partial 1.

## Name mapping from the RFS annual reports (useful for later matching)

2018/19 (AR p.26): Croobyar Rd = Kingiman (818); Yankees Gap Rd, Bemboka (820); Bristol Arms Rd, Ramornie (824); Mothersoles Rd, Ellangowan (823); Salt Ash (819); Richardson Rd (842); Moona Plains Rd, Armidale and Walcha (probably 847); Curembenya (853); Halls Creek Rd (855); Little Talbingo Mountain Rd (860); Tingha Plateau and Bruxner Highway (843/862/867); Silent Grove Rd, Torrington (864 area).
2017/18 (AR p.29): Rivertree and Cullendore Creek Rd (776); Cairncross, Aerodrome Lakes Way, Innes View, Belbora (772 / NSW1718-05); Tomalpin Link, Chichester Dam (Dungog side of NSW1718-05); Big Hill (NSW1718-06); Apple Tree (792); Masonite Rd, Dipper Rd, TJs, Bonnay/Eureka, Long Gully Taralga, Mt Canobolas, Bobbiwaa, 695 (NSW1718-09 to -19 range; assignment approximate).

## Discrepancies with values already in the dataset

- **Port Macquarie-Hastings / NSW1718-05 = 6 destroyed, 2 damaged.** ABC 25-26 Sep 2017 says 2 homes lost at Comboyne. I could not find a source for 6. If it is wrong, the 2017/18 residual grows from 3 to 7.
- **Kempsey / 880 = 1 (lower bound).** ABC 14 Aug 2019 lists 2 (Racing Track, Turners Flat, and Gilmores Gully, south of Bellbrook). I could not confirm that Turners Flat is in Kempsey Shire.
- **Bega Valley / 820 = 4.** Early count 2 (ABC 16 Aug 2018); Coroner: "destroyed or damaged at least three". 4 is the figure from the 2023 coronial hearing coverage in the brief; I did not re-verify it.
- **Clarence Valley / 871 = 168 is a whole-season council total that already contains the Bees Nest homes (at least 9) that belong to agrn 880.** Coroner Vol 1 also gives Liberation Trail = 124 destroyed / 36 damaged. Do not add the 880 figure on top of 871.

## (ii) Sources searched with no result

- **RFS Bush Fire Bulletin.** The RFS archive page for 2017-2020 lists only Vol 38(3), 39(1), 40(1), 41(1), 41(2), 42(1), 42(2). Vol 39(2), 39(3), 40(2), 40(3) and 41(3) are not published there, so they cannot be read. Read 41(2) (found the Aug 2019 winter-fire paragraph). 39(1), 40(1) and 41(1) are over the fetch tool's 10 MB limit (all already in used_sources).
- **RFS media releases.** I spot-checked the site's media-release index at ranks 501, 541, 561, 581 and 601 (Apr 2019 back to May 2018): only routine releases (cadet graduations, station openings), no incident or damage-assessment releases for Aug 2018 - Mar 2019 (ranks 511-540 not viewed). Incident releases are indexed from Sep 2019. Guessed slugs for 10, 11 and 13 Sep 2019 updates returned 404.
- **Disaster Assist AGRN pages** return 403 to the fetch tool. **NSW Reconstruction Authority FY2018-19 page**: declaration list only, no damage text.
- **NSW Parliament.** Research paper "Bushfires" returned 403; the two Hansard PDFs the search returned were 2013 sittings; nothing usable. Hansard questions on notice for 2017-2019 not reached.
- **AIDR Major Incidents Reports.** 2017-18: only Tathra and Holsworthy for NSW bushfires (Holsworthy: five properties minor damage, none lost). 2018-19: Kingiman narrative (no house count), Tingha Plateau (14 homes), Bruxner Hwy, Kooragang; no house counts for the other slice fires. AIDR Kingiman Knowledge Hub page: no loss figures.
- **NSW Coroner.** Findings search for "bushfire" and "inquiry into the fire": only Yankees Gap (2024), Reedy Swamp (2021), Sir Ivan/Leadville (2019), Marrangaroo (2019) and the 2019/20 volumes. Vol 1 has no chapter for the Jul-Aug 2019 fires (no hits for Clearfield, Old Station, Gilmores Gully, Turners Flat, Chambigne, Middle Creek, Kippenduff, Lindfield Park, Purgatory).
- **Councils.** Tenterfield Shire annual report 2017-18 (58 pp, text-searched): no reference to the Sep 2017 fires. Narrabri Shire "History of Natural Disasters": no 2017 or 2018 entry. Kempsey Shire bushfire page: no history. Others (Glen Innes Severn, Inverell, Armidale Regional, Tamworth Regional, Snowy Valleys, Upper Lachlan, Lithgow, Bathurst, Mid-Coast, Port Stephens, Cessnock, Singleton, Muswellbrook, Richmond Valley, Kyogle, Clarence Valley annual reports 2017/18 and 2018/19) were **not** reached: search quota ran out and I could not guess the file URLs. These are the obvious next step.
- **ABC.** Read with no loss statement: Big Hill Trail 7 Dec 2017; Clybucca 29 Aug 2017 (threat only); Putty fire 695, 14 and 15 Feb 2018; Salt Ash 22-23 Nov 2018 (three articles); Salt Ash and Hunter 19 Aug 2018 (one article has the "no confirmed reports" line, used for 819). No ABC article found for: Rockview, Melrose, Highland Creek, Halls Creek Rd, Snowy Valleys Jan 2019, Torrington Mar 2019, Dipper Rd/Pilliga, Bonnay, Tenterfield Sep 2017, Kempsey Aug 2017 outcome.
- **Wikipedia** 2017-18, 2018-19 season pages and the 2019-20 list: only Comboyne and Tathra (2017-18); Aug 2018 fires without house counts; nothing for Jul-Aug 2019 fires beyond Lindfield Park Rd.
- **ACM.** For Bonnay/Scrub Creek, Big Hill Trail, Salt Ash Nov 2018, Torrington Mar 2019, Pilliga Jan 2018 and Putty 695 the search engine returned ACM mastheads (Northern Daily Leader, Central Western Daily, The Land, Port News, Macleay Argus, Newcastle Herald, Port Stephens Examiner, Glen Innes Examiner, Tenterfield Star, Illawarra Mercury, South Coast Register, Ulladulla Times, Singleton Argus, Daily Examiner, Inverell Times, Armidale Express, Moree Champion). I did not use their content. Expect these rows to stay blank unless a non-ACM source turns up.

## (iii) New datasets or portals

Nothing found that lists building damage per fire or per LGA for 2017-2019 in a structured form. Leads, in order of usefulness:

1. **NSW Coroner, 2019/20 Bushfires Coronial Inquiry Vol 1** (`coroners.nsw.gov.au/documents/reports/bushfires/2019-20-NSW-Bushfires-Coronial-Inquiry-Vol1.pdf`, 420 pp, ~7.5 MB). Already used in aggregate, but each fire chapter carries "residences destroyed / damaged" lines (Bees Nest, Liberation Trail, Busbys Flat, Torrington Gulf Rd, Kangawalla, Mt McKenzie, Carrai Creek and others). Goes back only to Aug 2019. Read online; no download needed.
2. **RFS single-page BIA media releases** (Sep-Oct 2019): `190909-BIA-Assessment-2.pdf`, `191010-BIA-Assessment.pdf`, `191015-BIA-Assessment-Complete.pdf` under `rfs.nsw.gov.au/__data/assets/pdf_file/`. Per-fire homes destroyed/damaged. Only the 15 Oct and 9 Sep ones were read here; the in-between releases exist but I could not find their URLs.
3. **Coroner findings search** (`coroners.nsw.gov.au/coronial-findings-search.html?query=bushfire&start_rank=1`): the listing itself is fetchable; general inquiries into fires that destroyed property are rare (Yankees Gap is the only one in this slice).
4. **RFS annual report season loss boxes**, also mirrored at data.nsw.gov.au (`nsw_rfs_annual_report_2018_19_18591.pdf`). Statewide only.
5. NSW Natural Hazards Science hub and SEED bushfire dataset list: no damage data. AIDR Disaster Mapper (`knowledge.aidr.org.au/disasters/`): could not tell what fields it holds.

## (iv) Reliability

- **Quotes.** ABC/RFS web pages were read through a small-model fetch tool. I set quote_verified=yes only where the tool returned the sentence in quotation marks. For PDFs (RFS annual reports, Bulletin 41(2), AIDR MIR, Coroner reports) the fetch tool cached the raw PDF; I read the text locally (pypdf, output to screen only) and quoted from that, so those quotes are exact. I saved no files apart from the two outputs and a scratch script in the session scratchpad.
- **Only two ABC statements are explicit zeros or near-zeros** (Shoalhaven "no homes were destroyed"; Salt Ash "no confirmed reports of any loss or damage"), both first-24-hours statements. The Shoalhaven zero is supported by the same-day RFS BIA list and by the 2018/19 season budget; the Salt Ash line is only for Port Stephens.
- **Fire-to-row matching.** The Bees Nest match rests on name and date (30 Aug 2019, ~114k ha) and is good; the split across councils is unknown. The Kempsey/Turners Flat match is unverified.
- **The season budget is arithmetic, not observation.** It depends on RFS "habitable structures" meaning the same as the dataset's "homes", on the filled rows being right, and on RFS counting every fire. It bounds the total for the blank rows; it does not say which row holds the last home. In 2017/18 the bound is loose (3, or 7 if PMH is 2).
- **What I would trust:** Yankees Gap event totals, Tingha/Bruxner 32, Bees Nest at least 9, Aug 2019 weekend 4, RFS season boxes. **What I would not trust:** any per-row zero for 2017/18 beyond "at most 3 homes across the whole set".
