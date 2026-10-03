import numpy as np, pandas as pd, common as C
m = C.master(); b = pd.read_csv(C.ROOT + "Experiment 14/inputs/v4_indicators.csv")
pop = pd.to_numeric(m.X_council_council_population_pre, errors="coerce")
bad = m.loc[pop.isna() & m.X_council_council_population_pre.notna(), "X_council_council_population_pre"]
print("non-numeric population values:", bad.unique()[:10], "| rows with no population:", pop.isna().sum())
d = pd.to_numeric(m.SL_deaths_sourced, errors="coerce"); resp = pd.to_numeric(m.SL_deaths_responders, errors="coerce")
sl4 = d / pop * 1e5; sl4r = (d - resp.fillna(0)) / pop * 1e5
for nm, mine in [("SL4", sl4), ("SL4_resident", sl4r)]:
    built = b[nm]; both = mine.notna() & built.notna()
    print(nm, "n mine", mine.notna().sum(), "n built", built.notna().sum(), "only mine", (mine.notna() & built.isna()).sum(),
          "only built", (mine.isna() & built.notna()).sum(), "max abs diff", (mine - built)[both].abs().max())
print("population_pre built vs master max diff:", (b.population_pre - pop).abs().max())
print("deaths recorded:", d.notna().sum(), "| >0:", (d > 0).sum(), "| total deaths:", d.sum(), "| responders recorded:", resp.notna().sum(), "total", resp.sum())
print("rows with responders recorded but deaths blank:", (resp.notna() & d.isna()).sum())
tab = m.assign(deaths=d).groupby(m.info_SL_deaths_sourced_scope.fillna("(blank)")).agg(rows=("deaths", "size"), recorded=("deaths", lambda x: x.notna().sum()),
                                                          gt0=("deaths", lambda x: (x > 0).sum()), total=("deaths", "sum"))
print(tab.to_string())
x = m.assign(deaths=d, resp=resp)
cols = ["agrn", "region_name", "F", "deaths", "resp", "info_SL_deaths_sourced_scope", "info_SL_deaths_sourced_ref_type", "info_SL_deaths_type", "info_SL_deaths_type_basis", "info_reported_deaths"]
x[cols].to_csv("05_sl4_rows.csv", index=False)
print("zero scopes by season:\n", x[x.info_SL_deaths_sourced_scope.isin(["statewide_zero", "season_zero"])].groupby(["F", "info_SL_deaths_sourced_scope"]).size().to_string())
print("blank-scope rows by F:", x[x.info_SL_deaths_sourced_scope.isna()].groupby("F").size().to_dict())
print("deaths>0 rows:\n", x[x.deaths > 0][cols].to_string())
print("example season_zero / statewide_zero refs:\n", x[x.info_SL_deaths_sourced_scope.isin(["statewide_zero", "season_zero"])][["F", "info_SL_deaths_sourced_scope", "info_SL_deaths_sourced_ref_type", "info_SL_deaths_type_basis"]].drop_duplicates(["F", "info_SL_deaths_sourced_scope"]).to_string())
refs = m[m.info_SL_deaths_sourced_scope.isin(["statewide_zero", "season_zero"])].info_SL_deaths_sourced_ref.dropna().unique()
print("distinct refs for zero scopes:", len(refs)); [print("  ", str(r)[:220]) for r in refs[:12]]
# zeros that sit in a season where another row in the same season has deaths > 0
sz = x[x.info_SL_deaths_sourced_scope.isin(["statewide_zero", "season_zero"])]
print("zero-scope rows in seasons that have a death elsewhere:", sz[sz.F.isin(x[x.deaths > 0].F)].groupby(["F", "info_SL_deaths_sourced_scope"]).size().to_dict())
