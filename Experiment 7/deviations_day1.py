"""Experiment 7, Day 1 deviations (written AFTER the locked result; listed as deviations in FINDINGS_DAY1.md).

The locked rule kept V1: every V2 counterfactual failed its placebo, and the event profile showed pre-fire drifts
(income support) and fire-light contamination (night lights). Three follow-ups, all still free of pre-fire predictors:

D1  Trend-robust counterfactual: V2b plus a council-specific linear trend, night lights dropped. Same placebo gate.
D2  Average effects by fire size (stacked event study): for each indicator, post-fire change relative to the
    council's own pre-fire years (tau at rel 0..1 minus mean LOO residual at rel -3..-1), by burned-share bin.
    Rows with < 1% burned are the negative control. DL added for reference.
D3  Noise budget: the effect one council-year would need to stand out from normal variation (2 sigma), in
    natural units, next to the effect sizes the literature reports.

Run: python3 deviations_day1.py   (after build_y2.py)
"""
import json

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import build_y2 as B

OUT = B.OUT


class FETrend(B.FE):
    """B.FE plus a council-specific linear time trend (numeric column ('d', council))."""

    def __init__(self, d, groups, mode, quarterly):
        self.t0 = self._t(d.period).mean()
        super().__init__(d, groups, mode, quarterly)

    @staticmethod
    def _t(periods):
        return np.array([p.ordinal / 4 if hasattr(p, 'ordinal') else float(p) for p in periods])

    def _keys(self, r, p, season):
        return super()._keys(r, p, season) + [('d', r)]

    def _X(self, d):
        X = np.zeros((len(d), len(self.names)))
        t = self._t(d.period) - self.t0
        for i, (r, p, s) in enumerate(zip(d.region_id, d.period, d.season)):
            for k in super()._keys(r, p, s):
                X[i, self.ix[k]] = 1.0
            X[i, self.ix[('d', r)]] = t[i]
        return X

    def predict(self, r, p, season):
        base = super()._keys(r, p, season)
        if any(k not in self.ix for k in base + [('d', r)]):
            return np.nan
        t = self._t([p])[0] - self.t0
        return float(sum(self.beta[self.ix[k]] for k in base) + self.beta[self.ix[('d', r)]] * t)


INDS = [i for i in B.INDICATORS if i[0] != 'night_lights']


def fit_all(FEcls, panels, groups, m, bad):
    """tau / z / placebo z per master row plus per-indicator fits and LOO dictionaries."""
    res = {}
    for ind, pillar, sign, kind, offs, _ in INDS:
        d = panels[ind].copy()
        d['clean'] = ~B.unclean(d, bad)
        c = d[d.clean].reset_index(drop=True)
        fe = FEcls(c, groups, 'group', kind == 'q')
        loo = {(r, p): v for r, p, v in zip(c.region_id, c.period, fe.loo)}
        obs = {(r, p): (y, s) for r, p, y, s in zip(d.region_id, d.period, d.y, d.season)}
        wins = []
        for r, p in loo:
            ps = [p + (o - offs[0]) for o in offs]
            if all((r, x) in loo for x in ps):
                wins.append(np.mean([loo[(r, x)] for x in ps]))
        sigma = float(np.std(wins, ddof=1))

        def resid(r, p):
            if (r, p) in loo:
                return loo[(r, p)]
            if (r, p) in obs:
                y, s = obs[(r, p)]
                pr = fe.predict(r, p, s)
                return y - pr if np.isfinite(pr) else np.nan
            return np.nan

        tau, pz, pre, post = [], [], [], []
        for r, F, q0 in zip(m.region_id, m.F, m.q0):
            ps = B.windows(kind, F, q0, offs)
            v = [obs[(r, p)][0] - fe.predict(r, p, obs[(r, p)][1]) if (r, p) in obs else np.nan for p in ps]
            tau.append(np.mean(v))
            pps = B.windows(kind, F - B.PLACEBO_SHIFT, q0 - 4 * B.PLACEBO_SHIFT, offs)
            pz.append(sign * np.mean([loo[(r, x)] for x in pps]) / sigma if all((r, x) in loo for x in pps) else np.nan)
            # event-time residuals (annual steps; quarterly = mean of the 4 quarters of that relative year)
            def rel_val(rel):
                if kind == 'q':
                    vals = [resid(r, q0 + 1 + 4 * rel + k) for k in range(-1, 3)]
                else:
                    vals = [resid(r, B.windows(kind, F, q0, [offs[0]])[0] + rel)]
                vals = [x for x in vals if np.isfinite(x)]
                return np.mean(vals) if vals else np.nan
            pre.append(np.nanmean([rel_val(k) for k in (-3, -2, -1)]) if any(np.isfinite(rel_val(k)) for k in (-3, -2, -1)) else np.nan)
            post.append(np.nanmean([rel_val(k) for k in (0, 1)]) if any(np.isfinite(rel_val(k)) for k in (0, 1)) else np.nan)
        res[ind] = dict(tau=np.array(tau), z=sign * np.array(tau) / sigma, placebo_z=np.array(pz), sigma=sigma,
                        pre=np.array(pre), post=np.array(post), sign=sign)
    return res


def main():
    rng = np.random.default_rng(B.SEED + 1)
    m, ly = B.load()
    groups = B.olg_groups(ly)
    aff, master, _ = B.affected_fys(m)
    bad = aff | master
    panels = B.series(ly, groups)
    m = m.merge(groups[['region_id', 'group']], on='region_id', how='left')
    v1S = pd.DataFrame({'IL': m.IL, 'FP': m.FP, 'SL': m.SL}).mean(axis=1).where(
        m[['IL', 'FP', 'SL']].notna().sum(axis=1) >= 2)

    out = {}
    for label, cls in (('V2b_noNTL', B.FE), ('V2c_trend', FETrend)):
        r = fit_all(cls, panels, groups, m, bad)
        inds = [i[0] for i in INDS]
        oriented = {i: r[i]['sign'] * r[i]['tau'] for i in inds}
        P, S, Y = B.rank_y(oriented, m.DL, inds)
        pP, pS, _ = B.rank_y({i: r[i]['placebo_z'] for i in inds}, pd.Series(np.nan, index=m.index), inds)
        crit = dict(variant=label)
        crit['rows'], crit['rho_S_share'], crit['ci_low'], crit['ci_high'] = B.boot_rho(S, m.share, m.region_id, rng)
        _, crit['diff_vs_V1'], crit['diff_ci_low'], crit['diff_ci_high'] = B.boot_diff(S, v1S, m.share, m.region_id, rng)
        crit['placebo_rows'], crit['placebo_rho'], crit['placebo_ci_low'], crit['placebo_ci_high'] = \
            B.boot_rho(pS, m.share, m.region_id, rng)
        crit['placebo_pass'] = bool(crit['placebo_ci_low'] <= 0 <= crit['placebo_ci_high'])
        per = []
        for i in inds:
            n, e, lo, hi = B.boot_rho(r[i]['z'], m.share, m.region_id, rng)
            pn, pe, plo, phi = B.boot_rho(r[i]['placebo_z'], m.share, m.region_id, rng)
            per.append(dict(variant=label, indicator=i, rows=n, rho_share=e, ci_low=lo, ci_high=hi, placebo_rows=pn,
                            placebo_rho=pe, placebo_ci_low=plo, placebo_ci_high=phi, sigma=r[i]['sigma']))
        out[label] = dict(res=r, crit=crit, per=pd.DataFrame(per), S=S, Y=Y, P=P)
    crit = pd.DataFrame([o['crit'] for o in out.values()])
    crit.to_csv(OUT / 'DEV_D1_CRITERION.csv', index=False)
    pd.concat([o['per'] for o in out.values()]).to_csv(OUT / 'DEV_D1_INDICATORS.csv', index=False)
    print(crit.round(3).to_string())
    print(pd.concat([o['per'] for o in out.values()]).round(2).to_string())

    # ---------------- D2: average pre->post change by burned-share bin, both counterfactuals
    bins = pd.cut(m.share, B.BINS, labels=B.BIN_LABELS, right=False)
    rows = []
    for label, o in out.items():
        for i, r in o['res'].items():
            did = r['sign'] * (r['post'] - r['pre']) / r['sigma']          # + = worse, in SD of normal variation
            for b in B.BIN_LABELS + ['>=5%']:
                sel = (bins == b) if b != '>=5%' else (m.share >= 0.05)
                k, mu, lo, hi = B.boot_mean(did[sel.to_numpy()], m.region_id[sel.to_numpy()], rng)
                raw = r['sign'] * (r['post'] - r['pre'])
                rows.append(dict(variant=label, indicator=i, bin=b, rows=k, change_sd=mu, ci_low=lo, ci_high=hi,
                                 change_natural_units=float(np.nanmean(raw[sel.to_numpy()])) if k else np.nan))
    d2 = pd.DataFrame(rows)
    d2.to_csv(OUT / 'DEV_D2_AVERAGE_EFFECTS.csv', index=False)
    t = d2[d2.variant == 'V2c_trend'].copy()
    t['cell'] = t.change_sd.round(2).astype(str) + ' [' + t.ci_low.round(2).astype(str) + ', ' + t.ci_high.round(2).astype(str) + '] n=' + t.rows.astype(str)
    print(t.pivot_table(index='indicator', columns='bin', values='cell', aggfunc='first').to_string())
    t = d2[d2.variant == 'V2b_noNTL'].copy()
    t['cell'] = t.change_sd.round(2).astype(str) + ' [' + t.ci_low.round(2).astype(str) + ', ' + t.ci_high.round(2).astype(str) + '] n=' + t.rows.astype(str)
    print(t.pivot_table(index='indicator', columns='bin', values='cell', aggfunc='first').to_string())

    # DL by bin (homes destroyed per 1,000 dwellings; rows with a figure)
    dl = []
    for b in B.BIN_LABELS:
        sel = (bins == b).to_numpy()
        k, mu, lo, hi = B.boot_mean(m.DL_homes_destroyed_per_1000_dwellings[sel], m.region_id[sel], rng)
        dl.append(dict(bin=b, rows=k, homes_destroyed_per_1000=mu, ci_low=lo, ci_high=hi))
    pd.DataFrame(dl).to_csv(OUT / 'DEV_D2_DL_BY_BIN.csv', index=False)
    print(pd.DataFrame(dl).round(2))

    # ---------------- D3: noise budget
    units = {'total_income': ('% of council total income', 100), 'biz_count': ('% of businesses', 100),
             'cash_cover': ('months of cash cover', 1), 'services_share': ('pp of spending', 1),
             'renewals_ratio': ('pp renewals ratio', 1), 'income_support': ('recipients per 1,000 residents', 1)}
    nb = []
    for i, r in out['V2c_trend']['res'].items():
        u, k = units[i]
        nb.append(dict(indicator=i, unit=u, sigma_one_council_year=r['sigma'] * k,
                       needed_to_stand_out_2sd=2 * r['sigma'] * k))
    pd.DataFrame(nb).to_csv(OUT / 'DEV_D3_NOISE_BUDGET.csv', index=False)
    print(pd.DataFrame(nb).round(2))

    rows = m[['agrn', 'region_id', 'region_name', 'share']].copy()
    for label, o in out.items():
        rows[f'S_{label}'] = o['S'].to_numpy()
        for i, r in o['res'].items():
            rows[f'z_{i}_{label}'] = r['z']
            rows[f'did_{i}_{label}'] = r['sign'] * (r['post'] - r['pre']) / r['sigma']
    rows.to_csv(OUT / 'DEV_ROWS.csv', index=False)


if __name__ == '__main__':
    main()
