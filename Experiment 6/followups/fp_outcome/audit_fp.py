"""Part 1: audit of the existing FP pillar (fiscal pressure). Runs BEFORE the alternative definitions are frozen.

FP = mean of three percentile ranks:
  cash cover drawdown   -mean(FP_cash_cover_change_event_excess, FP_cash_cover_change_plus1_excess)
  services crowd-out    -FP_service_share_change_plus1_excess
  renewals ratio rise   +FP_renewals_ratio_change_plus1_excess
(each an 'excess' change: council change minus the median change in NSW councils with no fire >= 100 ha)

What is audited (nothing here touches damage, DL, the pre-fire score or any Y pillar other than FP itself):
  1. coverage of every component, by subset and by fire year
  2. noise: how large is the excess change relative to the normal movement of the same ratio in unburned councils
     (placebo distribution, same excess rule, year-matched), and how persistent/mean-reverting the ratios are
  3. agreement between the three components (rows with a fire, and unburned council-years as a placebo)
  4. mechanics: what each ratio co-moves with in unburned councils (grants, roads share), to flag sign ambiguity
Writes results/AUDIT.txt and results/AUDIT_*.csv.  Run: python3 audit_fp.py
"""
import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

from fpcommon import RESULTS, excess_for_rows, load_fire_flags, load_master, load_panel, wide

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 40)
lines = []


def log(s=''):
    print(s)
    lines.append(str(s))


# metric in the council fiscal panel, lag, kind, sign so that HIGHER = MORE PRESSURE (old FP convention)
COMP = {
    'cash_cover': ('cash_cover_months', 'diff', -1, 'months'),
    'service_share': ('service_share_pct', 'diff', -1, 'pp'),
    'renewals_ratio': ('building_infrastructure_renewals_ratio_pct', 'diff', +1, 'pp'),
    'operating_ratio': ('operating_ratio_pct', 'diff', -1, 'pp'),
    'own_source_rev': ('own_source_rev_aud', 'pct', -1, '%'),
}
LAGS = {0: 'event (FY t vs t-1)', 1: 'plus1 (FY t+1 vs t-1)'}


def unburned_excess(panel, flags, metric, lag, kind, window_before=0, window_after=None):
    """Placebo: excess change for every council-year with no fire >= 100 ha in FYs x-window_before .. x+lag(+after).
    Excess = change - year-matched median over comparison councils (the dataset's rule, without a fire row)."""
    tab = wide(panel, metric)
    after = lag if window_after is None else window_after
    rec = []
    for x in range(2013, 2024):
        if (x - 1) not in tab.columns or (x + lag) not in tab.columns:
            continue
        base = tab[x - 1]
        ch = (tab[x + lag] - base) if kind == 'diff' else (tab[x + lag] - base) / base.where(base > 0) * 100
        comp = [k for k in ch.index if not any((k, x + j) in flags for j in range(-window_before, after + 1))]
        med = float(ch.loc[comp].median())
        e = (ch.loc[comp] - med).dropna()
        rec += [(k, x, v, base.get(k, np.nan)) for k, v in e.items()]
    return pd.DataFrame(rec, columns=['key', 'fy', 'exc', 'level_pre'])


def robust_sd(v):
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    return 1.4826 * np.median(np.abs(v - np.median(v))) if len(v) else np.nan


def main():
    m, panel, flags = load_master(), load_panel(), load_fire_flags()
    # ---- rebuild the old FP exactly from the raw excess columns, to be sure we are auditing the same thing
    cash = -m[['FP_cash_cover_change_event_excess', 'FP_cash_cover_change_plus1_excess']].mean(axis=1, skipna=True)
    old = pd.DataFrame({'cash': cash.rank(pct=True),
                        'svc': (-m.FP_service_share_change_plus1_excess).rank(pct=True),
                        'ren': m.FP_renewals_ratio_change_plus1_excess.rank(pct=True)})
    fp_rebuilt = old.mean(axis=1, skipna=True)
    ok = (fp_rebuilt - m.FP).abs().max()
    log(f'== 0. rebuild check: max |rebuilt FP - master FP| = {ok:.2e} over {int(m.FP.notna().sum())} rows with FP')
    for a, b in [('cash', 'FP_rank_cash_cover_drawdown_excess_t_t1'), ('svc', 'FP_rank_services_crowd_out_excess_t_1'),
                 ('ren', 'FP_rank_renewals_ratio_rise_excess_t_1')]:
        log(f'   component {a}: max |rebuilt - master rank| = {(old[a] - m[b]).abs().max():.2e}')
    m = pd.concat([m, old.add_prefix('old_rank_')], axis=1)

    # ---- 1. coverage
    log('\n== 1. coverage (rows out of the subset size)')
    for lag in (0, 1):
        for c, (met, kind, sg, unit) in COMP.items():
            m[f'x_{c}_{lag}'] = excess_for_rows(panel, flags, m, met, lag, kind)
    m['x_cash'] = m[['x_cash_cover_0', 'x_cash_cover_1']].mean(axis=1, skipna=True)     # old cash component input
    subsets = {'all rows': m.index == m.index, 'fires >= 5% of council': (m.share >= 0.05).to_numpy(),
               'Black Summer (AGRN 871)': m.black_summer.to_numpy(), 'excluding Black Summer': (~m.black_summer).to_numpy()}
    cov_cols = {'old cash drawdown (event and/or plus1)': 'x_cash', '  cash: event only available': None,
                'old services crowd-out (plus1)': 'x_service_share_1', 'old renewals ratio (plus1)': 'x_renewals_ratio_1',
                'operating ratio event (t)': 'x_operating_ratio_0', 'operating ratio plus1 (t+1)': 'x_operating_ratio_1',
                'own-source revenue event (t)': 'x_own_source_rev_0', 'own-source revenue plus1 (t+1)': 'x_own_source_rev_1',
                'old FP (>=1 component)': 'FP'}
    cov = []
    for lab, col in cov_cols.items():
        row = {'component': lab}
        for sname, mask in subsets.items():
            sub = m[mask]
            if col is None:
                n = int((sub.x_cash_cover_0.notna() & sub.x_cash_cover_1.isna()).sum())
            else:
                n = int(sub[col].notna().sum())
            row[sname] = f'{n}/{len(sub)}'
        cov.append(row)
    cov = pd.DataFrame(cov)
    log(cov.to_string(index=False))
    npres = m[['old_rank_cash', 'old_rank_svc', 'old_rank_ren']].notna().sum(axis=1)
    log('old FP: number of components present per row -> ' + ', '.join(f'{k}: {int((npres == k).sum())}' for k in (3, 2, 1, 0)))
    log('rows with both cash-cover windows: ' + str(int((m.x_cash_cover_0.notna() & m.x_cash_cover_1.notna()).sum())) +
        '; event only: ' + str(int((m.x_cash_cover_0.notna() & m.x_cash_cover_1.isna()).sum())) +
        '; plus1 only: ' + str(int((m.x_cash_cover_0.isna() & m.x_cash_cover_1.notna()).sum())))
    by_fy = m.groupby('fy').agg(rows=('FP', 'size'), FP=('FP', lambda s: int(s.notna().sum())),
                                cash_event=('x_cash_cover_0', lambda s: int(s.notna().sum())),
                                cash_plus1=('x_cash_cover_1', lambda s: int(s.notna().sum())),
                                service_plus1=('x_service_share_1', lambda s: int(s.notna().sum())),
                                renewals_plus1=('x_renewals_ratio_1', lambda s: int(s.notna().sum())),
                                oper_event=('x_operating_ratio_0', lambda s: int(s.notna().sum())),
                                oper_plus1=('x_operating_ratio_1', lambda s: int(s.notna().sum())),
                                osr_event=('x_own_source_rev_0', lambda s: int(s.notna().sum())),
                                osr_plus1=('x_own_source_rev_1', lambda s: int(s.notna().sum())))
    log('\ncoverage by fire financial year (FY start year; FY2019 = Jul 2019-Jun 2020, Black Summer):')
    log(by_fy.to_string())
    cov.to_csv(RESULTS / 'AUDIT_coverage.csv', index=False)
    by_fy.to_csv(RESULTS / 'AUDIT_coverage_by_fy.csv')

    # ---- 2. noise: fire-row excess versus the placebo (unburned council-years), year-matched
    log('\n== 2. noise: size of the excess change relative to normal movement in unburned councils')
    log('unburned = no fire >= 100 ha inside the council in the financial years the change spans (same rule as the dataset).')
    log('z = excess / robust SD (1.4826 x MAD) of the unburned excess in the SAME fire year and window; signed so + = more pressure.')
    rows = []
    unb_store = {}
    for c, (met, kind, sg, unit) in COMP.items():
        for lag in (0, 1):
            u = unburned_excess(panel, flags, met, lag, kind)
            unb_store[(c, lag)] = u
            rsd_by_fy = u.groupby('fy').exc.apply(robust_sd)
            u['z'] = u.exc / u.fy.map(rsd_by_fy) * sg
            p10, p90 = np.nanpercentile(u.exc, [10, 90])
            p5, p95 = np.nanpercentile(u.exc, [5, 95])
            for sname in ('all rows', 'fires >= 5% of council', 'excluding Black Summer'):
                sub = m[subsets[sname]]
                x = sub[f'x_{c}_{lag}']
                ok = x.notna()
                z = (x[ok] / sub.fy[ok].map(rsd_by_fy) * sg)
                rows.append(dict(component=c, window=LAGS[lag], subset=sname, unit=unit, n_fire_rows=int(ok.sum()),
                                 unburned_council_years=len(u), unburned_robust_sd=robust_sd(u.exc), unburned_sd=u.exc.std(),
                                 fire_median_excess=x[ok].median(), fire_robust_sd=robust_sd(x[ok]),
                                 fire_over_unburned_spread=robust_sd(x[ok]) / robust_sd(u.exc),
                                 fire_median_z_pressure=z.median(), fire_mean_z_pressure=z.mean(),
                                 fire_share_abs_z_gt1=(z.abs() > 1).mean(), unburned_share_abs_z_gt1=(u.z.abs() > 1).mean(),
                                 fire_share_abs_z_gt2=(z.abs() > 2).mean(), unburned_share_abs_z_gt2=(u.z.abs() > 2).mean(),
                                 fire_share_inside_unburned_p10_p90=x[ok].between(p10, p90).mean(),
                                 fire_share_inside_unburned_p5_p95=x[ok].between(p5, p95).mean()))
    noise = pd.DataFrame(rows)
    noise.to_csv(RESULTS / 'AUDIT_noise.csv', index=False)
    show = noise[noise.subset == 'all rows'][['component', 'window', 'unit', 'n_fire_rows', 'unburned_robust_sd', 'fire_median_excess',
                                            'fire_robust_sd', 'fire_over_unburned_spread', 'fire_median_z_pressure',
                                            'fire_share_abs_z_gt1', 'unburned_share_abs_z_gt1', 'fire_share_abs_z_gt2',
                                            'unburned_share_abs_z_gt2', 'fire_share_inside_unburned_p10_p90']]
    log(show.round(2).to_string(index=False))
    log('reading: fire_over_unburned_spread near 1 = fire rows vary no more than unburned councils do; fire_median_z_pressure near 0 = '
        'no typical shift; share inside p10-p90 would be 0.80 if fire rows were drawn from the unburned distribution.')
    sub5 = noise[noise.subset == 'fires >= 5% of council'][['component', 'window', 'n_fire_rows', 'fire_median_z_pressure',
                                                            'fire_over_unburned_spread', 'fire_share_inside_unburned_p10_p90']]
    log('\nsame, fires >= 5% of the council only:')
    log(sub5.round(2).to_string(index=False))

    # noise check on comparison councils' spread by size of council (README: comparison councils are mostly metropolitan)
    log('\nrural check: unburned robust SD of the plus1 excess, low- vs high-population-density councils')
    dens = wide(panel.assign(_d=panel.council_population), '_d')
    med_pop = dens.median(axis=1)
    rows2 = []
    for c in COMP:
        u = unb_store[(c, 1)].copy()
        u['pop'] = u.key.map(med_pop)
        cut = u['pop'].median()
        rows2.append(dict(component=c, robust_sd_small_councils=robust_sd(u[u['pop'] <= cut].exc),
                          robust_sd_large_councils=robust_sd(u[u['pop'] > cut].exc)))
    log(pd.DataFrame(rows2).round(2).to_string(index=False))
    log('(small = at or below the median council population; small councils have the noisier ratios)')

    # placebo drift: do small and large unburned councils move differently in the same year? (rural vs metro comparison)
    log('\nplacebo drift among unburned councils: median excess of small (<= median population) minus large councils, '
        'in units of the unburned robust SD, by window (positive = small councils show MORE pressure than the state median)')
    drift = []
    for c, (met, kind, sg, unit) in COMP.items():
        for lag in (0, 1):
            u = unb_store[(c, lag)].copy()
            u['pop'] = u.key.map(med_pop)
            cut = u['pop'].median()
            u['small'] = u['pop'] <= cut
            rsd = robust_sd(u.exc)
            by = u.groupby(['fy', 'small']).exc.median().unstack()
            diff = (by[True] - by[False]) * sg / rsd
            drift.append(dict(component=c, window=LAGS[lag], median_gap_in_sd=diff.median(), max_abs_gap_in_sd=diff.abs().max(),
                              worst_fy=int(diff.abs().idxmax()), gap_in_worst_fy_sd=diff.loc[diff.abs().idxmax()]))
    drift = pd.DataFrame(drift)
    log(drift.round(2).to_string(index=False))
    drift.to_csv(RESULTS / 'AUDIT_small_vs_large_drift.csv', index=False)

    # persistence and mean reversion in unburned council-years (no fire in x-1, x, x+1)
    log('\npersistence / mean reversion among unburned council-years (no fire in FY x-1, x or x+1):')
    prs = []
    for c, (met, kind, sg, unit) in COMP.items():
        tab = wide(panel, met)
        a = unburned_excess(panel, flags, met, 0, kind, window_before=1, window_after=1)       # x-1 -> x
        # change x -> x+1 is stored at fy=x+1 in `a`; align it to x
        nxt = a.assign(fy=a.fy - 1)[['key', 'fy', 'exc']].rename(columns={'exc': 'exc_next'})
        d = a.merge(nxt, on=['key', 'fy']).dropna()
        r_auto = spearmanr(d.exc, d.exc_next)[0]
        # starting level: percentile within year, against the change that follows
        d2 = a.copy()
        d2['lvl_pct'] = d2.groupby('fy').level_pre.rank(pct=True)
        d2 = d2.dropna(subset=['exc', 'lvl_pct'])
        r_lvl = spearmanr(d2.lvl_pct, d2.exc)[0]
        prs.append(dict(component=c, n_pairs=len(d), autocorr_next_year_change=r_auto,
                        n_level=len(d2), rho_start_level_vs_change=r_lvl))
    prs = pd.DataFrame(prs)
    log(prs.round(2).to_string(index=False))
    log('autocorr < 0 = a rise this year tends to be followed by a fall (noise / mean reversion); rho_start_level < 0 = '
        'councils that start high fall more, so the excess change partly reflects where the ratio started.')
    prs.to_csv(RESULTS / 'AUDIT_persistence.csv', index=False)

    # ---- 3. agreement
    log('\n== 3. agreement between the three old FP components (higher = more pressure for all three)')
    sig = pd.DataFrame({'cash_drawdown': -m.x_cash, 'services_crowd_out': -m.x_service_share_1,
                        'renewals_rise': m.x_renewals_ratio_1})
    rk = old.rename(columns={'cash': 'cash_drawdown', 'svc': 'services_crowd_out', 'ren': 'renewals_rise'})
    agree = []
    for sname, mask in subsets.items():
        if sname == 'Black Summer (AGRN 871)':
            continue
        s = rk[mask]
        prs_ = {}
        for a_, b_ in [('cash_drawdown', 'services_crowd_out'), ('cash_drawdown', 'renewals_rise'),
                       ('services_crowd_out', 'renewals_rise')]:
            d = s[[a_, b_]].dropna()
            prs_[f'{a_} vs {b_}'] = (round(spearmanr(d[a_], d[b_])[0], 2), len(d))
        comp3 = s.dropna()
        k = 3
        cm = comp3.corr()
        rbar = cm.values[np.triu_indices(3, 1)].mean()
        alpha = k * rbar / (1 + (k - 1) * rbar)
        ev = np.linalg.eigvalsh(cm.values)[::-1]
        agree.append(dict(subset=sname, n_complete=len(comp3), **{k_: f'{v[0]:+.2f} (n={v[1]})' for k_, v in prs_.items()},
                          mean_pairwise_rho=round(rbar, 2), std_alpha=round(alpha, 2), first_PC_share=round(ev[0] / 3, 2)))
    agree = pd.DataFrame(agree)
    log(agree.to_string(index=False))
    fp_corr = pd.concat([rk, m.FP.rename('old_FP')], axis=1).corr('spearman')['old_FP'].drop('old_FP')
    log('Spearman of each component rank with old FP (all rows): ' + ', '.join(f'{k} {v:+.2f}' for k, v in fp_corr.items()))
    agree.to_csv(RESULTS / 'AUDIT_agreement.csv', index=False)

    # placebo: same three measures in unburned council-years (plus1 window for all three)
    def un_signed(c):
        u = unb_store[(c, 1)].copy()
        u['v'] = u.exc * COMP[c][2]
        return u.set_index(['key', 'fy']).v
    pl = pd.concat({'cash_drawdown': un_signed('cash_cover'), 'services_crowd_out': un_signed('service_share'),
                    'renewals_rise': un_signed('renewals_ratio')}, axis=1)
    log('\nplacebo agreement in unburned council-years (plus1 window), Spearman:')
    log(pl.corr('spearman').round(2).to_string())
    log(f'(n complete = {int(pl.dropna().shape[0])}); if the placebo correlation is as large as in fire rows, the co-movement is '
        'structural (accounting), not a fire effect')

    # ---- 3b. candidate replacement components (internal consistency only; no damage or pre-fire score used)
    log('\n== 3b. agreement between the candidate replacement components (higher = more pressure; ranks over the 218 rows)')
    cand = pd.DataFrame({'cash_drawdown': old.cash,
                         'operating_shock': (-m[['x_operating_ratio_0', 'x_operating_ratio_1']].mean(axis=1, skipna=True)).rank(pct=True),
                         'own_source_shortfall': (-m[['x_own_source_rev_0', 'x_own_source_rev_1']].mean(axis=1, skipna=True)).rank(pct=True)})
    agree2 = []
    for sname, mask in subsets.items():
        if sname == 'Black Summer (AGRN 871)':
            continue
        s_ = cand[mask]
        cm2 = s_.dropna().corr('spearman')
        rbar = cm2.values[np.triu_indices(3, 1)].mean()
        agree2.append(dict(subset=sname, n_complete=len(s_.dropna()),
                           cash_vs_operating=round(cm2.iloc[0, 1], 2), cash_vs_own_source=round(cm2.iloc[0, 2], 2),
                           operating_vs_own_source=round(cm2.iloc[1, 2], 2), mean_pairwise_rho=round(rbar, 2),
                           std_alpha=round(3 * rbar / (1 + 2 * rbar), 2)))
    agree2 = pd.DataFrame(agree2)
    log(agree2.to_string(index=False))
    agree2.to_csv(RESULTS / 'AUDIT_agreement_candidates.csv', index=False)
    log('rows with the candidate component present (of 218): ' + ', '.join(f'{c} {int(cand[c].notna().sum())}' for c in cand))
    log('rows with >= 2 of the 3 candidate components: ' + str(int((cand.notna().sum(axis=1) >= 2).sum())) +
        '; all 3: ' + str(int((cand.notna().sum(axis=1) == 3).sum())))

    # ---- 4. mechanics: what does each ratio co-move with in unburned councils?
    log('\n== 4. mechanics in unburned council-years (plus1 window, excess changes): Spearman')
    def ux(metric, kind='diff'):
        return unburned_excess(panel, flags, metric, 1, kind).set_index(['key', 'fy']).exc
    mech = pd.DataFrame({'d_cash_cover': ux('cash_cover_months'), 'd_service_share': ux('service_share_pct'),
                         'd_roads_share': ux('roads_share_pct'), 'd_renewals_ratio': ux('building_infrastructure_renewals_ratio_pct'),
                         'd_operating_ratio': ux('operating_ratio_pct'), 'd_grants_per_capita': ux('grants_per_capita_aud'),
                         'd_own_source_rev_pct': ux('own_source_rev_aud', 'pct')})
    cm = mech.corr('spearman').round(2)
    log(cm.to_string())
    log(f'(pairwise complete; n up to {int(mech.dropna(how="all").shape[0])})')
    cm.to_csv(RESULTS / 'AUDIT_mechanics.csv')

    # heavy tails of the renewals ratio
    log('\nrenewals ratio excess (plus1) in fire rows: quantiles ' +
        str(m.x_renewals_ratio_1.quantile([0, .05, .25, .5, .75, .95, 1]).round(0).to_dict()) +
        f'; share with |excess| > 100 pp: {(m.x_renewals_ratio_1.abs() > 100).mean():.2f}')
    (RESULTS / 'AUDIT.txt').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
