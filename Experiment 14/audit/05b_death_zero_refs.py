import pandas as pd, numpy as np, common as C
m = C.master()
z = m[m.info_SL_deaths_sourced_scope.isin(["statewide_zero", "season_zero"])]
for (F, sc), g in z.groupby(["F", "info_SL_deaths_sourced_scope"]):
    print(f"F={F} ({F}-{(F+1)%100:02d}) scope={sc} rows={len(g)} fire starts {g.start.min().date()}..{g.start.max().date()}")
    for ref in g.info_SL_deaths_sourced_ref.unique(): print("   REF:", ref)
pop = pd.to_numeric(m.X_council_council_population_pre, errors="coerce")
print("rows with deaths recorded but no population:\n", m[pop.isna() & m.SL_deaths_sourced.notna()][["agrn", "region_name", "F", "SL_deaths_sourced", "X_council_council_population_pre"]])
