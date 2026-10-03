"""Experiment 18 full build, step 2: Y_measured vs Y_hybrid models (PRESPEC C, D, E).

Uses the UNCHANGED Experiment 14 pipeline copied into ../pipeline (imported, not edited).
  python3 full/run_models_hybrid.py main     -> results/MODEL_METRICS.csv, PERM_IMPORTANCE.csv, OOF_PREDICTIONS.csv,
                                                results/GUARD.csv, results/MATCH_EXP14.csv, results/HYBRID_TABLE.csv
  python3 full/run_models_hybrid.py shuffle  -> results/SHUFFLE_CHECK.csv (100 shuffles per target; DEVIATIONS)
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

EXP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EXP / "pipeline"))
import data as D  # noqa: E402  (copied Experiment 14 data.py; OUT = pipeline/results)
import run_models as R  # noqa: E402  (copied Experiment 14 run_models.py)

RES = EXP / "results"
OVERLAP_X = ["log_share", "log_homes_in_fire_per_1000", "log_homes_within_1km_per_1000"]   # PRESPEC E
MEASURED = ["Y_v4", "DL", "IL", "FP", "SL"]          # Y_measured = Y_v4 and its pillars (primary)
HYBRID = ["Y_hybrid", "IL_model"]                     # secondary, "partly assumed"
NSHUF = 100


def table():
    T = pd.read_csv(EXP / "pipeline/results/ANALYSIS_TABLE_exp14_copy.csv", dtype={"agrn": str, "region_id": str})
    # confirm Y_v4 is reproduced by the copied pillar/composite code
    P = D.pillars(T, "main")
    y_re = D.composite(P)
    match = float(np.nanmax(np.abs(y_re - T.Y_v4)))
    il = pd.read_csv(RES / "IL_MODELLED.csv", dtype={"agrn": str, "region_id": str})
    T = T.merge(il[["agrn", "region_id", "season", "IL_model", "IL_model_gross"]], on=["agrn", "region_id", "season"],
                how="left", validate="1:1")
    H = T[["DL", "IL", "FP", "SL"]].copy()
    H["IL"] = T["IL_model"]
    T["Y_hybrid"] = D.composite(H).to_numpy()
    Hg = H.copy()
    Hg["IL"] = T["IL_model_gross"]
    T["Y_hybrid_gross"] = D.composite(Hg).to_numpy()
    assert len(T) == 218
    return T, match


def paired_boot_diff(d, ya, pa, yb, pb, rng, n=2000):
    """Council-cluster bootstrap CI of rho(pa, ya) - rho(pb, yb) on the same rows."""
    gs = R.clusters(d)
    out = []
    for _ in range(n):
        idx = np.concatenate([gs[i] for i in rng.integers(0, len(gs), len(gs))])
        out.append(spearmanr(pa[idx], ya[idx])[0] - spearmanr(pb[idx], yb[idx])[0])
    return float(spearmanr(pa, ya)[0] - spearmanr(pb, yb)[0]), *np.nanpercentile(out, [2.5, 97.5])


def main():
    T, match = table()
    T.to_csv(RES / "HYBRID_TABLE.csv", index=False)
    rng = np.random.default_rng(R.SEED)
    met, imp, oof, preds = [], [], [], {}
    t0 = time.time()
    xsets = dict(R.XSETS)
    xsets["PRE+FIRE-guard"] = [c for c in R.XSETS["PRE+FIRE"] if c not in OVERLAP_X]
    plan = [(t, xs) for t in MEASURED for xs in ("PRE", "PRE+FIRE")] + \
           [(t, xs) for t in HYBRID for xs in ("PRE", "PRE+FIRE")] + \
           [(t, "PRE+FIRE-guard") for t in ["Y_v4", "IL", "Y_hybrid", "IL_model"]] + \
           [("IL_model_gross", "PRE+FIRE"), ("Y_hybrid_gross", "PRE+FIRE")]
    for target, xs in plan:
        d = T.dropna(subset=[target]).reset_index(drop=True)
        xcols = xsets[xs]
        schemes = ("season", "council") if xs != "PRE+FIRE-guard" else ("season",)
        for scheme in schemes:
            models = ("mean", "ridge", "size_line", "rf") + (("poisson",) if target == "DL" else ())
            P, kept = R.cv_run(d, target, xcols, scheme, keep_models=(scheme == "season"), models=models)
            for r in R.metrics(d, target, P, rng):
                met.append(dict(target=target, xset=xs, cv=scheme, **r))
            if scheme == "season":
                preds[(target, xs)] = (d, P["rf"])
                if xs != "PRE+FIRE-guard":
                    for r in R.perm_importance(d, target, xcols, kept, rng):
                        imp.append(dict(target=target, xset=xs, **r))
                o = d[["agrn", "region_id", "region_name", "season", target]].rename(columns={target: "actual"})
                for n, p in P.items():
                    o[f"pred_{n}"] = p
                oof.append(o.assign(target=target, xset=xs))
        print(f"{target} {xs} done {time.time() - t0:.0f}s", flush=True)
    M = pd.DataFrame(met)
    M.insert(0, "status", np.where(M.target.isin(MEASURED), "measured (primary)", "partly assumed (secondary)"))
    M.to_csv(RES / "MODEL_METRICS.csv", index=False)
    pd.DataFrame(imp).to_csv(RES / "PERM_IMPORTANCE.csv", index=False)
    pd.concat(oof).to_csv(RES / "OOF_PREDICTIONS.csv", index=False)

    # match with Experiment 14 (same code, same seed, same order for the measured targets)
    e14 = pd.read_csv(EXP.parent / "Experiment 14/results/METRICS.csv")
    k = ["target", "xset", "cv", "model"]
    mm = M[M.target.isin(MEASURED)].merge(e14, on=k, suffixes=("", "_e14"))
    mm["abs_diff_rho"] = (mm.rho - mm.rho_e14).abs()
    mm["abs_diff_rho_lo"] = (mm.rho_lo - mm.rho_lo_e14).abs()
    mm[k + ["rho", "rho_e14", "abs_diff_rho", "rho_lo", "rho_lo_e14", "abs_diff_rho_lo"]].to_csv(RES / "MATCH_EXP14.csv", index=False)

    # leakage / circularity guards (PRESPEC E)
    g = []
    def rows_of(t, xs):
        d, p = preds[(t, xs)]
        return d.set_index(["agrn", "region_id", "season"]), p
    for t in ["Y_hybrid", "IL_model", "Y_v4", "IL"]:
        da, pa = preds[(t, "PRE+FIRE")]
        db, pb = preds[(t, "PRE+FIRE-guard")]
        assert (da.agrn.values == db.agrn.values).all()
        y = da[t].to_numpy()
        dr, lo, hi = paired_boot_diff(da, y, pa, y, pb, rng)
        g.append(dict(comparison=f"{t}: rho(full X) - rho(overlap X removed)", rows=len(da), diff=dr, lo=lo, hi=hi))
    da, pa = preds[("Y_hybrid", "PRE+FIRE")]
    db, pb = preds[("Y_v4", "PRE+FIRE")]
    assert (da.agrn.values == db.agrn.values).all() and (da.region_id.values == db.region_id.values).all()
    dr, lo, hi = paired_boot_diff(da, da.Y_hybrid.to_numpy(), pa, db.Y_v4.to_numpy(), pb, rng)
    g.append(dict(comparison="rho(Y_hybrid) - rho(Y_measured), PRE+FIRE", rows=len(da), diff=dr, lo=lo, hi=hi))
    da, pa = preds[("Y_hybrid", "PRE")]
    db, pb = preds[("Y_v4", "PRE")]
    dr, lo, hi = paired_boot_diff(da, da.Y_hybrid.to_numpy(), pa, db.Y_v4.to_numpy(), pb, rng)
    g.append(dict(comparison="rho(Y_hybrid) - rho(Y_measured), PRE", rows=len(da), diff=dr, lo=lo, hi=hi))
    G = pd.DataFrame(g)
    G.to_csv(RES / "GUARD.csv", index=False)

    def sp(a, b):
        ok = T[a].notna() & T[b].notna()
        return [float(spearmanr(T.loc[ok, a], T.loc[ok, b])[0]), int(ok.sum())]
    desc = dict(y_v4_reproduced_max_abs_diff=match,
                spearman=dict(IL_model_vs_DL=sp("IL_model", "DL"), IL_model_vs_IL_measured=sp("IL_model", "IL"),
                              IL_model_gross_vs_DL=sp("IL_model_gross", "DL"),
                              IL_model_vs_IL_model_gross=sp("IL_model", "IL_model_gross"),
                              Y_hybrid_vs_Y_measured=sp("Y_hybrid", "Y_v4"),
                              Y_hybrid_gross_vs_Y_measured=sp("Y_hybrid_gross", "Y_v4")),
                rows=dict(Y_hybrid=int(T.Y_hybrid.notna().sum()), IL_model=int(T.IL_model.notna().sum()),
                          IL_measured=int(T.IL.notna().sum())),
                max_abs_diff_vs_exp14_rho=float(mm.abs_diff_rho.max()),
                max_abs_diff_vs_exp14_rho_lo=float(mm.abs_diff_rho_lo.max()))
    (RES / "MODEL_SUMMARY.json").write_text(json.dumps(desc, indent=1))
    print(json.dumps(desc, indent=1))
    print(G.to_string(index=False))


def shuffle():
    T, _ = table()
    rng = np.random.default_rng(R.SEED + 18)
    M = pd.read_csv(RES / "MODEL_METRICS.csv")
    sh, nulls = [], {}
    for target, xs in [("Y_v4", "PRE+FIRE"), ("Y_hybrid", "PRE+FIRE"), ("IL_model", "PRE+FIRE")]:
        d = T.dropna(subset=[target]).reset_index(drop=True)
        real = M[(M.target == target) & (M.xset == xs) & (M.cv == "season") & (M.model == "rf")].rho.iloc[0]
        r, null = R.shuffle_check(d, target, R.XSETS[xs], NSHUF, rng, real)
        sh.append(dict(target=target, xset=xs, **r))
        nulls[f"{target}|{xs}"] = null.tolist()
        pd.DataFrame(sh).to_csv(RES / "SHUFFLE_CHECK.csv", index=False)
        print(f"shuffle {target} {xs} p={r['p']:.3f}", flush=True)
    json.dump(nulls, open(RES / "SHUFFLE_NULLS.json", "w"))


if __name__ == "__main__":
    {"main": main, "shuffle": shuffle}[sys.argv[1]]()
