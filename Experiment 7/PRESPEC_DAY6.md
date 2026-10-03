# Experiment 7, Day 6: unemployment (Bowen's suggestion). Rules fixed first

Written 2026-10-01 before any unemployment number. Locked in `LOCK_DAY6.txt`.
- Data: DEWR SALM smoothed unemployment rate (%), council (LGA 2025 codes), quarterly Dec-2010 to Mar-2026
  (fire_event_dataset/data/salm/salm_lga.csv, already in the project). Caveat: SALM is model-based and smoothed
  (4-quarter averages), which damps short shocks.
- Same design as Day 4: counterfactual = council + council×season + Metro/Regional/Rural × quarter effects on clean
  quarters (Day 1 rules); change = mean residual q0+1..q0+4 minus mean q0-4..q0-1 (a year after, because
  smoothing spreads a shock over 4 quarters), standardised by the clean pseudo-fire SD; + = unemployment rose.
- Dose: share of residents within 1 km of the fire (Day 4). Test: OLS slope per 10 pp affected, council-cluster
  bootstrap 2,000 (seed 20261001). Pre-trend: q0-1 minus mean q0-4..q0-2. "Detected" if CI above 0 and pre-trend CI
  includes 0. Also reported: change in percentage points, area-share dose, Black Summer excluded.
