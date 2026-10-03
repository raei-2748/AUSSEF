# Experiment 7, Day 10: where did the loss go? Rules fixed first

Written 2026-10-01 before any Day 10 number. Locked in `LOCK_DAY10.txt`. One small download approved by Ray:
ABS Regional population 2024-25, 32180DS0003_2001-25.xlsx (SA2 ERP 2001-2025, ~672 KB, abs.gov.au).
Doses: council level = homes destroyed per 1,000 dwellings (DL_FILLED v2); SA2 level = share of homes inside the
fire outline (panels/sa2_fy_dose_homes_in.parquet, effectively Black Summer).

A. Follow the money (council): FP_grants_per_capita_change_plus1_excess (grants per resident, FY after vs before,
   minus comparison median) vs homes destroyed per 1,000. Spearman and OLS slope per 10 homes per 1,000, council
   cluster bootstrap (2,000, seed 20261001). Expected: grants rise with homes lost. Descriptive: Black Summer
   reported grants total (FP_reported_black_summer_grants_total_aud) per home destroyed.
B. Rents (council, quarterly DCJ median weekly rent of new bonds, log): Day 4 quarterly machinery (council + council
   × season + Metro/Regional/Rural × quarter effects on clean quarters); change = mean residual q0+1..q0+4 minus
   q0-4..q0-1, in %; pre-trend q0-1 minus mean q0-4..q0-2. OLS slope per 10 homes destroyed per 1,000, council
   cluster bootstrap. Expected: rents rise.
C. Hard-hit sectors (SA2 CABEE counts by industry division, log): A agriculture, G retail, H accommodation & food
   (expected down), E construction (expected up). Day 9 model (SA2 FE, GCCSA × year, lags 0-5, leads 1-2, SA3
   clusters). Primary: mean of lags 0-2 per 10 pp of homes inside the fire; placebo leads must include 0; Holm across
   the 4 sectors.
D. Population (SA2 ERP, log, 30 June): Day 9 model with June y assigned to FY y-1. Primary: mean of lags 1-5
   (populations at the end of the fire FY and later); expected down. Placebo leads.
"Detected" = CI excludes 0 in the expected direction and placebo/pre-trend CI includes 0.
