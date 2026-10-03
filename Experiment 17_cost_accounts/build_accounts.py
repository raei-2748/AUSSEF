"""Experiment 17: bottom-up cost account per council x fire and per fire event: who carried the cost.

Every number used comes from ASSUMPTIONS.csv (low / mid / high, each with bibliography source ids) or from project
data (master workbook, Experiment 6 DL_FILLED, council_side.py output). Run council_side.py first.

Two blocks, kept apart so transfers are not counted twice:
  A. LOSS ACCOUNT (what was destroyed or had to be cleaned up)
     A1 homes destroyed x rebuild cost  -> split insurer / household (non-insurance, under-insurance)
     A2 other insured losses (contents, cars, business, farm) = ICA event loss (NSW part) - insurer part of A1,
        only for events in the ICA list; apportioned to councils by share of the event's homes destroyed
     A3 clean-up of destroyed homes (government-run program; Black Summer only) -> Commonwealth / NSW
  B. RECOVERY MONEY (paid by governments after the fire; not a loss, a response)
     B1 Disaster Recovery Payment + Allowance to households (Commonwealth), Black Summer only, event level,
        apportioned by homes destroyed + damaged (rough)
     B2 recovery programs in the master (AGRN 871 only): NBRA package, BSBR (Commonwealth); BLER, BCRRF (joint
        50:50), EPA green waste (joint, Commonwealth 50-75%), EPA council landfills (NSW only)
  Not implemented: council asset restoration (DRFA Category B) - no event-level figure (memo in FINDINGS only).
  Councils' own share: Experiment 7 Day 11 net-cost slope (not detected; memo_ columns, not added to totals).
  Payer totals are reported separately for the loss account (A) and recovery money (B); see who_paid().

Run: python3 build_accounts.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'Experiment 7'))
from build_y2 import load  # noqa: E402

OUT = HERE / 'results'
SC = ('low', 'mid', 'high')


def num(s):
    return pd.to_numeric(s, errors='coerce')


def assumptions():
    a = pd.read_csv(HERE / 'ASSUMPTIONS.csv', comment='#')
    return {r.key: {s: float(getattr(r, s)) for s in SC} for r in a.itertuples()}


def rows():
    m, ly = load()
    dl = pd.read_csv(ROOT / 'Experiment 6/followups/dl_fill/DL_FILLED.csv', dtype={'agrn': str, 'region_id': str})
    m = m.merge(dl[['agrn', 'region_id', 'DL_fill_flag', 'homes_per_1000_v2_inferred', 'dwellings']],
                on=['agrn', 'region_id'], how='left')
    m['homes'] = (m.homes_per_1000_v2_inferred * m.dwellings / 1000).round(0)
    m['homes_damaged'] = num(m.DL_homes_damaged_sourced).fillna(0)
    m.loc[m.homes.isna(), 'homes_damaged'] = np.nan
    m['pop'] = num(m.X_council_council_population_pre)
    for k in ['nbra_lga_package_grant', 'bsbr_project_funding', 'bler_project_funding', 'bcrrf1_grant',
              'epa_green_waste_grant', 'epa_landfills_grant', 'audit_lg2020_damage_estimate',
              'audit_lg2020_funding_received']:
        m[k] = num(m[f'FP_reported_{k}_aud'])
    cs = pd.read_csv(OUT / 'COUNCIL_SIDE.csv', dtype={'agrn': str, 'region_id': str})
    m = m.merge(cs.drop(columns=['region_name', 'F']), on=['agrn', 'region_id'], how='left')
    return m


# ICA catastrophes linked to panel events (local ICA list, E17-008); NSW share per assumption key
ICA = {
    '871': ('CAT195 NSW part (A$1.88bn, E17-027) + CAT193 Sep 2019 NSW/QLD (A$13.5m)', 'ica_871_nsw'),
    'NSW1718-20': ('CAT182 Tathra + SW Victoria (A$82.5m)', 'ica_tathra_nsw'),
    'CAT171': ('CAT171 NSW bushfires Feb 2017 (A$33.5m)', 'ica_cat171'),
    'NOV2016': ('Undeclared NSW bushfires Nov 2016 (A$1.0m)', 'ica_nov2016'),
}


def ica_group(agrn):
    if agrn == '871':
        return '871'
    if agrn == 'NSW1718-20':
        return 'NSW1718-20'
    if agrn in ('RAA-raa_2016_p13_r17', 'RAA-raa_2016_p13_r23'):
        return 'CAT171'
    if agrn in ('RAA-raa_2016_p13_r06', 'RAA-raa_2016_p13_r07', 'RAA-raa_2016_p13_r08'):
        return 'NOV2016'
    return None


# ABS average value per new house approved, Rest of NSW, by FY (E17R-038, A$'000); FY16 and FY18 interpolated
ABS_REST_NSW = {2015: 285.6, 2016: (285.6 + 308.9) / 2, 2017: 308.9, 2018: (308.9 + 338.5) / 2, 2019: 338.5,
                2020: 344.3, 2021: 360.9, 2022: 392.5, 2023: 459.9, 2024: 476.1, 2025: 521.0}


def rebuild_index(F):
    """Cost level of the fire's own financial year (ABS keys = year the FY ends) relative to FY2019-20."""
    return ABS_REST_NSW[F + 1] / ABS_REST_NSW[2020]


def build(A, m):
    m = m.copy()
    m['ica_group'] = m.agrn.map(ica_group)
    out = m[['agrn', 'region_id', 'region_name', 'F', 'DL_fill_flag', 'homes', 'homes_damaged', 'pop',
             'ica_group']].copy()
    out['rebuild_index'] = m.F.map(rebuild_index)
    bs = m.agrn == '871'
    hb = m.homes.where(bs).fillna(0)
    for s in SC:
        C = A['rebuild_cost_per_home'][s] * out.rebuild_index
        u = A['uninsured_share'][s]
        g = A['underinsured_shortfall'][s]          # average shortfall across insured destroyed homes
        rebuild = m.homes * C
        ins_home = rebuild * (1 - u) * (1 - g)
        out[f'A1_rebuild_{s}'] = rebuild
        out[f'A1_insurer_{s}'] = ins_home
        out[f'A1_household_{s}'] = rebuild - ins_home
        # A2: event insured loss apportioned by homes share (equal split if the event has no homes destroyed)
        a2 = pd.Series(np.nan, index=m.index)
        for grp, (_, key) in ICA.items():
            ix = m.index[m.ica_group == grp]
            h = m.loc[ix, 'homes'].fillna(0)
            w = h / h.sum() if h.sum() > 0 else pd.Series(1 / len(ix), index=ix)
            a2.loc[ix] = A[key][s] * w - ins_home.loc[ix].fillna(0)
        out[f'A2_other_insured_{s}'] = a2
        # A3 clean-up (Black Summer program, event total apportioned by homes destroyed)
        out[f'A3_cleanup_{s}'] = np.where(bs, A['cleanup_total_871'][s] * hb / hb.sum(), np.nan)
        out[f'A3_cleanup_cth_{s}'] = out[f'A3_cleanup_{s}'] * A['cleanup_cth_share'][s]
        # B1 DRP/DRA (NSW, Black Summer) apportioned by homes destroyed + damaged (rough)
        hd = (m.homes.fillna(0) + m.homes_damaged.fillna(0)).where(bs, 0)
        out[f'B1_drp_{s}'] = np.where(bs, A['drp_dra_nsw_871'][s] * hd / hd.sum(), np.nan)
        # B2 programs: Commonwealth = NBRA + BSBR + Cth share of BLER, BCRRF, green waste; NSW = rest + landfills
        f0 = lambda k: m[k].fillna(0)  # noqa: E731
        cth = (f0('nbra_lga_package_grant') + f0('bsbr_project_funding')
               + A['joint_cth_share'][s] * (f0('bler_project_funding') + f0('bcrrf1_grant'))
               + A['greenwaste_cth_share'][s] * f0('epa_green_waste_grant'))
        tot = (f0('nbra_lga_package_grant') + f0('bsbr_project_funding') + f0('bler_project_funding')
               + f0('bcrrf1_grant') + f0('epa_green_waste_grant') + f0('epa_landfills_grant'))
        out[f'B2_programs_{s}'] = np.where(bs, tot, np.nan)
        out[f'B2_programs_cth_{s}'] = np.where(bs, cth, np.nan)
        # memo: councils' own net cost (Day 11 slope, A$/resident/yr per 10 homes per 1,000 dwellings, 3 years)
        out[f'memo_council_own_{s}'] = A['council_net_slope'][s] * m.homes_per_1000_v2_inferred / 10 * m['pop'] * 3
    for k in ['nbra_lga_package_grant', 'bsbr_project_funding', 'bler_project_funding', 'bcrrf1_grant',
              'epa_green_waste_grant', 'epa_landfills_grant', 'audit_lg2020_damage_estimate',
              'audit_lg2020_funding_received', 'stmt_fire_grants_extra_aud_strict', 'stmt_fire_grants_extra_aud_wide',
              'stmt_capex_extra_aud', 'olg_grants_extra_aud_F0_F2']:
        out['memo_' + k] = m[k]
    return out


def who_paid(t, s, A):
    """Totals by payer for one scenario (A$), loss account and recovery money kept apart."""
    ct = A['cleanup_cth_share'][s]
    z = lambda x: 0.0 if pd.isna(x) else x   # noqa: E731
    f = lambda c: z(t[c].sum(min_count=1))   # noqa: E731
    clean, drp = f(f'A3_cleanup_{s}'), f(f'B1_drp_{s}')
    prog, prog_cth = f(f'B2_programs_{s}'), f(f'B2_programs_cth_{s}')
    d = dict(loss_households_uninsured=f(f'A1_household_{s}'),
             loss_insurers=f(f'A1_insurer_{s}') + f(f'A2_other_insured_{s}'),
             loss_commonwealth_cleanup=clean * ct, loss_nsw_cleanup=clean * (1 - ct),
             rec_commonwealth=drp + prog_cth, rec_nsw=prog - prog_cth, rec_household_payments=drp)
    d['loss_account'] = (d['loss_households_uninsured'] + d['loss_insurers'] + clean)
    d['recovery_money'] = drp + prog
    # combined view (gross: losses plus government outlays; transfers to households are not netted off)
    d['households_uninsured'] = d['loss_households_uninsured']
    d['insurers'] = d['loss_insurers']
    d['commonwealth'] = d['loss_commonwealth_cleanup'] + d['rec_commonwealth']
    d['nsw_state'] = d['loss_nsw_cleanup'] + d['rec_nsw']
    d['total'] = d['loss_account'] + d['recovery_money']
    return d


def main():
    A = assumptions()
    m = rows()
    acc = build(A, m)
    acc.to_csv(OUT / 'ACCOUNT_BY_COUNCIL.csv', index=False)
    ev = []
    for agrn, t in acc.groupby('agrn'):
        r = dict(agrn=agrn, F=int(t.F.iloc[0]), n_councils=len(t), homes=t.homes.sum(min_count=1),
                 homes_unknown_rows=int(t.homes.isna().sum()))
        for s in SC:
            for k, v in who_paid(t, s, A).items():
                r[f'{k}_{s}'] = v
        ev.append(r)
    ev = pd.DataFrame(ev).sort_values(['F', 'agrn'])
    ev.to_csv(OUT / 'ACCOUNT_BY_FIRE.csv', index=False)
    return A, acc, ev


if __name__ == '__main__':
    A, acc, ev = main()
    pd.set_option('display.width', 250)
    show = ev[ev.homes > 0][['agrn', 'F', 'homes'] + [c for c in ev.columns if c.endswith('_mid')]]
    print((show.set_index(['agrn', 'F', 'homes']) / 1e6).round(1).to_string())
