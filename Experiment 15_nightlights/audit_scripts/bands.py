import numpy as np, pandas as pd
from pathlib import Path
EXP = Path("/Users/ray/Research/AUSSEF - Local/.claude/worktrees/quirky-lamport-88ae45/Experiment 15_nightlights")
d = pd.read_csv(EXP/"results/pixels_south_coast.csv")
for w in ["early","y1_2","later"]:
    for ring in ["inside","ring_0_1km","ring_1_5km"]:
        s = d[(d.window==w)&(d.ring==ring)]
        lo = s[s.base_mean<1]; hi = s[s.base_mean>=1]
        f = lambda x: f"{100*(np.exp(np.log(x.sum_r.sum()/x.sum_E.sum()))-1):+.1f}% (n={len(x)}, share of E={x.sum_E.sum()/s.sum_E.sum():.2f})"
        print(w, ring, "all", f(s), "| base<1:", f(lo), "| base>=1:", f(hi))
s = d[(d.window=="early")&(d.ring=="inside")]
print("inside base_mean quantiles", s.base_mean.quantile([.1,.5,.9]).round(2).tolist(), "dwell median", s.dwell.median())
