"""Experiment 7, Day 4: affected-people dose, pooled dose-response, quarterly welfare data, and (if a signal is
detected) per-fire empirical-Bayes estimates. Rules: PRESPEC_DAY4.md (LOCK_DAY4.txt).
Run: python3 day4_blurry.py"""
import json

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import build_y2 as B

OUT = B.OUT
rng = np.random.default_rng(20261001)
N_BOOT = 2000
INDS = [i for i in B.INDICATORS if i[0] != 'night_lights']


def paths(panels, groups, m, bad):
    """Per row and indicator: standardised post-minus-pre change and pre-trend, plus null SDs."""
    out = {}
    for ind, pillar, sign, kind, offs, _ in INDS:
        d = panels[ind].copy()
        d['clean'] = ~B.unclean(d, bad)
        c = d[d.clean].reset_index(drop=True)
        fe = B.FE(c, groups, 'group', kind == 'q')
        loo = {(r, p): v for r, p, v in zip(c.region_id, c.period, fe.loo)}
        obs = {(r, p): (y, s) for r, p, y, s in zip(d.region_id, d.period, d.y, d.season)}

        def resid(r, p):
            if (r, p) in loo:
                return loo[(r, p)]
            if (r, p) in obs:
                y, s = obs[(r, p)]
                pr = fe.predict(r, p, s)
                return y - pr if np.isfinite(pr) else np.nan
            return np.nan

        if kind == 'q':
            after, before, late, early = [1, 2], [-4, -3, -2, -1], [-1], [-4, -3, -2]
        else:
            after, before, late, early = [0, 1], [-3, -2, -1], [-1], [-3, -2]

        def base_of(F, q0):
            return q0 if kind == 'q' else B.windows(kind, F, q0, [offs[0]])[0]

        def change(r, b, fn, strict=False):
            a = [fn(r, b + k) for k in after]
            p = [fn(r, b + k) for k in before]
            pt_l = [fn(r, b + k) for k in late]
            pt_e = [fn(r, b + k) for k in early]
            if strict and not all(np.isfinite(a + p + pt_l + pt_e)):
                return np.nan, np.nan
            a, p = [x for x in a if np.isfinite(x)], [x for x in p if np.isfinite(x)]
            pl, pe = [x for x in pt_l if np.isfinite(x)], [x for x in pt_e if np.isfinite(x)]
            ch = np.mean(a) - np.mean(p) if a and p else np.nan
            pt = np.mean(pl) - np.mean(pe) if pl and pe else np.nan
            return ch, pt

        # null: every clean council-period used as a pseudo fire, all periods clean (LOO residuals only)
        lfn = lambda r, p: loo.get((r, p), np.nan)  # noqa: E731
        nch, npt = [], []
        for (r, p) in loo:
            ch, pt = change(r, p, lfn, strict=True)
            if np.isfinite(ch):
                nch.append(ch)
                npt.append(pt)
        sd_ch, sd_pt = np.std(nch, ddof=1), np.std(npt, ddof=1)
        ch_rows, pt_rows = [], []
        for r, F, q0 in zip(m.region_id, m.F, m.q0):
            ch, pt = change(r, base_of(F, q0), resid)
            ch_rows.append(sign * ch / sd_ch)
            pt_rows.append(sign * pt / sd_pt)
        out[ind] = dict(change=np.array(ch_rows), pretrend=np.array(pt_rows), sd_change=float(sd_ch),
                        sd_pretrend=float(sd_pt), null_n=len(nch), null_mean=float(np.mean(nch) / sd_ch))
    return out


def slope_boot(y, x, g, n=N_BOOT):
    d = pd.DataFrame({'y': y, 'x': x, 'g': g}).dropna()
    if len(d) < 10:
        return dict(rows=len(d))
    X = np.column_stack([np.ones(len(d)), d.x])
    b = np.linalg.lstsq(X, d.y, rcond=None)[0][1]
    gs = [s[['y', 'x']].to_numpy() for _, s in d.groupby('g')]
    bs = []
    for _ in range(n):
        a = np.vstack([gs[i] for i in rng.integers(0, len(gs), len(gs))])
        bs.append(np.linalg.lstsq(np.column_stack([np.ones(len(a)), a[:, 1]]), a[:, 0], rcond=None)[0][1])
    bs = np.array(bs)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    p = min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean()))
    return dict(rows=len(d), councils=int(d.g.nunique()), slope_per_10pp=float(b), ci_low=float(lo), ci_high=float(hi),
                p_boot=float(p), spearman=float(spearmanr(d.x, d.y)[0]))


def holm(ps):
    order = np.argsort(ps)
    adj = np.empty(len(ps))
    run = 0
    for k, i in enumerate(order):
        run = max(run, (len(ps) - k) * ps[i])
        adj[i] = min(1.0, run)
    return adj


def main():
    m, ly = B.load()
    groups = B.olg_groups(ly)
    aff, master, _ = B.affected_fys(m)
    panels = B.series(ly, groups)
    ap = pd.read_parquet(B.DATASET / 'data/enrich/affected_pop_event_council.parquet')
    ap['agrn'] = ap.agrn.astype(str)
    ap['region_id'] = ap.region_id.astype(str)
    m = m.merge(ap[['agrn', 'region_id', 'pop_in_fire', 'pop_within_1km']], on=['agrn', 'region_id'], how='left',
                validate='1:1')
    pop = ly.set_index(['region_id', 'year']).population
    m['pop_pre'] = [pop.get((r, F), np.nan) for r, F in zip(m.region_id, m.F)]
    m['dose'] = m.pop_within_1km / m.pop_pre
    m['dose_in'] = m.pop_in_fire / m.pop_pre
    print(m[['dose', 'dose_in', 'share']].describe().round(4).T)

    res = paths(panels, groups, m, aff | master)
    names = [i[0] for i in INDS]
    rows = []
    for ind in names:
        ch, pt = res[ind]['change'], res[ind]['pretrend']
        rec = dict(indicator=ind, null_mean_sd=res[ind]['null_mean'], null_n=res[ind]['null_n'])
        for lab, x in (('dose', m.dose * 10), ('dose_in', m.dose_in * 10), ('area_share', m.share * 10)):
            s = slope_boot(ch, x.to_numpy(), m.region_id.to_numpy())
            rec.update({f'{lab}_{k}': v for k, v in s.items()})
        s = slope_boot(pt, (m.dose * 10).to_numpy(), m.region_id.to_numpy())
        rec.update({f'pretrend_{k}': v for k, v in s.items()})
        nb = (m.agrn != '871').to_numpy()
        s = slope_boot(ch[nb], (m.dose * 10).to_numpy()[nb], m.region_id.to_numpy()[nb])
        rec.update({f'exclBS_{k}': v for k, v in s.items()})
        rows.append(rec)
    t = pd.DataFrame(rows)
    t['dose_p_holm'] = holm(t.dose_p_boot.to_numpy())
    t['detected'] = (t.dose_p_holm < 0.05) & (t.dose_slope_per_10pp > 0) & (t.pretrend_ci_low <= 0) & (t.pretrend_ci_high >= 0)
    Z = pd.DataFrame({i: res[i]['change'] for i in names})
    comp = Z.mean(axis=1).where(Z.notna().sum(axis=1) >= 3)
    Zp = pd.DataFrame({i: res[i]['pretrend'] for i in names})
    compp = Zp.mean(axis=1).where(Zp.notna().sum(axis=1) >= 3)
    c = dict(indicator='COMPOSITE')
    for lab, x in (('dose', m.dose * 10), ('dose_in', m.dose_in * 10), ('area_share', m.share * 10)):
        c.update({f'{lab}_{k}': v for k, v in slope_boot(comp.to_numpy(), x.to_numpy(), m.region_id.to_numpy()).items()})
    c.update({f'pretrend_{k}': v for k, v in slope_boot(compp.to_numpy(), (m.dose * 10).to_numpy(),
                                                        m.region_id.to_numpy()).items()})
    c['detected'] = bool(c['dose_p_boot'] < 0.05 and c['dose_slope_per_10pp'] > 0 and c['pretrend_ci_low'] <= 0 <= c['pretrend_ci_high'])
    t = pd.concat([t, pd.DataFrame([c])], ignore_index=True)
    t.to_csv(OUT / 'DAY4_POOLED.csv', index=False)
    show = ['indicator', 'dose_rows', 'dose_slope_per_10pp', 'dose_ci_low', 'dose_ci_high', 'dose_p_holm', 'dose_spearman',
            'pretrend_slope_per_10pp', 'pretrend_ci_low', 'pretrend_ci_high', 'area_share_slope_per_10pp',
            'exclBS_slope_per_10pp', 'exclBS_ci_low', 'exclBS_ci_high', 'detected']
    print(t[show].round(3).to_string())

    rowsout = m[['agrn', 'region_id', 'region_name', 'F', 'share', 'dose', 'dose_in']].copy()
    for i in names:
        rowsout[f'change_{i}'] = res[i]['change']
        rowsout[f'pretrend_{i}'] = res[i]['pretrend']
    rowsout['change_composite'] = comp.to_numpy()

    # ---- option 4: empirical Bayes per fire, only for detected outcomes
    det = [r.indicator for r in t.itertuples() if r.detected]
    eb_meta = {}
    for ind in det:
        y = (comp if ind == 'COMPOSITE' else pd.Series(res[ind]['change'])).to_numpy()
        x = (m.dose * 10).to_numpy()
        ok = np.isfinite(y) & np.isfinite(x)
        X = np.column_stack([np.ones(ok.sum()), x[ok]])
        beta = np.linalg.lstsq(X, y[ok], rcond=None)[0]
        prior = beta[0] + beta[1] * x
        noise = 1.0 if ind != 'COMPOSITE' else float(np.nanvar(Z[ok].mean(axis=1)) if False else 1.0)
        tau2 = max(0.0, float(np.var(y[ok] - prior[ok], ddof=2)) - noise)
        w = tau2 / (tau2 + noise)
        est = prior + w * (y - prior)
        sd = np.sqrt(w * noise) if tau2 > 0 else 0.0
        rowsout[f'EB_{ind}'] = np.where(ok, est, np.nan)
        rowsout[f'EB_{ind}_lo90'] = np.where(ok, est - 1.645 * sd, np.nan)
        rowsout[f'EB_{ind}_hi90'] = np.where(ok, est + 1.645 * sd, np.nan)
        eb_meta[ind] = dict(intercept=float(beta[0]), slope_per_10pp=float(beta[1]), tau2=tau2, weight_on_own_data=w)
    rowsout.to_csv(OUT / 'DAY4_ROWS.csv', index=False)
    json.dump(dict(detected=det, eb=eb_meta, sd={i: res[i]['sd_change'] for i in names}), open(OUT / 'DAY4_META.json', 'w'),
              indent=2)
    print('detected:', det, eb_meta)


if __name__ == '__main__':
    main()
