import glob, numpy as np, pandas as pd, common as C
for f in sorted(glob.glob(C.ROOT + "fire_event_dataset/data/raw/abs_building_approvals/BA_LGA20*.csv"))[2:]:
    d = pd.read_csv(f, usecols=["REGION", "Region", "TIME_PERIOD"], dtype=str)
    x = d[d.REGION.isin(["10130", "14200", "10180", "14170"])].groupby(["REGION", "Region"]).TIME_PERIOD.agg(["min", "max", "count"])
    print(f[-12:], x.to_dict("index"))
m = C.master(); r = m[(m.agrn.astype(str) == "843") & (m.region_name == "Tenterfield")]
print("Tenterfield 843 m0:", r.m0.iloc[0], "-> pre window", r.m0.iloc[0] - 12, "to", r.m0.iloc[0] - 1, "| months from 2018-07 in it:", sum(1 for k in range(1, 13) if r.m0.iloc[0] - k >= pd.Period("2018-07", "M")))
