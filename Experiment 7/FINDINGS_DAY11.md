# Experiment 7, Day 11: council cost with and without reimbursement

Date: 2 Oct 2026. Rules locked first: `PRESPEC_DAY11.md` (LOCK_DAY11.txt). Script: `day11_council_net_cost.py`;
results `results/DAY11_NET_COST.json`. Data already in the project.

Per 10 homes destroyed per 1,000 dwellings, change over the fire year and next 2 years vs the 3 years before,
relative to similar councils (A$ per resident):

| Measure | Estimate | 95% CI | Councils with >= 5 homes lost per 1,000 (14) vs rows with none |
|---|---|---|---|
| Gross cost (total operating expenses) | +115 | -82 to +303 | +173 vs +85 |
| Grants received (all) | +56 | -295 to +386 | +12 vs -93 |
| Net cost borne (expenses - grants) | +58 | -377 to +451 | +161 vs +180 |

None detected (pre-trends pass). The operating-only versions (capital grants removed) could not be estimated:
capital grants are published only from 2019-20, so Black Summer councils have no "before" years (23 usable rows).

## Reading
- Spending per resident rose a little more in the hardest-hit councils (about A$90 per resident more than
  councils with no homes lost), but this is within normal year-to-year swings.
- Net cost borne is about the same in hard-hit and unaffected councils, consistent with reimbursement covering most
  of the extra spending, but not proven.
- Day 10 found grants clearly higher in the year after the fire (+A$330 per resident per 10 homes per 1,000). Over a
  3-year average the grant rise is diluted, which fits a one-off reimbursement spike.
- Limits: rebuilding (capital) spending is not in operating expenses; council budgets swing by hundreds of dollars per
  resident a year; most fires destroy few homes.
