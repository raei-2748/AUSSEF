"""Audit B (independent): recompute addendum-B numbers. Reads project files only; prints results (writes nothing).
Run: python3 audit/audit_b_recompute.py
Data loading reuses the project's loaders; the model arithmetic for the chosen settings is re-implemented here."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

EXP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EXP / "src")); sys.path.insert(0, str(EXP / "full"))
import io_model as m, run_pilot as rp, build_il as B  # noqa: E402

RES = EXP / "results"
OUT = {}
io = m.load_io()
rows = B.build_rows_all()
bs = (rows.season == 2019).values
dose_h = (rows.homes_in / rows.homes_council * 10).values

# ---------- 5. count and quantiles straight from the CSV ----------
G = pd.read_csv(RES / "v2_IL_GRID.csv")
ic_flag = (G.income_slope_B >= -3.1) & (G.income_slope_B <= 0.8) & (G.income_slope_B >= -2.6) & (G.income_slope_B <= -0.7)
v = G.loc[ic_flag, "bs_gross_lost_trade_Am"]
OUT["csv_recount"] = dict(n_rows=len(G), n_ic_from_slope=int(ic_flag.sum()), n_ic_column=int(G.income_consistent.sum()),
                          agree=bool((ic_flag == G.income_consistent).all()),
                          min=v.min(), p05=v.quantile(.05), median=v.median(), p95=v.quantile(.95), max=v.max(),
                          n_M2_only=int(G.inside_M2.sum()),
                          near_edge_005=int(((G.income_slope_B + 0.7).abs() < 0.05).sum() + ((G.income_slope_B + 2.6).abs() < 0.05).sum()),
                          ic_if_M2b_upper_minus06=int(((G.income_slope_B >= -2.6) & (G.income_slope_B <= -0.6)).sum()),
                          ic_if_M2b_upper_minus08=int(((G.income_slope_B >= -2.6) & (G.income_slope_B <= -0.8)).sum()),
                          ic_by_typ=G[G.income_consistent].typ.value_counts().to_dict(),
                          ic_by_b=G[G.income_consistent].b.value_counts().sort_index().to_dict(),
                          ic_by_r=G[G.income_consistent].r.value_counts().to_dict())

# ---------- 3. v1 path reproduces v1 files ----------
r1, b1 = m.unit_responses(rows, io)                        # exclude_zero_jobs=False (v1)
g1 = pd.read_csv(RES / "IL_GRID_B.csv")
diffs = []
for _, s in g1.iterrows():
    st = dict(d=int(s.d), r=s.r, b=float(s.b), delta=float(s.delta), typ=int(s.typ))
    o = rp.row_outputs(rows, r1, b1, io, st).reindex(rows.index)
    sl = rp.slope0(dose_h[bs], o.y_income.values[bs])
    diffs.append(abs(sl - s.M2_slope) / max(abs(s.M2_slope), 1e-9))
dflt = rp.DEFAULT
o1g = rp.row_outputs(rows, r1, b1, io, dflt, offset=False).reindex(rows.index)
o1n = rp.row_outputs(rows, r1, b1, io, dflt, offset=True).reindex(rows.index)
v1s = json.loads((RES / "IL_SUMMARY.json").read_text())["totals"]["unconstrained"]["black_summer"]
mod = pd.read_csv(RES / "IL_MODELLED.csv")
OUT["v1_reproduction"] = dict(
    grid_B_M2_slope_max_rel_diff_1620=float(max(diffs)),
    bs_gross_recomputed=float(o1g.loss_m[bs].sum()), bs_gross_IL_SUMMARY=v1s["output_loss_gross_Am"],
    bs_direct_bi_recomputed=float(o1n.direct_bi_m[bs].sum()), bs_direct_bi_IL_SUMMARY=v1s["direct_bi_Am"],
    per_row_gross_max_rel_diff=float(np.nanmax(np.abs(o1g.loss_m.values - mod.unconstrained_gross_loss_m.values) /
                                                np.abs(mod.unconstrained_gross_loss_m.values))))

# ---------- 3b. what changes between v1 and v2 ----------
r2, b2 = m.unit_responses(rows, io, exclude_zero_jobs=True)
o2n = rp.row_outputs(rows, r2, b2, io, dflt, offset=True).reindex(rows.index)
ks = [k for k in b1 if k in b2]
same_tour = all(np.allclose(r1[k]["tour"], r2[k]["tour"]) and np.allclose(r1[k]["cons"], r2[k]["cons"]) for k in r1)
OUT["what_changes"] = dict(
    tour_and_cons_responses_identical=bool(same_tour),
    bi_responses_identical=bool(all(np.allclose(r1[k]["bi"], r2[k]["bi"]) for k in r1)),
    base_jobs_identical=bool(all(b1[k]["jobs"] == b2[k]["jobs"] for k in ks)),
    base_lab_identical=bool(all(np.isclose(b1[k]["lab"], b2[k]["lab"]) for k in ks)),
    base_af_identical=bool(all(np.isclose(b1[k]["af_out"], b2[k]["af_out"]) for k in ks)),
    base_out_changed_rows=int(sum(not np.isclose(b1[k]["out"], b2[k]["out"]) for k in ks)),
    default_bs_direct_tour_v1_v2=[float(o1n.direct_tour_m[bs].sum()), float(o2n.direct_tour_m[bs].sum())],
    default_bs_offset_v1_v2=[float(o1n.offset_m[bs].sum()), float(o2n.offset_m[bs].sum())],
    default_bs_direct_bi_v1_v2=[float(o1n.direct_bi_m[bs].sum()), float(o2n.direct_bi_m[bs].sum())])
del r1, b1

# ---------- 4. independent re-implementation for 3 settings ----------
cens = {y: m.load_census(y) for y in (2016, 2021)}
nsw = {y: c.sum() for y, c in cens.items()}
n = len(io["codes"])
keep = io["jobs"] > 0
xk = np.where(keep, io["x"], 0.0)
divs = io["divs"]
cidx = {c: k for k, c in enumerate(io["codes"])}
tour = np.zeros(n)
for c, s in io["tour_split"].items():
    tour[cidx[c]] = s
cons = np.zeros(n); cons[cidx["3001"]] = 1.0
jpm = io["jobs"] / io["x"]
zero_idx = [cidx[c] for c in ("6700", "6701")]


def my_row(r, s):
    yr = 2016 if r.season <= 2020 else 2021
    if r.region_id not in cens[yr].index:
        yr = 2021 if yr == 2016 else 2016
        if r.region_id not in cens[yr].index:
            return None
    if not (np.isfinite(r.tra_spend_m) and np.isfinite(r.homes_v2)):
        return None
    emp = cens[yr].loc[r.region_id].astype(float)
    tot = emp.sum()
    lqd = (emp / tot) / (nsw[yr] / nsw[yr].sum())
    lq = np.array([lqd[d] for d in divs])
    lam = np.log2(1 + tot / nsw[yr].sum()) ** s["delta"]
    inv = np.array([1 / q if q > 0 else 0.0 for q in lq])      # same convention as project: zero-LQ buyer -> 0
    cilq = np.outer(lq, inv); np.fill_diagonal(cilq, lq)
    Ar = io["A"] * np.minimum(1, cilq * lam)
    if s["typ"] == 1:
        L = np.linalg.inv(np.eye(n) - Ar)
    else:
        M = np.zeros((n + 1, n + 1)); M[:n, :n] = Ar
        M[:n, n] = io["h"] * np.minimum(1, lq * lam)
        M[n, :n] = io["w"] * np.minimum(1, lam * inv)
        L = np.linalg.inv(np.eye(n + 1) - M)[:n, :n]
    bi = np.zeros(n); base_out = base_lab = 0.0
    for d in m.DIVS:
        sel = divs == d
        opj = xk[sel].sum() / io["jobs"][sel].sum()
        bi[sel] = emp[d] * opj * xk[sel] / xk[sel].sum()
        base_out += emp[d] * opj
        base_lab += emp[d] * (xk[sel] * io["w"][sel]).sum() / io["jobs"][sel].sum()
    e = {"inside": r.residents_in, "1km": r.residents_1km, "council": r.residents_council}[s["r"]] / r.residents_council
    wsh = r.workplace_mb_in / r.workplace_mb_council if r.workplace_mb_council > 0 else 0.0
    flow = r.tra_spend_m * e * (L @ tour) + wsh * (L @ bi)
    fl24, fo24 = min(s["d"], 24) / 12, 18 / 30
    off = r.homes_v2 * 0.3443 * s["b"] * (L @ cons)
    gross = flow * fl24
    net = gross - off * fo24
    return dict(gross=gross.sum(), gross_lab=gross @ io["w"], y_income=-(net @ io["w"]) / (2 * base_lab) * 100,
                tour_direct=r.tra_spend_m * e * fl24, bi_direct=wsh * bi.sum() * fl24, base_out=base_out,
                gross_in_6700_6701=gross[zero_idx].sum(), e=e, wsh=wsh, emp=emp, tra=r.tra_spend_m)


ic = G[G.income_consistent]
picks = {"default": dflt,
         "low_end": ic.sort_values("bs_gross_lost_trade_Am").iloc[0][["d", "r", "b", "delta", "typ"]].to_dict(),
         "near_median": ic.iloc[(ic.bs_gross_lost_trade_Am - ic.bs_gross_lost_trade_Am.median()).abs().argsort().iloc[0]][["d", "r", "b", "delta", "typ"]].to_dict()}
OUT["independent"] = {}
hand = None
for name, s in picks.items():
    s = dict(d=int(s["d"]), r=s["r"], b=float(s["b"]), delta=float(s["delta"]), typ=int(s["typ"]))
    res = {i: my_row(r, s) for i, r in rows.iterrows() if bs[rows.index.get_loc(i)]}
    res = {i: x for i, x in res.items() if x is not None}
    idx = list(res)
    y = np.full(len(rows), np.nan)
    for i in idx:
        y[rows.index.get_loc(i)] = res[i]["y_income"]
    slope = rp.slope0(dose_h[bs], y[bs])
    xs, ys = dose_h[bs], y[bs]; ok = np.isfinite(xs) & np.isfinite(ys)
    slope_np = float(np.linalg.lstsq(xs[ok][:, None], ys[ok], rcond=None)[0][0])
    gsum = sum(res[i]["gross"] for i in idx)
    grow = G[(G.d == s["d"]) & (G.r == s["r"]) & np.isclose(G.b, s["b"]) & np.isclose(G.delta, s["delta"])
             & (G.typ == s["typ"])].iloc[0]
    OUT["independent"][name] = dict(setting=s, rows=len(idx), my_gross=gsum, grid_gross=float(grow.bs_gross_lost_trade_Am),
                                    my_slope_lstsq=slope_np, grid_slope=float(grow.income_slope_B),
                                    my_gross_lab=sum(res[i]["gross_lab"] for i in idx),
                                    grid_gross_lab=float(grow.bs_gross_labour_income_loss_Am),
                                    my_tour_direct=sum(res[i]["tour_direct"] for i in idx), grid_tour=float(grow.bs_direct_tourism_Am),
                                    my_bi_direct=sum(res[i]["bi_direct"] for i in idx), grid_bi=float(grow.bs_direct_bi_Am),
                                    share_gross_in_6700_6701=sum(res[i]["gross_in_6700_6701"] for i in idx) / gsum,
                                    grid_income_consistent=bool(grow.income_consistent))
    if name == "default":
        i0 = max(idx, key=lambda i: res[i]["gross"])
        h = res[i0]
        hand = dict(row=rows.loc[i0, "region_name"], agrn=int(rows.loc[i0, "agrn"]), tra_spend_m=h["tra"], e_1km=h["e"],
                    tour_direct=h["tour_direct"], hand_tour=h["tra"] * h["e"] * 6 / 12, wsh=h["wsh"], base_out=h["base_out"],
                    bi_direct=h["bi_direct"], hand_bi=h["wsh"] * h["base_out"] * 0.5,
                    project_tour=float(o2n.loc[i0, "direct_tour_m"]), project_bi=float(o2n.loc[i0, "direct_bi_m"]),
                    emp_H=float(h["emp"]["H"]), emp_L=float(h["emp"]["L"]), emp_total=float(h["emp"].sum()))
OUT["hand_check_row"] = hand
selL = divs == "L"
OUT["division_L_output_per_job"] = dict(v1=float(io["x"][selL].sum() / io["jobs"][selL].sum()),
                                        v2=float(xk[selL].sum() / io["jobs"][selL].sum()))
OUT["household_spend_share_6700_6701"] = float(io["h"][zero_idx].sum())
print(json.dumps(OUT, indent=1, default=float))   # printed only; no files written
