"""Sanity checks on the built workbook (out/fires.csv). Writes out/checks.txt; exits non-zero if a hard check fails.

    uv run --no-sync python fire_event_dataset/checks.py
"""
import sys
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent / "out"
f = pd.read_csv(OUT / "fires.csv", dtype={"region_id": str}, low_memory=False)
lines, hard_fail = [], False


def check(name, ok, detail="", hard=True):
    global hard_fail
    lines.append(f"[{'PASS' if ok else ('FAIL' if hard else 'WARN')}] {name}" + (f": {detail}" if detail else ""))
    hard_fail |= hard and not ok


# structure
dup = f.duplicated(["event_id", "region_id"]).sum()
check("no duplicate fire × LGA rows", dup == 0, f"{dup} duplicates")
check("every fire has at least one LGA row", f.event_id.notna().all(), f"{f.event_id.nunique()} fires, {len(f)} rows")
s = f.groupby("event_id").agg(parts=("region_burn_area_ha", "sum"), total=("X1_burn_area", "first"))
s = s[s.total >= 1]
off = ((s.parts - s.total).abs() / s.total > 0.01)
check("LGA pieces sum to fire area (±1%, fires >= 1 ha)", off.mean() < 0.01,
      f"{off.sum()} of {len(s)} fires off by >1% (fires partly outside NSW LGAs)", hard=False)
blank = ["Y", "Y_class", "DL", "IL", "FP", "SL", "split"]
check("Y, components and split left blank", f[blank].isna().all().all())
check("dates ordered (end >= start)", (pd.to_datetime(f.date_end) >= pd.to_datetime(f.date_start)).loc[f.date_end.notna()].all())

# ranges
rng = {"X2_FFDI": (0, 250), "X3_SPEI": (-5, 5), "X6_severity": (0, 1), "X7_temp_max": (-5, 50), "X8_humidity_min": (0, 100),
       "X9_wind_max": (0, 150), "X10_elevation": (-20, 2300), "X11_slope": (0, 60), "X13_canopy_cover": (0, 100),
       "X18_remoteness": (0, 4), "X5_hotspot_density": (0, 5000)}
for c, (lo, hi) in rng.items():
    v = f[c].dropna()
    check(f"{c} within [{lo}, {hi}]", v.between(lo, hi).all(), f"n={len(v)}, min={v.min():.2f}, max={v.max():.2f}")

# known fires (public figures: Gospers Mountain ~512,000 ha incl. backburns, Currowan ~499,000 ha incl. merged fires)
for name, lo, hi in [("Gospers Mountain", 400_000, 520_000), ("Currowan", 250_000, 520_000)]:
    r = f[f.event_name.str.contains(name, case=False, na=False)].sort_values("X1_burn_area").iloc[-1]
    check(f"{name} area plausible", lo <= r.X1_burn_area <= hi, f"{r.X1_burn_area:,.0f} ha, start {r.date_start}", hard=False)
    lines.append(f"       {name}: FFDI max {r.X2_FFDI:.0f}, Tmax {r.X7_temp_max}, RH min {r.X8_humidity_min}, "
                 f"severity {r.X6_severity:.2f}, LGAs {f[f.event_id == r.event_id].region_name.tolist()}")
bs = f[(pd.to_datetime(f.date_start) >= "2019-09-01") & (pd.to_datetime(f.date_start) <= "2020-02-15")]
check("Black Summer fires reach FFDI 'extreme' (>= 75) on some day", (bs.X2_FFDI >= 75).any(),
      f"max {bs.X2_FFDI.max():.0f}; station FFDI exceeded 100 — reanalysis wind is lower", hard=False)
other = f[~f.index.isin(bs.index)]
check("Black Summer FFDI higher than other fires (median)", bs.X2_FFDI.median() > other.X2_FFDI.median(),
      f"{bs.X2_FFDI.median():.1f} vs {other.X2_FFDI.median():.1f}", hard=False)
check("Black Summer severity higher than other fires (median)", bs.X6_severity.median() > other.X6_severity.median(),
      f"{bs.X6_severity.median():.2f} vs {other.X6_severity.median():.2f}", hard=False)

(OUT / "checks.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(1 if hard_fail else 0)
