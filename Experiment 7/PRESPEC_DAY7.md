# Experiment 7, Day 7: SA2 unemployment (unsmoothed), welfare and businesses. Rules fixed first

Written 2026-10-01 before any of these files was downloaded. Locked in `LOCK_DAY7.txt`. Ray approved the three
downloads on 2026-10-01. Downloads: official sources only (dewr.gov.au, data.gov.au, dss.gov.au, abs.gov.au), at most
50 MB per file, saved under fire_event_dataset/data/raw/sa2/<dataset>/ and listed in `results/DAY7_DOWNLOADS.csv`
(file, URL, bytes, sha256). Nothing in the master workbook changes.

## Data
- U: DEWR SALM UNSMOOTHED SA2 unemployment rate (%), quarterly, ASGS 2021.
- W: DSS working-age income-support recipients by SA2, quarterly (JobSeeker/Newstart, Youth Allowance other,
  Parenting Payment, DSP, Carer Payment, Special Benefit, summed where available; same definition as
  fire_event_dataset/src/dss.py), per 1,000 residents (Census 2021 SA2 persons from panels/sa2_info.parquet).
  SA2 vintages other than ASGS 2021 are used only where the code is unchanged.
- B: ABS CABEE (8165.0) business counts by SA2, June, all industries; log count.
- Dose: share of SA2 residents within 1 km of fires (panels/sa2_quarter_dose.parquet for U and W by fire-start
  quarter; panels/sa2_fy_dose.parquet for B by financial year).

## Models (SA2 fixed effects, GCCSA × period effects, SEs clustered by SA3)
- Quarterly (U, W): y = a[s] + a[s,season] + b[GCCSA,q] + sum_{k=0..4} beta_k D[s,q-k] + sum_{k=1..4} lambda_k D[s,q+k].
  Primary: mean of beta_0..beta_4 (effect over the fire quarter and the next 4), per 10 pp of residents affected.
  Placebo: mean of lambda_1..lambda_4. Sample: quarters 2016Q1 (or first available) to 2025Q2.
- Annual (B): log count[s, June y] = a[s] + b[GCCSA,y] + beta0 D[s,FY y-1] + beta1 D[s,FY y-2] + lambda1 D[s,FY y]
  + lambda2 D[s,FY y+1]. Primary beta0 + beta1; placebo lambda1 + lambda2.
- Expected direction ("worse"): U up, W up, B down. "Detected" = primary 95% CI excludes 0 in the worse
  direction AND placebo CI includes 0. Otherwise report the bound (the CI edge in the worse direction).
- Also reported: heavily affected SA2s (dose >= 25%) and Black Summer only (fire quarters 2019Q3-2020Q1).
