"""Step 2b (no Y): face validity against councils named in official sources as being in financial difficulty.

Input KNOWN_COUNCILS.csv (written by hand from the cited sources BEFORE this script was run):
  council   = lga_year region_name; status = distress_financial | administration_nonfinancial | strong;
  event_fy  = financial-year START year in which the distress/administration became public (window = the 3 FYs before it,
              same rule as the fire windows); source_url; quote (<25 words).
For each council: benchmarks met in each pre-event year, the pooled share, and its percentile rank (0 = lowest share)
among all councils measured over the same 3 financial years.
Run: python3 02b_face_validity_named.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

from bench_common import window_measure

HERE = Path(__file__).resolve().parent
lines = []


def log(s=''):
    print(s)
    lines.append(str(s))


def main():
    yt = pd.read_csv(HERE / 'BENCHMARK_YEAR_TABLE.csv')
    known = pd.read_csv(HERE / 'KNOWN_COUNCILS.csv')
    all_ids = yt.region_id.unique()
    cache = {}

    def universe(years):
        key = tuple(years)
        if key not in cache:
            cache[key] = pd.Series({rid: window_measure(yt, rid, years).get('bench_share', np.nan) for rid in all_ids})
        return cache[key]

    out = []
    for _, k in known.iterrows():
        rid = yt.loc[yt.region_name == k.council, 'region_id'].unique()
        if len(rid) != 1:
            out.append(dict(council=k.council, status=k.status, note='not found in lga_year'))
            continue
        rid = rid[0]
        years = [int(k.event_fy) - j for j in (1, 2, 3)]
        w = window_measure(yt, rid, years)
        u = universe(years).dropna()
        def yr(y):
            r = yt[(yt.region_id == rid) & (yt.year == y) & yt.usable]
            return f'{y}:{int(r.n_met.iloc[0])}/{int(r.n_measurable.iloc[0])}' if len(r) else f'{y}:-'
        per_year = ' '.join(yr(y) for y in sorted(years))
        if 'bench_share' in w:
            pr = (u < w['bench_share']).mean() + 0.5 * (u == w['bench_share']).mean()
            out.append(dict(council=k.council, status=k.status, event_fy=int(k.event_fy), window=f'{min(years)}-{max(years)}',
                            years_usable=w['years_usable'], met_by_year=per_year, bench_share=round(w['bench_share'], 3),
                            n_met_of8=round(w['bench_n_met_of8'], 2), pct_rank=round(pr, 2), of_councils=len(u)))
        else:
            out.append(dict(council=k.council, status=k.status, event_fy=int(k.event_fy),
                            window=f'{min(years)}-{max(years)}', years_usable=w['years_usable'],
                            note='window not usable (needs >= 2 usable years)'))
    res = pd.DataFrame(out)
    res.to_csv(HERE / 'FACE_VALIDITY_NAMED.csv', index=False)
    log(res.to_string(index=False))
    r = res.dropna(subset=['pct_rank'])
    for st, g in r.groupby('status'):
        log(f'\n{st}: n={len(g)}, median percentile rank {g.pct_rank.median():.2f} (0 = weakest of all councils), '
            f'mean benchmarks met of 8 {g.n_met_of8.mean():.1f}; in weakest third: {(g.pct_rank <= 1/3).sum()}, '
            f'weakest half: {(g.pct_rank <= 0.5).sum()}')
    (HERE / 'FACE_VALIDITY_NAMED.txt').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
