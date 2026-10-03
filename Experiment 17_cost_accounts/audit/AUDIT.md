# Experiment 17 audit (cost accounts)

Independent audit, 2 Oct 2026. I did not build this experiment. I re-ran the two scripts, re-did the arithmetic,
checked every source id in FINDINGS.md against the bibliography parts, and opened two web sources to check
quotes (logged as E17A-001 and E17A-002 in `bibliography/parts/exp17_audit_2026-10-02.csv`). I changed no project
file except this one. I downloaded nothing into the project.

## Summary verdict

**Mostly sound, but one high-severity issue that changes the headline household number.**

- The scripts reproduce exactly (byte-identical outputs). Every number in FINDINGS.md matches the results or simple
  arithmetic. Every cited id exists. The funder splits match the cited sources. There is no double counting
  between the insurer lines and no negative "other insured" rows. The CAT171 and Nov 2016 events map to the right
  rows. No ACM source is used. All bibliography rows have 16 columns. No data files are saved in the folder.
- **High:** the under-insurance assumption misreads its source. The Canberra 2003 shortfall figures (27%, 40%) are
  averages over *all* destroyed homes. The model treats them as averages over *under-insured* homes only and
  multiplies them by a share under-insured (50% or 80%). That halves the mid shortfall. If the source is read as
  written, the Black Summer household gap is about **A$293m (8.6%, A$118k per home)**, not A$189m (5.8%, A$76k).
  The high scenario becomes A$523m, not A$450m.
- **Medium:** (1) the "who paid" total adds losses and government transfers together, and the household line is
  gross of payments made to households; (2) the council-statement claim rests on incomplete years and leaves out
  the wide-rule figure, which goes the other way; (3) the high rebuild cost (+25% for bushfire-rated building)
  cites a source (ABCB 2009) that says 4-7%.
- Several low issues: wrong docstrings, small wording overstatements, one wrong citation, duplicate bibliography rows.

## Findings

### 1. Reproducibility: PASS
`python3 council_side.py` then `python3 summarise.py` both ran without error. All six files in `results/` are
byte-identical to the versions there before the re-run (compared with `cmp`). CHECKS.txt matches FINDINGS.md.
No `__pycache__` or other files were left behind.

### 2. HIGH: the under-insurance shortfall is applied twice (assumption `underinsured_shortfall`)
- **What the code does.** Gap per insured destroyed home = share under-insured x average shortfall:
  mid 50% x 27% = 13.5%, high 80% x 40% = 32%, low 20% x 20% = 4%.
- **What the source says.** ASIC Report 54 (E17I-022; I re-checked it as E17A-002), PDF p.12 says the homes
  destroyed in the ACT bushfires "were underinsured by 40% of the replacement cost, on average" (IDRO). PDF p.16
  says ASIC's 19 like-for-like rebuilders "were on average 27% underinsured". Both are averages over all the
  destroyed homes, or all the surveyed people. They are not averages over only the under-insured homes. So
  multiplying again by "50% under-insured" counts the share twice.
- **Effect** (I re-ran `build()` in memory with mid 0.27 and high 0.40; nothing was saved). Black Summer
  household gap: mid A$189m -> A$293m (5.8% -> 8.6% of the total; A$76k -> A$118k per home). High A$450m ->
  A$523m (11.0% -> 12.6%). Insurers' total does not change, because it is fixed by the ICA figure; only the split
  between home claims and "other insured" moves. The small-fire per-home figure (A$76k) and every council's
  household gap rise by the same ratio.
- **Fix.** Pick one of these:
  - (a) Use the Canberra averages directly as the shortfall over all insured destroyed homes: low 0.04 (or a
    sourced lower value), mid 0.27, high 0.40. Then drop the 50% / 80% factor.
  - (b) Keep ICA's Black Summer "about 50% under-insured" (E17I-073, verified as E17A-001). Pair it with a
    shortfall measured *among under-insured homes only*, from a source that reports that figure. Note the two
    averages come from different events.

  Then update ASSUMPTIONS.csv (note column), re-run, and update FINDINGS.md: the table, the per-home figures, the
  estimator section and the council paragraph. Also note in Limits that the ASIC 27% rests on 19 homes.

### 3. MEDIUM: the "Total counted" adds losses and transfers, and the household line is gross
- The total (A$3,284m) and the shares add three different kinds of money. (a) Losses carried by households and
  insurers. (b) Government spending on clean-up. (c) Government transfers and programs. Part of (c) goes *to*
  the same households: the Disaster Recovery Payment and Allowance, A$266m, is larger than the whole mid household
  gap. The NSW Disaster Welfare Rebuild Program (A$26m, E17I-077) pays part of exactly the uninsured rebuild gap.
  BLER and BSBR fund new community and economic projects, not repairs of fire losses.
- The household line counts only the uninsured *building* gap. The insurer line counts everything insured
  (contents, cars, business, damaged homes). The comparison is lopsided by design, so the household share is
  biased low. FINDINGS lists these items under "not counted", but the shares are still presented as "who carried
  the cost".
- **Fix.** In FINDINGS.md:
  - Show two tables, or two clearly labelled blocks: a loss account (household gap, insurers, clean-up by funder)
    and recovery spending (DRP and programs by funder). The CHECKS output already has `loss_account` and
    `recovery_money`.
  - Call the combined figure "losses plus government outlays (gross, not net)".
  - Say the household share is before DRP, the welfare rebuild program and charity, and covers buildings only.
  - Optionally move the A$26m welfare rebuild money from households to NSW in the mid case.
  - In the estimator section, say the A$1.3m per home is not a cost per home.

### 4. MEDIUM: the council-statement comparison (A$49.7m vs A$74.3m) is over-read
- FINDINGS says fire-labelled grants "rose by A$49.7m over the fire year and the next two". In fact only 13 of the
  23 councils have all three post-fire years. The other 10 have two (FY2021-22 is missing). They include the
  largest: Bega Valley, Eurobodalla, Snowy Valleys, Clarence Valley and Shoalhaven. Their baseline is also a single
  pre-fire year (FY2018-19), because FY2017-18 is missing. Example: Bega's fire lines were A$0.7m in FY2019-20 and
  A$9.1m in FY2020-21, with FY2021-22 unknown.
- With the wider Experiment 9 rule (adds "natural disaster" lines), the same councils show **A$80.9m**. That is
  *more* than the A$74.3m of NBRA, BCRRF and EPA money. FINDINGS does not report this figure.
- So the sentence "so a lot of recovery money is booked under other headings: the statement figure is a lower
  bound" is only partly supported. The gap can come from missing years as much as from labels. The capital-spending
  measure (`stmt_capex_extra_aud`, A$-465.5m in total, driven by Central Coast) is also computed but not mentioned.
- **Fix.** Reword:
  - "A$49.7m under the strict rule and A$80.9m under the wide rule, over up to three years; 10 of 23 councils
    lack FY2021-22."
  - Drop "a lot of ... booked under other headings", or support it with the label evidence. Shoalhaven shows a fall
    under the strict rule and books disaster money under "natural disaster" lines.
  - Mention the capital-spending result in one line, or say it was not used.

### 5. MEDIUM: the high rebuild cost (+25% for bushfire-rated building) is mis-cited
- FINDINGS: "A$430,000 (adds about 25% for bushfire-rated building [E17R-055, E17R-050])". But E17R-050 (ABCB 2009
  RIS) gives BAL extra costs of A$11.5k-A$20.9k on a base house of about A$284k, which is **4-7%**. That is what
  ASSUMPTIONS.csv itself says. Only the IAG fact sheet (E17R-055) supports something like 25% (A$86k), and its notes
  say the label-to-value mapping is ambiguous. Most destroyed homes would also not be rebuilt at the highest BAL
  levels.
- **Fix.** In FINDINGS, write "about 25% (IAG fact sheet, highest-risk sites; ABCB 2009 gives 4-7%)". Better, set
  high to about mid + 7% to 10% and keep 25% as a sensitivity. Either way, cite E17R-050 as a source for the lower
  figure, not for 25%.

### 6. Accounting logic: PASS, with low notes
Checked and correct:
- **Household gap formula.** `rebuild - rebuild x (1-u) x (1-g)` = `rebuild x (u + (1-u) g)`. Re-derived:
  low 8.8% of A$260k = A$23k; mid 22.2% of A$344.3k = A$76k; high 42.2% of A$430k = A$181k.
- **A2 "other insured".** It is the ICA event loss times the event's home share, minus the modelled insurer home
  payouts. So insurers in total always equal the ICA figure: no double count between A1 and A2. No row is negative
  (CHECKS).
- **Funder splits match the sources.**
  - BLER 50/50 (E17-015 quote, ANAO Table 4.4 E17G-008).
  - BCRRF joint under the DRFA (E17-018), 50/50 assumed (DRFA cl. 4.4.3, E17G-026).
  - Green waste joint DRFA (E17-020), 50% (75% high).
  - Landfills NSW only (E17G-045 quote; code puts it in the NSW line only).
  - NBRA and BSBR Commonwealth.
  - Clean-up 50:50 (E17R-018 quote).
  - DRP Commonwealth (E17G-011).
- **Apportionment.** Clean-up and the insurer event loss are split by homes destroyed. DRP is split by destroyed +
  damaged. Program money is measured per council. All of this is stated in FINDINGS.
- **Scenarios.** All-low and all-high together; ranges are the min-max over the three scenarios. Stated honestly.
- **Rebuild index by year.** The ABS keys are the year the FY *ends* (2020 = FY2019-20, matching E17R-038). The
  code uses `ABS[F+1]`, where F is the FY starting in July of year F. So it is the cost level of the fire's own FY.
  Black Summer: F=2019 -> index 1.000. Tathra: F=2017 -> 323.7/344.3 = 0.940. Feb 2017: F=2016 -> 0.897. This
  matches "FY2019-20 dollars".
- **Event mapping.** The CAT171 (ICA, NSW bushfires 12-18 Feb 2017, A$33.5m) rows are RAA r17 (Mid-Western, Sir
  Ivan) and r23 (Sir Ivan + Hickeys Creek: Warrumbungle 35 homes, Kempsey 2, Mid-Western 1). That is correct; all
  A$33.5m goes to r23, because r17 has no known homes. The Nov 2016 undeclared event (6-8 Nov 2016, A$1.0m) maps
  to r06, r07 and r08 (Kempsey, Tenterfield, and the Lone Pine fire rows), which started 4-5 Nov 2016. That is
  correct; it is split equally, since no homes were destroyed. Tathra CAT182 (A$82.5m, NSW + Vic) -> NSW1718-20
  Bega Valley 65 homes: correct.

Low notes:
- (a) The `rebuild_index` docstring says "FY after the fire start". It is the fire's own FY; the code is right.
  The `build_accounts.py` header says landfills are "joint, 50:50" (the code correctly treats them as NSW only).
  It also lists a "B3 council asset restoration" line that is not implemented. Fix the docstrings.
- (b) FY2015-16 and FY2017-18 ABS values are interpolated, although the same BA_GCCSA series covers them. Compute
  the real values if the data are read again.
- (c) RAA r26 (Singleton, Carrowbrook fire, started 11 Feb 2017) is plausibly part of CAT171 but is not in the
  group. This has no numerical effect (its homes are unknown). AGRN 880 (Jul 2019, 3 homes) is not linked to
  CAT193/195. This is tiny.
- (d) Clean-up mid A$265m is cash received in 2019-20, and A$82.2m was still prepaid in June 2021 (E17R-072). The
  mid figure may overstate actual spending. Say so in FINDINGS, not only in ASSUMPTIONS. Also possible: overlap
  between clean-up tipping and the NSW landfill program (small).

### 7. council_side.py: PASS, with notes
- **Labels.** The strict regex matches bushfire, RFS, BLER, BSBR, NBRA and BCRRF lines. Flood and storm lines are
  excluded; "Storm/flood/fire damage" is dropped, which is conservative. Fire councils' "Bushfire and emergency
  services" lines sit under `disaster_grant_*`, while comparison councils have them under
  `bushfire_emergency_services_grant`. Including that item only for comparisons is correct harmonisation.
- **Windows and comparisons.** Baseline is FY F-2 and F-1; post is FY F to F+2. The `fy` "2019-20" is read as F=2019,
  correct. Comparison councils must be unburned (under 0.5% burned) in F-2..F+2. This leaves 70-71 councils for
  OLG, and 21 of 24 statement councils for Black Summer.
- **Units.** `value_aud` is in A$ (total expenses median about A$53m). The share-of-expenses change times the
  pre-fire expenses gives A$. This is fine.
- **Missing years.** Rows with missing post years are summed over fewer years; see finding 4. The `_nyears` column
  records it, but FINDINGS does not use it.
- **OLG year label.** This is inherited from Experiment 7 and not independently verified. It is a memo only, so
  low.

### 8. Overstatement and honesty: mostly PASS
- FINDINGS clearly says council figures are "an ALLOCATION, not a measurement", that totals are lower bounds, and
  that the council net-cost slope is not detected (memo only). This is good.
- (Low) "the household share is about 5-7% in every council by construction" is not accurate. Among the 34
  councils with homes destroyed it runs from 1.4% to 6.5% (median 5.1%). It is lower where program money is large.
  Fix the wording.
- (Low) The "What is NOT counted" list should add DRFA Category B restoration of council and state assets (roads,
  bridges, parks) and Category A relief. The A$81.7m is mentioned elsewhere but is not in this list.
- (Low) "Fires with no ICA event (2018, 2022-2024)" also includes Sept 2017 (NSW1718-05) and Jul 2019 (AGRN 880).
- (Low) "No downloads". No files were saved, but data were read in memory from the ABS API (E17R-038, 792 obs),
  the NEMA table (E17G-039) and curl streams, and WebFetch auto-cached PDFs outside the project. Say "no files saved
  to the project".

### 9. Citations: PASS for existence; four mis-citations or weak supports (low, except finding 5)
- All 53 ids cited in FINDINGS.md, ASSUMPTIONS.csv and the scripts exist. None are missing.
- (Low) The RAA "A$103.4m paid in 2019-20 for all disasters [E17-033]" figure is supported by the same report, but
  the logged quote is in **E17G-061**, not E17-033 (whose quote is about the A$265m). Cite E17G-061.
- (Low) The "Commonwealth only" funder for NBRA and BSBR: E17-022 has an empty quote, and E17G-039's quote does
  not name the funder. Add a quote stating Commonwealth funding.
- (Low) "the council dataset was withdrawn" [E17-009] and "about 2 MB" [E17R-033, E17R-036] are not in the logged
  quotes. Add them or drop the words.
- **Verified in this audit:** E17I-033 / E17I-073 (ICA "about 50 per cent ... under-insured", 9,478 claims,
  A$131,848, A$640m), confirmed on the ABC page (E17A-001). E17I-022 is confirmed, but it supports finding 2's
  reading (E17A-002).
- (Low) Duplicate rows for the same source break the README "one row per distinct source" rule: E17I-033 = E17I-073;
  E17I-021 = E17I-022; E17I-077 = E17R-023; E17-033 = E17G-061. Merge them at consolidation.

### 10. Rule compliance: PASS
- **ACM.** All 20 ACM-host or `/story/NNNNNNN/` URLs in the four parts are marked "excluded: ACM (AI-use ban)" and
  "not opened". No ACM source is cited. (Low) `stockjournal.com.au` (E17G-032) is not in `acm_hosts.txt`; add it.
- **16 columns.** Every row in all four parts (34 + 73 + 83 + 89) and in the audit part has 16 fields.
- **No downloaded files in the folder.** It holds only 4 .py, 2 .md, 1 .csv, 6 results (.csv/.txt) and this audit.

## Numbers I re-derived (all match FINDINGS unless noted)

| Claim | Re-derivation |
|---|---|
| Homes 2,480 (871) | sum of `homes` over 50 rows; 0 unknown |
| Rebuild A$854m (645-1,066) | 2,480 x 344,300 = 853.9m; x 260,000 = 644.8m; x 430,000 = 1,066.4m |
| Household gap 22% / 9% / 42% | 0.10 + 0.9 x 0.135 = 22.15%; 0.05 + 0.95 x 0.04 = 8.8%; 0.15 + 0.85 x 0.32 = 42.2% (but see finding 2) |
| A$76k / 23k / 181k per home | 344.3k x 22.15%; 260k x 8.8%; 430k x 42.2% |
| Insurers NSW A$1.88bn | 2.32bn x 81% = 1.879bn; + 0/6.75/13.5m (CAT193) = 1,880 / 1,887 / 1,894 |
| Insurer home payouts A$665m | 853.9 x 0.9 x 0.865 = 664.8m; other insured 1,886.75 - 664.8 = 1,222m |
| ICA home-claims check A$1.0bn | 9,478 x 131,848 x 0.81 = 1,012m |
| Programs A$677m | NBRA 43.5 + BSBR 154.9 + BLER 417.7 + BCRRF 7.25 + green waste 31.5 + landfills 22.1 = 676.9m |
| Commonwealth A$825m (750-1,102) | DRP 265.9 + clean-up 132.5 + programs (43.5 + 154.9 + 0.5 x 424.9 + 0.5 x 31.5 = 426.6) = 825.0; low 233.8 + 90 + 426.6 = 750.4; high 265.9 + 401.5 + 434.5 = 1,101.9 |
| NSW A$383m | 132.5 + (676.9 - 426.6) = 382.8 |
| Total A$3,284m; shares 5.8 / 57.5 / 25.1 / 11.7% | sum of payers; CHECKS |
| Recovery money A$943m | 676.9 + 265.9 |
| Per home 1.32m / 76k / 761k / 333k / 154k | totals / 2,480 |
| Clean-up low A$180m | 50,000 x 3,600 |
| Tathra 71% NSW; insurers A$59m | 65 / 91 = 71.4%; 82.49 x 0.714 = 58.9m |
| Council memo A$92m | 58 x (homes per 1,000 / 10) x pop x 3, summed over 50 rows = 92.1m (low -599, high +716) |
| Statements A$49.7m vs A$74.3m | reproduced; wide rule A$80.9m; 13 of 23 councils have all 3 years |
| Central Coast -A$243m | -242.6m |
| Govt lines about 1/4 of A$4.4bn | (825 + 383) / 4,400 = 27% |
| Unknown-home rows add about 18 homes | sum of v3 estimate x dwellings / 1000 over 83 rows = 18.0 |
| Other fires 14 events, 167 homes, A$123.8m | CHECKS; Tathra 63.6 (42.6-93.6); Feb 2017 36.1 |
| Household share by council | 1.4% to 6.5% (not "5-7% in every council") |
| Alternative shortfall (finding 2) | mid household A$293m (8.6%), A$118k per home; high A$523m (12.6%) |

## Responses by the Experiment 17 session (2 Oct 2026, after this audit)
- Finding 2 (high): FIXED. `underinsured_shortfall` is now the average over all insured destroyed homes: low 0.135
  (50% x 27%), mid 0.27, high 0.40. Black Summer household gap is now A$293m mid (A$115m to A$481m), A$118k per home.
- Finding 3 (medium): FIXED. FINDINGS now shows a loss account and a recovery-money account separately
  (results/BLACK_SUMMER_ACCOUNT.csv; who_paid() returns both); the combined figure is labelled gross; household
  payments (A$266m) and the A$26m uninsured rebuild program are discussed.
- Finding 4 (medium): FIXED. Strict A$49.7m and wide A$80.9m both reported, with 13 of 23 councils having all three
  years; "booked under other headings" removed; capital spending noted as not used.
- Finding 5 (medium): FIXED. High rebuild cost now mid + 15% (builder 10-15% [E17R-064]; ABCB 4-7% [E17R-050]);
  IAG +25% kept as a sensitivity in CHECKS.txt (high household gap A$523m).
- Low items: docstrings fixed; household share by council now stated as 2.0% to 9.8% (median 7.6%); "not counted"
  list extended (DRFA asset restoration, A$26m program); A$103.4m now cited to E17G-061; NBRA/BSBR funder cited to
  E17-019 and E17G-008 (re-check of NEMA/ANAO pages timed out, logged E17-035/036); "no downloads" reworded to "no
  files saved to the project"; stockjournal.com.au added to bibliography/acm_hosts.txt. Duplicate bibliography rows
  (E17I-033/073, E17I-021/022, E17I-077/E17R-023, E17-033/E17G-061) left for the consolidation step to merge.
  Interpolated FY2015-16 and FY2017-18 rebuild levels kept (noted in Limits).

## Re-check by the auditor (2 Oct 2026, after the responses): PASS
Re-ran both scripts twice; all results files byte-identical; every number in the rewritten FINDINGS.md matches the
results. The high finding and the three medium findings are resolved. Two low items remained and were handled in
FINDINGS.md: (1) NBRA/BSBR Commonwealth funding is now marked "funder inferred, not quoted"; (2) the low under-insurance
shortfall (0.135) is now labelled as using the rejected reading, i.e. a generous lower bound.
