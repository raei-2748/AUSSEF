import pandas as pd
r = pd.read_csv("13_fp2_fp3_rows.csv")
for c in [x[:-5] for x in r.columns if x.endswith("_mine")]:
    v = r[r[c + "_mine"].notna()]; print(c, "rows", len(v), "| min / max comparison councils with a value:", int(v[c + "_ncmp"].min()), int(v[c + "_ncmp"].max()))
