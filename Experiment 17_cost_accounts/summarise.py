"""Experiment 17: summary tables and internal checks from build_accounts.py outputs.
Run: python3 summarise.py  ->  results/SUMMARY_BY_FIRE.csv, results/BLACK_SUMMER_BY_COUNCIL.csv, results/CHECKS.txt"""
from pathlib import Path

import numpy as np
import pandas as pd

from build_accounts import main as build_main

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
PAYERS = ['households_uninsured', 'insurers', 'commonwealth', 'nsw_state']
LOSS = ['loss_households_uninsured', 'loss_insurers', 'loss_commonwealth_cleanup', 'loss_nsw_cleanup']
REC = ['rec_commonwealth', 'rec_nsw']


def main():
    A, acc, ev = build_main()
    # ---- per fire: A$m, low-mid-high and mid shares
    rows = []
    for r in ev.itertuples():
        d = dict(agrn=r.agrn, F=r.F, councils=r.n_councils, homes_destroyed=r.homes, rows_homes_unknown=r.homes_unknown_rows)
        for p in LOSS + REC + PAYERS + ['loss_account', 'recovery_money', 'total']:
            lo, mi, hi = (getattr(r, f'{p}_{s}') / 1e6 for s in ('low', 'mid', 'high'))
            d[f'{p}_A$m_mid'] = round(mi, 1)
            d[f'{p}_A$m_range'] = f'{min(lo, mi, hi):.1f} to {max(lo, mi, hi):.1f}'   # min-max over scenarios
        for p in PAYERS:
            d[f'{p}_share_mid'] = round(getattr(r, f'{p}_mid') / r.total_mid, 3) if r.total_mid > 0 else np.nan
            d[f'{p}_share_low_high_scen'] = (f'{getattr(r, f"{p}_low") / r.total_low:.2f} / '
                                             f'{getattr(r, f"{p}_high") / r.total_high:.2f}') if r.total_low > 0 else ''
        d['government_lines_included'] = 'yes (871 only)' if r.agrn == '871' else 'no data (homes and ICA only)'
        rows.append(d)
    S = pd.DataFrame(rows)
    S.to_csv(OUT / 'SUMMARY_BY_FIRE.csv', index=False)

    # ---- Black Summer by council (mid, A$m) with ranges for the household gap
    b = acc[acc.agrn == '871'].copy()
    cols = {'homes': 'homes_destroyed', 'homes_damaged': 'homes_damaged'}
    t = b[['region_name'] + list(cols)].rename(columns=cols)
    mm = lambda c: (b[c] / 1e6).round(2)  # noqa: E731
    t['rebuild_cost_mid'] = mm('A1_rebuild_mid')
    t['household_uninsured_mid'] = mm('A1_household_mid')
    t['household_uninsured_range'] = [f'{min(lo, hi) / 1e6:.2f} to {max(lo, hi) / 1e6:.2f}' for lo, hi in
                                      zip(b.A1_household_low, b.A1_household_high)]
    t['insurers_homes_mid'] = mm('A1_insurer_mid')
    t['insurers_other_mid'] = mm('A2_other_insured_mid')
    t['cleanup_mid'] = mm('A3_cleanup_mid')
    t['drp_dra_mid'] = mm('B1_drp_mid')
    t['programs_total'] = mm('B2_programs_mid')
    t['programs_commonwealth'] = mm('B2_programs_cth_mid')
    t['commonwealth_mid'] = ((b.A3_cleanup_cth_mid + b.B1_drp_mid + b.B2_programs_cth_mid) / 1e6).round(2)
    t['nsw_mid'] = ((b.A3_cleanup_mid - b.A3_cleanup_cth_mid + b.B2_programs_mid - b.B2_programs_cth_mid) / 1e6).round(2)
    t['total_mid'] = (t[['household_uninsured_mid', 'insurers_homes_mid', 'insurers_other_mid', 'commonwealth_mid',
                         'nsw_mid']].sum(axis=1)).round(2)
    t['household_share_mid'] = (t.household_uninsured_mid / t.total_mid).round(3)
    t['memo_stmt_fire_grants_extra'] = mm('memo_stmt_fire_grants_extra_aud_strict')
    t['memo_audit_office_damage_est'] = mm('memo_audit_lg2020_damage_estimate')
    t['memo_council_own_net_mid'] = mm('memo_council_own_mid')
    t = t.sort_values('homes_destroyed', ascending=False)
    t.to_csv(OUT / 'BLACK_SUMMER_BY_COUNCIL.csv', index=False)

    # ---- checks
    L = []
    bs = ev[ev.agrn == '871'].iloc[0]
    L.append(f"871 clean-up rows sum {b.A3_cleanup_mid.sum() / 1e6:.1f} vs assumption {A['cleanup_total_871']['mid'] / 1e6:.1f}")
    L.append(f"871 DRP rows sum {b.B1_drp_mid.sum() / 1e6:.1f} vs assumption {A['drp_dra_nsw_871']['mid'] / 1e6:.1f}")
    ins = b.A1_insurer_mid.sum() + b.A2_other_insured_mid.sum()
    L.append(f"871 insurer rows sum {ins / 1e6:.1f} vs ICA NSW {A['ica_871_nsw']['mid'] / 1e6:.1f}")
    L.append(f"871 payers sum {sum(bs[p + '_mid'] for p in PAYERS) / 1e6:.1f} = total {bs.total_mid / 1e6:.1f}")
    L.append(f"871 homes in panel {b.homes.sum():.0f} (NSW official 2,476 in E17-015; 2,448 in key_events)")
    hi = b.A1_insurer_mid.sum()
    L.append(f"871 insurer part of destroyed homes {hi / 1e6:.0f}m vs NSW home-building claims implied by ICA "
             f"(9,478 x $131,848 x 81% = {9478 * 131848 * 0.81 / 1e6:.0f}m, includes damaged homes; E17I-073, E17I-029)")
    neg = acc[[c for c in acc.columns if c.startswith('A2_other_insured_')]].lt(0).any(axis=1)
    L.append(f"rows with negative other-insured (ICA smaller than modelled home claims): {int(neg.sum())} "
             f"{acc.loc[neg, ['agrn', 'region_name']].values.tolist()}")
    L.append(f"rows with homes unknown: {int(acc.homes.isna().sum())}; rows with homes > 0: {int((acc.homes > 0).sum())}")
    nh = ev[(ev.homes > 0) & (ev.agrn != '871')]
    L.append(f"non-Black Summer events with homes destroyed: {len(nh)}, homes {nh.homes.sum():.0f}, "
             f"total mid {nh.total_mid.sum() / 1e6:.1f}m")
    for s in ('low', 'mid', 'high'):
        L.append(f"871 {s}: " + ', '.join(f"{p} {bs[p + '_' + s] / 1e6:.0f}m ({bs[p + '_' + s] / bs['total_' + s]:.1%})"
                                         for p in PAYERS) + f", total {bs['total_' + s] / 1e6:.0f}m")
    per = {p: bs[p + '_mid'] / b.homes.sum() for p in PAYERS + ['total']}
    L.append('871 per home destroyed (mid, A$k): ' + ', '.join(f'{k} {v / 1e3:.0f}' for k, v in per.items()))
    C = A['rebuild_cost_per_home']; u = A['uninsured_share']; g = A['underinsured_shortfall']
    L.append('household gap per destroyed home (FY2019-20 A$k): ' + ', '.join(
        f"{s} {C[s] * (u[s] + (1 - u[s]) * g[s]) / 1e3:.0f} ({u[s] + (1 - u[s]) * g[s]:.1%} of {C[s] / 1e3:.0f}k)"
        for s in ('low', 'mid', 'high')))
    memo = b[['memo_stmt_fire_grants_extra_aud_strict', 'memo_nbra_lga_package_grant', 'memo_bcrrf1_grant',
              'memo_epa_green_waste_grant', 'memo_epa_landfills_grant']].dropna(subset=['memo_stmt_fire_grants_extra_aud_strict'])
    L.append(f"871 councils with statements: {len(memo)}; statement fire-grant rise FY F..F+2 "
             f"{memo.memo_stmt_fire_grants_extra_aud_strict.sum() / 1e6:.1f}m vs council-paid programs (NBRA+BCRRF+EPA) "
             f"{memo.iloc[:, 1:].fillna(0).sum().sum() / 1e6:.1f}m in the same councils")
    # Black Summer two-block account, low/mid/high (A$m)
    blk = []
    for p in LOSS + ['loss_account'] + REC + ['rec_household_payments', 'recovery_money']:
        blk.append(dict(line=p, **{sc: round(bs[f'{p}_{sc}'] / 1e6, 1) for sc in ('low', 'mid', 'high')},
                        share_of_block_mid=round(bs[f'{p}_mid'] / bs['loss_account_mid' if p.startswith('loss')
                                                                        else 'recovery_money_mid'], 3)))
    pd.DataFrame(blk).to_csv(OUT / 'BLACK_SUMMER_ACCOUNT.csv', index=False)
    L.append('871 loss account (A$m low/mid/high): ' + '; '.join(
        f"{r['line']} {r['low']}/{r['mid']}/{r['high']} ({r['share_of_block_mid']:.1%})" for r in blk))
    hh = t[t.homes_destroyed > 0].household_share_mid
    L.append(f"871 household share of combined total by council (councils with homes): {hh.min():.1%} to {hh.max():.1%}, "
             f"median {hh.median():.1%}, n={len(hh)}")
    # sensitivity: high rebuild cost +25% (IAG) instead of +15%
    import copy
    from build_accounts import build, rows as get_rows
    A2 = copy.deepcopy(A); A2['rebuild_cost_per_home']['high'] = 430000
    acc2 = build(A2, get_rows()); b2 = acc2[acc2.agrn == '871']
    L.append(f"sensitivity rebuild high 430k (+25%, IAG): 871 household gap high {b2.A1_household_high.sum() / 1e6:.0f}m "
             f"vs {b.A1_household_high.sum() / 1e6:.0f}m; rebuild high {b2.A1_rebuild_high.sum() / 1e6:.0f}m")
    st = b.dropna(subset=['memo_stmt_fire_grants_extra_aud_strict'])
    cs = pd.read_csv(OUT / 'COUNCIL_SIDE.csv', dtype={'agrn': str})
    cs = cs[(cs.agrn == '871') & cs.stmt_fire_grants_extra_aud_strict.notna()]
    L.append(f"871 statements: strict {cs.stmt_fire_grants_extra_aud_strict.sum() / 1e6:.1f}m, wide "
             f"{cs.stmt_fire_grants_extra_aud_wide.sum() / 1e6:.1f}m; councils {len(cs)}, with all 3 post years "
             f"{int((cs.stmt_fire_grants_extra_aud_strict_nyears == 3).sum())}; capex change (not used) "
             f"{cs.stmt_capex_extra_aud.sum() / 1e6:.1f}m")
    (OUT / 'CHECKS.txt').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))
    pd.set_option('display.width', 250)
    print(t.head(15).to_string(index=False))


if __name__ == '__main__':
    main()
