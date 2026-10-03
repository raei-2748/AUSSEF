"""Experiment 18 full build, step 1: modelled IL for all 218 rows (PRESPEC A, B; gate F already passed in pilot).

Reuses src/io_model.py and src/run_pilot.py unchanged. Differences from the pilot (DEVIATIONS D14-D16):
  * M1 slope over ALL rows with a model (its measured CI covers all seasons); M1b/M2/M2b/M3 over Black Summer rows.
  * P-calibration: M1b/M2/M3 slopes over pre-COVID rows (seasons 2009-2018), matching Exp 13 sample P.
Run: python3 full/build_il.py  -> results/IL_MODELLED.csv, results/IL_CHECKS.csv, results/IL_GRID_*.csv, results/IL_SUMMARY.json
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import io_model as m  # noqa: E402
import run_pilot as rp  # noqa: E402

RES = m.EXP / "results"
RES.mkdir(exist_ok=True)


def build_rows_all():
    a = pd.read_csv(m.ANALYSIS)
    e = pd.read_csv(m.EXPOSURE)
    rows = a[["agrn", "region_id", "region_name", "season", "share", "homes_v2", "DL", "IL", "FP", "SL", "Y_v4"]].merge(
        e, on=["agrn", "region_id", "season"], how="left", suffixes=("", "_e"))
    assert len(rows) == len(a) == 218
    rows["tra_spend_m"] = rows.region_name.map(m.load_tra())
    rows["census_year"] = np.where(rows.season <= 2020, 2016, 2021)
    return rows


def checks(rows, o, checkset, sample):
    """sample: 'B' -> dose-response slopes over Black Summer rows; 'P' -> over pre-COVID rows. M1 always all rows."""
    o = o.reindex(rows.index)
    dose_res = (rows.residents_1km / rows.residents_council * 10).values
    dose_h = (rows.homes_in / rows.homes_council * 10).values
    sub = (rows.season == 2019).values if sample == "B" else (rows.season <= 2018).values
    allr = np.ones(len(rows), bool)
    yy = {k: o[k].values for k in ("y_unemp", "y_income", "y_af")}
    def s(dose, y, mask):
        return rp.slope0(dose[mask], y[mask])
    sl = {"M1": s(dose_res, yy["y_unemp"], allr), "M1b": s(dose_h, yy["y_unemp"], sub),
          "M2": s(dose_h, yy["y_income"], sub), "M2b": s(dose_h, yy["y_income"], sub), "M3": s(dose_h, yy["y_af"], sub)}
    return {k: (sl[k], rp.verdict(sl[k], c)) for k, c in checkset.items()}


def search(rows, resp, base, io, checkset, sample):
    res = []
    for d, r, b, dl, typ in itertools.product(*rp.GRID.values()):
        s = dict(d=d, r=r, b=b, delta=dl, typ=typ)
        ch = checks(rows, rp.row_outputs(rows, resp, base, io, s), checkset, sample)
        prim_in = sum(v[1] == "inside" for k, v in ch.items() if checkset[k]["primary"])
        sec_out = sum(v[1] != "inside" for k, v in ch.items() if not checkset[k]["primary"])
        rec = dict(s, prim_in=prim_in, sec_out=sec_out, dist=rp.dist(s))
        for k, v in ch.items():
            rec[f"{k}_slope"], rec[f"{k}_verdict"] = v
        res.append(rec)
    g = pd.DataFrame(res)
    return g.sort_values(["prim_in", "sec_out", "dist", "typ"], ascending=[False, True, True, False])


def pick_of(g):
    p = g.iloc[0]
    return dict(d=int(p["d"]), r=p["r"], b=float(p["b"]), delta=float(p["delta"]), typ=int(p["typ"]))


def main():
    io = m.load_io()
    rows = build_rows_all()
    resp, base = m.unit_responses(rows, io)
    has = [((i, 0.3, 2) in resp) and np.isfinite(r.tra_spend_m) and np.isfinite(r.homes_v2) for i, r in rows.iterrows()]
    rows["has_model"] = has
    reason = np.where(rows.tra_spend_m.isna(), "no TRA visitor spend",
                      np.where(rows.homes_v2.isna(), "no homes-destroyed count (no rebuild offset)",
                               np.where(rows.census_used.isna(), "no Census industry counts", "")))
    rows["missing_reason"] = reason

    grid = search(rows, resp, base, io, rp.CHECKS_B, "B")
    grid.to_csv(RES / "IL_GRID_B.csv", index=False, float_format="%.5g")
    gridp = search(rows, resp, base, io, rp.CHECKS_P, "P")
    gridp.to_csv(RES / "IL_GRID_P.csv", index=False, float_format="%.5g")
    settings = {"unconstrained": rp.DEFAULT, "constrained": pick_of(grid), "P_calibrated": pick_of(gridp)}

    chk_rows, per, totals = [], {}, {}
    for name, s in settings.items():
        for off in (True, False):
            o = rp.row_outputs(rows, resp, base, io, s, offset=off)
            per[name + ("" if off else "_gross")] = o.reindex(rows.index)
        o = per[name]
        for samp, cs in (("B", rp.CHECKS_B), ("P", rp.CHECKS_P)):
            for k, (sl, v) in checks(rows, o, cs, samp).items():
                c = cs[k]
                chk_rows.append(dict(setting=name, sample=samp, check=k, primary=c["primary"], model_slope=sl,
                                     measured_lo=c["lo"], measured_hi=c["hi"], verdict=v, measured_source=c["src"]))
        og = per[name + "_gross"]
        bs = rows.season == 2019
        totals[name] = dict(setting=s, rows_with_model=int(o.loss_m.notna().sum()),
                            all_rows=dict(output_loss_net_Am=float(o.loss_m.sum()),
                                          output_loss_gross_Am=float(og.loss_m.sum()),
                                          offset_in_24m_Am=float(o.offset_m.sum()),
                                          direct_tourism_Am=float(o.direct_tour_m.sum()),
                                          direct_bi_Am=float(o.direct_bi_m.sum()),
                                          jobs_year1=float(o.jobs_12.sum()),
                                          labour_income_loss_Am=float(o.lab_24.sum())),
                            black_summer=dict(output_loss_net_Am=float(o.loss_m[bs].sum()),
                                              output_loss_gross_Am=float(og.loss_m[bs].sum()),
                                              offset_in_24m_Am=float(o.offset_m[bs].sum()),
                                              direct_tourism_Am=float(o.direct_tour_m[bs].sum()),
                                              direct_bi_Am=float(o.direct_bi_m[bs].sum()),
                                              labour_income_loss_Am=float(o.lab_24[bs].sum()),
                                              labour_income_loss_gross_Am=float(og.lab_24[bs].sum()),
                                              rows=int(o.loss_m[bs].notna().sum())))
    chk = pd.DataFrame(chk_rows)
    chk.to_csv(RES / "IL_CHECKS.csv", index=False, float_format="%.4g")

    # IL_model: constrained net output-loss share, sign +1, percentile rank (1 = worst) (PRESPEC C)
    il = per["constrained"].il_share
    il_rank = il.rank(pct=True)
    vals = il.dropna().round(12)
    tied = int(vals.duplicated(keep=False).sum())
    nontrivial = bool(len(vals) > 0 and vals.nunique() > 1 and (vals != 0).any() and tied < len(vals) / 2)

    out = rows[["agrn", "region_id", "region_name", "season", "share", "homes_v2", "tra_spend_m", "census_used",
                "missing_reason"]].copy()
    out["residents_share_in_or_1km"] = rows.residents_1km / rows.residents_council
    out["homes_share_inside"] = rows.homes_in / rows.homes_council
    for name in ("unconstrained", "constrained", "P_calibrated"):
        o = per[name]
        for k in ("loss_m", "il_share", "jobs_12", "lab_24", "y_unemp", "y_income", "y_af", "direct_tour_m",
                  "direct_bi_m", "offset_m"):
            out[f"{name}_{k}"] = o[k]
        out[f"{name}_gross_il_share"] = per[name + "_gross"].il_share
        out[f"{name}_gross_loss_m"] = per[name + "_gross"].loss_m
    out["IL_model"] = il_rank
    out["IL_model_gross"] = per["constrained_gross"].il_share.rank(pct=True)
    out.to_csv(RES / "IL_MODELLED.csv", index=False, float_format="%.6g")

    def sp(a, b):
        ok = a.notna() & b.notna()
        return [float(spearmanr(a[ok], b[ok])[0]), int(ok.sum())] if ok.sum() > 3 else [None, int(ok.sum())]
    oos = chk[(chk.setting == "P_calibrated") & (chk["sample"] == "B")].set_index("check").verdict.to_dict()
    cprim = chk[(chk.setting == "constrained") & (chk["sample"] == "B") & chk.primary]
    summary = dict(
        n_rows=len(rows), n_rows_with_model=int(il.notna().sum()),
        rows_with_model_by_season=out[out.IL_model.notna()].season.value_counts().sort_index().to_dict(),
        missing_reasons=out.missing_reason.replace("", "has model").value_counts().to_dict(),
        settings=settings, totals=totals,
        constrained_primary_inside=int((cprim.verdict == "inside").sum()),
        same_pick_as_pilot=settings["constrained"] == dict(d=1, r="inside", b=0.66, delta=0.3, typ=2),
        out_of_sample_P_calibrated_on_B_checks=oos,
        il_model_nontrivial=nontrivial, il_model_tied_rows=tied,
        n_settings=len(grid), n_settings_3_primary_inside=int((grid.prim_in == 3).sum()),
        n_settings_2plus_primary_inside=int((grid.prim_in >= 2).sum()),
        spearman=dict(ILmodel_vs_DL=sp(il_rank, rows.DL), ILmodel_vs_ILmeasured=sp(il_rank, rows.IL),
                      ILmodel_vs_share=sp(il_rank, rows.share), ILmodel_vs_gross=sp(il_rank, out.IL_model_gross),
                      ILgross_vs_DL=sp(out.IL_model_gross, rows.DL),
                      ILgross_vs_ILmeasured=sp(out.IL_model_gross, rows.IL)),
        jobs_year1_per_home_destroyed=dict(
            constrained=float(per["constrained"].jobs_12.sum() / rows.loc[per["constrained"].jobs_12.notna(), "homes_v2"].sum()),
            unconstrained=float(per["unconstrained"].jobs_12.sum() / rows.loc[per["unconstrained"].jobs_12.notna(), "homes_v2"].sum()),
            exp12_income_support_per_home_upper=4.48),
    )
    (RES / "IL_SUMMARY.json").write_text(json.dumps(summary, indent=1, default=str))
    print(chk[chk["sample"] == "B"].to_string(index=False))
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
