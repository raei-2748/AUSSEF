"""Amendment 1 evidence: 12 synthetic null datasets (no planted effect). Compares the spread of the real-group estimate
with the spread of pseudo-town draws. Run from src/: SYNTH=1 uv run ... python synth_coverage_test.py"""
import os, sys, numpy as np
os.environ["SYNTH"]="1"; os.environ["SYNTH_EFFECT"]="1.0"
sys.path.insert(0, ".")
import analysis as A
out=[]
for seed in range(12):
    os.environ["SYNTH_SEED"]=str(seed)
    A.RAD = A.synthetic()
    for name, ids in [("sc", A.SOUTH_COAST), ("ta", A.TATHRA)]:
        g=A.Group(ids)
        R0=g.ratio(np.ones(len(g.cb_ids)))
        a,e,_=g.sums("inside", np.ones(len(g.tb_ids)), R0)
        m0,m1=g.windows()["early"]; cols=(A.MO>=m0)&(A.MO<=m1)
        d=np.log(a[cols].sum()/e[cols].sum())
        NA,NE=g.null_draws("inside", 200)
        nd=np.log(NA[:,cols].sum(1)/NE[:,cols].sum(1))
        out.append((seed,name,d,nd.mean(),nd.std()))
        print(seed,name,round(d,3),'null mean',round(nd.mean(),3),'sd',round(nd.std(),3), flush=True)
import pandas as pd
o=pd.DataFrame(out,columns=['seed','g','d','nm','ns'])
print(o.groupby('g')[['d','nm','ns']].agg(['mean','std']).round(4))
