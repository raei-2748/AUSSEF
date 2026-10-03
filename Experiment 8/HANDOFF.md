# Experiment 8 handoff: disaster -> socioeconomic mechanisms (from the Experiment 7 session, 2 Oct 2026)

## Why this exists
Ray (high-school researcher, AUSSEF report due 11 Nov 2026; mentor Bowen) is studying NSW bushfire socioeconomic
impacts (council x fire panel, 218 rows, 96 fires, 2015-25; framework Y = DL + IL + FP + SL; X groups; RF + importance).
Experiment 7 (`../Experiment 7/README.md`, FINDINGS_DAY1..DAY10.md) showed: only direct loss (homes destroyed) tracks
fire size; income, unemployment, welfare, businesses, rents, population, council finances show no detectable effect at
council or SA2 level (upper bounds stated), except: area total income -1.6% two years later where homes burned (fewer
earners), and council grants rise with homes lost. Pre-fire housing-loss map AUC 0.91 on Black Summer; rapid post-fire
estimate (homes inside the fire) cut error 88%.

## Ray's new direction (his reasoning)
Blunt annual, whole-area regressions can't find patterns. Go mechanism-first:
1. Use many search agents to collect HOW disasters affect people's socioeconomic status: academic papers, government and
   agency reports, inquiries (e.g. NSW Bushfire Inquiry, Royal Commission into National Natural Disaster Arrangements),
   news articles and first-person accounts / interviews / surveys (e.g. Beyond Bushfires, ABC, local news).
2. Build a mechanism table: each mechanism, its pillar (DL / IL / FP / SL), how often it is reported (frequency across
   sources, split by source type), direction, who is affected, time scale (days / months / years), evidence strength.
   Examples to seed (not exhaustive): workplace / shop / facility destroyed -> job loss (also for workers living
   elsewhere: spillover); job and occupational mobility costs; displacement -> higher rent / overcrowding / moving far;
   insurance gaps, underinsurance, premiums; debt and savings drawdown; tourism and farm income loss; supply-chain
   disruption; health and mental health; domestic violence; education disruption; unpaid recovery work; government and
   council cost shifting and OPPORTUNITY COST of recovery spending (money that could have gone elsewhere).
3. For each mechanism: what public data could measure it, at what time scale and geography (aim for finer pieces:
   monthly/quarterly, SA2/SA1, workplace zones), and whether Experiment 7 already tested it (and the result).
4. Then propose (do NOT run yet) 2-3 targeted tests that break data into smaller time/space pieces matched to the fire
   footprint and date, filling gaps with transparent estimates where needed (as the housing-loss estimate did).
   Candidates already noted: jobs located inside fire outlines (ABS Census destination-zone working population +
   journey-to-work) -> unemployment in workers' home areas; BOCSAR monthly domestic violence by LGA.

## Rules (from Ray, keep them)
- Ray reads Chinese; never translate forwarded Chinese. Plain simple English in replies.
- Never use or cite ACM = Australian Community Media regional newspapers (Canberra Times, Bega District News, Newcastle Herald, The Land, etc.; host list in bibliography/acm_hosts.txt): their terms bar AI use. ABC is fine.
- Downloads: list file name, source and size and get Ray's OK first (except trivially small reference pages).
- Any new statistical test: write a PRESPEC and hash-lock it before running; label later changes as deviations.
- Do not modify the master workbook or other experiments' folders. Don't commit unless Ray asks.
- Don't say "no effect"; say "no detectable effect above X". Don't propose more fire collection.

## Stay inside Bowen's direction (Ray, 2 Oct)
This is NOT a new direction. It enriches Bowen's framework: composite Y = DL + IL + FP + SL, X variable groups,
council x fire panel, random forest + variable importance, severity tiers, pre-fire risk score/map. The mechanism
table explains and fills the pillars (what each pillar should measure and why), and any new fine-grained measures
become better Y indicators or X variables inside that same framework.

## Main Y (Ray, 2 Oct, later)
Bowen has NOT agreed to make homes destroyed the main Y. The main Y stays the composite DL + IL + FP + SL.
Homes destroyed is the DL pillar. The goal of the mechanism work is to find better, fire-matched indicators for IL, FP
and SL so the composite Y measures real fire impact.
