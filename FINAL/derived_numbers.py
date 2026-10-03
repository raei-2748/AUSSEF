"""Derived numbers that translate money into household terms (used in the report abstract).
Run: python3 FINAL/derived_numbers.py -> FINAL/derived_numbers.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
acc = pd.read_csv(ROOT / "Experiment 17_cost_accounts/results/BLACK_SUMMER_ACCOUNT.csv").set_index("line")["mid"]
t = pd.read_csv(ROOT / "Experiment 14/results/ANALYSIS_TABLE.csv")
bs = t[(t.season == 2019) & (t.homes_v2 > 0)][["region_id", "homes_v2"]]
g02 = pd.read_csv(ROOT / "fire_event_dataset/data/abs/gcp2016/2016 Census GCP Local Government Areas for NSW/2016Census_G02_NSW_LGA.csv")
g02["region_id"] = g02.LGA_CODE_2016.str.replace("LGA", "").astype(int)
bs = bs.merge(g02[["region_id", "Median_tot_hhd_inc_weekly"]], on="region_id", how="inner")
annual = np.average(bs.Median_tot_hhd_inc_weekly * 52, weights=bs.homes_v2)
gap_per_home = acc.loss_households_uninsured * 1e6 / t[(t.season == 2019)].homes_v2.sum()
g01 = pd.read_csv(ROOT / "fire_event_dataset/data/abs/gcp2021/2021 Census GCP Local Government Areas for NSW/2021Census_G01_NSW_LGA.csv")
kempsey_pop = int(g01[g01.LGA_CODE_2021 == "LGA14350"].Tot_P_P.iloc[0])
out = dict(
    household_gap_per_destroyed_home_A=float(gap_per_home),
    bs_median_household_income_annual_A_weighted_by_homes_lost=float(annual),
    years_of_income=float(gap_per_home / annual),
    kempsey_population_2021=kempsey_pop,
    kempsey_impact_per_resident_A=115e6 / kempsey_pop,  # A$115m impact (LGNSW 20 Feb 2026, bibliography PP08)
)
(ROOT / "FINAL/derived_numbers.json").write_text(json.dumps(out, indent=1))
print(out)
