"""Step 4b: the simple check, before vs after the DL fill.

Spearman(Experiment 6 v2 risk score, and its H / E / V blocks, vs DL pillar), council-cluster bootstrap 95% CI,
on (a) all rows and (b) fires burning >= 5% of the council. DL variants come from DL_FILLED.csv (04_build_filled.py).
The scores are pre-fire and do not change; only the DL side does.
"""
import sys

import numpy as np
import pandas as pd

from common import E6_RESULTS, HERE, OUT
from spearman_check import N_BOOT, paired_boot

SCORES = ['risk_add', 'H', 'E', 'V']
EXTRA = ['F', 'risk_HV_mean']                    # reported in the CSV, not discussed
VARIANTS = ['DL_v0_original', 'DL_v1_reported', 'DL_v2_inferred', 'DL_v3_estimated']
SUBSETS = {'all rows': lambda d: np.ones(len(d), bool), 'fires >=5% burned': lambda d: (d.share >= 0.05).to_numpy()}


def main():
    filled = pd.read_csv(HERE / 'DL_FILLED.csv', dtype={'agrn': str})
    rows = pd.read_csv(E6_RESULTS / 'ROWS_WITH_SCORE_v2.csv', dtype={'agrn': str})
    d = rows[['agrn', 'region_id', 'region_name', 'share'] + SCORES + EXTRA].merge(
        filled[['agrn', 'region_id'] + VARIANTS], on=['agrn', 'region_id'], how='left', validate='1:1')
    assert len(d) == 218
    out = []
    for sname, fn in SUBSETS.items():
        sub = d[fn(d)]
        for sc in SCORES + EXTRA:
            est, chg = paired_boot(sub, sc, VARIANTS, n_boot=N_BOOT)
            for v in VARIANTS:
                n, rho, lo, hi = est[v]
                c = chg.get(v, (np.nan, np.nan, np.nan))
                out.append(dict(subset=sname, score=sc, variant=v, rows_in_subset=len(sub), n_with_DL=n, rho=rho,
                                ci_low=lo, ci_high=hi, change_vs_original=c[0], change_ci_low=c[1], change_ci_high=c[2]))
    res = pd.DataFrame(out)
    res.to_csv(OUT / 'RERUN_SPEARMAN.csv', index=False)
    show = res[res.score.isin(SCORES)].copy()
    show['rho_ci'] = show.apply(lambda r: f'{r.rho:+.2f} [{r.ci_low:+.2f}, {r.ci_high:+.2f}]', axis=1)
    show['change'] = show.apply(lambda r: '' if r.variant == VARIANTS[0] else f'{r.change_vs_original:+.2f} [{r.change_ci_low:+.2f}, {r.change_ci_high:+.2f}]', axis=1)
    pd.set_option('display.width', 220)
    print(show[['subset', 'score', 'variant', 'n_with_DL', 'rho_ci', 'change']].to_string(index=False))
    return res


if __name__ == '__main__':
    main()
