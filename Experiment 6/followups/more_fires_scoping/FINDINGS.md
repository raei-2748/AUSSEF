# More real large fires for Experiment 6: scoping (2026-09-29)

**Status: scoping only.** Nothing was downloaded, committed or pushed. `Experiment 6/REPORT.md` is untouched. Everything is in `Experiment 6/followups/more_fires_scoping/` of the worktree `trusting-lalande-eee748`. No fire was simulated. The research agents were told not to use Wikipedia or Australian Community Media (ACM) sources and report that they did not; ABC, AIDR, government, inquiry and audit-office sources were used.

Labels used throughout: **[M]** measured here by overlaying files already on your disk; **[R]** reported by a source an agent opened (URLs in `notes/`); **[E]** my arithmetic on reported numbers; **[J]** judgement.

## 1. Plain summary (5 lines)

1. **The fire outlines and council boundaries for every candidate are already on your disk** (Geoscience Australia national layer, ABS LGA files), so I measured [M] how much of each council burned instead of guessing: Black Saturday 2009 puts 9 Victorian councils at 5% or more (Murrindindi 40%, Nillumbik 23%); Pinery 2015 puts Light (SA) at 30%; NSW Oct 2013 puts 5 councils at 5% or more (largest 18%).
2. **Best value for effort: NSW Oct 2013 first (same state, same sources, 216 homes lost), then South Australia (4 fires, 8 councils at 5% or more, per-council home counts for Pinery, one state pipeline).** Together they add 13 rows at 5% or more (38 to 51) and lift the rows outside the Black Summer season from 8 to 18, from 3 new independent fire events.
3. **Largest single gain, but incomplete: Victoria's Black Saturday** (+9 rows at 5% or more, 2 at 20% or more). It falls before the on-disk unemployment, business-count and income-support series, and no official per-council house table exists, so it would support a partial Y only. Victorian, SA (Cudlee Creek, Kangaroo Island) and Qld 2019 rows belong to the same 2019-20 season as NSW Black Summer: more rows, not a new independent event.
4. **Comparability problems that no download fixes:** council-finance ratios are defined differently in every state (no state has the NSW infrastructure backlog ratio; own-source revenue is defined differently in WA and Tasmania), so the fiscal block cannot be a like-for-like replication; NSW OLG has a definition break between FY2012-13 and FY2013-14; only Queensland (2014) and SA (2006-2015) have a genuine pre-fire hazard layer.
5. **Decision for you:** approve the 16 files (about 34.6 MB) in section 8, packages P0-P2, to do NSW Oct 2013 and South Australia; Victoria, WA, Tasmania and Queensland (P3-P6) are listed separately and are optional. Whatever you approve, freeze the score and the Y definitions before any new-state Y is built, so the new fires are a fresh test.

## 2. What is already on your disk (not on the download list)

Paths: `D` = `/Users/ray/Research/AUSSEF/fire_event_dataset/data/`, `P1` = `/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0/dataset_phase1/raw/`.

| Item | Coverage on disk | Note |
|---|---|---|
| Geoscience Australia historical bushfire boundaries, `P1/ga_original.zip` (458,831,604 B) + `fire_attributes.csv` | ACT, NSW, Qld, SA, Tas, Vic, WA (no NT). Records to 2022 (Vic, Tas) or 2023 (others) | [M] Holds every candidate below. Qld polygons are parks-estate only. The Waroona-Yarloop outline was found by location and area (68,246 ha polygon "Murray Road" inside Waroona and Harvey, vs 69,165 ha reported), not by name |
| ABS LGA boundaries, `P1/lga_2015, 2016, 2018, 2020, 2021, 2023` | National | [M] used for the overlay |
| ABS Personal Income in Australia (PIA) | National LGA, FY2011-12 to FY2022-23 (four workbooks) | Older income (FY2001-02 to 2010-11) is a different product, not on disk |
| ABS business counts (CABEE) `D/cabee/` | National LGA, **June 2015** to June 2025 | [M] The file names say "Jun 2013 to Jun 2017" but that release holds only the June 2015, 2016 and 2017 sheets. The parquet made from it is NSW only |
| DEWR SALM unemployment, `D/salm/salm_lga.csv` | National, Dec 2010 to Mar 2026, 2025 boundaries | [M] Only 436 of 544 LGAs have any value at Dec 2010 (WA 84 of 137, Qld 52 of 77 [R, agent A7]); 40 more start Mar 2020 and 68 start Jun 2024 |
| DSS payments by LGA, `D/dss/` | National, Mar 2016 to 2026 | [M] The parquet is NSW only. DSS publishes LGA data back to Sep 2013 [R, A7] |
| ABS ERP by LGA | 2001-2025 (2025 boundaries) | Covers every denominator |
| ABS SEIFA `P1/seifa_2016.xls`, `seifa_2021.xlsx` | National LGA | 2006 and 2011 vintages are not on disk |
| NSW OLG council files `D/olg/` | Raw files 1994 to FY2024-25; the parsed table `olg_wide.parquet` starts FY2013-14 | FY2012-13 (the natural baseline for Oct 2013) is on disk but unparsed [R, A1] |
| ABS Census profiles `D/abs/gcp2016, gcp2021` | **NSW only** | National packs are needed for any non-NSW dwelling denominator |
| ICA catastrophe list, `D/ica/ica_catastrophes.xlsx` | 1967-2024, event level | Cross-checks event dates and insured loss; not council level |

**Corrections to assumptions inside the fire notes** (the fire agents worked from file names): CABEE at LGA level starts June 2015, not June 2013 [M]; DSS by LGA is public from Sep 2013 although the on-disk file starts Mar 2016 [R]; the NEMA "DRFA Activation History by LGA" table says "2006 to current" but its earliest row is Sep 2017 and it has no SA bushfire rows [R, A7], so it cannot supply pre-2017 declared councils.

## 3. Measured burned share for every candidate [M]

Method (`overlay_candidates.py`, local files only): for each event I selected Geoscience Australia bushfire or unknown-type polygons by state, ignition-date window and minimum size (FID and area attributes were asserted to match the CSV), dissolved them, intersected with the ABS LGA layer of the nearest vintage (2015, 2016, 2018, 2020 or 2021 as noted in `overlay_candidates.csv`), and divided by council area. This is a similar basis to the existing 38-row count (GA outlines split by council boundaries, there on LGA 2021). GA outlines are mapped extents and can include unburnt islands, so shares are slightly high. The selection of polygons is my choice: read the events as "the fires in that window", not as verified single incidents.

| Event (GA outlines selected by state, ignition-date window and size) | GA polygons | Union area km² | Councils with ≥5% burned (share of council area) | ≥5% | ≥20% |
|---|---:|---:|---|---:|---:|
| Vic Jan-Mar 2003 alpine fires | 4 | 14,114 | Alpine 55.7%; Towong 40.4%; East Gippsland 24.3% | 3 | 3 |
| Vic 2006-07 Great Divide | 4 | 11,233 | Mansfield 49.4%; Wellington 42.3%; Alpine 39.2%; Wangaratta 29.5%; Baw Baw 10.5%; East Gippsland 5.6%; Benalla 5.6% | 7 | 4 |
| Vic Black Saturday 7 Feb 2009 (fires ignited 4-8 Feb) | 14 | 3,878 | Murrindindi 40.3%; Nillumbik 23.2%; Yarra Ranges 18.8%; Whittlesea 17.2%; Mitchell 12.6%; Latrobe 10.9%; South Gippsland 7.4%; Alpine 7.3%; Baw Baw 5.5% | 9 | 2 |
| Vic Jan 2013 (Aberfeldy etc.) | 4 | 1,526 | Wellington 5.8%; Southern Grampians 5.3% | 2 | 0 |
| Vic Jan-Feb 2014 | 15 | 3,787 | East Gippsland 8.8%; Hume 7.0%; Northern Grampians 6.9%; Macedon Ranges 6.5% | 4 | 0 |
| Vic Dec 2015 (Wye River, Scotsburn) | 3 | 138 | none | 0 | 0 |
| Vic Black Summer 2019-20 | 21 | 22,273 | East Gippsland 51.0%; Towong 37.7%; Alpine 29.2% | 3 | 3 |
| SA Wangary Jan 2005 | 1 | 771 | Lower Eyre Peninsula 12.8%; Tumby Bay 6.3% | 2 | 0 |
| SA Sampson Flat Jan 2015 | 1 | 115 | Adelaide Hills 11.7%; Playford 5.5% | 2 | 0 |
| SA Pinery Nov 2015 | 1 | 785 | Light 29.7%; Mallala 13.8%; Wakefield 5.3% | 3 | 1 |
| SA Cudlee Creek Dec 2019 | 1 | 225 | Adelaide Hills 18.3%; Mount Barker 11.6% | 2 | 0 |
| SA Kangaroo Island Dec 2019-Jan 2020 | 2 | 2,012 | Kangaroo Island 45.7% | 1 | 1 |
| Tas Jan 2013 (Forcett-Dunalley etc.) | 5 | 823 | Sorell 23.9%; Tasman 14.3% | 2 | 1 |
| Tas Jan-Feb 2016 (mostly World Heritage area) | 3 | 1,078 | Circular Head 17.0%; Meander Valley 7.3% | 2 | 0 |
| Tas Jan 2019 (Riveaux Rd etc.) | 4 | 1,555 | Huon Valley 11.4%; Central Highlands 6.4% | 2 | 0 |
| Qld Nov-Dec 2018 (parks estate polygons only) | 34 | 11,193 | Redland 9.5%; Mareeba 6.6% | 2 | 0 |
| Qld Sep-Nov 2019 (parks estate polygons only) | 28 | 7,955 | Noosa 10.1%; Lockyer Valley 8.9%; Scenic Rim 7.0% | 3 | 0 |
| WA Jan-Feb 2011 (Roleystone area) | 32 | 530 | none | 0 | 0 |
| WA Nov 2011 (Milyeannup polygon) | 1 | 515 | Nannup 16.9% | 1 | 0 |
| WA Jan 2014 (all polygons; Parkerville) | 407 | 16,151 | Port Hedland 6.2% | 1 | 0 |
| WA Nov 2015 (Esperance + others) | 55 | 11,560 | Esperance 7.1%; Exmouth 5.4% | 2 | 0 |
| WA Jan 2016 (Waroona-Yarloop) | 6 | 1,210 | Waroona 49.4%; Harvey 15.7% | 2 | 1 |
| Vic Mar 2018 (Terang, Camperdown) | 3 | 141 | none | 0 | 0 |
| Vic Feb-Mar 2019 (Bunyip, Licola, Dargo) | 6 | 1,272 | Wellington 10.0% | 1 | 0 |
| SA Bangor Jan-Feb 2014 | 0 | - | no GA polygon of 1,000 ha or more in the window | - | - |
| SA Keilira Dec 2019-Jan 2020 | 1 | 228 | Kingston 6.8% | 1 | 0 |
| WA Wooroloo Feb 2021 | 1 | 107 | Swan 9.4% | 1 | 0 |
| WA Feb 2022 (Wheatbelt, South West) | 5 | 814 | Corrigin 12.8%; Narrogin 10.3% | 2 | 0 |
| NSW Jan 2013 (Wambelong etc.) | 5 | 945 | none | 0 | 0 |
| NSW Oct 2013 (State Mine, Linksview etc.) | 16 | 2,317 | Hawkesbury 18.2%; Blue Mountains 14.1%; Muswellbrook 13.5%; Lithgow 8.3%; Port Stephens 7.0% | 5 | 0 |


Full per-council results: `overlay_candidates.csv` (all councils, shares, ERP 2016). Remote pastoral and Cape York councils show large shares in Qld and WA windows; those are not household events and are ignored in the ranking. Vic Black Saturday with only the 7-8 Feb polygons: the same top eight councils (Murrindindi 40.3% down to Alpine 5.5%); Baw Baw (5.5% above) falls below 1% because its burn comes from the polygon ignited 4 Feb (Bunyip Ridge), so the count is 8 or 9 depending on whether that fire is included. It is part of Black Saturday in the Royal Commission's account.

**Cross-checks against figures other sources give** (agreement means the overlay is on the right footing):

| Council | Overlay [M] | Other figure | Verdict |
|---|---|---|---|
| Murrindindi (Black Saturday) | 40.3% | about 40% (council); 39.8% [E] | agrees |
| Yarra Ranges (Black Saturday) | 18.8% | 19.6% (council GIS) | agrees |
| Kangaroo Island | 45.7% | 48% (CFS area over ESCOSA area) [E]; "almost 50%" | agrees |
| East Gippsland / Towong / Alpine (2019-20) | 51.0 / 37.7 / 29.2% | over 50 / 32.7 / 29% (council plans) | agrees |
| Waroona + Harvey pair | 26.6% | at least 26.9% [E, A4] | agrees |
| Sorell + Tasman pair | 18.8% | 19-20% [E, A3] | agrees |
| Wooroloo: Swan | 9.4% | between 6.4% and 16.7% [E, A4] | agrees |
| **Adelaide Hills (Cudlee Creek)** | **18.3%** | **about 30% "directly impacted" (council audited statements)** | **disagrees; definition of "impacted" unknown; keep both** |

## 4. Ranked candidates (extra large-fire rows per unit of effort)

**Score (my judgement, for ordering only; inputs shown so you can re-weight):** `usable rows = rows at 5% or more x (pillars buildable / 4)`; `ratio = usable rows / effort`. Pillars buildable (0-4) counts DL, IL, FP and SL at 1 each and a half when only partly buildable. Effort (1 low, 2 medium, 3 high, 4 very high) is the stand-alone cost as the first event in its state: new finance pipeline, hazard layer, per-council loss sourcing, extra downloads. Rows are councils at 5% or more burned [M]; the second number is the count at 20% or more.

| Rank | Candidate | Homes destroyed / deaths [R] | Councils at 5% or more, share % [M] | Rows 5% / 20% | Per-council loss data [R] | Pillars buildable | P | E | Usable rows / effort | Independence from Black Summer | Main comparability flags |
|---|---|---|---|---|---|---|---:|---:|---:|---|---|
| 1 | **NSW Oct 2013 (Springwood-Winmalee, State Mine, Hawkesbury, Muswellbrook, Port Stephens)** | 216 homes (RFS); 197 / 196 / 221 in other sources; 2 deaths | Hawkesbury 18.2, Blue Mountains 14.1, Muswellbrook 13.5, Lithgow 8.3, Port Stephens 7.0 | 5 / 0 | Partly: Blue Mountains about 195-205, Port Stephens 4; State Mine 5 and Hall Rd 2 not split; none found for Hawkesbury, Muswellbrook | DL half; IL yes (income on disk, business counts need 1 small ABS file); FP yes (OLG on disk); SL no | 2.5 | 1.5 | **2.08** | New year (2013) | Same state and sources. All 5 councils unmerged in 2016. OLG scale break FY2012-13 to FY2013-14. BFPL is the current mapping. |
| 2 | **SA Pinery, 25 Nov 2015 (Light, Mallala/Adelaide Plains, Wakefield, Clare and Gilbert Valleys)** | 97 dwellings by council (Recovery Final Report); about 91 elsewhere; 2 deaths | Light 29.7, Mallala (now Adelaide Plains) 13.8, Wakefield 5.3 (Clare and Gilbert Valleys 4.97, just under) | 3 / 1 | Yes: Light 41, Wakefield 36, Adelaide Plains 15, Clare and Gilbert Valleys 5 | DL yes; IL yes (both on disk); FP yes (SA reports); SL yes after 1 DSS file | 4 | 2 | **1.50** | New year (2015) | Declared LGAs match the 4 councils. Mallala renamed 2016. No unrestricted-current or backlog ratio in SA. |
| 3 | **Vic Black Saturday, 7 Feb 2009 (with Delburn 28 Jan and Bunyip Ridge 4 Feb)** | 2,133 houses (VBRC); 2,029 (AIDR); 173 deaths | Murrindindi 40.3, Nillumbik 23.2, Yarra Ranges 18.8, Whittlesea 17.2, Mitchell 12.6, Latrobe 10.9, South Gippsland 7.4, Alpine 7.3, Baw Baw 5.5 | 9 / 2 | No official table. Councils' own counts: Murrindindi 1,397, Yarra Ranges 304, on a wider basis than VBRC's per-fire figures | DL half; IL yes (2 extra ABS files); FP half (6 VAGO ratios in PDF); SL no; no unemployment | 2 | 4 | **1.12** | New year (2009) | Falls before SALM (Dec 2010), CABEE LGA (Jun 2015), DSS (Sep 2013). No pre-2011 hazard layer (use NV2005 vegetation). Y would be a partial composite. |
| 4 | **Vic Black Summer, Nov 2019-Feb 2020 (East Gippsland, Towong, Alpine)** | 300+ to 400+ homes (sources differ); 5 deaths | East Gippsland 51.0, Towong 37.7, Alpine 29.2 | 3 / 3 | Yes for 3 councils: East Gippsland 410 residential properties, Towong 38 primary residences, Alpine 1 | DL yes; IL yes; FP yes (LGPRF, VAGO, VGC); SL yes | 4 | 3 | **1.00** | SAME season as NSW Black Summer | Adds councils and a second state's comparison group, not a new independent year. Statewide smoke/COVID shock hits non-burnt councils. |
| 5 | **SA Cudlee Creek, 20 Dec 2019 (Adelaide Hills, Mount Barker)** | 85 homes (CFS); 84 (AIDR); 1 death | Adelaide Hills 18.3, Mount Barker 11.6 | 2 / 0 | Total known; council split not found | DL half; IL yes; FP yes; SL yes (on disk) | 3.5 | 2 | **0.88** | SAME season (Dec 2019) | Adelaide Hills Council says about 30% of its area was directly impacted; the outline gives 18.3%. Unresolved. |
| 6 | **SA Sampson Flat, 2 Jan 2015 (Adelaide Hills, Playford)** | 24 homes (CFS/council); 27 (AIDR); 0 deaths | Adelaide Hills 11.7, Playford 5.5 | 2 / 0 | Yes: 24 in Adelaide Hills | DL yes; IL half (no June 2014 business count); FP yes; SL yes after 2 DSS files | 3.25 | 2 | **0.81** | New year (2015) | Playford is a suburban council with about 0 homes lost. Fire year FY2014-15. |
| 7 | **Qld Sep-Dec 2019 (AGRN 909: Noosa, Lockyer Valley, Scenic Rim, Livingstone, Gladstone)** | 49 homes statewide (QRA); no deaths stated | Noosa 10.1, Lockyer Valley 8.9, Scenic Rim 7.0 | 3 / 0 | Yes: Livingstone 14, Scenic Rim 11, Gladstone 8, Somerset 4, Noosa 2, Toowoomba 1 | DL yes; IL yes; FP half (old F1-F10 ratios, no cash cover); SL yes (on disk) | 3.5 | 3.5 | **0.75** | Prelude to Black Summer, same drought season | GA has Qld parks-estate polygons only. Fires are routine in Qld, so the no-fire comparison group is thin. Hazard layer is 1.6 GiB with an unclear access route. |
| 8 | **SA Kangaroo Island, Dec 2019-Jan 2020** | 87 dwellings/assets (CFS) vs 56 homes (AIDR); 2 deaths | Kangaroo Island 45.7 | 1 / 1 | Yes (single council) | DL yes; IL yes; FP yes; SL yes | 4 | 2 | **0.50** | SAME season | One row. Tourism and COVID confound. |
| 9 | **WA Waroona-Yarloop, Jan 2016 (Waroona, Harvey)** | 181 buildings destroyed (Ferguson report; counts inconsistent across sources); 2 deaths | Waroona 49.4, Harvey 15.7 | 2 / 1 | Partly: Yarloop is in Harvey (166 dwellings per the inquiry); Waroona shire share of losses not split | DL half; IL yes; FP half (no cash balances in MyCouncil); SL yes after 1 DSS file | 3 | 3 | **0.50** | New year (2016) | Burn share is largest in Waroona but loss sits in Harvey. Small shires (about 4,000 people). SALM has pre-2020 values for only 84 of 137 WA LGAs. |
| 10 | **WA Feb 2022 Wheatbelt and South West (Shackleton, Narrogin East, Bridgetown)** | 15 houses (Shackleton) + 8 (Bridgetown) + 4 (Denmark); Narrogin East 31 buildings; deaths none stated | Corrigin 12.8, Narrogin 10.3 | 2 / 0 | Incident level only | DL half; IL yes; FP half (only 4 LGFI ratios after 2020/21); SL yes | 3 | 3 | **0.50** | New year (2022) | Councils of about 1,200 and 5,200 people: very noisy denominators. DRFA status not verified. |
| 11 | **Tas Forcett-Dunalley, Jan 2013 (Sorell, Tasman)** | 203 homes for the January 2013 complex (TFS); no civilian deaths | Sorell 23.9, Tasman 14.3 | 2 / 1 | Locality level only (Inquiry has more, behind a login wall) | DL half; IL yes (PIA + 1 ABS file); FP yes (CDC + audit reports); SL no | 2.5 | 3 | **0.42** | New year (2013) | Only 29 councils, so the no-fire comparison group is about a dozen (estimate). No pre-fire hazard layer (Tas overlay dates from 2020). No DSS or CABEE baseline. |
| 12 | **WA Wooroloo, Feb 2021 (Swan, Mundaring)** | 86 homes (80 Swan, 6 Mundaring; AFAC review); 0 deaths | Swan 9.4 | 1 / 0 | Yes: Swan 80, Mundaring 6 | DL yes; IL yes; FP half (only 4 LGFI ratios after 2020/21); SL yes | 3.5 | 3 | **0.29** | New year (2021) | Cleanest per-council loss split of any candidate. Marginal effort is low once a WA pipeline exists (Waroona). |
| 13 | **NSW Jan 2013 (Wambelong / Warrumbungle)** | 53 homes Wambelong (RFS); 57 for the fortnight; 0 deaths | none (Warrumbungle 3.3) | 0 / 0 | Yes: Warrumbungle 53, Cooma-Monaro 4 | DL half; IL yes (NRP 2009-13); FP half (no FY2011-12 cash cover); SL no | 2 | 1.5 | **0.00** | New year (2013) | Adds no council at 5% or more, but has the highest loss rate of the NSW candidates (about 13.8 homes per 1,000 rating assessments, estimate). Cheap DL contrast. |

Also in `candidates_ranked.csv`.

**Not recommended (with reason):**
- **Wye River Dec 2015** (116 houses; under 1% of Colac Otway per the Victoria agent's estimate; a holiday-home town of about 100-200 residents), **Terang/Camperdown Mar 2018** (26 residences, 1.8% of Corangamite), **Scotsburn 2015** (12 houses), **Parkerville 2014** (57 houses, about 1% of Mundaring), **Roleystone 2011** (71 houses), **Toodyay 2009** (38), **Margaret River 2011**: household loss but no council near 5% burned. This is a limit of using burned share to define "large": interface fires with many houses lost are excluded (the existing 5% cut has the same property).
- **Vic Feb-Mar 2019** (Wellington 10.0%, 31 homes elsewhere), **Qld Nov 2018** (9 dwellings), **Tas 2016 and 2019** (wilderness, no homes), **Esperance Nov 2015** (4 deaths, 2 homes, 7.1% of the shire), **Vic Jan 2013 Aberfeldy** (22 homes, 5.8% of Wellington, no pre-fire business count): big burn with almost no loss; useful only as "high hazard, little loss" rows, cheap only once that state's pipeline exists.
- **Pre-2010 fires** (SA Wangary 2005: 93 houses, 9 deaths, Lower Eyre 12.8%; Vic 2003 and 2006-07: 41 and 51 houses; KI 2007: no homes): real, but before every LGA series except ERP, so DL-only.
- **Tasmania and Queensland "large but empty" seasons** are not household events.

## 5. Clusters, minimum viable set, and what it buys

State pipelines are shared costs, so the marginal effort of a second event in a state is small (about 0.5). Cluster view:

| Cluster | Events | Rows at 5% or more (20% or more) | Usable rows | Effort (pipeline + extras) | Usable rows / effort |
|---|---|---:|---:|---:|---:|
| NSW 2013 | Oct 2013 + Jan 2013 | 5 (0) | 3.1 | 2.0 | 1.6 |
| **South Australia** | Pinery, Sampson Flat, Cudlee Creek, Kangaroo Island | 8 (2) | 7.4 | 3.5 | 2.1 |
| Victoria | Black Summer + Black Saturday | 12 (5) | 7.5 | 6.0 | 1.3 |
| Western Australia | Waroona, Wooroloo, Feb 2022 | 5 (1) | 3.9 | 4.5 | 0.9 |
| Queensland | Sep-Dec 2019 | 3 (0) | 2.6 | 3.5 | 0.8 |
| Tasmania | Dunalley 2013 | 2 (1) | 1.3 | 3.0 | 0.4 |

**Recommended minimum viable set: NSW Oct 2013 (with Jan 2013 as a cheap loss-rate contrast) plus the four South Australian fires.**
- Adds 13 rows at 5% or more: 38 to 51. Outside the Black Summer season: 8 to 18 (NSW Oct 2013: 5; Pinery: 3; Sampson Flat: 2). Inside the 2019-20 season: 3 (Cudlee Creek 2, Kangaroo Island 1).
- Adds 2 rows at 20% or more (Light, Kangaroo Island); only Light is outside Black Summer.
- Three new independent fire events outside 2019-20 (Oct 2013, Jan 2015, Nov 2015). Rows inside one event share weather and burn, and the existing intervals cluster by council, not by fire; so the effective gain is closer to the number of events than to the number of rows.
- All four pillars for Pinery, Kangaroo Island and Cudlee Creek (three of four for the others). Per-council home counts exist for Pinery (4 councils).
- Needs only a handful of small ABS files, one new state pipeline (SA) and SA's 4 MB Bushfire Protection Areas layer.

**Next, in order:** Victoria (Black Summer first, because it completes a Victorian pipeline; Black Saturday second, as a partial-Y test with the largest number of new 20%-plus councils: Murrindindi and Nillumbik), then WA (Waroona, Wooroloo), then Queensland 2019; Tasmania last.

**If the aim is 20%-plus councils outside Black Summer** only five exist among all candidates: Murrindindi, Nillumbik (Black Saturday), Light (Pinery), Sorell (Dunalley), Waroona (Waroona-Yarloop). The minimum set gets one (Light).

**Full optional set (all events in the ranking):** about +35 rows at 5% or more beyond the current 38 (about 73); rows outside the Black Summer season would go from 8 to about 34 (Qld 2019 counted with the 2019-20 season). Still far fewer than the 218 rows on which the earlier fiscal null was informative, so the fiscal question on large fires stays under-powered even then; the vulnerability question (78% power at rho 0.3 with 38 rows in the earlier power check) benefits more. This is an inference from the earlier power table, not a new run.

## 6. Feasibility of the four Y pillars and the pre-fire inputs

Pillar definitions follow `fire_event_dataset/README.md` and `src/vulnerable.py`: SL is "quarter after the fire-start quarter minus the same quarter a year earlier", so it needs a DSS quarter about 15 months before the fire.

| Input / pillar | NSW build | Post-2015 non-NSW fires (Vic, SA, Tas, Qld, WA) | Earlier fires (2009, 2013) | Gap |
|---|---|---|---|---|
| **DL** homes destroyed | Sourced per-council facts (90 of 218 rows) | Per-council counts exist for SA Pinery, Wooroloo, Qld 2019, Vic Black Summer (3 councils) | No official per-council table for Black Saturday; NSW Oct 2013 for 2 councils | Zeros need a source that says so |
| DL denominator (Census dwellings) | Census 2016 G32 / 2021 G36 (NSW packs) | National 2016 / 2021 packs needed (12.8 MB / 13.8 MB) | 2011 B31 (9.4 MB); 2006 has no national pack, per-region files only | Vintage rule: latest census at or before the fire year, else earliest after |
| **IL income** | PIA, fire FY vs prior FY | On disk (FY2011-12 to 2022-23) | Black Saturday: EPISA FY2005-06 to 2010-11 (1.0 MB); 2013 fires: PIA on disk | EPISA and PIA are different products: never form a change across 2010-11 / 2011-12; the excess design is safe inside one product |
| **IL business counts** | CABEE, both years from the same release | On disk from June 2015: fire FY2015-16 and later only | ABS National Regional Profile (LGA 2012 boundaries): Jun 2008-2014 (0.4-0.8 MB files) or SLA cubes for 2007-09 | Series break between NRP and CABEE; so Sampson Flat (FY2014-15) has no prior-year count |
| **FP** council finances | NSW OLG time series | See 6a: SA, Vic, Tas, Qld, WA each need a new pipeline | NSW 2013: OLG FY2012-13 baseline on disk; Vic 2009 only 6 VAGO ratios | No state has the NSW infrastructure backlog ratio; see section 7 |
| **SL** income support | DSS by LGA, 2016 on | On disk from Mar 2016; earlier quarters from Sep 2013 (small downloads) | Not buildable for 2013 or 2009 (no year-earlier quarter) | Pre-2016 DSS quarterly workbooks: LGA tab not verified [R, A7] |
| X SEIFA IRSD | 2016 for fires to 2020 | 2016, 2021 on disk | 2011 (0.7 MB) or 2006 (0.7 MB) downloads | Scores are rescaled every census: use percentiles (the score already does) |
| X median income | PIA | on disk | EPISA / PIA as above | as above |
| X unemployment | SALM smoothed rate | Dec 2010 on, 436 of 544 LGAs | none before Dec 2010 | Black Saturday and Wangary have no unemployment; 108 LGAs lack pre-2020 values for 2019-20 rows (ask DEWR) |
| X population / density | ERP | on disk | on disk | 2025 boundaries: back-cast |
| X hazard (BFPL) | NSW BFPL Cat 1-2 share + NVIS forest | See 6b | See 6b | Hazard layers differ in class and date by state |

### 6a. Council finance sources by state (from notes A5, A6, A1)

| State | Best source | Years | Has cash and function split? | Closest to NSW ratios | Fire years fully buildable (prior, fire, after) |
|---|---|---|---|---|---|
| NSW (pre-2015) | OLG raw files on disk | FY2008-09 to FY2014-15 (152 councils) | Cash cover only from FY2012-13 | Same series; **definition break FY2012-13 to 2013-14** (median cash cover 3.9 to 9.3 months; own-source 59.6 to 71.4) | Oct 2013 (FY2013-14) |
| SA | LGGC Database Reports (PDF, 68 councils) | FY1995-96 to 2023-24; 10 reports from FY2011-12 | Yes: cash and investments every year; function split from FY2011-12 | Operating surplus, asset sustainability; no unrestricted current ratio, no backlog. Files FY2006-07 to 2012-13 carry an "internal use only" notice | 2014-15, 2015-16, 2019-20 (and 2004-05) |
| Vic | LGPRF (FY2014-15 on), VAGO CSV/xlsx (about FY2015-16 on), VGC returns (FY2015-16 on), VAGO PDF ratios FY2006-07 to 2014-15 | see left | Function split and cash only from FY2014-15/2015-16 | LGPRF L1/L2 (liquidity, unrestricted cash as a ratio, not months), asset renewal, debt repayments/rates | 2015-16 and 2019-20; 2008-09 and 2013-14 only as 6 PDF ratios |
| Tas | Consolidated Data Collection (2 zips, 30 MB) + Audit Office and dashboards | 2000-01 to 2025 | Yes; TAO-adjusted unrestricted cash only from FY2013-14 | Closest of the new states (cash expense cover, debt service cover); own-source is over operating expense, not revenue | 2012-13 (self-computed cash), 2015-16, 2018-19 |
| Qld | Comparative-information workbooks | 2002-03 to 2024-25 | Unverified; no cash cover before 2023-24 | Legacy F1-F10 ratios (working capital, debt servicing, etc.) | 2018-19, 2019-20 |
| WA | MyCouncil OData | Ratios 2012/13-2020/21; 4 LGFI ratios 2018/19-2023/24; expenditure by program 2010/11 on | Function split yes; **no cash balances** | Own-source (over expenses), debt service cover, current ratio, renewals; no backlog | 2013-14, 2015-16, 2020-21 (LGFI only); 2010-11 not buildable |

Cross-cutting: Commonwealth Financial Assistance Grant advance payments shift income between years (FY2013-14/2014-15, FY2018-19 to 2020-21); the state median of no-fire councils cancels a uniform shift.

### 6b. Hazard layers by state (from notes A5, A6)

| State | Layer | First version | Pre-fire for | Fit to NSW BFPL | Size |
|---|---|---|---|---|---|
| NSW | BFPL (on disk) | current mapping | (post-2019 mapping; existing limit 3) | reference | on disk |
| SA | Bushfire Protection Areas (High / Medium / General; 39 councils) | 2006-2015 amendments | 2014-15, 2015-16, 2019-20; not 2005 | Moderate: modelled risk classes, not vegetation categories | 4.1 MB |
| Vic | Bushfire Prone Area (single class), Bushfire Management Overlay | gazetted 7 Sep 2011; current version only | none for 2009; earlier gazettes unavailable | Low: BPA covers nearly all non-metro land, so it barely discriminates | size unknown |
| Vic (fuel proxy) | NV2005 EVC vegetation (2001-04) | 2005 | all Victorian candidates including 2009 | Vegetation only | size unknown (2.39M polygons) |
| Qld | CSIRO/QFES bushfire prone area (Very High / High / Medium + buffer) | SPP 2013, published 2015 | 2018-19, 2019-20 | Good | about 1.6 GiB; access route unclear |
| WA | Map of Bush Fire Prone Areas | first designation 8 Dec 2015 | Waroona 2016 and 2021 via designation dates (inference); nothing for 2011, 2014, Nov 2015 | Weak: binary | 469 polygons; download blocked |
| Tas | Bushfire-Prone Areas overlay | layer created 26 Jun 2020 | none | Weak: single class | 1.32 GB (all overlays) |
| All | NVIS (national) | v6.0 used by the pipeline; v7.0 now served | all (time-invariant) | Forest share only, no slope or interface | on disk (v7.0 GDB unreadable by current GDAL; v6.0 needs a per-state fetch) |

## 7. Comparability problems and design decisions

1. **The fiscal block cannot be replicated like for like.** Own-source revenue is a share of revenue in NSW but coverage of operating expenses in WA and Tasmania; cash expense cover is available directly only in NSW, computed from cash and investments in SA, TAO-adjusted from 2013-14 in Tasmania, only from 2023-24 in Queensland, not computable from MyCouncil in WA (no cash balances); the infrastructure backlog ratio exists nowhere else. The new-state F block would be built from analogues and ranked within state, so the NSW result (F vs Y +0.03) does not simply extend.
2. **NSW OLG definition break FY2012-13 to FY2013-14** affects the FP change for Oct 2013. A state median cancels a uniform shift, not a definition change that differs by council; treat Oct 2013 FP as lower confidence or use only ratios that did not break.
3. **Boundaries are clean for the councils that matter** [M]: 61 of the 62 councils at 5% or more keep the same ABS code and area in LGA 2021 (`boundary_check_2021.csv`). The exception is Mallala (merged into Adelaide Plains, 2016). NSW 2016 mergers do not touch the Oct 2013 five, but do touch Jan 2013 councils (Cooma-Monaro, Harden). WA MyCouncil has two councils called Narrogin (key on the council id).
4. **The no-fire comparison group** for the excess-change design: adequate in SA (about 50 regional councils [J]) and probably Victoria (30-50 [J]); thin in Tasmania (29 councils, about a dozen comparators [J]); weak in Queensland and northern WA where 100 ha fires are routine. Compute the group from the GA outlines and the LGA layer, not from declarations. Statewide shocks (Vic 2019-20 smoke and COVID, Kangaroo Island tourism) hit non-burnt councils too.
5. **Y is a within-sample percentile composite.** Adding rows re-ranks the NSW rows unless the reference distribution is fixed first. Decide before building: rank within state, pooled, or against the frozen NSW distribution. The score structure (H+V, exposure v2) was chosen after seeing NSW results, so freeze it now and treat the new fires as the fresh test the report asks for.
6. **Declared-event unit.** Pre-2017 declared councils must come from DisasterAssist event pages read one by one (AGRNs are in `notes/A2-A4`); the NEMA table starts Sep 2017 and the ICA list is event level. The unit "declared event x council" is therefore reproducible for post-2017 events by table and for earlier events by hand.
7. **Independence.** Rows within one event share weather and burn. Vic, SA (Cudlee Creek, Kangaroo Island) and Qld 2019 rows share the 2019-20 season with NSW Black Summer.
8. **Data licence.** SA LGGC files for FY2006-07 to 2012-13 say council internal use only; none is needed for the recommended years. Several state hosts (LGV, SA DHUD, planning.vic, Queensland departments) block programmatic requests: some downloads may have to be done in a browser.

## 8. Download list awaiting your approval (nothing downloaded yet)

Sizes are HEAD Content-Length unless marked. "Archive size" means the length of a web-archive copy because the live host blocks HEAD.

### P0. Shared national Census pack (needed by every non-NSW event from 2015)
| # | File | Source | Size | Purpose |
|---|---|---|---:|---|
| 1 | `2016_GCP_LGA_for_AUS_short-header.zip` | https://www.abs.gov.au/census/find-census-data/datapacks/download/2016_GCP_LGA_for_AUS_short-header.zip | 12,823,638 B | Dwellings per LGA (G32) for SA, Vic, Qld, Tas, WA fires 2015-2020; industry shares |
| (opt) | `2021_GCP_LGA_for_AUS_short-header.zip` | same folder, `2021_GCP_LGA_for_AUS_short-header.zip` | 13,827,380 B | Only for WA Wooroloo 2021 (and later) |

### P1. NSW 2013 (recommended)
| # | File | Source | Size | Purpose |
|---|---|---|---:|---|
| 2 | `2033.0.55.001 lga indexes.xls` (SEIFA 2011, LGA; note it was published Jul 2013, so for the Jan 2013 fires only the 2006 vintage was public at the time [A7]) | https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&2033.0.55.001%20lga%20indexes.xls&2033.0.55.001&Data%20Cubes&28EF8569335AC7CDCA257BAB00136B0F&0&2011&18.07.2013&Latest | 667,136 B | Pre-fire disadvantage index for 2013 fires |
| 3 | `1379055001_economy_2009-2013_lga_201506.zip` (ABS National Regional Profile, economy, LGA) | https://www.abs.gov.au/AUSSTATS/SUBSCRIBER.NSF/log?openagent&1379055001_economy_2009-2013_lga_201506.zip&1379.0.55.001&Data%20Cubes&DC45B9F767450EB4CA257E70001519A8&0&2009-13&29.06.2015&Latest | 448,264 B | Business counts June 2012 and 2013 (Jan 2013 fires; both years from one release) |
| 4 | `1379055001_economy_2010-2014_lga_201606.zip` | https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&1379055001_economy_2010-2014_lga_201606.zip&1379.0.55.001&Data%20Cubes&5622F64E4A0E1742CA2580360016C571&0&2010-14&23.09.2016&Latest | 784,749 B | Business counts June 2013 and 2014 (Oct 2013 fires) |
| 5 | `2011_BCP_LGA_for_AUST_short-header.zip` (Census 2011 Basic Community Profile, table B31 dwellings) | https://www.abs.gov.au/census/find-census-data/datapacks/download/2011_BCP_LGA_for_AUST_short-header.zip | 9,445,666 B | Dwelling denominator for 2013 fires (2011 is the latest census at or before the fire year) |

P1 total 11,345,815 B (11.3 MB). No SL for 2013 fires, so no DSS file. Nothing else is needed: PIA, SALM, ERP, OLG, GA outlines and the 2015 LGA boundaries are on disk.

### P2. South Australia (recommended)
| # | File | Source | Size | Purpose |
|---|---|---|---:|---|
| 6 | DSS demographics **Jun 2014** workbook, `dss-demographics-june-2014-jan-2020-edit.xlsx` | data.gov.au dataset `dss-payment-demographic-data`, resource f0615bb3-463f-4352-902c-0b6bb0e22e7d (full URL to be read from the dataset metadata, which transfers no data file) | 1,100,863 B | Sampson Flat: quarter a year before the after-quarter (Jun 2014) |
| 7 | DSS demographics **Mar 2015** workbook | same dataset; resource id and file name from the metadata | 1,726,694 B | Pinery: Mar 2016 (on disk) minus Mar 2015 |
| 8 | DSS demographics **Jun 2015** workbook | same dataset; resource id and file name from the metadata | 1,719,096 B | Sampson Flat after-quarter; also Waroona 2016 |
| 9-15 | LGGC "Database Reports" PDFs, FY2013-14, 2014-15, 2015-16, 2016-17, 2018-19, 2019-20, 2020-21 | `https://dit.sa.gov.au/local-government/documents/office-of-local-government/grants-commission/lggc-database-reports/database_reports_YYYY-YY.pdf`; FY2020-21: https://www.dit.sa.gov.au/__data/assets/pdf_file/0003/1093314/Database_Reports_2020-21.pdf | Archive sizes: 157,972; 165,808; 161,070; 181,730; 214,397; 429,953; about 500,000 B | Council finances for the SA fire years (prior, fire, after) |
| 16 | `BushfireProtectionAreas_shp.zip` | https://www.dptiapps.com.au/dataportal/BushfireProtectionAreas_shp.zip | 4,103,082 B | SA hazard layer (39 councils; pre-fire for 2014-15 to 2019-20) |

P2 total about 10.5 MB (DSS 4,546,653 B; PDFs about 1.8 MB; layer 4,103,082 B). Risk: the LGA tab of the pre-2016 DSS quarterly workbooks is unverified [A7]. If absent, ABS Data by Region 14100DO0004 (on disk, June 2015 baseline) is the fallback.

**Recommended approval: P0 (2016 only) + P1 + P2 = 16 files, about 34.6 MB.**

### Optional packages (not recommended for approval yet)
| Package | Files (name, size) | Source | Enables |
|---|---|---|---|
| **P3 Victoria, 2019-20** | LGPRF 2020-2025 full data set 3,241,185 B (catalogue size); an earlier rolling LGPRF file covering FY2018-19 to 2020-21 (about 3 MB, web-archive only); VAGO council data FY2019-20 xlsx 653,947 B, FY2018-19 xlsx 788,798 B, FY2020-21 Financial data.csv 2,944,835 B and Indicator data 215,876 B; VGC1 returns FY2018-19 to 2020-21 (about 830-880 KB each) and ABS2-3 (about 140 KB each); Vic hazard: Bushfire Prone Area and Bushfire Management Overlay via WFS (size unknown) | LGV, VAGO, data.vic (URLs in `notes/A5` section A1 and E1) | Victorian Black Summer rows |
| **P3b Victoria, Black Saturday extras** | EPISA `6524055002do003_200506201011.xls` 1,019,904 B; NRP economy LGA 2008-2012 zip 488,524 B; SEIFA 2006 LGA xls 697,856 B; VAGO "Results of 2010-11 audits" PDF 4,580,719 B; NV2005 EVC vegetation (size unknown) | ABS, VAGO, DEECA (URLs in `notes/A7` section 14A, `A5`) | Black Saturday DL, IL, partial FP |
| **P4 Western Australia** | MyCouncil OData (an API, no file); WA Bush Fire Prone Areas layer (469 polygons, size unknown, download returned 403); Census 2021 pack (P0 optional); DSS Jun 2015 (already item 8) | data.wa.gov.au, DFES | Waroona 2016, Wooroloo 2021 |
| **P5 Tasmania** | `LGA_CDC_Data_Repository_2000-2015.zip` 16,835,035 B and `LGA_CDC_Data_Repository_2015-2025.zip` 13,432,951 B (30.3 MB together) at https://listdata.thelist.tas.gov.au/opendata/ ; Audit Office volumes (PDF) | LIST, TAO | Dunalley 2013 |
| **P6 Queensland** | Comparative-information workbooks FY2017-18 to FY2020-21, Financial input and Financial PIs (26-33 KB each, 237,885 B for the 8 files; base `https://www.dlgwv.qld.gov.au/__data/assets/excel_doc/`, paths in `notes/A6` appendix); Qld bushfire-prone layer about 1.6 GiB (access unclear) | Qld Dept of Local Government | Qld 2019 |
| Other | NEMA DRFA Activation History CSV 367,919 B; ICA July-2026 catastrophe list 273,626 B; ABS LGA 2009 boundaries 41,290,643 B | data.gov.au; ICA; ABS | Low value: DRFA starts Sep 2017; ICA already on disk to 2024; Vic LGAs unchanged 2009-2021 [J] so the 2015 boundaries suffice |

**Not needed (already on disk):** the GA outlines (all states), ABS LGA boundaries 2015-2023, PIA 2011-12 on, CABEE June 2015 on, SALM, DSS Mar 2016 on, ERP, SEIFA 2016/2021, OLG raw files, ICA list.

## 9. What is not verified, and where sources disagree

- **All seven research agents exhausted the shared web-search budget (200 searches).** The last third of each used direct page reads. Each `notes/` file lists its unverified items. I re-verified only what I could on disk: the burned shares, the on-disk coverage claims (CABEE June 2015, SALM 436 of 544), and the boundary continuity. Home counts, deaths and council statements come from pages the agents opened; spot-check before use.
- **Source conflicts kept visible:** Oct 2013 homes 216 (RFS bulletin sum), 197, 196, 221 (ICA "residential properties"); Black Saturday 2,133 (VBRC), 2,029 (AIDR), "almost 2,500 properties" (recovery authority); Kangaroo Island 87 dwellings/assets vs 56 homes; Cudlee Creek 85 vs 84; Pinery 97 by council vs about 91; Vic Black Summer 300+, 400+, "313 primary and 145 non-primary residences" (an excerpt only, IGEM page returned 403); Tas Dunalley 203 for the complex vs about 93-100 at Forcett; Waroona 181 buildings with inconsistent definitions.
- **Not opened or blocked:** DisasterAssist as a data list (script-driven); Tasmanian Bushfires Inquiry PDFs (login wall); SA Recovery site; IGEM report; Queensland department sites (403 to programs, open in a browser); LGV, SA DHUD, planning.vic (Cloudflare). Sizes for their files are archive or catalogue sizes.
- **Unresolved:** Cudlee Creek council "30%" vs outline 18.3%; whether WA polygon designation dates can rebuild pre-fire extents (inference); NRP and pre-2016 DSS workbook contents; VAGO and VGC column headers (reading the header line would be a data-file request, so it was not done); whether the SA LGGC "internal use only" years matter (they do not for the recommended years).
- **Overlay selection is mine:** polygons were chosen by state, date window and size, not matched one by one to named incidents (Qld and WA windows contain remote pastoral and park fires). The Bangor fire (SA, Jan-Feb 2014) has no GA polygon of 1,000 ha or more in my window.

## 10. Key source URLs (full lists in `notes/`)

- **NSW 2013:** RFS Bush Fire Bulletin 2014 vol 36 no 2 https://www.rfs.nsw.gov.au/__data/assets/pdf_file/0020/25922/Bush-Fire-Bulletin-2014-Vol-36-No-2.pdf ; RFS bulletin Jan 2013 https://www.rfs.nsw.gov.au/__data/assets/pdf_file/0013/4054/Bush-Fire-Bulletin-2013-Vol-35-No-1.pdf ; RFS AR 2013-14 summary https://www.rfs.nsw.gov.au/__data/assets/pdf_file/0011/28289/NSW-RFS-Annual-Report-2013-14-Summary-Review-of-Operations.pdf ; AIDR https://knowledge.aidr.org.au/resources/bushfire-blue-mountains-2013/ ; declarations (archived) https://web.archive.org/web/2020/https://www.emergency.nsw.gov.au/Pages/publications/natural-disaster-declarations/2013-2014.aspx
- **Victoria:** VBRC summary http://royalcommission.vic.gov.au/finaldocuments/summary/PF/VBRC_Summary_PF.pdf ; VBRC vol 1 chapters http://royalcommission.vic.gov.au/Finaldocuments/volume-1/HR/VBRC_Vol1_ChapterNN_HR.pdf (NN 03-14) ; DisasterAssist Black Saturday https://www.disasterassist.gov.au/Pages/disasters/previous-disasters/Victoria/Victorian-bushfires-January-to-February-2009.aspx ; DisasterAssist 2019-20 https://www.disasterassist.gov.au/Pages/disasters/current-disasters/Victoria/victorian-bushfires-november-2019-onwards.aspx ; East Gippsland Shire https://www.eastgippsland.vic.gov.au/media-releases/east-gippslanders-dismayed-by-fire-grants-program ; Towong recovery plan https://www.towong.vic.gov.au/repository/libraries/id:2cvu1xfyg1cxby8c14xc/hierarchy/Bushfire%20Recovery/Municipal%20Recovery%20Plan/municipal-recovery-plan.pdf ; AIDR Black Saturday https://knowledge.aidr.org.au/resources/bushfire-black-saturday-victoria-2009
- **SA and Tasmania:** DisasterAssist Pinery https://www.disasterassist.gov.au/Pages/disasters/current-disasters/South-Australia/Lower-Mid-North-Bushfire-25-November-2015.aspx ; DisasterAssist Sampson Flat https://www.disasterassist.gov.au/Pages/disasters/current-disasters/South-Australia/Bushfires-January-2015.aspx ; DisasterAssist SA Nov 2019 onwards https://www.disasterassist.gov.au/Pages/disasters/current-disasters/South-Australia/Yorketown-bushfire-112019-onwards.aspx ; DisasterAssist Tas Jan 2013 https://www.disasterassist.gov.au/Pages/disasters/current-disasters/Tasmania/Bushfires-January-2013.aspx ; AIDR Major Incidents Report 2019-20 https://knowledge.aidr.org.au/media/8049/aidr_major-incidents-report_2019-20.pdf
- **WA and Queensland:** Ferguson special inquiry (Waroona) https://www.wa.gov.au/system/files/2020-02/Reframing%20Rural%20Fire%20Management%20-%20Report%20of%20the%20Special%20Inquiry%20into%20the%20January%202016%20Waroona%20Fire.pdf ; AFAC Wooroloo review https://www.wa.gov.au/system/files/2022-09/Wooroloo-Bushfire-Review-2021.pdf ; DisasterAssist Wooroloo https://www.disasterassist.gov.au/Pages/disasters/current-disasters/Western-Australia/bushfires-1-february-2021-onwards.aspx ; QRA 2019 recovery plan https://www.qra.qld.gov.au/sites/default/files/2020-08/2019_qld_bushfires_recplan_2019-20_lr.pdf ; DisasterAssist Qld 2019 https://www.disasterassist.gov.au/Pages/disasters/current-disasters/Queensland/queensland-bushfires-september-december-2019.aspx
- **Data catalogues:** NEMA DRFA activation history https://data.gov.au/data/dataset/drfa-activation-history-by-lga ; ICA data hub https://insurancecouncil.com.au/resources/data-hub/ ; ABS DataPacks https://www.abs.gov.au/census/find-census-data/datapacks ; Tasmania open data https://listdata.thelist.tas.gov.au/opendata/ ; MyCouncil https://mycouncil.wa.gov.au/ ; Victoria LGPRF https://discover.data.vic.gov.au/dataset/local-government-performance-reporting

## 11. Files in this folder

| File | What |
|---|---|
| `FINDINGS.md` | This document |
| `candidates_ranked.csv` | The ranking table as data |
| `overlay_candidates.py` | Local overlay (GA outlines x ABS LGA), reads files on disk only |
| `overlay_candidates.csv`, `overlay_summary.csv` | Council shares for every event and per-event counts |
| `boundary_check_2021.csv` | Councils at 5% or more: same ABS code and area in LGA 2021? |
| `notes/A1_nsw_2009_2014.md` ... `A7_national_series.md` | Agent notes with every table, figure and URL behind this summary (A1 NSW 2009-14; A2 Victoria; A3 SA and Tasmania; A4 Qld and WA; A5 Vic and SA finance and hazard; A6 Qld, Tas and WA finance and hazard; A7 national series) |
