"""Consistency checks for out/master_event_council.csv (run after src.xy_format).

Recomputes, with plain loops independent of src/master.py's vectorised code:
  every lga_year window value, every fire aggregate, Y and Y_class; plus key, label and range checks.
Run: uv run --no-sync --with openpyxl python tests/test_master.py
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import master, panel_extra  # noqa: E402
from src.xy_format import CLASS_CUTS, MIN_PILLARS, PILLARS  # noqa: E402

OUT = ROOT / "out"
NA = ["N/A"]  # "N/A" = cannot exist (see na_rule); read as missing here
m = pd.read_csv(OUT / "master_event_council.csv", low_memory=False, dtype={"region_id": str, "agrn": str},
                na_values=NA)
master_cols = list(m.columns)
for d in ("post_fire_levels", "business_detail"):  # same rows, split off the master; checked together
    x = pd.read_csv(OUT / f"master_{d}.csv", low_memory=False, dtype={"region_id": str, "agrn": str}, na_values=NA)
    assert (x.agrn.values == m.agrn.values).all() and (x.region_id.values == m.region_id.values).all(), d
    m = pd.concat([m, x.drop(columns=[c for c in x.columns if c in m.columns])], axis=1)
var_all = pd.read_csv(OUT / "master_variables.csv")
var_m = var_all[var_all.sheet == "master"]
var = pd.concat([var_m, var_all[var_all.sheet.isin(["post_fire_levels", "business_detail"]) & (var_all.role != "ID")]])
var = var.set_index("column")
fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)


# keys and labels
check(len(m) == 218, f"rows {len(m)}")
check(not m.duplicated(["agrn", "region_id"]).any(), "duplicate agrn × region_id")
check(m.columns.is_unique, "duplicate columns")
check(set(m.columns) == set(var.index), "codebook does not list exactly the master + detail columns")
check(var_m.code.fillna("").ne("").sum() == var_m.role.isin(["X", "Y"]).sum() - var_m.column.isin(
    ["Y_class", "Y_class_label", "Y", "Y_norm", "Y_class_reason", "Y_class_from_Y", "Y_class_excl_responder_deaths",
     "Y_pillars_n", "DL", "IL", "FP", "SL"]).sum() - var_m.column.str.contains("_rank_").sum(),
      "every master X / Y predictor or impact column has a code")
codes_ = var_m.code.dropna()
for p_ in ("X", "Y"):
    n = sorted(int(c[1:]) for c in codes_ if c.startswith(p_))
    check(n == list(range(1, len(n) + 1)), f"{p_} codes are not 1..n")
check(var.source.notna().all(), "columns without a source")
check(var.role.isin(["ID", "X", "Y", "Info"]).all(), "unexpected role")

# panel windows: master value == lga_year (extended) value at the right council-year
ly = panel_extra.extend_lga_year(pd.read_csv(OUT / "lga_year.csv"))
ly["region_id"] = ly.region_id.astype(str)
cell = {(r, int(y)): row for r, y, row in zip(ly.region_id, ly.year, ly.to_dict("records"))}
start = pd.to_datetime(m.first_fire_start)
n_checked = 0
for col, meaning in var.meaning.items():
    mt = re.match(r"^lga_year\.(\S+), (pre|event|plus1|one-off value) ", str(meaning))
    if not mt:
        continue
    v, win = mt.groups()
    kind = master.time_kind(v)
    for i in range(len(m)):
        s = start[i]
        fy = s.year if s.month >= 7 else s.year - 1
        ce = s.year if s.month <= 6 else s.year + 1
        if kind == "static":  # latest dated at or before the fire year, else earliest after
            have = sorted(y for (r, y), row in cell.items() if r == m.region_id[i] and not pd.isna(row.get(v)))
            before = [y for y in have if y <= s.year]
            y = before[-1] if before else (have[0] if have else None)
        else:
            y = {"cal": {"pre": s.year - 1, "event": ce, "plus1": ce + 1},
                 "fy": {"pre": fy - 1, "event": fy, "plus1": fy + 1},
                 "june": {"pre": fy, "event": fy + 1, "plus1": fy + 2}}[kind][win]
        want = cell.get((m.region_id[i], y), {}).get(v, np.nan)
        got = m[col][i]
        same = (pd.isna(want) and pd.isna(got)) or (not pd.isna(want) and not pd.isna(got) and (
            str(want) == str(got) or (isinstance(want, (int, float)) and np.isclose(float(got), float(want)))))
        check(same, f"{col} row {i} ({m.agrn[i]}, {m.region_id[i]}): master {got} vs lga_year[{y}] {want}")
        n_checked += 1

# fire aggregates
fires = pd.read_csv(OUT / "fires.csv", low_memory=False, dtype={"region_id": str})
for i in range(len(m)):
    a, r = m.agrn[i], m.region_id[i]
    g = fires[(fires.region_id == r) & fires.official_declaration_agrn.fillna("").astype(str).str.split(";").map(
        lambda xs: a in xs)]
    check(len(g) > 0, f"no fires for {a}, {r}")
    w = g.region_burn_area_ha.fillna(0).clip(lower=1e-9)
    for src, how, new in master.FIRE_AGG:
        v = pd.to_numeric(g[src], errors="coerce")
        ok = v.notna()
        want = np.nan if not ok.any() else (
            (v[ok] * w[ok]).sum() / w[ok].sum() if how == "wmean" else
            (v[ok] * g.region_share_of_fire[ok]).sum() if how == "share_sum" else getattr(v[ok], how)())
        if new not in m:  # pruned (all blank or duplicate): see removed_columns
            continue
        got = m[new][i]
        check((pd.isna(want) and pd.isna(got)) or np.isclose(got, want), f"{new} {a},{r}: {got} vs {want}")

# Y hierarchy
Y = m[PILLARS].mean(axis=1).where(m[PILLARS].notna().sum(axis=1) >= MIN_PILLARS)
check(np.allclose(Y.fillna(-1), m.Y.fillna(-1)), "Y is not the mean of available pillars")
pct = m.Y.rank(pct=True)
base = np.select([pct >= CLASS_CUTS[2], pct >= CLASS_CUTS[1], pct >= CLASS_CUTS[0]], [4, 3, 2], 1)
check((m.Y_class_from_Y.to_numpy() == base).all(), "Y_class_from_Y does not follow the cut points")
check((m.Y_class >= m.Y_class_from_Y).all(), "floor lowered a class")

# ranges
for col in m.columns:
    num = m[col].dtype.kind in "fi" and not re.search(r"(change|excess|growth|area_share|_proxy)", col)
    if num and re.search(r"(_share$|_share_|share_of)", col) and "_pct" not in col:
        s = m[col].dropna()
        check(((s >= -1e-9) & (s <= 1 + 1e-6)).all(), f"{col} outside 0-1: {s.min()}..{s.max()}")
    if num and re.search(r"(share_pct|_pct_fy)", col) and "ratio" not in col:
        s = m[col].dropna()
        check(((s >= 0) & (s <= 100 + 1e-6)).all(), f"{col} outside 0-100: {s.min()}..{s.max()}")
    if re.search(r"(_count|_n$|businesses|recipients|population|dwellings)", col) and m[col].dtype.kind in "fi" \
            and "change" not in col and "excess" not in col:
        check((m[col].dropna() >= 0).all(), f"{col} negative")

print(f"panel cells checked: {n_checked:,}; fire aggregates: {len(m) * len(master.FIRE_AGG):,}")
print("FAIL" if fails else "PASS", len(fails))
for f in fails[:40]:
    print(" -", f)
sys.exit(1 if fails else 0)
