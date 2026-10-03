"""Experiment 18 pilot: Black Summer rows (season 2019). PRESPEC sections A, B and F.

Run: python3 src/run_pilot.py   (writes pilot/*.csv and pilot/SUMMARY.json)
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
import io_model as m  # noqa: E402

OUT = m.EXP / "pilot"
OUT.mkdir(exist_ok=True)

DEFAULT = dict(d=6, r="1km", b=0.66, delta=0.3, typ=2)
GRID = dict(d=[1, 2, 3, 6, 9, 12, 18, 24, 30], r=["inside", "1km", "council"], b=[0, 0.25, 0.5, 0.66, 0.75, 1],
            delta=[0.1, 0.2, 0.3, 0.4, 0.5], typ=[1, 2])
R_ORDER = {"inside": 0, "1km": 1, "council": 2}

# Measured 95% CIs (PRESPEC B). harm = which end is the harmful one ("hi" = higher is worse).
CHECKS_B = {
    "M1": dict(lo=-0.35, hi=0.59, harm="hi", primary=True, src="Exp 7 Day 6, council, all seasons"),
    "M1b": dict(lo=-0.29, hi=0.12, harm="hi", primary=False, src="Exp 13 SA2 unemployment B (placebo fails)"),
    "M2": dict(lo=-3.1, hi=0.8, harm="lo", primary=True, src="Exp 13 ATO postcode income B"),
    "M2b": dict(lo=-2.6, hi=-0.7, harm="lo", primary=False, src="Exp 13 SA2 PIA income B"),
    "M3": dict(lo=-1.2, hi=8.6, harm="lo", primary=True, src="Exp 13 CABEE businesses B"),
}
# Pre-COVID (P) CIs for the out-of-sample calibration (Exp 13 ALL_RESULTS primary rows, sample P).
CHECKS_P = {
    "M1": CHECKS_B["M1"],
    "M1b": dict(lo=-0.83, hi=1.05, harm="hi", primary=False, src="Exp 13 SA2 unemployment P"),
    "M2": dict(lo=-2.7, hi=4.4, harm="lo", primary=True, src="Exp 13 ATO postcode income P"),
    "M3": dict(lo=-6.4, hi=26.0, harm="lo", primary=True, src="Exp 13 CABEE businesses P"),
}


def verdict(slope, c):
    if not np.isfinite(slope):
        return "missing"
    if c["harm"] == "hi":
        return "overstates" if slope > c["hi"] else ("understates" if slope < c["lo"] else "inside")
    return "overstates" if slope < c["lo"] else ("understates" if slope > c["hi"] else "inside")


def slope0(x, y):
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    return float((x * y).sum() / (x * x).sum()) if (x * x).sum() > 0 else np.nan


def win(d, W):
    """Fractions of annual loss flow and of total rebuild offset that fall in the first W months."""
    return min(d, W) / 12.0, max(0, min(W, 36) - 6) / 30.0


def row_outputs(rows, resp, base, io, s, offset=True):
    recs = []
    for i, r in rows.iterrows():
        key = (i, s["delta"], s["typ"])
        if key not in resp or not np.isfinite(r.tra_spend_m) or not np.isfinite(r.homes_v2):
            recs.append(dict(idx=i))
            continue
        e = {"inside": r.residents_in, "1km": r.residents_1km, "council": r.residents_council}[s["r"]] / r.residents_council
        wsh = r.workplace_mb_in / r.workplace_mb_council if r.workplace_mb_council > 0 else 0.0
        R = resp[key]
        flow = r.tra_spend_m * e * R["tour"] + wsh * R["bi"]           # annual loss flow response ($m output)
        off = r.homes_v2 * m.REBUILD_COST_M * s["b"] * R["cons"] if offset else 0 * R["cons"]
        out = dict(idx=i)
        for W in (12, 24):
            fl, fo = win(s["d"], W)
            dx = flow * fl - off * fo                                   # net output LOSS vector
            t = m.summarise(dx, io)
            for k, v in t.items():
                out[f"{k}_{W}"] = v
        b = base[i]
        out.update(
            loss_m=out["output_24"], jobs_yr=out["jobs_24"],
            il_share=out["output_24"] / (2 * b["out"]),
            y_unemp=out["jobs_12"] / b["jobs"] * 100,                   # pts, year 1 (upper bound: all held by residents)
            y_income=-out["lab_24"] / (2 * b["lab"]) * 100,             # % change, years 1-2
            y_af=-out["af_24"] / (2 * b["af_out"]) * 100 if b["af_out"] > 0 else np.nan,
            direct_tour_m=r.tra_spend_m * e * win(s["d"], 24)[0],
            direct_bi_m=wsh * b["bi_annual"].sum() * win(s["d"], 24)[0],
            offset_m=r.homes_v2 * m.REBUILD_COST_M * s["b"] * win(s["d"], 24)[1] if offset else 0.0,
        )
        recs.append(out)
    return pd.DataFrame(recs).set_index("idx")


def checks(rows, o, checkset):
    dose_res = (rows.residents_1km / rows.residents_council * 10).values      # per 10% residents in/within 1 km
    dose_h = (rows.homes_in / rows.homes_council * 10).values                 # per 10 pp homes inside
    yy = {k: o.reindex(rows.index)[k].values for k in ("y_unemp", "y_income", "y_af")}
    sl = {"M1": slope0(dose_res, yy["y_unemp"]), "M1b": slope0(dose_h, yy["y_unemp"]),
          "M2": slope0(dose_h, yy["y_income"]), "M2b": slope0(dose_h, yy["y_income"]), "M3": slope0(dose_h, yy["y_af"])}
    return {k: (sl[k], verdict(sl[k], c)) for k, c in checkset.items()}


def dist(s):
    return (abs(s["d"] - 6) / 29 + abs(R_ORDER[s["r"]] - 1) / 2 + abs(s["b"] - 0.66) / 1 + abs(s["delta"] - 0.3) / 0.4)


def search(rows, resp, base, io, checkset):
    res = []
    for d, r, b, dl, typ in itertools.product(*GRID.values()):
        s = dict(d=d, r=r, b=b, delta=dl, typ=typ)
        ch = checks(rows, row_outputs(rows, resp, base, io, s), checkset)
        prim_in = sum(v[1] == "inside" for k, v in ch.items() if checkset[k]["primary"])
        sec_out = sum(v[1] != "inside" for k, v in ch.items() if not checkset[k]["primary"])
        rec = dict(s, prim_in=prim_in, sec_out=sec_out, dist=dist(s))
        for k, v in ch.items():
            rec[f"{k}_slope"], rec[f"{k}_verdict"] = v
        res.append(rec)
    g = pd.DataFrame(res)
    g = g.sort_values(["prim_in", "sec_out", "dist", "typ"], ascending=[False, True, True, False])
    return g


def main():
    io = m.load_io()
    rows = m.build_rows(2019)
    resp, base = m.unit_responses(rows, io)
    rows["has_model_inputs"] = [((i, 0.3, 2) in resp) and np.isfinite(r.tra_spend_m) and np.isfinite(r.homes_v2)
                                for i, r in rows.iterrows()]

    grid = search(rows, resp, base, io, CHECKS_B)
    grid.to_csv(OUT / "GRID_B.csv", index=False, float_format="%.5g")
    gridp = search(rows, resp, base, io, CHECKS_P)
    gridp.to_csv(OUT / "GRID_P.csv", index=False, float_format="%.5g")

    pick = {k: grid.iloc[0][k] for k in DEFAULT}
    pick = dict(d=int(pick["d"]), r=pick["r"], b=float(pick["b"]), delta=float(pick["delta"]), typ=int(pick["typ"]))
    pickp = {k: gridp.iloc[0][k] for k in DEFAULT}
    pickp = dict(d=int(pickp["d"]), r=pickp["r"], b=float(pickp["b"]), delta=float(pickp["delta"]), typ=int(pickp["typ"]))

    settings = {"unconstrained": DEFAULT, "constrained": pick, "P_calibrated": pickp}
    chk_rows, per_row, totals = [], {}, {}
    for name, s in settings.items():
        o = row_outputs(rows, resp, base, io, s)
        per_row[name] = o
        ch = checks(rows, o, CHECKS_B)
        for k, (sl, v) in ch.items():
            c = CHECKS_B[k]
            chk_rows.append(dict(setting=name, check=k, primary=c["primary"], model_slope=sl, measured_lo=c["lo"],
                                 measured_hi=c["hi"], verdict=v, measured_source=c["src"]))
        ok = o.loss_m.notna()
        totals[name] = dict(setting=s, rows_with_model=int(ok.sum()),
                            output_loss_net_Am=float(o.loss_m.sum()), job_years_net=float(o.jobs_yr.sum()),
                            jobs_year1=float(o.jobs_12.sum()), labour_income_loss_Am=float(o.lab_24.sum()),
                            direct_tourism_Am=float(o.direct_tour_m.sum()), direct_bi_Am=float(o.direct_bi_m.sum()),
                            offset_in_24m_Am=float(o.offset_m.sum()))
        # gross (no rebuild offset) for transparency
        og = row_outputs(rows, resp, base, io, s, offset=False)
        totals[name].update(output_loss_gross_Am=float(og.loss_m.sum()), job_years_gross=float(og.jobs_yr.sum()))
        per_row[name + "_gross"] = og
    chk = pd.DataFrame(chk_rows)
    chk.to_csv(OUT / "CHECKS.csv", index=False, float_format="%.4g")

    # P-calibrated setting: does it pass the Black Summer checks?
    oos = chk[chk.setting == "P_calibrated"][["check", "verdict"]].set_index("check").verdict.to_dict()

    # IL_model (constrained), triviality and descriptives
    oc = per_row["constrained"]
    il = oc.il_share.reindex(rows.index)
    n_il = int(il.notna().sum())
    vals = il.dropna().round(12)
    tied = int(vals.duplicated(keep=False).sum())
    nontrivial = bool(n_il > 0 and vals.nunique() > 1 and (vals != 0).any() and tied < n_il / 2)
    il_rank = il.rank(pct=True)  # 1 = worst (largest loss share)
    ilg = per_row["constrained_gross"].il_share.reindex(rows.index)
    def sp(a, b):
        ok = a.notna() & b.notna()
        return (float(spearmanr(a[ok], b[ok])[0]), int(ok.sum())) if ok.sum() > 3 else (np.nan, int(ok.sum()))
    desc = dict(
        spearman_ILmodel_DL=sp(il_rank, rows.DL), spearman_ILmodel_ILmeasured=sp(il_rank, rows.IL),
        spearman_ILmodel_share=sp(il_rank, rows.share), spearman_ILmodel_vs_gross=sp(il, ilg),
        jobs_year1_per_home_destroyed_constrained=float(oc.jobs_12.sum() / rows.loc[oc.jobs_12.notna(), "homes_v2"].sum()),
        jobs_year1_per_home_destroyed_unconstrained=float(per_row["unconstrained"].jobs_12.sum() /
                                                           rows.loc[per_row["unconstrained"].jobs_12.notna(), "homes_v2"].sum()),
        exp12_income_support_per_home_upper=4.48,
    )

    # gate (PRESPEC F)
    cprim = chk[(chk.setting == "constrained") & chk.primary]
    n_inside = int((cprim.verdict == "inside").sum())
    in_bounds = 1 <= pick["d"] <= 30 and 0 <= pick["b"] <= 1 and 0.1 <= pick["delta"] <= 0.5
    proceed = bool(n_inside >= 2 and in_bounds and nontrivial)

    out_rows = rows[["agrn", "region_id", "region_name", "season", "share", "homes_v2", "tra_spend_m", "census_used",
                     "DL", "IL"]].copy()
    for name in ("unconstrained", "constrained"):
        o = per_row[name].reindex(rows.index)
        for k in ("loss_m", "jobs_yr", "jobs_12", "il_share", "y_unemp", "y_income", "y_af"):
            out_rows[f"{name}_{k}"] = o[k]
    out_rows["IL_model_rank"] = il_rank
    out_rows["IL_model_gross_share"] = ilg
    out_rows.to_csv(OUT / "ROWS_MODEL.csv", index=False, float_format="%.5g")

    summary = dict(n_rows=len(rows), n_rows_with_model=n_il,
                   missing_reasons=dict(no_tra_spend=int(rows.tra_spend_m.isna().sum()),
                                        no_homes_v2=int(rows.homes_v2.isna().sum()),
                                        no_census=int(rows.census_used.isna().sum())),
                   totals=totals, out_of_sample_P_calibrated_on_B_checks=oos,
                   il_model_nontrivial=nontrivial, il_model_tied_rows=tied, descriptives=desc,
                   gate=dict(primary_inside=n_inside, params_in_bounds=in_bounds, nontrivial=nontrivial,
                             proceed=proceed),
                   n_settings_searched=len(grid),
                   n_settings_with_2plus_primary_inside=int((grid.prim_in >= 2).sum()),
                   n_settings_with_3_primary_inside=int((grid.prim_in == 3).sum()))
    (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=1, default=float))
    print(chk.to_string(index=False))
    print(json.dumps(summary, indent=1, default=float))


if __name__ == "__main__":
    main()
