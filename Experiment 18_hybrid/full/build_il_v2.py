"""Experiment 18 addendum B (PRESPEC_ADDENDUM_B.md, LOCK_B.txt): check the IO model only against measured income,
with zero-job industries removed from business interruption. Headline = Black Summer gross lost trade.
Run: python3 full/build_il_v2.py -> results/v2_IL_GRID.csv, results/v2_IL_SUMMARY.json"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "src"))
import build_il as B, io_model as m, run_pilot as rp  # noqa: E402

RES = m.EXP / "results"
M2, M2B, M2P = rp.CHECKS_B["M2"], rp.CHECKS_B["M2b"], rp.CHECKS_P["M2"]
TOT = ("loss_m", "lab_24", "jobs_12", "offset_m", "direct_tour_m", "direct_bi_m")


def inside(x, c):
    return bool(np.isfinite(x) and c["lo"] <= x <= c["hi"])


def income_slope(rows, o, mask):
    o = o.reindex(rows.index)
    dose_h = (rows.homes_in / rows.homes_council * 10).values
    return rp.slope0(dose_h[mask], o.y_income.values[mask])


def main():
    io = m.load_io()
    zero = [c for c, j in zip(io["codes"], io["jobs"]) if j <= 0]
    rows = B.build_rows_all()
    bs = (rows.season == 2019).values
    pre = (rows.season <= 2018).values

    # v1 reproduction check (default setting, v1 model): must equal results/IL_BOUND_RANGE.csv
    r1, b1 = m.unit_responses(rows, io)
    v1_default = float(rp.row_outputs(rows, r1, b1, io, rp.DEFAULT, offset=False).reindex(rows.index).loss_m[bs].sum())
    v1_file = pd.read_csv(RES / "IL_BOUND_RANGE.csv").query("d==6 and r=='1km' and b==0.66 and delta==0.3 and typ==2")
    del r1, b1

    resp, base = m.unit_responses(rows, io, exclude_zero_jobs=True)
    rec = []
    for d, r, b, dl, typ in itertools.product(*rp.GRID.values()):
        s = dict(d=d, r=r, b=b, delta=dl, typ=typ)
        net = rp.row_outputs(rows, resp, base, io, s, offset=True).reindex(rows.index)
        gross = rp.row_outputs(rows, resp, base, io, s, offset=False).reindex(rows.index)
        sb, sp = income_slope(rows, net, bs), income_slope(rows, net, pre)
        rec.append(dict(s, income_slope_B=sb, inside_M2=inside(sb, M2), inside_M2b=inside(sb, M2B),
                        income_slope_P=sp, inside_M2_P=inside(sp, M2P),
                        bs_gross_lost_trade_Am=gross.loss_m[bs].sum(), bs_gross_labour_income_loss_Am=gross.lab_24[bs].sum(),
                        bs_gross_jobs_year1=gross.jobs_12[bs].sum(), bs_rebuild_offset_24m_Am=net.offset_m[bs].sum(),
                        bs_direct_tourism_Am=gross.direct_tour_m[bs].sum(), bs_direct_bi_Am=gross.direct_bi_m[bs].sum(),
                        bs_rows=int(gross.loss_m[bs].notna().sum())))
    G = pd.DataFrame(rec)
    G["income_consistent"] = G.inside_M2 & G.inside_M2b
    G.to_csv(RES / "v2_IL_GRID.csv", index=False, float_format="%.5g")

    def rng(x):
        v = x.bs_gross_lost_trade_Am
        return dict(n=int(len(x)), min=float(v.min()), p05=float(v.quantile(.05)), median=float(v.median()),
                    p95=float(v.quantile(.95)), max=float(v.max()),
                    labour_income_median=float(x.bs_gross_labour_income_loss_Am.median()),
                    jobs_year1_median=float(x.bs_gross_jobs_year1.median()),
                    disruption_months_allowed=sorted(int(z) for z in x.d.unique())) if len(x) else dict(n=0)

    ic = G[G.income_consistent]
    dflt = G.query("d==6 and r=='1km' and b==0.66 and delta==0.3 and typ==2").iloc[0]
    net_d = rp.row_outputs(rows, resp, base, io, rp.DEFAULT, offset=True)
    desc = {k: dict(slope=sl, verdict=v, measured_lo=rp.CHECKS_B[k]["lo"], measured_hi=rp.CHECKS_B[k]["hi"])
            for k, (sl, v) in B.checks(rows, net_d, rp.CHECKS_B, "B").items()}
    summary = dict(
        zero_job_industries_removed=zero,
        v1_reproduction=dict(default_gross_bs_Am_recomputed=v1_default,
                             default_gross_bs_Am_file=float(v1_file.bs_gross_output_loss_Am.iloc[0])),
        n_settings=len(G), bs_rows_with_model=int(dflt.bs_rows),
        income_consistent=rng(ic), sensitivity_M2_only=rng(G[G.inside_M2]),
        default=dict(setting=rp.DEFAULT, income_slope_B=float(dflt.income_slope_B), income_consistent=bool(dflt.income_consistent),
                     bs_gross_lost_trade_Am=float(dflt.bs_gross_lost_trade_Am),
                     bs_gross_labour_income_loss_Am=float(dflt.bs_gross_labour_income_loss_Am),
                     bs_gross_jobs_year1=float(dflt.bs_gross_jobs_year1),
                     bs_rebuild_offset_24m_Am=float(dflt.bs_rebuild_offset_24m_Am),
                     bs_direct_tourism_Am=float(dflt.bs_direct_tourism_Am), bs_direct_bi_Am=float(dflt.bs_direct_bi_Am),
                     descriptive_checks_not_valid_tests=desc),
        out_of_sample_share_also_inside_preCOVID_income=float(ic.inside_M2_P.mean()) if len(ic) else None,
    )
    (RES / "v2_IL_SUMMARY.json").write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
