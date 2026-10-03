"""Experiment 17, part 1: what councils received and spent after each fire (council x fire rows).

Two measures, both "extra" = change from the council's own pre-fire level minus the median change in unburned
councils over the same years, summed over the fire year and the next two (FY F, F+1, F+2; Experiment 11 showed council
money keeps rising for 3 years):

1. OLG grants (all grants and contributions; NSW Office of Local Government time series via the master's lga_year
   sheet): extra A$ = sum_t [(g_t - g_base) - median_comp(g_t - g_base)] * population_t, g = grants per resident,
   base = mean of FY F-2, F-1. Available for every council.
2. Audited statements (Experiment 10): fire-related grant lines and capital spending, as shares of total expenses,
   converted to A$ with the council's pre-fire total expenses. Only councils with statements.

Fire-line rule (stricter than Experiment 9, which also counted generic "natural disaster" lines that can be flood
money): bushfire / rural fire / fire protection / fire service / emergency services / Black Summer / BLER /
local economic recovery. Storm or flood lines are excluded. Sensitivity: the Experiment 9 rule (adds natural disaster
and disaster recovery lines).

Run: python3 council_side.py   ->  results/COUNCIL_SIDE.csv
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'Experiment 7'))
from build_y2 import load, affected_fys  # noqa: E402

E10 = ROOT / 'Experiment 10'
STRICT = re.compile(r'bush ?fire|rural fire|fire protection|fire service|emergency services|black summer|'
                    r'\bBLER\b|local economic recovery', re.I)
WIDE = re.compile(r'bush ?fire|rural fire|fire protection|fire service|emergency services|disaster recover|'
                  r'natural disaster|bushfire relief|bushfire recovery', re.I)       # Experiment 9 rule
EXCL = re.compile(r'storm|flood', re.I)
POST = (0, 1, 2)
PRE = (-2, -1)


def statement_panel(path, items, pat):
    t = pd.read_csv(path, dtype={'region_id': str})
    t['F'] = t.fy.str[:4].astype(int)
    lab = t.label.fillna('')
    lines = t[t['item'].isin(items) & lab.str.contains(pat) & ~lab.str.contains(EXCL)]
    fire = lines.groupby(['region_id', 'F']).value_aud.sum()
    te = t[t['item'] == 'total_expenses'].groupby(['region_id', 'F']).value_aud.sum()
    cap = t[t['item'] == 'capex_ippe'].groupby(['region_id', 'F']).value_aud.sum()
    s = pd.DataFrame({'te': te, 'fire': fire, 'cap': cap})
    s = s[s.te > 0]
    # a council's fire lines count as 0 in a year only if its grants note was read in some year
    has = set(lines.region_id)
    s['fire'] = np.where(s.index.get_level_values(0).isin(has), s.fire.fillna(0), np.nan)
    s['fire_share'] = s.fire / s.te
    s['cap_share'] = s.cap / s.te
    return s


def changes(s, reg, F, col):
    """Per post year: value minus pre-fire mean (NaN if missing); also returns the pre-fire mean."""
    def val(y):
        try:
            return s.loc[(reg, y), col]
        except KeyError:
            return np.nan
    pre = [val(F + k) for k in PRE]
    pre = [x for x in pre if pd.notna(x)]
    if not pre:
        return [np.nan] * len(POST), np.nan
    b = np.mean(pre)
    return [val(F + k) - b for k in POST], b


def main():
    m, ly = load()
    aff, _, _ = affected_fys(m)

    def clean(r, F):        # unburned (council-FY burned share < 0.5%) in FY F-2 .. F+2
        return all((r, F + k) not in aff for k in range(-2, 3))

    # ---------- 1. OLG grants per resident
    ly = ly.copy()
    ly['g'] = pd.to_numeric(ly.fiscal_grants_per_capita_aud_fy, errors='coerce')
    ly['pop'] = pd.to_numeric(ly.fiscal_council_population_fy, errors='coerce').fillna(
        pd.to_numeric(ly.population, errors='coerce'))
    G = ly.set_index(['region_id', 'year'])[['g', 'pop']]
    regs = ly.region_id.unique()

    out = []
    for r in m.itertuples():
        row = dict(agrn=r.agrn, region_id=r.region_id, region_name=r.region_name, F=r.F)
        own, gb = changes(G, r.region_id, r.F, 'g')
        comp = np.array([changes(G, c, r.F, 'g')[0] for c in regs if c != r.region_id and clean(c, r.F)], dtype=float)
        ex = []
        for i, k in enumerate(POST):
            cm = np.nanmedian(comp[:, i]) if len(comp) and np.isfinite(comp[:, i]).any() else np.nan
            ex.append((own[i] - cm) * G['pop'].get((r.region_id, r.F + k), np.nan))
        row['olg_grants_base_per_res'] = gb
        row['olg_grants_extra_aud_F0_F2'] = np.sum(ex) if np.isfinite(ex).all() else np.nan
        row['olg_grants_extra_aud_F0_F1'] = np.sum(ex[:2]) if np.isfinite(ex[:2]).all() else np.nan
        row['olg_n_comp_councils'] = int(np.isfinite(comp[:, 0]).sum()) if len(comp) else 0
        out.append(row)
    res = pd.DataFrame(out)

    # ---------- 2. audited statements
    for tag, pat in (('strict', STRICT), ('wide', WIDE)):
        fs = statement_panel(E10 / 'A_fire_councils/statements_tidy.csv',
                             ['disaster_grant_operating', 'disaster_grant_capital'], pat)
        cs = statement_panel(E10 / 'A_comparison_councils/statements_tidy.csv',
                             ['disaster_grant_operating', 'disaster_grant_capital', 'bushfire_emergency_services_grant'],
                             pat)
        comp_regs = cs.index.get_level_values(0).unique()
        cols = [('fire_share', f'stmt_fire_grants_extra_aud_{tag}')]
        if tag == 'strict':
            cols.append(('cap_share', 'stmt_capex_extra_aud'))
        for col, name in cols:
            vals, nyrs = [], []
            for r in m.itertuples():
                own, _ = changes(fs, r.region_id, r.F, col)
                _, teb = changes(fs, r.region_id, r.F, 'te')
                comp = np.array([changes(cs, c, r.F, col)[0] for c in comp_regs if clean(c, r.F)], dtype=float)
                tot, n = 0.0, 0
                for i in range(len(POST)):
                    if pd.notna(own[i]) and len(comp) and np.isfinite(comp[:, i]).any():
                        tot += (own[i] - np.nanmedian(comp[:, i])) * teb
                        n += 1
                vals.append(tot if n else np.nan)
                nyrs.append(n)
            res[name] = vals
            res[name + '_nyears'] = nyrs
    res.to_csv(HERE / 'results/COUNCIL_SIDE.csv', index=False)
    print(res.describe().T.round(0).to_string())
    bs = res[res.agrn == '871'].copy()
    money = ['olg_grants_extra_aud_F0_F2', 'stmt_fire_grants_extra_aud_strict', 'stmt_fire_grants_extra_aud_wide',
             'stmt_capex_extra_aud']
    print('\nBlack Summer (AGRN 871), sum A$m:'); print((bs[money].sum() / 1e6).round(1))
    for c in money:
        bs[c] = (bs[c] / 1e6).round(1)
    print(bs[['region_name'] + money + ['stmt_fire_grants_extra_aud_strict_nyears']]
          .sort_values('olg_grants_extra_aud_F0_F2', ascending=False).to_string())


if __name__ == '__main__':
    main()
