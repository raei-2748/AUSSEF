# Experiment 7, Day 9: longer timeline (up to 5 years) and a sharper dose. Rules fixed first

Written 2026-10-01 before any Day 9 number. Locked in `LOCK_DAY9.txt`. No new downloads.

## Dose (sharper)
H[s,t] = share of the SA2's dwellings (Census 2021 mesh blocks, area-weighted) inside the union of fire outlines
that started in financial year t (no buffer). This is the quantity that predicted homes destroyed on Day 8.

## Outcomes (annual SA2 panel, financial years; quarterly series averaged within the FY)
- Unemployment rate, unsmoothed (panels/sa2_unemployment.parquet), FY 2015-16 to 2024-25.
- Income-support recipients per 1,000 (panels/sa2_welfare.parquet; codes unchanged; pop >= 100), FY means.
- Business count, log (panels/sa2_businesses.parquet), June y assigned to FY y-1 (the FY it ends).
- Income: log total income and log median income (Day 5 panel), FY 2015-16 to 2021-22 (horizon limited to 2 years).

## Model
y[s,t] = a[s] + b[GCCSA,t] + sum_{k=0..5} beta_k H[s,t-k] + lambda_1 H[s,t+1] + lambda_2 H[s,t+2] + e,
SEs clustered by SA3 (income: k = 0..2 only). Per 10 percentage points of dwellings inside the fire.
- Primary: long-run effect = mean of beta_2..beta_5 (years 2-5 after). Income: beta_2.
- Short-run (reported): mean of beta_0..beta_1.
- Placebo: mean of lambda_1, lambda_2 must include 0, else no claim.
- "Long-run effect detected" if the primary CI excludes 0 in the worse direction (unemployment up, welfare up,
  businesses down, income down) and the placebo passes. Holm correction across the 5 outcomes.
- Also reported: each beta_k (the time path) and the result without fire years 2019-20 controls for COVID? No:
  reported as-is; the COVID overlap is a stated caveat.
