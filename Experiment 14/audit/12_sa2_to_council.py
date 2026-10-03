"""SA2 (ASGS 2021) -> council by most 2021 Census residents (mesh blocks). Auditor's own build; cached."""
import pandas as pd, openpyxl, common as C
A = C.ROOT + "fire_event_dataset/data/raw/grp_insurance/asgs/"
def rows(path, sheet, header_row):
    ws = openpyxl.load_workbook(path, read_only=True)[sheet]; it = ws.iter_rows(values_only=True)
    for _ in range(header_row - 1): next(it)
    hdr = next(it); return pd.DataFrame([r for r in it if r and r[0] is not None], columns=hdr)
mb = rows(A + "MB_2021_AUST.xlsx", "MB_2021_AUST", 1)[["MB_CODE_2021", "SA2_CODE_2021", "GCCSA_CODE_2021"]]
mb = mb[mb.MB_CODE_2021.astype(str).str[0] == "1"]
lga = rows(A + "LGA_2021_AUST.xlsx", "LGA_2021_AUST", 1)[["MB_CODE_2021", "LGA_CODE_2021", "LGA_NAME_2021"]]
lga = lga[lga.MB_CODE_2021.astype(str).str[0] == "1"]
cnt = pd.concat([rows(A + "Mesh_Block_Counts_2021.xlsx", s, 7) for s in ["Table 1", "Table 1.1"]])[["MB_CODE_2021", "Person"]]
for d in (mb, lga, cnt): d["MB_CODE_2021"] = d.MB_CODE_2021.astype(str)
x = mb.merge(lga, on="MB_CODE_2021", how="left").merge(cnt, on="MB_CODE_2021", how="left")
print("NSW mesh blocks:", len(x), "| without LGA:", x.LGA_CODE_2021.isna().sum(), "| without count:", x.Person.isna().sum())
x["Person"] = pd.to_numeric(x.Person, errors="coerce").fillna(0)
g = x.groupby(["SA2_CODE_2021", "LGA_CODE_2021"]).Person.sum().reset_index()
tot = g.groupby("SA2_CODE_2021").Person.transform("sum"); g["share"] = g.Person / tot.where(tot > 0)
top = g.sort_values(["SA2_CODE_2021", "Person"], ascending=[True, False]).drop_duplicates("SA2_CODE_2021")
top = top.rename(columns={"SA2_CODE_2021": "SA2", "LGA_CODE_2021": "region_id", "share": "resident_share"})
top["SA2"] = top.SA2.astype(str); top["region_id"] = top.region_id.astype(int)
ids = set(C.councils().region_id)
print("SA2s:", len(top), "| assigned to id outside the 129:", sorted(set(top.region_id) - ids)[:10], "| SA2s with 0 residents:", (top.Person == 0).sum())
print("SA2s whose top council holds < 60% of residents:", (top.resident_share < 0.6).sum())
top[["SA2", "region_id", "Person", "resident_share"]].to_csv("12_sa2_to_council.csv", index=False)
