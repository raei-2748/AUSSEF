"""Experiment 13 shared model code (PRESPEC.md section 2). Every channel script calls run_channel().

panel columns required: unit (str), year (int, financial year labelled by its starting year), y (outcome).
Dose tables come from exposure/out/dose_<unit>.parquet (unit, fy, H, R, S).
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyfixest as pf
from scipy import stats

E13 = Path(__file__).resolve().parent
EXP = E13 / 'exposure/out'
BS = 2019              # Black Summer fire year (July 2019 - June 2020)
P_LAST_FIRE = 2018     # sample P: fires up to 2018-19
SCALE = 0.1            # per 10 percentage points


def check_lock():
    lock = (E13 / 'LOCK.txt').read_text().split()
    h = hashlib.sha256((E13 / 'PRESPEC.md').read_bytes()).hexdigest()
    assert h in lock, 'PRESPEC.md changed after the lock'


def load_dose(unit_kind, col='H'):
    d = pd.read_parquet(EXP / f'dose_{unit_kind}.parquet')
    d['unit'] = d.unit.astype(str)
    return {(u, int(f)): float(v) for u, f, v in zip(d.unit, d.fy, d[col])}


def load_units(unit_kind):
    u = pd.read_parquet(EXP / f'units_{unit_kind}.parquet')
    u['unit'] = u.unit.astype(str)
    return u


def add_regions(panel, unit_kind):
    u = load_units(unit_kind)[['unit', 'SA3', 'SA4', 'GCCSA', 'dwellings', 'persons']]
    p = panel.merge(u, on='unit', how='inner')
    return p[p.dwellings > 0].copy()


def _g(D, u, f):
    return D.get((u, f), 0.0)


def design(p, D, sample, kind='main', binary=False):
    """Adds regressor columns; returns (p, names of the BS/primary lags, names of controls)."""
    p = p.copy()
    T = (lambda v: float(v >= 0.10)) if binary else (lambda v: v)
    u, yr = p.unit.values, p.year.values
    main, ctrl = [], []
    if sample == 'P':
        if kind == 'main':
            for k in range(4):
                c = f'd{k}'
                p[c] = [T(_g(D, a, y - k)) if y - k <= P_LAST_FIRE else 0.0 for a, y in zip(u, yr)]
                main.append(c)
        else:   # placebo: fake fire 2 years before each real fire, fake lags 0 and 1
            for k in range(2):
                c = f'f{k}'
                p[c] = [T(_g(D, a, y - k + 2)) if y - k + 2 <= P_LAST_FIRE else 0.0 for a, y in zip(u, yr)]
                main.append(c)
            # drop area-years within 0-3 years after a real fire year with H >= 0.001
            post = [any(_g(D, a, y - k) >= 0.001 for k in range(4)) for a, y in zip(u, yr)]
            p = p[~np.array(post)].copy()
    else:
        if kind == 'main':
            K = int(p.year.max()) - BS
            for k in range(0, K + 1):
                c = f'bs{k}'
                p[c] = [T(_g(D, a, BS)) if y - k == BS else 0.0 for a, y in zip(p.unit.values, p.year.values)]
                main.append(c)
        else:
            p = p[p.year <= BS - 1].copy()
            for k in range(2):
                c = f'fbs{k}'
                p[c] = [T(_g(D, a, BS)) if y - k == BS - 2 else 0.0 for a, y in zip(p.unit.values, p.year.values)]
                main.append(c)
        for k in range(4):
            c = f'o{k}'
            p[c] = [T(_g(D, a, y - k)) if y - k != BS else 0.0 for a, y in zip(p.unit.values, p.year.values)]
            ctrl.append(c)
    keep = [c for c in main + ctrl if p[c].abs().sum() > 0]
    return p, [c for c in main if c in keep], [c for c in ctrl if c in keep]


def fit(p, names, ctrl, model, fe='SA4'):
    fe_term = 'unit + SA4^year' if fe == 'SA4' else 'unit + GCCSA^year'
    fml = f"y ~ {' + '.join(names + ctrl)} | {fe_term}"
    p = p.copy()
    p['SA4'] = p.SA4.astype(str)
    p['GCCSA'] = p.GCCSA.astype(str)
    if model == 'ols':
        m = pf.feols(fml, data=p, vcov={'CRV1': 'SA3'})
    else:
        m = pf.fepois(fml, data=p, vcov={'CRV1': 'SA3'})
    return m


def combo(m, cols, w=None):
    """Linear combination (default average) of coefficients; returns est, se, df."""
    b = m.coef()
    V = m._vcov
    names = list(b.index)
    w = np.ones(len(cols)) / len(cols) if w is None else np.asarray(w, float)
    a = np.zeros(len(names))
    for c, wi in zip(cols, w):
        a[names.index(c)] = wi
    est = float(a @ b.values)
    se = float(np.sqrt(a @ V @ a))
    G = getattr(m, '_G', None)
    G = int(G[0]) if isinstance(G, (list, tuple, np.ndarray)) else (int(G) if G else None)
    return est, se, (G - 1 if G else 1e6)


def summarise(est, se, df, scale_kind):
    """Per-10pp effect with CI. scale_kind: 'log' or 'pois' -> % change; 'level' -> units of y."""
    t = stats.t.ppf(0.975, df)
    lo, hi = est - t * se, est + t * se
    p = 2 * stats.t.sf(abs(est / se), df) if se > 0 else np.nan
    if scale_kind in ('log', 'pois'):
        f = lambda x: 100 * (np.exp(SCALE * x) - 1)          # noqa: E731
        f1 = lambda x: 100 * (np.exp(x) - 1)                  # noqa: E731
    else:
        f = lambda x: SCALE * x                               # noqa: E731
        f1 = lambda x: x                                      # noqa: E731
    return dict(per10=f(est), lo=f(lo), hi=f(hi), full=f1(est), full_lo=f1(lo), full_hi=f1(hi), p=p, coef=est, se=se,
                df=df)


def run_channel(panel, unit_kind, model, scale_kind, sample, dose='H', fe='SA4', binary=False, extra=None):
    """Main estimate (avg of k=1,2), time path, and placebo for one outcome/sample."""
    D = load_dose(unit_kind, dose)
    p0 = add_regions(panel, unit_kind)
    out = dict(sample=sample, dose=dose, fe=fe, binary=binary, model=model, n_units=int(p0.unit.nunique()),
               years=f'{int(p0.year.min())}-{int(p0.year.max())}', **(extra or {}))
    p, names, ctrl = design(p0, D, sample, 'main', binary)
    pre = 'd' if sample == 'P' else 'bs'
    m = fit(p, names, ctrl, model, fe)
    k12 = [f'{pre}1', f'{pre}2']
    if all(c in m.coef().index for c in k12):
        out.update({f'main_{k}': v for k, v in summarise(*combo(m, k12), scale_kind).items()})
    out['n_obs'] = int(m._N)
    out['n_exposed_units'] = int(p.loc[p[names].abs().sum(axis=1) > 0, 'unit'].nunique())
    path = {}
    for c in names:
        if c in m.coef().index:
            s = summarise(*combo(m, [c]), scale_kind)
            path[c] = dict(per10=s['per10'], lo=s['lo'], hi=s['hi'])
    out['path'] = path
    # placebo
    pp, pn, pc = design(p0, D, sample, 'placebo', binary)
    try:
        mp = fit(pp, pn, pc, model, fe)
        cols = [c for c in pn if c in mp.coef().index]
        s = summarise(*combo(mp, cols), scale_kind)
        out.update({f'placebo_{k}': v for k, v in s.items()})
        out['placebo_terms'] = cols
        out['placebo_n_obs'] = int(mp._N)
    except Exception as e:  # noqa: BLE001
        out['placebo_error'] = repr(e)[:300]
    return out


def holm(pvals):
    p = np.asarray(pvals, float)
    o = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    run = 0.0
    for i, idx in enumerate(o):
        run = max(run, (m - i) * p[idx])
        adj[idx] = min(1.0, run)
    return adj


def save(obj, path):
    Path(path).write_text(json.dumps(obj, indent=1, default=float))
