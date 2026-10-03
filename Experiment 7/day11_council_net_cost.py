"""Experiment 7, Day 11: council gross cost, grants and net cost per resident (PRESPEC_DAY11.md, LOCK_DAY11.txt).
Run: python3 day11_council_net_cost.py"""
import json

import numpy as np
import pandas as pd

import build_y2 as B
import day4_blurry as D4
import day10_where_loss_went as D10

D4.rng = np.random.default_rng(20261002)
OUT = B.OUT


def main():
    m, ly = D10.council_rows()
    groups = B.olg_groups(ly)
    aff, master, _ = B.affected_fys(m)
    bad = aff | master
    ly = ly[ly.region_id.isin(set(groups.region_id))].copy()
    pop = ly.population.astype(float)
    ly['G'] = ly.fiscal_total_expenses_cont_ops_aud_fy / pop
    ly['R'] = ly.fiscal_grants_per_capita_aud_fy
    ly['N'] = ly.G - ly.R
    ly['R_op'] = ly.R - ly.fp_olg_capital_grants_derived_aud_fy / pop
    ly['N_op'] = ly.G - ly.R_op
    res = {}
    for name in ('G', 'R', 'N', 'R_op', 'N_op'):
        d = ly[['region_id', 'year', name]].dropna().rename(columns={name: 'y'})
        d = d.assign(period=d.year.astype(int), fy=d.year.astype(int), season=0)[['region_id', 'period', 'y', 'fy', 'season']]
        d = d.reset_index(drop=True)
        d['clean'] = ~B.unclean(d, bad)
        c = d[d.clean].reset_index(drop=True)
        fe = B.FE(c, groups, 'group', False)
        loo = {(a, p): v for a, p, v in zip(c.region_id, c.period, fe.loo)}
        obs = {(a, p): y for a, p, y in zip(d.region_id, d.period, d.y)}

        def resid(a, p):
            if (a, p) in loo:
                return loo[(a, p)]
            if (a, p) in obs:
                pr = fe.predict(a, p, 0)
                return obs[(a, p)] - pr if np.isfinite(pr) else np.nan
            return np.nan

        def mean(a, F, ks):
            v = [resid(a, F + k) for k in ks]
            v = [x for x in v if np.isfinite(x)]
            return np.mean(v) if v else np.nan
        ch = np.array([mean(a, F, [0, 1, 2]) - mean(a, F, [-3, -2, -1]) for a, F in zip(m.region_id, m.F)])
        pt = np.array([mean(a, F, [-1]) - mean(a, F, [-3, -2]) for a, F in zip(m.region_id, m.F)])
        g = m.region_id.to_numpy()
        main_ = D4.slope_boot(ch, m.dose10.to_numpy(float), g)
        pre = D4.slope_boot(pt, m.dose10.to_numpy(float), g)
        area = D4.slope_boot(ch, (m.share * 10).to_numpy(float), g)
        ok = main_.get('ci_low', 0) * main_.get('ci_high', 0) > 0 and pre.get('ci_low', 1) <= 0 <= pre.get('ci_high', -1)
        big = (m[TARGET] >= 5).to_numpy() if (TARGET := 'homes_per_1000_v2_inferred') else None
        res[name] = dict(per_10_homes_per_1000=main_, pretrend=pre, per_10pp_area=area, detected=bool(ok),
                         mean_change_councils_ge5_homes_per_1000=[float(np.nanmean(ch[big])), int(np.isfinite(ch[big]).sum())],
                         mean_change_councils_no_homes=[float(np.nanmean(ch[(m[TARGET] == 0).to_numpy()])),
                                                        int(np.isfinite(ch[(m[TARGET] == 0).to_numpy()]).sum())],
                         sd_level_aud=float(d.y.std()))
    json.dump(res, open(OUT / 'DAY11_NET_COST.json', 'w'), indent=2, default=float)
    for k, v in res.items():
        a = v['per_10_homes_per_1000']
        print(f"{k:5s} slope {a['slope_per_10pp']:9.1f} [{a['ci_low']:8.1f}, {a['ci_high']:8.1f}] n={a['rows']}  "
              f"pretrend [{v['pretrend']['ci_low']:.0f}, {v['pretrend']['ci_high']:.0f}]  detected={v['detected']}  "
              f">=5 homes/1000 mean {v['mean_change_councils_ge5_homes_per_1000'][0]:.0f} (n={v['mean_change_councils_ge5_homes_per_1000'][1]}), "
              f"0 homes mean {v['mean_change_councils_no_homes'][0]:.0f}")


if __name__ == '__main__':
    main()
