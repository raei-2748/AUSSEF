"""Step 1b: compact per-event listing of the 218 rows (DL present / missing) as markdown, for FINDINGS.md appendix."""
import pandas as pd
from common import OUT

d = pd.read_csv(OUT / 'DL_ROW_STATUS.csv', dtype={'agrn': str})
d['first'] = pd.to_datetime(d.first_fire_start)
lines = ['| agrn | event (declaration) | start | councils with DL (homes destroyed) | councils MISSING DL (share burned) |', '|---|---|---|---|---|']
ev = d.groupby('agrn', sort=False).agg(name=('declaration_name', 'first'), start=('first', 'min')).sort_values('start')
for a, e in ev.iterrows():
    g = d[d.agrn == a]
    have = '; '.join(f"{r.region_name} ({int(r.homes_destroyed)})" for r in g[g.DL_present].itertuples()) or '-'
    miss = '; '.join(f"{r.region_name} ({r.share*100:.2f}%)" for r in g[~g.DL_present].itertuples()) or '-'
    lines.append(f"| {a} | {e['name'][:70]} | {e.start:%Y-%m-%d} | {have} | {miss} |")
(OUT / 'ROW_LISTING_BY_EVENT.md').write_text('\n'.join(lines))
print(len(ev), 'events')
