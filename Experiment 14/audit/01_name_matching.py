import pandas as pd, common as C
c = C.councils(); ids = set(c.region_id); out = []
# OLG
o = C.olg_long()
um = o[o.region_id.isna()].groupby("council_name").fy_start.agg(["min", "max"]).reset_index()
um["source"] = "OLG"; um.to_csv("01_unmatched_olg.csv", index=False)
post = um[um["max"] >= 2016]
print("OLG unmatched names:", len(um), "| unmatched with data FY2016+:", len(post), post.council_name.tolist())
dup = o[o.region_id.notna()].groupby(["region_id", "fy_start", "metric"]).council_name.nunique()
dup = dup[dup > 1].reset_index()
print("OLG: council-FY-metric with >1 source name mapped:", len(dup)); dup.to_csv("01_olg_two_names_one_council.csv", index=False)
cov = o[o.region_id.notna()].groupby("fy_start").region_id.nunique(); print("OLG councils matched per FY:\n", cov.to_string())
same = o[o.key.isin(C.PRE2016_SAME_NAME) & (o.fy_start < 2016)].groupby(["council_name"]).fy_start.agg(["min","max"])
print("pre-2016 entities sharing a key with a post-merger council:\n", same)
miss_any = sorted(ids - set(o.region_id.dropna().astype(int)))
print("councils never matched in OLG:", c[c.region_id.isin(miss_any)].region_name_x.tolist())
# OLG groups
g = C.olg_groups()
print("OLG groups: rows", len(g), "matched", g.region_id.notna().sum(), "unmatched", g[g.region_id.isna()].council.tolist(),
      "councils without group:", c[~c.region_id.isin(g.region_id)].region_name_x.tolist(), "dupe ids:", g.region_id.duplicated().sum())
# BOCSAR
b = C.bocsar_dv(); k2id = dict(zip(c.key, c.region_id))
names = pd.Series(b.lga.unique()); mp = names.map(lambda s: k2id.get(C.norm(s)))
bu = names[mp.isna()].tolist(); print("BOCSAR unmatched:", bu)
pd.DataFrame({"lga": bu}).to_csv("01_unmatched_bocsar.csv", index=False)
cnt = mp.dropna().value_counts(); print("BOCSAR two names -> one council:", cnt[cnt > 1].to_dict())
print("councils without BOCSAR:", c[~c.region_id.isin(mp.dropna())].region_name_x.tolist())
# id joins
r = C.rent(); a, nb = C.adjacency(); bs = C.burned_share_fy().reset_index()
rr = pd.read_parquet(C.ROOT + "fire_event_dataset/data/rent/rent_lga_quarter.parquet")
print("rent rows with no region_id:", rr.region_id.isna().sum(), rr[rr.region_id.isna()].lga_name.unique()[:20])
for nm, s in [("rent", set(r.region_id)), ("adjacency", set(a.region_id) | set(a.neighbour_id)), ("fires.csv", set(bs.region_id))]:
    print(nm, "ids not in 129:", sorted(s - ids), "| councils absent:", c[~c.region_id.isin(s)].region_name_x.tolist())
asym = sum(1 for x, y in a.itertuples(index=False) if not ((a.region_id == y) & (a.neighbour_id == x)).any())
print("adjacency pairs listed one way only:", asym, "of", len(a))
m = C.master(); print("master ids not in 129:", sorted(set(m.region_id) - ids))
print("master duplicated (agrn, region_id):", m.duplicated(["agrn", "region_id"]).sum(),
      "| duplicated (region_id, F):", m.duplicated(["region_id", "F"]).sum())
print("master F (info_fire_fy) != FY of first_fire_start:", (m.F != m.F_from_date).sum())
# rent name vs id
rn = rr.dropna(subset=["region_id"]).assign(region_id=lambda d: d.region_id.astype(int)).groupby("region_id").lga_name.unique()
diff = [(i, list(v), c.set_index("region_id").region_name_x.get(i)) for i, v in rn.items() if any(C.norm(x) != C.norm(c.set_index("region_id").region_name_x.get(i, "")) for x in v)]
print("rent ids where file name differs from council name:", diff)
