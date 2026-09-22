# Do bushfires cut all of a town's exit roads at once? A pre-registered measurement study of NSW towns

**Project:** AUSSEF. **Date:** 22 September 2026. **Code, data record and pre-registrations:**
`pilot_exit_correlation/` (git branch `pilot-exit-correlation`).

## Abstract

Evacuation planning often treats the number of roads out of a town as a measure of redundancy:
three exits sound safer than one. That only holds if exits fail independently. We measured how
often mapped bushfires cut **every** exit of a New South Wales town, compared with how often that
would happen if each exit failed independently.

We combined a 2019 road network (1.21 million public road edges), 526 towns (ABS Urban Centres and
Localities, population ≥ 200), and two independent fire records: 912 fire events from 2019–23 and
6,470 historical fire events from 1950–2019. Every test was pre-registered before its numbers were
computed.

Across the historical record, all exits were cut together **14.9 times** more often than
independence predicts (95% CI 3.9–31). The result held when only roads cut outside the town counted
(13.8×, CI 3.1–29). Satellite fire detections showed that exits were often reached at different
times. With a strict 12-hour rule timed along the whole route, the effect was not statistically
supported (6.9×, CI 0–12). Timed near the town, where people are trapped, it was (8.4×, CI 1.9–14.4).
Official closure records were too sparse to confirm any all-exits-closed day.

We conclude that exit counts overstate redundancy because fires tend to cut a town's exits together,
though often over hours to days rather than all at once.

## 1. Question and hypothesis

**Question.** When a bushfire reaches a NSW town, how much more often are all of its exit roads cut
than would happen if each exit failed independently?

**Hypothesis.** Exits fail together, because one fire can cover several roads. Exit counts therefore
overstate true redundancy.

**Measure.** The pooled ratio R = observed full cut-offs ÷ full cut-offs expected under independence.
R = 1 means "no different from chance". R = 2 means twice as often.

## 2. Data

| Input | Source | Size |
|---|---|---|
| Road network, 1 January 2019 | OpenStreetMap snapshot; `service` roads excluded | 1,214,545 edges |
| Towns | ABS Urban Centres and Localities 2021 + 2021 Census population | 526 towns with population ≥ 200 |
| Fire record A (2019–23) | Geoscience Australia perimeters grouped into fire families (events within 3 days and 5 km) | 1,034 families |
| Fire record B (1950–2019) | Geoscience Australia historical bushfire boundaries, NSW records (NSW national parks mapping) | 11,106 fires → 7,729 events; season composites and undated records removed |
| Satellite fire detections | DEA Hotspots (Geoscience Australia), MODIS/VIIRS/Himawari | 590,000 detections for 12 fire events |
| Road-closure records | Live Traffic NSW archive and Home Affairs FOI briefings (curated earlier) | 37 records |

Every input is SHA-256 hash-verified on each run. The canonical AUSSEF database was never modified.

## 3. Methods

1. **Exits.** For each town, the exits are the number of separate routes (sharing no road segment) from the town to a ring 20 km from its centre. They were found by max-flow on the road graph (median 4 exits in eligible towns). One shortest set of routes is stored per town.
2. **Closure.** A road segment is closed by a fire if the mapped fire perimeter touches it (rule S0). The sensitivity rule S100 also counts segments within 100 m.
3. **Full cut-off.** A fire cuts a town off if, after removing every segment it closes, no route from the town reaches the ring.
4. **Expected under independence.** For each town, p_j is the share of nearby fires (within 30 km) that closed exit j. Independence predicts n × Π p_j full cut-offs. We sum observed and expected counts over all towns.
5. **Uncertainty.** A bootstrap over whole fire events (1,000 resamples) gives the 95% CI. Resampling whole events accounts for one fire hitting several towns.
6. **Decision rule** (fixed in advance): PASS if R ≥ 2 **and** the lower 95% bound is > 1.

Each stage's rules were committed to git before any of its results existed. Changes made after
seeing results are logged as deviations.

## 4. Results

| Stage | Test | Observed vs expected | R (95% CI) | Verdict |
|---|---|---|---|---|
| 1 | Each town separately (217 eligible towns) | at most 1 cut-off per town | — | FAIL: too few events per town to test |
| 2 | Pooled, 2019–23 fires | 22 vs 3.3 | 6.6 (0.90–8.5) | FAIL (narrowly) |
| 2 | **Pooled, 1950–2019 fires (confirmatory)** | **24 vs 1.6** | **14.9 (3.9–31)** | **PASS** |
| 3a | Only roads cut outside the town, 1950–2019 | 20 vs 1.5 | 13.8 (3.1–29) | PASS |
| 3b | Satellite: all exits reached within 12 h, anywhere on the route | 9 vs 1.3 | 6.9 (0–12.4) | FAIL |
| 4 | Satellite: all exits reached within 12 h, within 5 km of town* | 11 vs 1.3 | 8.4 (1.9–14.4) | PASS |
| 5 | Official closure records (descriptive) | 0 of 22 cut-offs with every exit recorded closed on one day | — | no verdict |
| 6 | Public finance: do councils with cut-off towns have less own revenue? | median own-source share 68.0% vs 62.0% (10 vs 72 councils) | difference +6.0 pp (0.9 to 15.0) | NOT SUPPORTED: opposite direction |
| 7 | Social: are cut-off towns older (% aged 65+)? | median 27.7% vs 23.1% (43 vs 418 towns) | difference +4.6 pp (−0.002 to 7.0) | NOT SUPPORTED (borderline) |
| 8 | Socioeconomic change 2016→2021: Black Summer cut-off vs burned-only towns (exploratory) | median population growth 10.3% vs 4.2% (19 vs 119 towns) | difference +6.1 pp (2.2 to 12.7) | "BETTER": most likely coastal growth, not an effect of being cut off |

\*Stage 4 was designed after seeing stage 3's timing table, so it is supporting evidence, not independent confirmation.

**In plain words.** When a fire blocked at least one road out of a town, it blocked **all** of them
2.0% of the time in the historical record. Independence predicts about 0.1%. In 2019–23 the figures
were 9.6% against 1.1%.

**Robustness (stage 2, historical):**
- The ratio stays above 1 for every ring size (10, 20, 30 km), under both closure rules, and with undated fires added.
- Removing the single most influential fire (the Hylands fires of December 2001, 10 of the 24 cut-offs) leaves R = 9.4 (CI 3.2–19.3).

**Timing.**
- Timed near the town, the median gap between fire reaching the first and the last exit was about 22 hours (29 of 31 cut-offs dated).
- 11 gaps were within 12 hours and 17 within 24 hours.
- Along the whole 20 km route, the median gap was about 55 hours.
- Mogo shows the difference clearly: 1.9 hours near town, against 830 hours along the whole route.

**Closure records.** Located Live Traffic records confirm individual closures near cut-off towns
(Yowani Road at Rosedale, Araluen Road at Moruya, Wilson Drive at Hill Top). No cut-off had records
on every exit. The records have large gaps, including 30 December 2019 to 11 January 2020 when most
cut-offs happened. The Home Affairs corridor records were too coarse to place: one record matched 14 towns.

**Public finance (stage 6).**
- We tested whether councils containing towns ever fully cut off by fire have weaker finances (2018-19, before Black Summer).
- They do not. Their own-source revenue share was *higher* (68% vs 62%), and their grant dependence lower.
- This held with a fuller council list that adds the 2016-amalgamated councils: 15 vs 85 councils, +6.4 points (CI 2.2 to 13.3).
- Compared only with councils whose towns were touched by fire but never cut off, the difference was small and not clear (+2.1, CI −2.4 to 11.7).
- Exposed councils are mostly coastal and peri-urban (Shoalhaven, Eurobodalla, Lake Macquarie, Wingecarribee, Blue Mountains), with large rate bases. They manage far fewer road kilometres per resident (median 21 vs 128 per 1,000).
- The risk sits in councils that can raise their own money, not in the poorest councils. Many exits are also state highways (such as the Princes Highway), which the state, not the council, pays for.

**Who lives there (stage 7).**
- **80,061 people** live in the 43 towns where fire has cut every road out at least once (2021 Census).
- They include **23,873 people aged 65 or over**, **6,251 people who need help with everyday activities**, and **1,378 homes with no car**.
- Cut-off towns are older at the median (27.7% vs 23.1% aged 65+), but the 95% range just reaches zero, so by the pre-registered rule this is not a clear difference.
- Households without a car were, if anything, less common (2.6% vs 4.1%). Need for assistance and income were similar.
- Most of these people live in two councils: Shoalhaven (13,439 aged 65+ in 15 cut-off towns) and Eurobodalla (5,817 in 6 towns).
- Per resident aged 65+ in their cut-off towns, those councils raise about $17,000–18,000 a year of their own revenue. Councils with only one or two small cut-off towns raise $200,000–2.4 million per such resident. Council own-source revenue is a whole budget, not money for evacuation roads.

**What happened afterwards (stage 8, exploratory).**
- Towns fully cut off by Black Summer fires grew *faster* from 2016 to 2021 than towns burned but not cut off: a median of 10.3% vs 4.2%.
- Income and employment changes showed no clear difference.
- The fast growers are coastal towns and new estates (Red Head +55%, Tallwoods Village +41%) during a period of strong coastal and COVID-era migration.
- Cut-off inland or heavily damaged towns barely grew or shrank (Batlow +0.1%, Mogo −1.6%).
- This most likely reflects location, not a benefit of being cut off. Separating the two would need a 2011–2016 pre-trend or a coastal-only comparison.

## 5. Discussion

The main result is consistent across independent fire records and stricter closure rules. Mapped
fires cut all of a town's exits together far more often than independence predicts. A town with
three exits is therefore not three times as safe as a town with one, and planning that counts exits
overstates redundancy.

Timing adds nuance. Many "full cut-offs" build up over hours to days, as fire reaches one road and
then another. That matters for evacuation: it can leave a window to leave, or it can trap people who
waited. Our timing checks measure when fire first **arrived** at each road, not how long roads stayed
closed. They cannot show whether all roads were shut at the same moment. Closure-duration records
would be needed, and the records available here are too sparse.

## 6. Limitations

- **Closure is inferred** from fire maps and satellite detections, not observed. The ratios from final perimeters are upper bounds.
- **Few events.** The historical PASS rests on 24 cut-offs from 13 fire events, and the 2019–23 test on 22 cut-offs from 4 events.
- **Coverage.** Historical fire maps come from national-parks records and may miss fires elsewhere, especially before the 1990s. Satellite timing is only possible from 2002.
- **One road network.** The 2019 network is used for fires back to 1950.
- **Hotspot error.** Hotspot locations are uncertain by 375 m to 1 km, satellites pass a few times a day, and smoke and cloud hide fire.
- **Choices.** Exit routes are one shortest decomposition, and results depend on the 20 km ring and 30 km fire radius. Sensitivity runs at 10 and 30 km agree in direction.
- **Measurement only.** This study makes no causal claims and no claims about lives.

## 7. Conclusion

Counting exit roads overstates how well connected a bushfire-prone NSW town really is. Across seven
decades of mapped fires, all of a town's exits were cut together about 14–15 times more often than
chance would predict, and the result survives stricter closure rules. Satellites show these cut-offs
often unfold over hours to days rather than in a single moment, so the next step is to measure how
long exit roads stay closed.

## 8. Reproducibility

Each stage folder (`./`, `stage2/`–`stage5/`) contains `PREREGISTRATION.md`, `DECISIONS.md`,
`DEVIATIONS.md`, `RUN_LOG.md`, `README.md`, `RESULTS.md`, a one-command runner and tests.
- Every stage run twice gave byte-identical outputs (fixed seed 20260921).
- Downloaded ABS and satellite files are not in git; their URLs and hashes are recorded so they can be re-downloaded and verified.

Git history:

| Commit | What it contains |
|---|---|
| `1e8cd4f` | Stages 1–2 |
| `08fbe52` | Stage 3 pre-registration |
| `2154785` | Stage 3 |
| `f27b5c5` | Stage 4 pre-registration |
| `60329e6` | Stage 4 |
| `2851eea` | Stage 5 pre-registration |
| `e4833ca` | Stage 5 |
| `b7f0124` | Stage 6 pre-registration |
| `115641d` | Stage 6 |
| `b52d066` | Stage 7 pre-registration |
| `19b9502` | Stage 7 |
| `57e3835` | Stage 8 pre-registration |
