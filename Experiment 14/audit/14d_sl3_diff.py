import pandas as pd
a = pd.read_csv("14c_sl3_rows.csv"); b = pd.read_csv("14c_sl3_fixcodes_rows.csv")
print("rows only in auditor (relaxed pre gate):\n", a[a.SL3_mine.notna() & a.SL3_built.isna()][["agrn", "region_name", "F", "first_fire_start", "homes_v2", "SL3_mine", "g_far", "n_far"]].to_string())
print("Tenterfield 843:", a.loc[(a.region_name == "Tenterfield") & (a.F == 2018), ["SL3_mine", "SL3_built"]].to_dict("records"))
d = (a.SL3_mine - b.SL3_mine).abs(); print("ABS code fix changes", int((d > 1e-9).sum()), "rows, max", d.max())
print("rows gained when ABS codes 10130/14200 are mapped:\n", b[b.SL3_mine.notna() & a.SL3_mine.isna()][["agrn", "region_name", "F", "first_fire_start", "homes_v2", "SL3_mine", "SL3_mine_no_growth_adj", "g_far"]].to_string())
