"""Experiment 16 POST HOC (not in PRESPEC.md; written after Part 1 results; part 2 added after the audit). Part 1 showed 'homes inside the fire'
ranking facilities and outbuildings destroyed better than the type-matched counts. Checks: is homes_in (and the OSM
non-residential site count) better than area burned for each damage type? Same bootstrap as damage_check.py.
(Season totals by function are in season_totals.py, de-duplicated.) Run: ./run.sh posthoc.py"""
import sys
sys.dont_write_bytecode = True
import json  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import damage_check as D  # noqa: E402

d = D.load()
rng = np.random.default_rng(D.SEED + 1)
out = {}
for y, cands in {'homes_destroyed': ['homes_in'], 'facilities_destroyed': ['homes_in', 'nonres_osm_in'],
                 'outbuildings_destroyed': ['homes_in', 'farm_osm_in']}.items():
    s = d[d[y].notna()].reset_index(drop=True)
    cols = cands + ['burned_km2']
    bs = D.boot(s, y, cols, rng)
    for i, c in enumerate(cands):
        est = D.rho(s[c].to_numpy(), s[y].to_numpy()) - D.rho(s.burned_km2.to_numpy(), s[y].to_numpy())
        out[f'{y}: rho({c}) - rho(area burned)'] = dict(diff=est, ci=D.ci(bs[:, i] - bs[:, -1]), rows=len(s))
json.dump(out, open(D.RES / 'posthoc/POSTHOC_DAMAGE.json', 'w'), indent=2)
print(json.dumps(out, indent=1))


# ---- POST HOC 2 (after the audit): declarations 871 and 880 overlap (9 shared fires; 7 councils have rows under
# both), so council-total damage counts may be counted twice. Rerun the pre-registered damage check without the
# AGRN 880 rows.
rows, ver = D.run(d[d.agrn != '880'].reset_index(drop=True), 'without AGRN 880', np.random.default_rng(D.SEED))
pd.DataFrame(rows).to_csv(D.RES / 'posthoc/DAMAGE_CHECK_WITHOUT_880.csv', index=False)
json.dump(ver, open(D.RES / 'posthoc/DAMAGE_CHECK_WITHOUT_880.json', 'w'), indent=2)
print(json.dumps({k: {kk: v[kk] for kk in ('rows', 'rho', 'rho_ci', 'minus_area', 'minus_area_ci', 'verdict')}
                  for k, v in ver.items()}, indent=1))
