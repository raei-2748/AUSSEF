"""IL2 income / IL3 businesses in affected SA2s, excess vs zero-dose SA2s in FAR councils (same GCCSA).
Auditor's own change, control and weighting logic. Income panel loaded with Experiment 7 day5_sa2_income.panel()."""
import sys, numpy as np, pandas as pd, common as C
sys.path.insert(0, C.ROOT + "Experiment 7"); import day5_sa2_income as D7
m = C.master(); far = C.far_sets(m); b = pd.read_csv(C.ROOT + "Experiment 14/inputs/v4_indicators.csv")
P = C.ROOT + "Experiment 7/panels/"
dose = pd.read_parquet(P + "sa2_fy_dose.parquet"); info = pd.read_parquet(P + "sa2_info.parquet")
bus = pd.read_parquet(P + "sa2_businesses.parquet"); inc, _ = D7.panel()
s2c = pd.read_csv("12_sa2_to_council.csv", dtype={"SA2": str}).set_index("SA2").region_id.to_dict()
gcc = info.set_index("SA2").GCCSA.to_dict(); pop = info.set_index("SA2")["pop"].to_dict()
DOSE = {(s, f): (p, d) for s, f, p, d in zip(dose.SA2, dose.fy, dose.persons, dose.dose)}
INC = {(s, f): v for s, f, v in zip(inc.SA2, inc.fy, inc["sum"]) if v > 0}
INC_OK = {(s, f) for s, f, e, v in zip(inc.SA2, inc.fy, inc.earners, inc["sum"]) if e > 0 and v > 0}
BUS = {(s, j): v for s, j, v in zip(bus.SA2, bus.june, bus.value) if v > 0}
SA2S = sorted(info.SA2)
print("SA2s in sa2_info:", len(SA2S), "| without council map:", sum(s not in s2c for s in SA2S))
def chg(kind, s, F):
    if kind == "IL2":
        a, z = (s, F + 2), (s, F - 1); return np.log(INC[a]) - np.log(INC[z]) if a in INC and z in INC else np.nan
    a, z = (s, F + 2), (s, F); return np.log(BUS[a]) - np.log(BUS[z]) if a in BUS and z in BUS else np.nan
def zero(s, F): return all(DOSE.get((s, F + k), (0, 0))[1] <= 0 for k in (-1, 0, 1, 2))
def build(kind, gmode="per_sa2", popmin=0):
    vals = []
    for _, row in m.iterrows():
        F = row.F
        if kind == "IL2" and F > 2019: vals.append(np.nan); continue
        aff = [s for s in SA2S if s2c.get(s) == row.region_id and DOSE.get((s, F), (0, 0))[1] > 0 and pop.get(s, 0) >= popmin]
        if not aff: vals.append(np.nan); continue
        farset = set(far[F]); ctrl = [s for s in SA2S if s2c.get(s) in farset and zero(s, F) and pop.get(s, 0) >= popmin]
        cm = {}
        for g in set(gcc[s] for s in aff):
            v = [chg(kind, s, F) for s in ctrl if gcc[s] == g]; v = [x for x in v if np.isfinite(x)]
            cm[g] = np.mean(v) if v else np.nan
        num = den = 0.0
        if gmode == "per_sa2":
            for s in aff:
                c = chg(kind, s, F) - cm[gcc[s]]
                if np.isfinite(c): num += DOSE[(s, F)][0] * c; den += DOSE[(s, F)][0]
            vals.append(num / den if den > 0 else np.nan)
        else:  # weighted own change minus control of the council's majority GCCSA
            o = [(DOSE[(s, F)][0], chg(kind, s, F)) for s in aff]; o = [(w, c) for w, c in o if np.isfinite(c)]
            g = pd.Series({s: gcc[s] for s in aff}).mode()[0]
            vals.append(sum(w * c for w, c in o) / sum(w for w, _ in o) - cm[g] if o else np.nan)
    return np.array(vals)
rows = []; out = m[["agrn", "region_id", "region_name", "F"]].copy()
for kind in ("IL2", "IL3"):
    for gmode in ("per_sa2", "council_gccsa"):
        for popmin in (0, 100):
            mine = build(kind, gmode, popmin); built = b[kind].values; both = np.isfinite(mine) & np.isfinite(built); d = np.abs(mine - built)[both]
            rows.append(dict(indicator=kind, gccsa_mode=gmode, sa2_pop_min=popmin, n_mine=int(np.isfinite(mine).sum()), n_built=int(np.isfinite(built).sum()),
                             only_mine=int((np.isfinite(mine) & ~np.isfinite(built)).sum()), only_built=int((~np.isfinite(mine) & np.isfinite(built)).sum()),
                             max_abs_diff=d.max() if len(d) else np.nan, n_differ=int((d > 1e-9).sum())))
            out[f"{kind}_{gmode}_{popmin}"] = mine
            print(rows[-1], flush=True)
    out[kind + "_built"] = b[kind]
s = pd.DataFrame(rows); s.to_csv("15_il2_il3_summary.csv", index=False); out.to_csv("15_il2_il3_rows.csv", index=False); print(s.to_string())
