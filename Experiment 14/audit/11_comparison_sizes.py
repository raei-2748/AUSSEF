import numpy as np, pandas as pd, common as C
f = pd.read_csv("03_fp1_rows.csv"); s = pd.read_csv("04_sl1_rows.csv"); b = pd.read_csv(C.ROOT + "Experiment 14/inputs/v4_indicators.csv")
print("FP1_main: min / median FAR councils with a value (rows with a value):", int(f.loc[f.FP1_main_built.notna(), "FP1_main_n_far_with_value"].min()), int(f.loc[f.FP1_main_built.notna(), "FP1_main_n_far_with_value"].median()))
print("FP1_main FAR-with-value by F:", f.groupby("F").FP1_main_n_far_with_value.first().to_dict())
print("SL1_main: min FAR councils with a value:", int(s.loc[s.SL1_main_built.notna(), "SL1_main_nfar"].min()))
rows = []
for c in [x for x in b.columns if x.endswith("_olg")]:
    base = c[:-4]
    if base in b: rows.append(dict(indicator=base, n_main=int(b[base].notna().sum()), n_olg=int(b[c].notna().sum())))
t = pd.DataFrame(rows); print(t.to_string()); t.to_csv("11_olg_sensitivity_coverage.csv", index=False)
g = C.olg_groups(); print("OLG classes:", g.cls.value_counts().to_dict())
