# Experiment 17 findings: who carried the cost of each fire (cost accounts)

2 Oct 2026 (revised after the independent audit, `audit/AUDIT.md`). Descriptive accounting, no statistical test.
Scripts: `council_side.py` -> `build_accounts.py` -> `summarise.py`. Assumptions (low / mid / high, each with sources):
`ASSUMPTIONS.csv`. Tables in `results/`. No files saved to the project (some sources were read online only).
Source ids in [brackets] are rows in `bibliography/parts/exp17_*_2026-10-02.csv` (E17-: main session; E17R-: rebuild
cost; E17I-: insurance gap; E17G-: government payments; E17A-: audit).

## The idea
Area averages hide household harm. Instead, follow the money: for each fire, add up what was lost and what was paid
out, and who paid: households (the uninsured part of rebuilding their home), insurers, the Commonwealth, the NSW
Government and councils. Losses and government recovery money are kept in two separate accounts, because some
recovery money goes back to the same households (adding them would count a transfer as a cost).

## Black Summer, NSW (AGRN 871, 50 councils, 2,480 homes destroyed in the panel [E17-026]; official 2,476 [E17-015])

### 1. Loss account: what was destroyed or had to be cleaned up, and who paid for it

| Who paid | Mid, A$m | Low to high, A$m | Share (mid) | Share, low / high scenario |
|---|---|---|---|---|
| Households: uninsured part of rebuilding destroyed homes | 293 | 115 to 481 | 12.0% | 5.3% / 15.1% |
| Insurers (everything insured, NSW part) | 1,887 | 1,880 to 1,894 | 77.2% | 86.4% / 59.6% |
| Commonwealth: half of clean-up | 133 | 90 to 402 | 5.4% | 4.1% / 12.6% |
| NSW Government: half of clean-up | 133 | 90 to 402 | 5.4% | 4.1% / 12.6% |
| **Loss account total** | **2,445** | **2,175 to 3,178** | | |

### 2. Recovery money: paid by governments after the fire

| Who paid | Mid, A$m | Low to high, A$m | Share (mid) |
|---|---|---|---|
| Commonwealth (household payments, NBRA, BSBR, half of BLER and BCRRF, half of green waste) | 693 | 660 to 700 | 73.5% |
| NSW Government (other half of BLER, BCRRF, green waste; all of council landfills) | 250 | 242 to 250 | 26.5% |
| **Recovery money total** | **943** | **911 to 943** | |
| of which paid to households (Disaster Recovery Payment + Allowance + child payments) | 266 | 234 to 266 | 28.2% |

Both accounts together: A$3.39bn mid (A$3.09bn to A$4.12bn). This is gross (losses plus government outlays), not a
net cost to society. Per home destroyed (mid): household gap A$118k; insurers A$761k; Commonwealth A$333k; NSW
A$154k; both accounts A$1.37m.

**Reading.** Insurers carried most of the measured loss (about three quarters). Households carried about one eighth
(A$293m), which is about the same size as the Disaster Recovery Payments paid to NSW households (A$266m). But those
payments are for immediate needs and went to many more people than those who lost homes, so they do not cancel the
rebuild gap for the households that had it. Governments added about A$0.9bn of recovery programs on top, mostly
Commonwealth money.

### What is inside each line
- **Homes:** 2,480 homes x rebuild cost A$344,300 (ABS average value of a new house approved in Rest of NSW,
  2019-20; building only, no land) [E17R-038, E17R-040]; low A$260,000 (NSW program to rebuild uninsured homes: A$26m
  for up to 100 homes [E17I-077]); high A$396,000 (+15% for bushfire-rated building: a builder says BAL-40 "added
  about 10-15 per cent" [E17R-064]; ABCB 2009 gives 4-7% [E17R-050]). Total A$854m (A$645m to A$982m). With an
  insurer's +25% figure instead (IAG fact sheet, ambiguous [E17R-055]) the high household gap would be A$523m, not
  A$481m.
- **Household gap per destroyed home:** 10% of destroyed homes uninsured (ICA to the Senate: "perhaps 10 or 11 per
  cent" [E17I-064, E17I-009]; range 5-15% [E17I-038, E17I-024, E17I-031]). Insured homes were on average 27% short of
  the rebuild cost (ASIC survey after the Canberra 2003 fires, only 19 homes [E17I-022, E17A-002]); high 40% (Canberra,
  insurance ombudsman [E17I-022]); low 13.5% (ICA: about half of Black Summer homes were under-insured [E17I-073,
  E17A-001], times 27%; this low end treats 27% as the gap among under-insured homes only, the reading the audit
  rejected, so it is a generous lower bound). Result: households carry 34% of the rebuild cost (A$118k per home); range 18% (A$46k) to 49%
  (A$194k).
- **Insurers:** ICA catastrophe loss, NSW part A$1.88bn (81% of A$2.32bn) [E17-027, E17I-029], plus 0-100% of the
  Sept 2019 NSW/QLD event (A$13.5m) [E17-008]. About A$561m of this is our estimate of payouts for destroyed homes;
  the other A$1.33bn is contents, cars, businesses, farms and damaged homes. Check: ICA's home-building claims
  (9,478 x A$131,848 [E17I-073]) x 81% = about A$1.0bn, above our A$561m as it should be (it includes damaged homes).
- **Clean-up of destroyed properties (government-run, 50:50 Commonwealth and NSW [E17R-018]):** mid A$265m, the money
  Public Works Advisory received in 2019-20 [E17-033]; some of it was still unspent in June 2021 (A$82.2m prepaid
  [E17R-072]), so mid may be high. Low A$180m (about A$50,000 x 3,600 properties [E17R-031, E17R-024]); high A$803m
  (funding allocated [E17R-012]). No audited final cost was found; this is the widest range.
- **Household payments:** Disaster Recovery Payment + Allowance for "NSW Bushfires - September 2019", A$233.8m, plus
  A$32.2m child payments, as at 5 July 2020 (Commonwealth) [E17G-011].
- **Programs** (amounts per council from the master workbook [E17-007]; A$677m in the 50 panel councils, the same as
  Experiment 7 Day 10 [E17-004]): NBRA council package A$43.5m and Black Summer Bushfire Recovery grants A$154.9m are
  Commonwealth-agency programs (funder inferred, not quoted: the NBRA release comes from the Commonwealth minister and
  Prime Minister [E17-019]; both are in the ANAO audit of the Commonwealth recovery agency [E17G-008]); BLER A$417.7m, 50% each [E17-015, E17G-008]; BCRRF
  A$7.2m, joint [E17-018], 50/50 [E17G-026]; EPA green waste A$31.5m, joint [E17-020] (Commonwealth 50%, 75% in the
  high case [E17G-026]); EPA council landfills A$22.1m, NSW only [E17G-045].

## By council (Black Summer): `results/BLACK_SUMMER_BY_COUNCIL.csv`
Largest (both accounts, mid): Eurobodalla A$616m (510 homes), Bega Valley A$571m (467), Shoalhaven A$357m (285),
Snowy Valleys A$300m (193), Clarence Valley A$230m (168). Uninsured household gap: Eurobodalla A$60m (A$24m to A$99m),
Bega Valley A$55m (A$22m to A$91m), Shoalhaven A$34m (A$13m to A$55m).

**Important:** most council figures are an ALLOCATION, not a measurement. Insurer losses, clean-up and household
payments are known only for NSW as a whole and are split by homes destroyed (household payments by homes destroyed +
damaged). Only the program money (BLER, BSBR, NBRA, BCRRF, EPA) is truly measured per council; it is why the
household share varies between councils (2.0% to 9.8% of the combined total, median 7.6%, 34 councils with homes
destroyed): it is lower where program money is large (Snowy Valleys: A$91m of programs for 193 homes).

## Councils' own share: not measurable
- Audited statements (23 Black Summer councils [E17-011, E17-012]): fire-labelled grants rose by A$49.7m (strict
  label rule) or A$80.9m (wider rule, adds "natural disaster" lines that can include flood money) over the fire year
  and up to two more years, compared with unburned councils. Only 13 of the 23 councils have all three years; 10
  (including Bega Valley, Eurobodalla and Snowy Valleys) lack 2021-22. For comparison, NBRA, BCRRF and EPA money
  paid to the same councils was A$74.3m. So the statements are consistent with the program money, but they cannot
  separate council-paid costs from passed-through grants. Capital spending changes were computed but not used
  (dominated by large councils' own trends; COUNCIL_SIDE.csv).
- Council damage estimates exist for very few councils: Bega Valley A$20.5m, Eurobodalla A$10.0m (14 bridges only)
  [E17-016, E17-017]. In 2019-20, NSW councils reported A$81.7m of eligible council asset repairs, for all disasters
  that year (fires, storms, floods) [E17-016]. Under the funding rules the Commonwealth pays 50% of these repairs
  between a state's two thresholds and up to 75% above the second [E17G-026]; councils pay only what is not eligible.
- Net cost borne by councils (spending minus grants) was not detected in Experiment 7 Day 11: +A$58 per resident per
  year per 10 homes per 1,000 dwellings, 95% CI -377 to +451 [E17-005]. Applied to Black Summer this would be about
  A$92m over three years, with a CI that includes zero; memo only, not in the accounts.
- The OLG all-grants measure is too noisy to use: it includes developer contributions and swings by A$100m+ in large
  growth councils (e.g. Central Coast -A$243m) [E17-025]. Kept in COUNCIL_SIDE.csv only.

## Other fires (14 events with homes destroyed, 167 homes): `results/SUMMARY_BY_FIRE.csv`
- Only homes and insurance can be counted. No household payment or program totals were found for these events (no
  Disaster Recovery Payment activation found for Tathra 2018 or Sir Ivan 2017 [E17G-048, E17G-049, E17G-071,
  E17G-073]). So these accounts are incomplete and their household shares are not comparable with Black Summer.
- Tathra 2018 (65 homes): about A$66m (A$44m to A$94m); insurers A$59m = the NSW part of the Tathra + south-west
  Victoria catastrophe (A$82.5m) [E17-008], split 71% to NSW by homes destroyed (65 vs 26 [E17-030, E17-031]). NSW
  also committed up to A$10m for asbestos clean-up [E17G-049], not added (a commitment, not spending).
- Sir Ivan and other February 2017 fires (38 homes): about A$38m, mostly the ICA loss of A$33.5m [E17-008].
- Events not in the ICA list (Sept 2017, 2018, July 2019, 2022-2024; 1-32 homes each): homes only, each under A$11m.

## What is NOT counted (so the accounts are lower bounds)
Firefighting and emergency response; restoration of council and state assets (roads, bridges, parks) under the
disaster funding arrangements, beyond the A$81.7m memo above; farm losses (fencing, livestock, pasture) except what
was insured; business income and tourism losses; uninsured contents, cars and damaged homes; temporary housing beyond
the Disaster Recovery Payment; health and environment; donations (charities raised about A$640m nationally
[E17I-033, E17A-001]); RAA disaster relief grants to farmers and small businesses (A$103.4m paid in 2019-20 for all
disasters [E17G-061]); the NSW rebuild program for uninsured low-income owners (A$26m [E17I-077]; it would move a
little of the household gap to NSW); the higher rents seen in Experiment 12. For scale: NSW and the Commonwealth
committed A$4.4bn to Black Summer response, recovery and preparedness in NSW [E17-015]; the government lines counted
here (A$1.2bn mid) are about a quarter of that.

## For the fire-to-funding estimator in the report
Per home destroyed (Black Summer, mid, 2019-20 dollars): household rebuild gap A$118k (A$46k to A$194k); insurers
about A$760k (homes and everything else insured); Commonwealth about A$330k; NSW about A$150k. The A$1.37m total is
losses plus government outlays, not a cost per home. For a small fire with no catastrophe declaration and no recovery
programs, only the homes line applies: about A$344k rebuild cost per home (2019-20 dollars), of which households about
A$118k. Insurer, government and total per-home ratios from Black Summer include very large non-home losses and
programs, so they should not be applied to small fires.

## Limits
- The under-insurance shortfall comes from Canberra 2003 (ASIC's 27% rests on 19 homes). No Black Summer figure was
  found for the average shortfall or the total uninsured housing loss; the Royal Commission "have not obtained
  rigorous estimates on underinsurance" [E17I-038].
- Rebuild cost is a NSW-regional average, not council-specific. ABS value of approvals by council exists from 2018-19
  [E17R-033, E17R-036]; not downloaded (would need Ray's OK). It would refine council values only.
- Homes destroyed are unknown in 83 of 218 rows (estimated zeros or missing in Experiment 6); estimates for those rows
  add about 18 homes [E17-026].
- Household payments are event-level only: the council-level payments dataset is no longer online and its data start
  in April 2020 [E17-009] (Experiment 14 checked it).
- Insurer payouts and government clean-up are counted separately; some policies also cover debris removal (possible
  small double count). FY2015-16 and FY2017-18 rebuild cost levels are interpolated.
