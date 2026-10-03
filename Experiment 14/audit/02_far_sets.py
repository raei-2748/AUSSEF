import pandas as pd, common as C
m = C.master(); mine = C.far_sets(m)
b = pd.read_csv(C.ROOT + "Experiment 14/inputs/FAR_SETS.csv")
rows = []
c = C.councils().set_index("region_id").region_name_x
_, nb = C.adjacency(); bs = C.burned_share_fy()
for _, r in b.iterrows():
    built = set(map(int, str(r.far_ids).split())); me = set(mine.get(r.F, []))
    mast = set(m[m.F == r.F].region_id); neigh = set().union(*[nb[x] for x in mast]) - mast
    burned = {x for x in c.index if x not in mast and x not in neigh and bs.get((x, r.F), 0) >= 0.005}
    rows.append(dict(F=r.F, master_mine=len(mast), neighbours_mine=len(neigh), burned_mine=len(burned), far_mine=len(me),
                     master_built=r.master, neighbours_built=r.neighbours, burned_built=r.burned_ge_0_5pct_not_master_not_neighbour,
                     far_built=r.far, only_in_mine=" ".join(map(str, sorted(me - built))), only_in_built=" ".join(map(str, sorted(built - me))),
                     identical=me == built))
out = pd.DataFrame(rows); out.to_csv("02_far_sets_compare.csv", index=False); print(out.to_string())
# borderline burned shares (0.3%-0.7%) for transparency
bl = [(F, x, c.get(x), round(bs.get((x, F), 0), 5)) for F in mine for x in c.index if 0.003 <= bs.get((x, F), 0) < 0.007]
print("borderline burned shares (0.3%-0.7%):", bl)
# FAR councils with OLG / rent data per F
w = C.olg_wide(); r = C.rent()
for F, s in mine.items():
    print(F, "FAR", len(s), "| with OLG FY F:", sum((x, F) in w.index for x in s), "| with any rent:", len(set(s) & set(r.region_id)))
