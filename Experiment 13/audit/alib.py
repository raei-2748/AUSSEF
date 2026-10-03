# Audit's own helper code (independent of e13lib.py / run_channels.py)
import pandas as pd, numpy as np, pyfixest as pf
from scipy import stats
E = '../exposure/out/'
BS = 2019

def load_dose(level, var='H'):
    d = pd.read_parquet(E + f'dose_{level}.parquet')
    return {(u, int(f)): h for u, f, h in zip(d.unit.astype(str), d.fy, d[var])}

def units(level):
    u = pd.read_parquet(E + f'units_{level}.parquet'); u['unit'] = u.unit.astype(str)
    return u[u.dwellings > 0].set_index('unit')

def add_lags(p, D, sample, K_bs=3, placebo=False):
    """p has columns unit, year. Adds dose columns; returns (df, list of names, estimand names)."""
    p = p.copy(); h = lambda u, f: D.get((u, f), 0.0)
    names = []
    if sample == 'B':
        if not placebo:
            for k in range(K_bs + 1):
                p[f'bs{k}'] = [h(u, BS) if y - k == BS else 0.0 for u, y in zip(p.unit, p.year)]; names.append(f'bs{k}')
            est = ['bs1', 'bs2']
        else:
            for k in (0, 1):  # fake dose[a,t] = real dose[a,t+2]; fake lag k: fake dose at t=y-k = real at y-k+2
                p[f'fk{k}'] = [h(u, BS) if y - k + 2 == BS else 0.0 for u, y in zip(p.unit, p.year)]; names.append(f'fk{k}')
            est = ['fk0', 'fk1']
        for k in range(4):
            p[f'ot{k}'] = [h(u, y - k) if y - k != BS else 0.0 for u, y in zip(p.unit, p.year)]; names.append(f'ot{k}')
    else:  # P
        if not placebo:
            for k in range(4):
                p[f'd{k}'] = [h(u, y - k) if y - k <= 2018 else 0.0 for u, y in zip(p.unit, p.year)]; names.append(f'd{k}')
            est = ['d1', 'd2']
        else:
            for k in (0, 1):
                p[f'fk{k}'] = [h(u, y - k + 2) if y - k + 2 <= 2018 else 0.0 for u, y in zip(p.unit, p.year)]; names.append(f'fk{k}')
            est = ['fk0', 'fk1']
    return p, names, est

def p_placebo_drop(p, D, thr=0.001):
    keep = [not any(D.get((u, f), 0.0) >= thr for f in range(y - 3, y + 1)) for u, y in zip(p.unit, p.year)]
    return p[np.array(keep)]

def fit(p, yvar, names, est, model='ols', fe='unit + sa4yr'):
    p = p.reset_index(drop=True).copy(); p['sa4yr'] = p.SA4.astype(str) + '_' + p.year.astype(str)
    fml = f'{yvar} ~ ' + ' + '.join(names) + f' | {fe}'
    if model == 'ols':
        m = pf.feols(fml, data=p, vcov={'CRV1': 'SA3'})
    else:
        m = pf.fepois(fml, data=p, vcov={'CRV1': 'SA3'})
    b = m.coef(); V = m.vcov if hasattr(m, 'vcov') and not callable(m.vcov) else m._vcov
    V = pd.DataFrame(np.asarray(V), index=b.index, columns=b.index)
    miss = [e for e in est if e not in b.index]
    if miss:
        return dict(err=f'not identified (dropped: {miss})', n=m._N, coefs=b.to_dict())
    w = pd.Series(0.0, index=b.index); w[est] = 1 / len(est)
    c = float(w @ b); se = float(np.sqrt(w @ V @ w))
    used = m._data
    G = int(used.SA3.nunique())
    t = stats.t.ppf(0.975, G - 1)
    lo, hi = c - t * se, c + t * se
    pval = 2 * stats.t.sf(abs(c / se), G - 1)
    return dict(coef=c, se=se, lo=lo, hi=hi, p=pval, n=int(m._N), G=G, units=int(used.unit.nunique()), coefs=b.round(4).to_dict())

def pct(r):
    f = lambda x: 100 * (np.exp(0.1 * x) - 1)
    if 'err' in r: return r['err']
    return f"{f(r['coef']):+.2f}% [{f(r['lo']):+.2f}, {f(r['hi']):+.2f}]"

def lin(r, scale=0.1):
    if 'err' in r: return r['err']
    return f"{scale*r['coef']:+.3f} [{scale*r['lo']:+.3f}, {scale*r['hi']:+.3f}]"
