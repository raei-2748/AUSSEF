"""Turn results/*.csv into the markdown tables pasted into FINDINGS.md (writes results/FINDINGS_TABLES.md)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_lib import RES

r = pd.read_csv(RES / 'ALLROWS_MODELS.csv')
om = pd.read_csv(RES / 'OMNIBUS.csv')
sl = pd.read_csv(RES / 'SIMPLE_SLOPES.csv')
v = pd.read_csv(RES / 'VERDICTS.csv')
san = pd.read_csv(RES / 'SANITY_CHECK.csv')
mde = pd.read_csv(RES / 'SANITY_MDE.csv')
cal1 = pd.read_csv(RES / 'sanity_v1' / 'INFERENCE_CALIBRATION.csv')
ph = pd.read_csv(RES / 'POSTHOC_V_BY_EVENT.csv')
phs = pd.read_csv(RES / 'POSTHOC_V_SLOPES.csv')
phd = pd.read_csv(RES / 'POSTHOC_V_DECOMP.csv')
BLK = ['H', 'E', 'V', 'F']
out = []


def cell(a, p=False):
    s = f'{a.est:+.2f} [{a.lo:+.2f}, {a.hi:+.2f}]'
    return s + (f' p={a.p:.2f}' if p else '')


def get(model, tgt, sm, term):
    x = r[(r.model == model) & (r.target == tgt) & (r['sample'] == sm) & (r.term == term)]
    return x.iloc[0] if len(x) else None


def md(df):
    return df.to_markdown(index=False)


# 1. primary model, Y
rows = []
for term, lab in [('size', 'size s (log burned share)'), ('b_H', 'b_H'), ('b_E', 'b_E'), ('b_V', 'b_V'), ('b_F', 'b_F'),
                  ('g_H', 'g_H (H x size)'), ('g_E', 'g_E (E x size)'), ('g_V', 'g_V (V x size)'), ('g_F', 'g_F (F x size)')]:
    a, b = get('M1_primary', 'Y', 'all', term), get('M1_primary', 'Y', 'excl_BS', term)
    rows.append({'term': lab, 'all 218 rows': cell(a), 'p': f'{a.p:.2f}', 'without Black Summer (168)': cell(b), 'p ': f'{b.p:.2f}'})
out.append('### T1. Primary model M1, target Y\n\n' + md(pd.DataFrame(rows)))
o = om[(om.model == 'M1_primary') & (om.target == 'Y')]
out.append('Omnibus test that all four g = 0: ' + '; '.join(
    f"{'all rows' if s == 'all' else 'without Black Summer'}: F({int(x.df1)},{int(x.df2)}) = {x.F:.2f}, p = {x.p:.2f}"
    for s, x in zip(o['sample'], o.itertuples())))

# 2. simple slopes
rows = []
for b in BLK:
    row = {'block': b}
    for sm in ['all']:
        for sh in [0.001, 0.01, 0.05, 0.20]:
            a = sl[(sl.target == 'Y') & (sl['sample'] == sm) & (sl.block == b) & (np.isclose(sl.share, sh))].iloc[0]
            row[f'{sh * 100:g}% burned'] = cell(a)
    rows.append(row)
out.append('### T2. Effect of +1 SD of a block on Y at a given burned share (M1, all rows)\n\n' + md(pd.DataFrame(rows)))

# 3. robustness of g
models = [('M1_primary', 'M1 primary (event dummies, jackknife)'),
          ('C0b_noevent_CR1_v1primary', 'C0b: v1 as first locked (no event dummies, CR1)'),
          ('C0a_noevent_jackknife', 'C0a: no event dummies, jackknife'),
          ('C1_size_share', 'C1: raw share'), ('C1_size_rank_share', 'C1: rank of share'),
          ('C1_size_log_burn_ha', 'C1: log burn ha'), ('C1_size_step5', 'C1: step share >= 5%'),
          ('C3_fraclogit', 'C3: fractional logit (log-odds)'), ('C4_mixed_ri', 'C4: mixed, council random intercept'),
          ('C4b_mixed_crossed', 'C4b: mixed, crossed council + fire'),
          ('C5_twoway_cluster', 'C5: two-way cluster (council, fire)'), ('C6_council_FE', 'C6: council fixed effects'),
          ('C7_pairs_bootstrap', 'C7: council-pairs bootstrap')]
for sm, ttl in [('all', 'all 218 rows'), ('excl_BS', 'without Black Summer (168 rows)')]:
    rows = []
    for m, lab in models:
        row = {'model': lab}
        for b in BLK:
            a = get(m, 'Y', sm, f'g_{b}')
            row[f'g_{b}'] = cell(a) if a is not None else ''
        rows.append(row)
    for b, lab in [(bb, f'C2: {bb} alone') for bb in BLK]:
        pass
    row = {'model': 'C2: one block at a time'}
    for b in BLK:
        row[f'g_{b}'] = cell(get(f'C2_one_block_{b}', 'Y', sm, f'g_{b}'))
    rows.append(row)
    a = get('C8_composite_score', 'Y', sm, 'g_risk_add')
    rows.append({'model': 'C8: composite score risk_add (g on the score)', 'g_H': cell(a), 'g_E': '', 'g_V': '', 'g_F': ''})
    out.append(f'### T3{"a" if sm == "all" else "b"}. Interaction g in every model, target Y, {ttl}\n\n' + md(pd.DataFrame(rows)))
rows = []
for m, lab in [('M1_primary', 'M1 primary'), ('C0b_noevent_CR1_v1primary', 'C0b v1 as first locked'),
               ('C0a_noevent_jackknife', 'C0a no event dummies, jackknife'), ('C1_size_share', 'raw share'),
               ('C1_size_rank_share', 'rank of share'), ('C1_size_log_burn_ha', 'log burn ha'), ('C1_size_step5', 'step >= 5%')]:
    row = {'model': lab}
    for sm in ['all', 'excl_BS']:
        x = om[(om.model == m) & (om.target == 'Y') & (om['sample'] == sm)].iloc[0]
        row[sm] = f'p = {x.p:.3f}'
    rows.append(row)
out.append('### T4. Omnibus p (all four g = 0), target Y\n\n' + md(pd.DataFrame(rows).rename(columns={'all': 'all rows', 'excl_BS': 'without Black Summer'})))

# 5. verdicts
vy = v[v.target == 'Y'].copy()
vy['g (95% CI)'] = vy.apply(lambda a: f'{a.g_est:+.2f} [{a.g_lo:+.2f}, {a.g_hi:+.2f}]', axis=1)
vy['without BS'] = vy.apply(lambda a: f'{a.g_exclBS:+.2f} [{a.g_exclBS_lo:+.2f}, {a.g_exclBS_hi:+.2f}]', axis=1)
vy['p'] = vy.p.map('{:.2f}'.format)
vy['Holm p'] = vy.p_holm.map('{:.2f}'.format)
for c, lab in [('A_ci_positive', 'A'), ('B_holm', 'B'), ('C_scale', 'C'), ('D_model_class', 'D'), ('E_excl_BS', 'E')]:
    vy[lab] = vy[c].map({True: 'yes', False: 'no'})
out.append('### T5. Verdicts, target Y (rule in the header of allrows_continuous.py)\n\n' +
           md(vy[['block', 'g (95% CI)', 'p', 'Holm p', 'A', 'B', 'C', 'D', 'E', 'without BS', 'verdict']]))
vp = v[v.target != 'Y'].copy()
vp['g (95% CI)'] = vp.apply(lambda a: f'{a.g_est:+.2f} [{a.g_lo:+.2f}, {a.g_hi:+.2f}]', axis=1)
vp['p'] = vp.p.map('{:.3f}'.format)
vp['Holm p (of 16)'] = vp.p_holm.map('{:.2f}'.format)
n = r[(r.model == 'M1_primary') & (r['sample'] == 'all') & (r.term == 'size')].set_index('target').n
vp['n'] = vp.target.map(n)
out.append('### T6. Pillars: g_B of M1 on all rows, Holm across all 16\n\n' + md(vp[['target', 'n', 'block', 'g (95% CI)', 'p', 'Holm p (of 16)', 'verdict']]))

# 7. sanity
nul = san[san.scenario.str.startswith('null') & (san.model == 'M1_primary')]
t = nul.pivot_table(index=['scenario', 'sample'], columns='term', values='rej_two_sided_pct')
t = t[[c for c in ['b_H', 'b_E', 'b_V', 'b_F', 'g_H', 'g_E', 'g_V', 'g_F', 'omnibus_g']]].round(1).reset_index()
out.append('### T7. Sanity check, v2 primary model: false-alarm % on a true null (nominal 5)\n\n' + md(t))
c1 = cal1[(cal1.model == 'M1') & (cal1.method == 'cr1')].pivot_table(index=['scenario', 'sample'], columns='term', values='false_alarm_pct')
c1 = c1[['b_H', 'b_E', 'b_V', 'b_F', 'g_H', 'g_E', 'g_V', 'g_F']].round(1).reset_index()
out.append('### T8. Same check for the v1 model as first locked (no event dummies, CR1): false-alarm %\n\n' + md(c1))
rows = []
for b in BLK:
    for rho in [0.05, 0.10, 0.15, 0.20, 0.30]:
        row = {}
        for sm in ['all', 'excl_BS']:
            x = san[(san.scenario == 'int') & (san.model == 'M1_primary') & (san.planted == b) & (san.strength == rho) &
                    (san['sample'] == sm) & (san.term == f'g_{b}')].iloc[0]
            row['block'], row['true g'] = b, round(x.implied_g, 2)
            row[f'bias ({sm})'] = round(x.mean_est / x.implied_g, 2)
            row[f'power % ({sm})'] = round(x.power_pos_pct)
            row[f'Holm power % ({sm})'] = round(x.power_pos_holm_pct)
        rows.append(row)
out.append('### T9. Planted interaction (fake Y): bias and power, M1 primary\n\n' + md(pd.DataFrame(rows)))
m = mde[mde.model == 'M1_primary'].copy()
m['mde'] = m.mde_g_80pct_power.map(lambda x: f'{x:.2f}' if pd.notna(x) else f'not reached (max g tested)')
m['at max g tested'] = m.apply(lambda a: f'{a.power_at_largest_rho_pct:.0f}% at g={a.largest_implied_g:.2f}', axis=1)
out.append('### T10. Smallest interaction g detected at 80% power\n\n' + md(m[['block', 'sample', 'rule', 'mde', 'at max g tested']]))
rows = []
for b in ['V', 'F']:
    for rr in [0.2, 0.4, 0.6]:
        row = {'planted on': b, 'r within >=5% rows': rr}
        for sm in ['all', 'excl_BS']:
            g = san[(san.scenario == 'thr') & (san.model == 'M1_primary') & (san.planted == b) & (san.strength == rr) &
                    (san['sample'] == sm) & (san.term == f'g_{b}')].iloc[0]
            o_ = san[(san.scenario == 'thr') & (san.model == 'M1_primary') & (san.planted == b) & (san.strength == rr) &
                     (san['sample'] == sm) & (san.term == 'omnibus_g')].iloc[0]
            row[f'g detected % ({sm})'] = round(g.power_pos_pct)
            row[f'g Holm % ({sm})'] = round(g.power_pos_holm_pct)
            row[f'omnibus % ({sm})'] = round(o_.power_pos_pct)
        rows.append(row)
out.append('### T11. Threshold-shaped effect (only fires >= 5% burned) planted in fake Y: power of the continuous model\n\n' + md(pd.DataFrame(rows)))

# 12. post hoc
p = ph[ph.target == 'Y'].merge(phs[['group', 'slope_Y_on_V', 'sd_Y', 'resid_sd']], on='group')
p['Spearman V-Y (95% CI)'] = p.apply(lambda a: f'{a.spearman_V:+.2f} [{a.lo:+.2f}, {a.hi:+.2f}]', axis=1)
p['slope'] = p.slope_Y_on_V.round(2)
p['SD of Y*'] = p.sd_Y.round(2)
p['resid SD'] = p.resid_sd.round(2)
out.append('### T12. POST HOC (not part of the locked test): V vs Y by event and size band\n\n' +
           md(p[['group', 'rows', 'councils', 'Spearman V-Y (95% CI)', 'slope', 'SD of Y*', 'resid SD']]))
phd['g_V (95% CI)'] = phd.apply(lambda a: f'{a.g_V:+.2f} [{a.lo:+.2f}, {a.hi:+.2f}]', axis=1)
out.append('### T13. POST HOC: V x size in simpler settings (Y, jackknife)\n\n' + md(phd[['model', 'rows', 'g_V (95% CI)', 'p']].round(2)))
(RES / 'FINDINGS_TABLES.md').write_text('\n\n'.join(out) + '\n')
print('\n\n'.join(out))
