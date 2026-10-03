# Experiment 7, Day 11: council cost with and without reimbursement. Rules fixed first

Written 2026-10-02 before any Day 11 number. Locked in `LOCK_DAY11.txt`. Data already in the project (lga_year).

## Outcomes (A$ per resident, yearly, FY 2014-15 to 2024-25)
- G gross cost: total expenses from continuing operations / population.
- R reimbursement and other grants: grants & contributions per resident (all grants, incl. capital).
- N net cost borne by the council: G - R.
- Where capital grants exist (FY 2019-20 on): R_op = R - capital grants per resident; N_op = G - R_op (secondary).
Caveat fixed in advance: capital (rebuilding) spending is not in G, while capital grants are in R, so N understates the
burden when capital grants rise; N_op avoids this but only covers 2019-20 on.

## Design (Day 1 V2b counterfactual)
Council effects + Metro/Regional/Rural x year effects fitted on clean council-years (Day 1 rules). For each of the 218
rows: change = mean residual in FY F, F+1, F+2 minus mean residual in FY F-3..F-1 (A$ per resident).
Pre-trend = residual F-1 minus mean of F-3, F-2.
Dose: homes destroyed per 1,000 dwellings (DL_FILLED v2), slope per 10 homes per 1,000, OLS with council-cluster
bootstrap (2,000, seed 20261002). Secondary dose: share of council burned (per 10 pp), all rows.
"Detected" = 95% CI excludes 0 and pre-trend CI includes 0. Expected: G up, R up; N is the question.
