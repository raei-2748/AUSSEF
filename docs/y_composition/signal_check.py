"""Do the candidate Y indicators move with fire exposure?

Reads the built fire-event outputs (read-only) and prints, for each candidate
indicator: Spearman rho with share of council burned across the 218 declared
event x council rows, and medians for heavily vs lightly burned Black Summer
councils. Descriptive only; no model is fitted.

    python3 docs/y_composition/signal_check.py
"""
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parents[2] / "fire_event_dataset" / "out"

CANDIDATES = [
    "DL_homes_destroyed_per_1000_dwellings",
    "IL_unemployment_rate_change_excess_pp",
    "IL_business_count_change_excess_pct",
    "SL_income_drop_excess_pct",
    "SL_vulnerable_loss_excess",
    "FP_service_share_change_plus1_excess",
    "FP_operating_ratio_change_plus1_excess",
    "FP_cash_cover_change_plus1_excess",
    "FP_debt_ratio_change_raw",
    # added with the 2026-09-26 data collection
    "IL_total_income_change_excess_pct",
    "SL_rent_change_excess_pct",
    "FP_cash_cover_change_event_excess",
    "FP_renewals_ratio_change_plus1_excess",
    "FP_grants_per_capita_change_plus1_excess",
]


def main() -> None:
    d = pd.read_csv(OUT / "key_event_council.csv", parse_dates=["first_fire_start"])
    share = d["share_of_council_burned"]
    black_summer = d.first_fire_start.between("2019-07-01", "2020-06-30")
    heavy = share >= 0.2
    groups = {
        "BS >=20% burned": black_summer & heavy,
        "BS <20% burned": black_summer & ~heavy,
        "other years": ~black_summer,
    }
    print(f"declared event x council rows: {len(d)}; group sizes:",
          {k: int(m.sum()) for k, m in groups.items()})
    rows = []
    for c in CANDIDATES:
        s = pd.to_numeric(d[c], errors="coerce")
        ok = s.notna()
        row = {"indicator": c, "n": int(ok.sum()),
               "rho_share_burned": round(s[ok].corr(share[ok], method="spearman"), 2)}
        row.update({k: round(s[m].median(), 2) for k, m in groups.items()})
        rows.append(row)
    print(pd.DataFrame(rows).to_string(index=False))

    y = d[CANDIDATES[1:]].apply(pd.to_numeric, errors="coerce")
    corr = y.corr(method="spearman").abs()
    off = corr.where(~pd.DataFrame(
        [[i == j for j in corr.columns] for i in corr.index],
        index=corr.index, columns=corr.columns))
    print(f"\nmax |rho| between council-level candidates: {off.max().max():.2f}")


if __name__ == "__main__":
    main()
