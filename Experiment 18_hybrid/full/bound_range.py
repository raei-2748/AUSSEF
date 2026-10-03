"""Descriptive extra (DEVIATIONS D22): Black Summer modelled indirect loss over ALL grid settings that put the three
primary checks inside their measured CIs (not just the picked one). Gives a data-consistent range.
Run: python3 full/bound_range.py -> results/IL_BOUND_RANGE.csv"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "src"))
import build_il as B, io_model as m, run_pilot as rp  # noqa
io = m.load_io(); rows = B.build_rows_all(); resp, base = m.unit_responses(rows, io)
g = pd.read_csv(m.EXP / "results/IL_GRID_B.csv")
bs = (rows.season == 2019).values
rec = []
for _, s in g.iterrows():
    st = dict(d=int(s.d), r=s.r, b=float(s.b), delta=float(s.delta), typ=int(s.typ))
    og = rp.row_outputs(rows, resp, base, io, st, offset=False).reindex(rows.index)
    rec.append(dict(st, prim_in=s.prim_in, bs_gross_output_loss_Am=og.loss_m[bs].sum(),
                    bs_gross_labour_income_loss_Am=og.lab_24[bs].sum(), bs_gross_jobs_year1=og.jobs_12[bs].sum()))
R = pd.DataFrame(rec); R.to_csv(m.EXP / "results/IL_BOUND_RANGE.csv", index=False, float_format="%.4g")
for k in (3, 2):
    x = R[R.prim_in >= k]
    print(k, len(x), x[["bs_gross_output_loss_Am", "bs_gross_labour_income_loss_Am", "bs_gross_jobs_year1"]].describe(percentiles=[]).round(1).to_string())
x = R[R.prim_in < 2]; print("fail", len(x), x.bs_gross_output_loss_Am.describe(percentiles=[]).round(1).to_dict())
print("default gross", R[(R.d==6)&(R.r=='1km')&(R.b==0.66)&(R.delta==0.3)&(R.typ==2)].bs_gross_output_loss_Am.iloc[0])
