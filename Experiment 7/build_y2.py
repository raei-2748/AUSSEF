"""Experiment 7, Day 1: rebuild the impact measure Y with a proper counterfactual, then check it against fire size.

Rules: PRESPEC_DAY1.md (hash in LOCK_DAY1.txt). Only the counterfactual changes; indicators, windows, signs and the
rank aggregation are v1's. No pre-fire predictor is read.

Counterfactual = imputation estimator: per indicator series, OLS on clean council-periods of
    y[i,t] = a[i] + b[t or (group,t)] (+ c[i,season] for quarterly series)
tau = observed - predicted at a master row's window (out of sample, because every master row's window is excluded
from the fit). Leave-one-out residuals of clean periods give the noise scale, the placebo and the null.

Run: python3 build_y2.py      (after prep_panels.py)
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
DATASET = HERE.parent / 'fire_event_dataset'
WORKBOOK = Path('/Users/ray/Research/AUSSEF - Local/data/master_workbook/nsw_bushfires_2015_2025_XY.xlsx')
SEED = 20260930
N_BOOT = 2000
AFFECTED_SHARE = 0.005          # council-FY burned share that makes FY F..F+2 unclean
POST_FY = 3                     # FY F, F+1, F+2 excluded from the fit
PLACEBO_SHIFT = 3               # pseudo fire F-3
BINS = [0, 0.01, 0.05, 0.20, 1.01]
BIN_LABELS = ['<1%', '1-5%', '5-20%', '>=20%']
GROUPS = {'Metropolitan': 'Metro', 'Metropolitan Fringe': 'Metro', 'Regional Town/City': 'Regional',
          'Rural': 'Rural', 'Large Rural': 'Rural'}

# name, pillar, sign (+1 = higher is worse), kind (fy | june | q), window offsets, v1 master column (for comparison)
INDICATORS = [
    ('total_income', 'IL', -1, 'fy', [0], 'IL_total_income_change_excess_pct'),
    ('biz_count', 'IL', -1, 'june', [1], 'IL_biz_count_change_excess_pct'),
    ('cash_cover', 'FP', -1, 'fy', [0, 1], None),                     # v1 = mean of event and plus1 excess
    ('services_share', 'FP', -1, 'fy', [1], 'FP_service_share_change_plus1_excess'),
    ('renewals_ratio', 'FP', +1, 'fy', [1], 'FP_renewals_ratio_change_plus1_excess'),
    ('income_support', 'SL', +1, 'q', [1], 'SL_vulnerable_loss_excess'),
    ('night_lights', 'IL', -1, 'q', [1], 'info_ntl_mean_exfire_yoy_pct_qp1_excess'),   # candidate only
]
V1_RANK = {'total_income': 'IL_rank_total_personal_income_fall_excess', 'biz_count': 'IL_rank_biz_count_fall_excess',
           'cash_cover': 'FP_rank_cash_cover_drawdown_excess_t_t1',
           'services_share': 'FP_rank_services_crowd_out_excess_t_1',
           'renewals_ratio': 'FP_rank_renewals_ratio_rise_excess_t_1',
           'income_support': 'SL_rank_income_support_recipients_rise_excess'}
VARIANTS = {'V2a': ('common', False), 'V2b': ('group', False), 'V2a+NTL': ('common', True), 'V2b+NTL': ('group', True)}


def norm(name):
    s = str(name).lower().replace('(nsw)', '')
    s = re.sub(r'\((a|c|s|m|rc|t)\)', ' ', s)
    s = re.sub(r'\b(city|council|shire|regional|municipal|of|the)\b', ' ', s)
    return re.sub(r'[^a-z]', '', s)


def fy_of(ts):
    ts = pd.Timestamp(ts)
    return ts.year if ts.month >= 7 else ts.year - 1


# ------------------------------------------------------------------ data
def load():
    m = pd.read_excel(WORKBOOK, sheet_name='master', header=2, keep_default_na=False, na_values=[''])
    m['region_id'] = m.region_id.astype(int).astype(str)
    m['agrn'] = m.agrn.astype(str)
    m['start'] = pd.to_datetime(m.first_fire_start)
    m['F'] = m.start.map(fy_of)
    m['q0'] = m.start.dt.to_period('Q')
    m['share'] = m.X_fire_share_of_council_burned
    ly = pd.read_excel(WORKBOOK, sheet_name='lga_year', header=1, keep_default_na=False, na_values=[''])
    ly['region_id'] = ly.region_id.astype(int).astype(str)
    return m, ly


def olg_groups(ly):
    x = pd.read_excel(DATASET / 'data/olg/time-series-data-2018-2019.xlsx', sheet_name='2018_19_Councils', header=None)
    d = x.iloc[3:, :3]
    d.columns = ['council', 'olg_group', 'cls']
    d = d[d.olg_group.notna()].assign(k=lambda t: t.council.map(norm).replace({'parramattanew': 'parramatta'}))
    c = ly[['region_id', 'region_name']].drop_duplicates().assign(k=lambda t: t.region_name.map(norm))
    c = c.merge(d[['k', 'cls', 'olg_group']], on='k', how='left')
    c['group'] = c.cls.map(GROUPS)
    return c.dropna(subset=['group'])[['region_id', 'region_name', 'cls', 'olg_group', 'group']]


def affected_fys(m):
    """(council, FY) with burned share >= AFFECTED_SHARE, plus NSW Oct 2013 councils."""
    f = pd.read_csv(DATASET / 'out/fires.csv', low_memory=False, dtype={'region_id': str})
    f['fy'] = pd.to_datetime(f.date_start).map(fy_of)
    g = f.groupby(['region_id', 'fy']).share_of_region_burned.sum().reset_index()
    aff = set(map(tuple, g.loc[g.share_of_region_burned >= AFFECTED_SHARE, ['region_id', 'fy']].to_numpy()))
    x = pd.read_csv(DATASET / 'data/extra_fires/extra_fire_rows.csv', dtype={'region_id': str})
    x = x[(x.event == 'NSW_2013_oct') & (x.share_burned >= AFFECTED_SHARE)]
    aff |= {(r, 2013) for r in x.region_id}
    master = {(r, F) for r, F in zip(m.region_id, m.F)}
    return aff, master, g


def series(ly, groups):
    """Long panels: region_id, period, y, fy (financial year the period belongs to), season."""
    keep = set(groups.region_id)
    ly = ly[ly.region_id.isin(keep)]
    out = {}

    def annual(col, kind, fn):
        d = ly[['region_id', 'year', col]].dropna()
        d = d.assign(period=d.year.astype(int), y=fn(d[col].astype(float)))
        d['fy'] = d.period if kind == 'fy' else d.period - 1      # June of year y ends FY y-1
        d['season'] = 0
        return d[['region_id', 'period', 'y', 'fy', 'season']]
    out['total_income'] = annual('total_income_aud_fy', 'fy', np.log)
    out['biz_count'] = annual('biz_total_june', 'june', np.log)
    out['cash_cover'] = annual('fiscal_cash_cover_months_fy', 'fy', lambda s: s)
    out['services_share'] = annual('fiscal_service_share_pct_fy', 'fy', lambda s: s)
    out['renewals_ratio'] = annual('fiscal_renewals_ratio_pct_fy', 'fy', lambda s: s)

    pop = ly.set_index(['region_id', 'year']).population
    d = pd.read_parquet(HERE / 'panels/dss_quarter.parquet')
    d = d[d.region_id.astype(str).isin(keep)].copy()
    d['region_id'] = d.region_id.astype(str)
    d['period'] = pd.PeriodIndex(d.quarter, freq='Q')
    june = [p.year if p.quarter >= 3 else p.year - 1 for p in d.period]       # most recent 30 June
    d['pop'] = [pop.get((r, y), np.nan) for r, y in zip(d.region_id, june)]
    d['y'] = d.income_support_total / d['pop'] * 1000
    d['fy'] = [p.year if p.quarter >= 3 else p.year - 1 for p in d.period]
    d['season'] = [p.quarter for p in d.period]
    out['income_support'] = d.dropna(subset=['y'])[['region_id', 'period', 'y', 'fy', 'season']]

    n = pd.read_parquet(DATASET / 'data/enrich/ntl_lga_quarter.parquet')
    n = n[n.region_id.astype(str).isin(keep)].copy()
    n['region_id'] = n.region_id.astype(str)
    n['period'] = pd.PeriodIndex(n.period, freq='Q')
    n['y'] = np.log(n.ntl_mean_rad_excl_fire)
    n['fy'] = [p.year if p.quarter >= 3 else p.year - 1 for p in n.period]
    n['season'] = [p.quarter for p in n.period]
    out['night_lights'] = n.dropna(subset=['y'])[['region_id', 'period', 'y', 'fy', 'season']]
    return out


# ------------------------------------------------------------------ model
class FE:
    """OLS with council, period (common or by group) and, for quarterly series, council x season effects."""

    def __init__(self, d, groups, mode, quarterly):
        self.g = groups.set_index('region_id').group
        self.mode, self.q = mode, quarterly
        cols = self._cols(d)
        self.names = sorted(set(cols))
        self.ix = {c: k for k, c in enumerate(self.names)}
        X = self._X(d)
        yv = d.y.to_numpy()
        U, s, Vt = np.linalg.svd(X, full_matrices=False)
        keep = s > s.max() * 1e-10
        U, s, Vt = U[:, keep], s[keep], Vt[keep]
        self.beta = Vt.T @ ((U.T @ yv) / s)
        self.fitted = X @ self.beta
        h = (U ** 2).sum(axis=1)
        self.loo = (yv - self.fitted) / np.clip(1 - h, 1e-6, None)
        self.lev = h

    def _keys(self, r, p, season):
        k = [('a', r), ('b', p if self.mode == 'common' else (self.g.get(r), p))]
        if self.q and season > 1:
            k.append(('c', r, season))
        return k

    def _cols(self, d):
        return [k for r, p, s in zip(d.region_id, d.period, d.season) for k in self._keys(r, p, s)]

    def _X(self, d):
        X = np.zeros((len(d), len(self.names)))
        for i, (r, p, s) in enumerate(zip(d.region_id, d.period, d.season)):
            for k in self._keys(r, p, s):
                X[i, self.ix[k]] = 1.0
        return X

    def predict(self, r, p, season):
        keys = self._keys(r, p, season)
        if any(k not in self.ix for k in keys):
            return np.nan
        return float(sum(self.beta[self.ix[k]] for k in keys))


def unclean(d, bad):
    """Period is unclean if its FY lies in F..F+POST_FY-1 of any (council, F) in bad."""
    return np.array([any((r, fy - k) in bad for k in range(POST_FY)) for r, fy in zip(d.region_id, d.fy)])


def windows(kind, F, q0, offsets):
    if kind == 'fy':
        return [F + o for o in offsets]
    if kind == 'june':
        return [F + o for o in offsets]            # June F+1 = end of the fire FY
    return [q0 + o for o in offsets]


def run_variant(name, mode, panels, groups, m, bad):
    """tau / z / placebo z for every master row, and the null z for pseudo fires at clean council-FYs."""
    rows = {k: {} for k in ('tau', 'z', 'placebo_z')}
    nulls, sig, fits = {}, {}, {}
    for ind, pillar, sign, kind, offs, _ in INDICATORS:
        d = panels[ind].copy()
        d['clean'] = ~unclean(d, bad)
        c = d[d.clean].reset_index(drop=True)
        fe = FE(c, groups, mode, kind == 'q')
        c['loo'] = fe.loo
        loo = {(r, p): v for r, p, v in zip(c.region_id, c.period, c.loo)}
        obs = {(r, p): (y, s) for r, p, y, s in zip(d.region_id, d.period, d.y, d.season)}
        # noise scale for this window shape: SD of window-averaged LOO residuals over clean periods
        wins = []
        for r, p in loo:
            ps = [p + (o - offs[0]) for o in offs]
            if all((r, x) in loo for x in ps):
                wins.append(np.mean([loo[(r, x)] for x in ps]))
        sigma = float(np.std(wins, ddof=1))
        sig[ind] = dict(sigma=sigma, n_clean=len(c), n_windows=len(wins), councils=int(c.region_id.nunique()))
        fits[ind] = fe

        def tau_at(r, ps):
            vals = []
            for p in ps:
                if (r, p) not in obs:
                    return np.nan
                y, s = obs[(r, p)]
                vals.append(y - fe.predict(r, p, s))
            return float(np.mean(vals))

        t, z, pz = [], [], []
        for r, F, q0 in zip(m.region_id, m.F, m.q0):
            ps = windows(kind, F, q0, offs)
            tv = tau_at(r, ps) if r in fe.g.index else np.nan
            t.append(tv)
            z.append(sign * tv / sigma)
            pps = windows(kind, F - PLACEBO_SHIFT, q0 - 4 * PLACEBO_SHIFT, offs)
            pz.append(sign * np.mean([loo[(r, x)] for x in pps]) / sigma if all((r, x) in loo for x in pps) else np.nan)
        rows['tau'][ind], rows['z'][ind], rows['placebo_z'][ind] = t, z, pz
        # null: every council-FY whose window is clean, pseudo q0 = first quarter of that FY
        nz = {}
        for r in sorted(set(c.region_id)):
            for Fp in range(2013, 2026):
                ps = windows(kind, Fp, pd.Period(f'{Fp}Q3', 'Q'), offs)
                if all((r, x) in loo for x in ps):
                    nz[(r, Fp)] = sign * np.mean([loo[(r, x)] for x in ps]) / sigma
        nulls[ind] = nz
    return rows, nulls, sig, fits


# ------------------------------------------------------------------ aggregation
def rank_y(ind_vals, dl_rank, inds):
    """v1 aggregation: rank each indicator across rows, pillar = mean of ranks, Y = mean of >= 2 pillars."""
    R = pd.DataFrame({i: pd.Series(ind_vals[i]).rank(pct=True) for i in inds})
    pil = {}
    for p in ('IL', 'FP', 'SL'):
        cols = [i for i in inds if PILLAR[i] == p]
        pil[p] = R[cols].mean(axis=1, skipna=True)
    P = pd.DataFrame(pil)
    P.insert(0, 'DL', dl_rank.to_numpy())
    S = P[['IL', 'FP', 'SL']].mean(axis=1, skipna=True).where(P[['IL', 'FP', 'SL']].notna().sum(axis=1) >= 2)
    Y = P.mean(axis=1, skipna=True).where(P.notna().sum(axis=1) >= 2)
    return P, S, Y


PILLAR = {i[0]: i[1] for i in INDICATORS}
SIGN = {i[0]: i[2] for i in INDICATORS}


def z_signal(zvals, inds):
    Z = pd.DataFrame({i: zvals[i] for i in inds})
    pil = pd.DataFrame({p: Z[[i for i in inds if PILLAR[i] == p]].mean(axis=1, skipna=True) for p in ('IL', 'FP', 'SL')})
    return pil.mean(axis=1, skipna=True).where(pil.notna().sum(axis=1) >= 2), pil


def boot_rho(x, y, g, rng, n=N_BOOT):
    d = pd.DataFrame({'x': np.asarray(x, float), 'y': np.asarray(y, float), 'g': np.asarray(g)}).dropna()
    est = spearmanr(d.x, d.y)[0]
    gs = [sub[['x', 'y']].to_numpy() for _, sub in d.groupby('g')]
    bs = []
    for _ in range(n):
        a = np.vstack([gs[i] for i in rng.integers(0, len(gs), len(gs))])
        bs.append(spearmanr(a[:, 0], a[:, 1])[0])
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return len(d), est, lo, hi


def boot_diff(x1, x2, y, g, rng, n=N_BOOT):
    d = pd.DataFrame({'a': x1, 'b': x2, 'y': y, 'g': g}).dropna()
    est = spearmanr(d.a, d.y)[0] - spearmanr(d.b, d.y)[0]
    gs = [sub[['a', 'b', 'y']].to_numpy() for _, sub in d.groupby('g')]
    bs = []
    for _ in range(n):
        a = np.vstack([gs[i] for i in rng.integers(0, len(gs), len(gs))])
        bs.append(spearmanr(a[:, 0], a[:, 2])[0] - spearmanr(a[:, 1], a[:, 2])[0])
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return len(d), est, lo, hi


def boot_mean(v, g, rng, n=N_BOOT):
    d = pd.DataFrame({'v': v, 'g': g}).dropna()
    if len(d) < 3:
        return len(d), (d.v.mean() if len(d) else np.nan), np.nan, np.nan
    gs = [sub.v.to_numpy() for _, sub in d.groupby('g')]
    bs = [np.concatenate([gs[i] for i in rng.integers(0, len(gs), len(gs))]).mean() for _ in range(n)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return len(d), d.v.mean(), lo, hi


# ------------------------------------------------------------------ main
def main():
    rng = np.random.default_rng(SEED)
    m, ly = load()
    groups = olg_groups(ly)
    aff, master, fire_fy = affected_fys(m)
    bad = aff | master
    panels = series(ly, groups)
    m = m.merge(groups[['region_id', 'group', 'cls']], on='region_id', how='left')
    print('master rows', len(m), 'without OLG group', m.group.isna().sum())
    print('affected council-FYs', len(aff), 'master council-FYs', len(master))

    # v1 sanity: rebuild v1 Y from the master's rank columns
    v1P = pd.DataFrame({'DL': m.DL, 'IL': m.IL, 'FP': m.FP, 'SL': m.SL})
    v1S = v1P[['IL', 'FP', 'SL']].mean(axis=1).where(v1P[['IL', 'FP', 'SL']].notna().sum(axis=1) >= 2)
    assert np.allclose(v1P.mean(axis=1).where(v1P.notna().sum(axis=1) >= 2), m.Y, equal_nan=True)
    dl_rank = m.DL                      # DL pillar = rank of homes destroyed per 1,000 dwellings (unchanged)

    res, crit, plac, all_rows, sigmas = {}, [], [], {}, {}
    base_inds = [i[0] for i in INDICATORS if i[0] != 'night_lights']
    for vname, (mode, ntl) in VARIANTS.items():
        key = mode
        if key not in res:
            res[key] = run_variant(vname, mode, panels, groups, m, bad)
        rows, nulls, sig, _ = res[key]
        sigmas[mode] = sig
        inds = base_inds + (['night_lights'] if ntl else [])
        oriented = {i: SIGN[i] * np.asarray(rows['tau'][i]) for i in inds}
        P, S, Y = rank_y(oriented, dl_rank, inds)
        pP, pS, _ = rank_y({i: np.asarray(rows['placebo_z'][i]) for i in inds}, pd.Series(np.nan, index=m.index), inds)
        all_rows[vname] = dict(P=P, S=S, Y=Y, pS=pS, inds=inds, mode=mode)
        n, e, lo, hi = boot_rho(S, m.share, m.region_id, rng)
        nd, ed, lod, hid = boot_diff(S, v1S, m.share, m.region_id, rng)
        pn, pe, plo, phi = boot_rho(pS, m.share, m.region_id, rng)
        crit.append(dict(variant=vname, rows=n, rho_S_share=e, ci_low=lo, ci_high=hi,
                         diff_vs_V1=ed, diff_ci_low=lod, diff_ci_high=hid, diff_rows=nd,
                         placebo_rows=pn, placebo_rho=pe, placebo_ci_low=plo, placebo_ci_high=phi,
                         placebo_pass=bool(plo <= 0 <= phi)))
    n, e, lo, hi = boot_rho(v1S, m.share, m.region_id, rng)
    crit.insert(0, dict(variant='V1', rows=n, rho_S_share=e, ci_low=lo, ci_high=hi))
    crit = pd.DataFrame(crit)
    crit.to_csv(OUT / 'CRITERION.csv', index=False)
    print(crit.round(3).to_string())

    ok = crit[(crit.variant != 'V1') & (crit.placebo_pass == True)]  # noqa: E712
    best = ok.sort_values('rho_S_share', ascending=False).iloc[0] if len(ok) else None
    v1rho = crit.loc[crit.variant == 'V1', 'rho_S_share'].iloc[0]
    chosen = best.variant if best is not None and best.rho_S_share > v1rho else 'V1'
    print('CHOSEN:', chosen)
    json.dump(dict(chosen=chosen, rule='highest rho(S, share) among V2 variants passing placebo; V1 if none beats it',
                   v1_rho=float(v1rho)), open(OUT / 'CHOICE.json', 'w'), indent=2)
    json.dump({k: v for k, v in sigmas.items()}, open(OUT / 'NOISE_SCALES.json', 'w'), indent=2)

    # ---------------- per-row output for every variant (tau, z, placebo) and the chosen Y2
    out = m[['agrn', 'region_id', 'region_name', 'group', 'cls', 'first_fire_start', 'F', 'share',
             'DL_homes_destroyed_in_council', 'DL_homes_destroyed_per_1000_dwellings', 'SL_deaths_sourced',
             'info_reported_deaths', 'Y', 'Y_class', 'DL', 'IL', 'FP', 'SL']].copy()
    out = out.rename(columns={'Y': 'Y_v1', 'Y_class': 'Y_class_v1', 'DL': 'DL_v1', 'IL': 'IL_v1', 'FP': 'FP_v1',
                              'SL': 'SL_v1'})
    out['S_v1'] = v1S
    for mode in res:
        rows = res[mode][0]
        for i in rows['tau']:
            out[f'tau_{i}_{mode}'] = rows['tau'][i]
            out[f'z_{i}_{mode}'] = rows['z'][i]
            out[f'placebo_z_{i}_{mode}'] = rows['placebo_z'][i]
    for v, d in all_rows.items():
        out[f'S_{v}'] = d['S'].to_numpy()
        out[f'Y_{v}'] = d['Y'].to_numpy()
        out[f'placebo_S_{v}'] = d['pS'].to_numpy()
    if chosen != 'V1':
        d = all_rows[chosen]
        rows, nulls, _, _ = res[d['mode']]
        for p in ('DL', 'IL', 'FP', 'SL'):
            out[f'{p}_v2'] = d['P'][p].to_numpy()
        out['Y_v2'] = d['Y'].to_numpy()
        out['S_v2'] = d['S'].to_numpy()
        # z-signal and severity classes anchored to the null (pseudo fires at clean council-FYs)
        zS, zpil = z_signal({i: np.asarray(rows['z'][i]) for i in d['inds']}, d['inds'])
        out['S_z'] = zS.to_numpy()
        for p in ('IL', 'FP', 'SL'):
            out[f'{p}_z'] = zpil[p].to_numpy()
        keys = sorted(set().union(*[set(nulls[i]) for i in d['inds']]))
        nullz = {i: np.array([nulls[i].get(k, np.nan) for k in keys]) for i in d['inds']}
        nS, _ = z_signal(nullz, d['inds'])
        nS = nS.dropna().to_numpy()
        q90, q975, q995 = np.percentile(nS, [90, 97.5, 99.5])
        json.dump(dict(null_n=int(len(nS)), null_mean=float(nS.mean()), null_sd=float(nS.std(ddof=1)),
                       p90=float(q90), p975=float(q975), p995=float(q995)), open(OUT / 'NULL_THRESHOLDS.json', 'w'),
                  indent=2)
        pd.DataFrame({'region_id': [k[0] for k in keys], 'pseudo_F': [k[1] for k in keys],
                      **{f'z_{i}': nullz[i] for i in d['inds']}}).to_csv(OUT / 'NULL_PSEUDO_FIRES.csv', index=False)
        base = np.select([out.S_z >= q995, out.S_z >= q975, out.S_z >= q90], [4, 3, 2], 1).astype(float)
        base[out.S_z.isna().to_numpy()] = np.nan
        homes = out.DL_homes_destroyed_in_council
        deaths = out.SL_deaths_sourced.fillna(out.info_reported_deaths)
        cls = pd.Series(base, index=out.index)
        one = (deaths >= 1) & (deaths < 2)
        cls = cls.where(~one, np.fmin(np.fmax(cls, cls + 1), np.fmax(cls, 3)))
        cls = cls.where(~((homes >= 10) | (deaths >= 2)), np.fmax(cls, 3))
        cls = cls.where(~(homes >= 100), 4)
        # rows without a socioeconomic signal but with a direct-loss floor still get a class
        cls = cls.where(cls.notna() | ~((homes >= 10) | (deaths >= 1)),
                        np.select([homes >= 100, (homes >= 10) | (deaths >= 2), deaths >= 1], [4, 3, 2], np.nan))
        out['Y_class_v2_from_signal'] = base
        out['Y_class_v2'] = cls
    out.to_csv(OUT / 'ROWS_Y2.csv', index=False)

    # ---------------- per-indicator dose response (both counterfactuals) and v1 comparison
    out['bin'] = pd.cut(out.share, BINS, labels=BIN_LABELS, right=False)
    rows_ind = []
    for mode in res:
        for ind, pillar, sign, kind, offs, v1col in INDICATORS:
            z = out[f'z_{ind}_{mode}']
            n, e, lo, hi = boot_rho(z, out.share, out.region_id, rng)
            pn, pe, plo, phi = boot_rho(out[f'placebo_z_{ind}_{mode}'], out.share, out.region_id, rng)
            rec = dict(counterfactual=mode, indicator=ind, pillar=pillar, rows=n, rho_share=e, ci_low=lo, ci_high=hi,
                       placebo_rows=pn, placebo_rho=pe, placebo_ci_low=plo, placebo_ci_high=phi)
            for b in BIN_LABELS:
                sel = out.bin == b
                k, mu, blo, bhi = boot_mean(z[sel], out.region_id[sel], rng)
                rec.update({f'z_mean_{b}': mu, f'z_lo_{b}': blo, f'z_hi_{b}': bhi, f'n_{b}': k})
            rows_ind.append(rec)
    for ind in V1_RANK:
        n, e, lo, hi = boot_rho(m[V1_RANK[ind]], m.share, m.region_id, rng)
        rows_ind.append(dict(counterfactual='v1', indicator=ind, pillar=PILLAR[ind], rows=n, rho_share=e, ci_low=lo,
                             ci_high=hi))
    n, e, lo, hi = boot_rho(-m['info_ntl_mean_exfire_yoy_pct_qp1_excess'], m.share, m.region_id, rng)
    rows_ind.append(dict(counterfactual='v1', indicator='night_lights', pillar='IL', rows=n, rho_share=e, ci_low=lo,
                         ci_high=hi))
    pd.DataFrame(rows_ind).to_csv(OUT / 'INDICATOR_DOSE_RESPONSE.csv', index=False)

    # ---------------- Black Summer split and composite by bin for V1 and chosen
    bs = out.agrn == '871'
    rows_split = []
    for v in ['V1'] + list(VARIANTS):
        S = out['S_v1'] if v == 'V1' else out[f'S_{v}']
        for lab, sel in {'all': np.ones(len(out), bool), 'Black Summer': bs, 'excluding Black Summer': ~bs,
                         'share >= 1%': out.share >= .01, 'share >= 1%, excl. Black Summer': (out.share >= .01) & ~bs}.items():
            n, e, lo, hi = boot_rho(S[sel], out.share[sel], out.region_id[sel], rng)
            rows_split.append(dict(variant=v, subset=lab, rows=n, rho_S_share=e, ci_low=lo, ci_high=hi))
    pd.DataFrame(rows_split).to_csv(OUT / 'CRITERION_SPLITS.csv', index=False)

    # ---------------- event-study profile for councils >= 20% burned (chosen counterfactual, or group if V1)
    mode = all_rows[chosen]['mode'] if chosen != 'V1' else 'group'
    fits = res[mode][3]
    prof = []
    big = m[m.share >= 0.20]
    for ind, pillar, sign, kind, offs, _ in INDICATORS:
        d = panels[ind]
        obs = {(r, p): (y, s) for r, p, y, s in zip(d.region_id, d.period, d.y, d.season)}
        fe = fits[ind]
        d2 = d.copy()
        d2['clean'] = ~unclean(d2, bad)
        c = d2[d2.clean].reset_index(drop=True)
        loo = {(r, p): v for r, p, v in zip(c.region_id, c.period, fe.loo)}
        for r, F, q0 in zip(big.region_id, big.F, big.q0):
            for rel in range(-3, 4):
                if kind == 'q':
                    ps = [q0 + 1 + 4 * rel + k for k in range(-1, 3)]      # 4 quarters centred on the window
                else:
                    ps = [windows(kind, F, q0, [offs[0]])[0] + rel]
                vals = []
                for p in ps:
                    if (r, p) in loo:
                        vals.append(loo[(r, p)])
                    elif (r, p) in obs:
                        y, s = obs[(r, p)]
                        pr = fe.predict(r, p, s)
                        if np.isfinite(pr):
                            vals.append(y - pr)
                if vals:
                    prof.append(dict(indicator=ind, region_id=r, rel=rel, z=sign * np.mean(vals) / sigmas[mode][ind]['sigma']))
    prof = pd.DataFrame(prof)
    prof.to_csv(OUT / 'EVENT_PROFILE_ROWS.csv', index=False)
    summ = []
    for (ind, rel), sub in prof.groupby(['indicator', 'rel']):
        k, mu, lo, hi = boot_mean(sub.z, sub.region_id, rng)
        summ.append(dict(indicator=ind, rel=rel, councils=k, z_mean=mu, ci_low=lo, ci_high=hi))
    pd.DataFrame(summ).to_csv(OUT / 'EVENT_PROFILE.csv', index=False)
    print(pd.DataFrame(summ).pivot_table(index='indicator', columns='rel', values='z_mean').round(2))


if __name__ == '__main__':
    main()
