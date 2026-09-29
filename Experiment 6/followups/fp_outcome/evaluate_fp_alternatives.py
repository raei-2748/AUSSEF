"""FROZEN 2026-09-29, BEFORE any new FP series was correlated with damage, DL, F or V.

WHAT WAS SEEN BEFORE THE FREEZE (results/AUDIT.txt): coverage; fire-row excess changes versus normal movement in unburned
councils; agreement between the old components; mechanics in unburned councils; small-vs-large council drift; agreement
between the three candidate replacement components. NO correlation of any candidate FP with burned share, DL, F, V or any other
Y pillar had been computed. (The old FP's relations, about +0.20 with DL, +0.30 with burned share on fires >= 5%, and -0.05 to
-0.14 with the pre-fire score, were known from Experiment 6.)

QUESTION. Does a better-built FP (a) respond more clearly to damage than the old FP, and (b) relate to the pre-fire fiscal (F) and
vulnerability (V) blocks? Nothing else is evaluated: no IL, SL or Y, no other threshold, no model fitting, no other variants.

OLD FP (unchanged, master column FP) = mean of the percentile ranks of: cash drawdown = -mean(cash-cover excess, FY t and t+1);
services crowd-out = -(services-share excess, t+1); renewals rise = +(renewals-ratio excess, t+1).

NEW DEFINITIONS. Every input is an 'excess' change built with the dataset's own rule (council change minus the median change in NSW
councils with no fire >= 100 ha inside; reproduced exactly, max error 1e-13, in fpcommon.py), taken for the fire FY (t) and the
next FY (t+1); the mean of whichever of the two exists is ranked (the old pipeline's rule, kept so the definitions stay
comparable). Ranks are percentiles over all 218 rows, ties averaged, 1 = most pressure.
  A_liquidity     = rank of -(cash expense cover excess, months).                 [= the old cash component]
  B_result_shock  = rank of -(operating performance ratio excess, pp).            [OLG ratio excludes capital grants]
  own_source_only = rank of -(own-source revenue % change excess); own-source revenue = own-source share x total revenue,
                    so it excludes all grants and contributions.                  [diagnostic component of C, not a separate alternative]
  C_composite     = mean of the three ranks above, needing at least 2 of 3.        [grants never count as a loss and never
                    offset one; renewals and services-share are dropped]
Why (details and sources in FINDINGS.md; only pages the author opened are relied on):
  - Cash expense cover, operating performance ratio and own-source revenue ratio are OLG performance measures whose good
    direction is unambiguous (higher is better; benchmarks >3 months, >=0%, >=60%) [NSW OLG Your Council finances page]. The OLG
    building and infrastructure renewals ratio is the opposite: above 100% is satisfactory and higher is good [OLG Your Council
    assets page], but the old FP counts a rise as pressure, and after a fire a rise is asset replacement (recovery spending).
    In unburned councils it moves with grants (+0.14) and with the operating ratio (+0.13) (audit section 4). Services share is a
    composition ratio; it moves against cash drawdown in fire rows (-0.21), which fits recovery spending, not crowd-out.
  - Disaster transfers are recovery funding: after US disasters state spending and federal transfers both rise and transfers finance
    much of the extra spending [Miao, Hou & Abrigo 2018, National Tax Journal]; local stress shows in own tax revenue and
    borrowing cost [Jerch, Kahn & Lin 2023, J. Urban Econ.]; liquidity is buffered by reserves [Chen 2020, Public Budg. Finance].
    NSW paid burnt properties' rates for a quarter and waived DA fees [ABC News, 4 Feb 2020], so own-source revenue is partly
    compensated by the State.
  - Advance Commonwealth Financial Assistance Grants distort operating results and cash in the years the advance share changes
    [VAGO, Results of 2019-20 Audits: Local Government, s3.1; ALGA on $1.3bn brought forward to 25 May 2020]. The comparison median
    removes the state-wide part; it does not remove differences by council size (audit: up to 1-1.7 SD in single years). This is a
    stated limit of A, B and C, not something fixed here.
  - Ratio sets should be small and theory-led because NSW ratios load on three independent factors [Drew & Dollery 2016, Aust.
    Account. Rev.].
Primary comparison: C_composite versus old_FP. A_liquidity and B_result_shock are the two alternatives that stand alone;
own_source_only is shown so that the reader can see which piece of C does the work.

DATA FRAME. Common set = rows where old FP, A, B, C and own_source_only are all present (about 198 of 218). Every series is
compared on these same rows so numbers and paired differences are like for like. Each series on its own full coverage is
reported as a sensitivity. Damage = burned share of the council (X_fire_share_of_council_burned) and DL (homes destroyed per
1,000 dwellings, as the DL rank; about 86 common rows). Pre-fire blocks = F and V from Experiment 6 ROWS_WITH_SCORE_v2.csv.
Subsets: all rows; fires burning >= 5% of the council; excluding Black Summer (AGRN 871); and, descriptive only (8 rows, no CI),
>= 5% excluding Black Summer.

STATISTICS. Spearman rho; 95% percentile CI from a council-cluster bootstrap (resample councils with replacement, 2,000 draws,
seed 20260929, the same resamples for every series within a subset). Paired difference = rho(new) - rho(old_FP) on the same
resamples. Expected sign: positive for burned share, DL, F (weaker finances = more pressure) and V. Known mechanical caveat, from
the audit: the cash-cover change depends on where the ratio started (rho -0.14 in unburned councils), so councils with little
cash have little room to draw down and A, B and C may correlate negatively with F for that reason alone.

DECISION RULE (fixed now). Cells = target x subset over the three main subsets (6 damage cells: burned share, DL; 6 pre-fire
cells: F, V). For each alternative and each of the two questions: CLEARLY BETTER if the paired-difference CI lies above 0 in at
least 2 cells and below 0 in none; WORSE if it lies below 0 in at least 2 cells and above in none; otherwise NO CLEAR CHANGE. One
isolated cell is treated as chance (3 alternatives x 12 cells = 36 paired intervals, so about 2 would exclude 0 by chance at
95%). If nothing meets the rule it is reported as no change. No definition is added, dropped or re-tuned after seeing results.
"""
import hashlib
import sys

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

from fpcommon import (N_BOOT, RESULTS, ROWS_V2, SEED, excess_for_rows, load_fire_flags, load_master, load_panel)

lines = []


def log(s=''):
    print(s)
    lines.append(str(s))


SERIES = ['old_FP', 'A_liquidity', 'B_result_shock', 'C_composite', 'own_source_only']
ALTS = ['A_liquidity', 'B_result_shock', 'C_composite']
TARGETS = {'burned_share': 'damage', 'DL': 'damage', 'F_block': 'prefire', 'V_block': 'prefire'}
MIN_ROWS_FOR_CI = 15


def build(m, panel, flags):
    """The frozen definitions. Percentile ranks are taken over all 218 rows, ties averaged, 1 = most pressure."""
    for lag in (0, 1):
        m[f'x_cash_{lag}'] = excess_for_rows(panel, flags, m, 'cash_cover_months', lag, 'diff')
        m[f'x_oper_{lag}'] = excess_for_rows(panel, flags, m, 'operating_ratio_pct', lag, 'diff')
        m[f'x_osr_{lag}'] = excess_for_rows(panel, flags, m, 'own_source_rev_aud', lag, 'pct')

    def rk(cols, sign):
        return (sign * m[cols].mean(axis=1, skipna=True)).rank(pct=True)

    m['A_liquidity'] = rk(['x_cash_0', 'x_cash_1'], -1)               # cash-cover drawdown; identical to the old cash component
    m['B_result_shock'] = rk(['x_oper_0', 'x_oper_1'], -1)             # fall in operating performance ratio
    m['own_source_only'] = rk(['x_osr_0', 'x_osr_1'], -1)              # fall in own-source revenue (grants excluded); component of C
    parts = m[['A_liquidity', 'B_result_shock', 'own_source_only']]
    m['C_composite'] = parts.mean(axis=1, skipna=True).where(parts.notna().sum(axis=1) >= 2)
    m['old_FP'] = m.FP
    m['burned_share'] = m.share
    return m


def attach_blocks(m):
    r = pd.read_csv(ROWS_V2, dtype={'agrn': str})[['agrn', 'region_id', 'F', 'V', 'FP']]
    assert not r.duplicated(['agrn', 'region_id']).any() and not m.duplicated(['agrn', 'region_id']).any()
    out = m.merge(r.rename(columns={'F': 'F_block', 'V': 'V_block', 'FP': 'FP_in_rows_file'}), on=['agrn', 'region_id'],
                  how='left', validate='one_to_one')
    assert len(out) == len(m)
    both = out.FP.notna() & out.FP_in_rows_file.notna()
    assert np.allclose(out.FP[both], out.FP_in_rows_file[both]), 'FP differs from the Experiment 6 rows file'
    return out


def rho(x, y):
    if len(x) < 6:
        return np.nan
    rx, ry = rankdata(x), rankdata(y)
    if rx.std() == 0 or ry.std() == 0:
        return np.nan
    return float(np.corrcoef(rx, ry)[0, 1])


def cluster_boot(d, pairs, n_boot, seed):
    """pairs: list of (series, target). Returns {pair: (rho, lo, hi)} and {(alt, target): (delta, lo, hi)} vs old_FP.
    One set of council resamples is shared by every pair, so paired differences have a proper interval."""
    rng = np.random.default_rng(seed)
    councils = d.region_id.to_numpy()
    uniq = np.unique(councils)
    where = {c: np.flatnonzero(councils == c) for c in uniq}
    res = {p: [] for p in pairs}
    dl = {}
    targets = sorted({t for _, t in pairs})
    for t in targets:
        for a in ALTS:
            dl[(a, t)] = []
    xs = {p: d[p[0]].to_numpy(float) for p in pairs}
    ys = {p: d[p[1]].to_numpy(float) for p in pairs}
    point = {}
    for p in pairs:
        ok = ~(np.isnan(xs[p]) | np.isnan(ys[p]))
        point[p] = rho(xs[p][ok], ys[p][ok])
    point_delta = {k: point[(k[0], k[1])] - point[('old_FP', k[1])] for k in dl if (k[0], k[1]) in point and ('old_FP', k[1]) in point}
    for _ in range(n_boot):
        pick = rng.choice(len(uniq), len(uniq))
        idx = np.concatenate([where[uniq[i]] for i in pick])
        cur = {}
        for p in pairs:
            x, y = xs[p][idx], ys[p][idx]
            ok = ~(np.isnan(x) | np.isnan(y))
            cur[p] = rho(x[ok], y[ok]) if ok.sum() >= 6 and len(np.unique(x[ok])) > 2 and len(np.unique(y[ok])) > 2 else np.nan
            res[p].append(cur[p])
        for (a, t) in dl:
            if (a, t) in point_delta and not np.isnan(cur.get((a, t), np.nan)) and not np.isnan(cur.get(('old_FP', t), np.nan)):
                dl[(a, t)].append(cur[(a, t)] - cur[('old_FP', t)])
    ci = {p: (point[p],) + tuple(np.nanpercentile(res[p], [2.5, 97.5])) for p in pairs}
    dci = {k: (point_delta[k],) + tuple(np.nanpercentile(dl[k], [2.5, 97.5])) for k in point_delta if len(dl[k]) > 100}
    return ci, dci


def main():
    header_hash = hashlib.sha256((__doc__ or '').encode()).hexdigest()
    log(f'frozen-header sha256: {header_hash}')
    m = load_master()
    panel, flags = load_panel(), load_fire_flags()
    m = attach_blocks(build(m, panel, flags))
    m['common'] = m[SERIES].notna().all(axis=1)
    log(f'rows: {len(m)}; rows with old FP and all four new series (common set): {int(m.common.sum())}')
    keep = ['agrn', 'region_id', 'region_name', 'fy', 'black_summer', 'burned_share', 'DL', 'F_block', 'V_block'] + SERIES
    m[keep].to_csv(RESULTS / 'ROWS_WITH_FP_ALTERNATIVES.csv', index=False)

    subsets = {
        'all rows': m.common,
        'fires >= 5% of council': m.common & (m.share >= 0.05),
        'excluding Black Summer': m.common & ~m.black_summer,
        'fires >= 5%, excl. Black Summer (descriptive)': m.common & (m.share >= 0.05) & ~m.black_summer,
    }
    pairs = [(s, t) for s in SERIES for t in TARGETS]
    out_rows = []
    delta_rows = []
    for sname, mask in subsets.items():
        d = m[mask].reset_index(drop=True)
        if len(d) < MIN_ROWS_FOR_CI:
            point = {}
            for p in pairs:
                ok = d[[p[0], p[1]]].dropna()
                point[p] = (rho(ok.iloc[:, 0].to_numpy(), ok.iloc[:, 1].to_numpy()) if len(ok) >= 6 else np.nan, np.nan, np.nan)
            ci, dci = point, {}
        else:
            ci, dci = cluster_boot(d, pairs, N_BOOT, SEED)
        for (s, t), (r_, lo, hi) in ci.items():
            ok = d[[s, t]].dropna()
            out_rows.append(dict(subset=sname, target=t, kind=TARGETS[t], series=s, n_rows=len(ok),
                                 n_councils=int(d.loc[ok.index, 'region_id'].nunique()), rho=r_, ci_low=lo, ci_high=hi))
        for (a, t), (dv, lo, hi) in dci.items():
            delta_rows.append(dict(subset=sname, target=t, kind=TARGETS[t], series=a, delta_vs_old=dv, ci_low=lo, ci_high=hi))
    res = pd.DataFrame(out_rows)
    dres = pd.DataFrame(delta_rows)
    res.to_csv(RESULTS / 'EVAL_correlations.csv', index=False)
    dres.to_csv(RESULTS / 'EVAL_paired_differences.csv', index=False)

    def fmt(r):
        return f'{r.rho:+.2f} [{r.ci_low:+.2f}, {r.ci_high:+.2f}]' if not np.isnan(r.ci_low) else f'{r.rho:+.2f} [no CI]'

    for kind, title in (('damage', 'A. response to damage'), ('prefire', 'B. relation to the pre-fire blocks (F fiscal, V vulnerability)')):
        log(f'\n===== {title}: Spearman (95% council-cluster bootstrap CI), n rows / n councils =====')
        for sname in subsets:
            log(f'\n-- {sname}')
            sub = res[(res.subset == sname) & (res.kind == kind)]
            tab = sub.assign(cell=sub.apply(fmt, axis=1)).pivot(index='series', columns='target', values='cell').reindex(SERIES)
            nn = sub[sub.series == 'old_FP'].set_index('target')
            log('   n rows/councils: ' + ', '.join(f'{t} {int(nn.loc[t, "n_rows"])}/{int(nn.loc[t, "n_councils"])}' for t in nn.index))
            log(tab.to_string())
            dsub = dres[(dres.subset == sname) & (dres.kind == kind)]
            if len(dsub):
                dt = dsub.assign(cell=dsub.apply(lambda r: f'{r.delta_vs_old:+.2f} [{r.ci_low:+.2f}, {r.ci_high:+.2f}]', axis=1)) \
                         .pivot(index='series', columns='target', values='cell')
                log('   paired difference (new minus old FP), same rows:')
                log(dt.to_string())

    # ---- pre-declared verdicts
    log('\n===== VERDICTS by the frozen rule =====')
    main_sub = ['all rows', 'fires >= 5% of council', 'excluding Black Summer']
    for a in ALTS:
        for kind, tgts, label in (('damage', ['burned_share', 'DL'], 'damage response'),
                                  ('prefire', ['F_block', 'V_block'], 'pre-fire relation')):
            d_ = dres[(dres.series == a) & (dres.subset.isin(main_sub)) & (dres.target.isin(tgts))]
            up = int((d_.ci_low > 0).sum())
            down = int((d_.ci_high < 0).sum())
            n_ = len(d_)
            r_ = res[(res.series == a) & (res.subset.isin(main_sub)) & (res.target.isin(tgts))]
            own_pos = int((r_.ci_low > 0).sum())
            own_neg = int((r_.ci_high < 0).sum())
            verdict = ('CLEARLY BETTER than old FP' if up >= 2 and down == 0 else
                       'WORSE than old FP' if down >= 2 and up == 0 else 'NO CLEAR CHANGE vs old FP')
            log(f'{a:16s} {label:18s}: paired difference CI above 0 in {up}/{n_} cells, below 0 in {down}/{n_}; '
                f'own rho CI above 0 in {own_pos}/{n_}, below 0 in {own_neg}/{n_}  ->  {verdict}')
    d_old = res[(res.series == 'old_FP') & (res.subset.isin(main_sub))]
    for kind, tgts in (('damage', ['burned_share', 'DL']), ('prefire', ['F_block', 'V_block'])):
        r_ = d_old[d_old.target.isin(tgts)]
        log(f'old_FP {kind}: own rho CI above 0 in {int((r_.ci_low > 0).sum())}/{len(r_)} cells, below 0 in {int((r_.ci_high < 0).sum())}/{len(r_)}')

    # ---- descriptive: how different are the new series from the old one (common rows)
    cm = m.loc[m.common, SERIES].corr('spearman').round(2)
    log('\n===== descriptive: Spearman between the FP series (common rows) =====')
    log(cm.to_string())
    cm.to_csv(RESULTS / 'EVAL_series_correlations.csv')
    # ---- own coverage (not restricted to common rows), damage on all rows
    rows = []
    for s in SERIES:
        for t in ('burned_share', 'DL', 'F_block', 'V_block'):
            ok = m[[s, t]].dropna()
            rows.append(dict(series=s, target=t, n_rows=len(ok), rho=rho(ok[s].to_numpy(), ok[t].to_numpy())))
    own = pd.DataFrame(rows).pivot(index='series', columns='target', values='rho').round(2).reindex(SERIES)
    n_own = {s: int(m[s].notna().sum()) for s in SERIES}
    log('\n===== sensitivity: each series on its own full coverage (all rows, no CI) =====')
    log(own.assign(n_rows=pd.Series(n_own)).to_string())
    (RESULTS / 'EVAL.txt').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    sys.exit(main())
