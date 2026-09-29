"""Stage 2 (EXPLORATORY re-estimate on seen rows; PRESPEC_STAGE2.md). Reuses the stage-1 score table and test functions unchanged.
New/changed inputs only: NSW 2013 SL pillar (DSS), Victorian DL cells added in stage2/inputs_dl/dl_stage2_additions.csv.
Refuses to run if the stage-2 pre-spec or its amendment changed, or if results_stage2/exploratory_test exists (run once).
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import run_frozen_test as rf  # noqa: E402  (functions only; its main() is not called)
from nf_lib import INP, place_signed  # noqa: E402

RES2 = HERE / 'results_stage2'
OUT = RES2 / 'exploratory_test'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    for m in ('PRESPEC_STAGE2', 'PRESPEC_STAGE2_AMENDMENT_1'):
        assert sha(HERE / f'{m}.md') in (HERE / f'{m}.lock').read_text(), f'{m} changed since lock'
    rf.verify_locks()                                   # stage-1 locks must still hold (score table, Y inputs, pre-spec)
    if OUT.exists():
        sys.exit('stage-2 exploratory test already run')
    OUT.mkdir(parents=True)
    D = pd.read_csv(HERE.parent / 'results/Y_indicators_new_rows.csv', dtype={'region_id': str})
    # Victorian DL additions (sourced only)
    add = HERE / 'inputs_dl/dl_stage2_additions.csv'
    dl2 = pd.read_csv(add, dtype={'region_id': str}) if add.exists() else pd.DataFrame(columns=['event', 'region_id', 'homes_destroyed', 'status'])
    ref = pd.read_csv(INP / 'master_reference_indicators.csv')
    D['homes_destroyed2'] = D.homes_destroyed
    D['flag_DL2'] = D.flag_DL
    for r in dl2.itertuples():
        m = (D.event == r.event) & (D.region_id == r.region_id)
        assert m.sum() == 1
        D.loc[m, 'homes_destroyed2'] = r.homes_destroyed
        D.loc[m, 'flag_DL2'] = r.status
    D['raw_DL2'] = np.where(D.homes_destroyed2.notna(), D.homes_destroyed2 / D.dwellings_census2011 * 1000, np.nan)
    D['DL2'] = [place_signed(v, ref.DL_homes_per_1000_dwellings_signed) for v in D.raw_DL2]
    sl = pd.read_csv(RES2 / 'SL_nsw2013.csv', dtype={'lga_code': str}).rename(columns={'lga_code': 'region_id'})
    D = D.merge(sl.assign(n_imputed=sl.n_imputed_before + sl.n_imputed_after)[['region_id', 'pct_SL', 'n_imputed']].assign(event='NSW_2013_oct'), on=['event', 'region_id'], how='left')
    D['SL2'] = D.pct_SL
    P = ['DL2', 'IL', 'FP', 'SL2']
    D['pillars_n2'] = D[P].notna().sum(axis=1)
    D['Y_new2'] = D[P].mean(axis=1, skipna=True).where(D.pillars_n2 >= 1)
    D['Y_new2_ge2pillars'] = D.Y_new2.where(D.pillars_n2 >= 2)
    Q = [p for p in P if p != 'FP']
    D['Y_new2_noFP'] = D[Q].mean(axis=1, skipna=True).where(D[Q].notna().sum(axis=1) >= 1)
    D['DL2_reported_only'] = D.DL2.where(D.flag_DL2 == 'reported')
    R = ['DL2', 'IL_biz_only', 'FP', 'SL2']
    D['Y_new2_vic_IL_biz_only'] = np.where(D.event.str.startswith('VIC'), D[['DL2', 'IL_biz_only']].mean(axis=1, skipna=True), D.Y_new2)
    D['is_vic'] = D.event.str.startswith('VIC')
    D.to_csv(RES2 / 'Y_stage2_rows.csv', index=False)
    D = D[D.risk_add_avail.notna()].copy()
    rng = np.random.default_rng(rf.SEED_BOOT)

    def T(tid, scope, sub, score, target, note=''):
        n, est, lo, hi = rf.boot(sub[score], sub[target], sub.region_id, rng)
        return dict(test=tid, scope=scope, score=score, target=target, n=n, spearman=est, ci_low=lo, ci_high=hi, note=note)
    scopes = {'pooled': D, 'NSW_2013': D[~D.is_vic], 'VIC_2009': D[D.is_vic]}
    res = []
    for sc, sub in scopes.items():
        res.append(T('PRIMARY_EXPLORATORY' if sc == 'pooled' else 'primary_by_event', sc, sub, 'risk_add_avail', 'Y_new2'))
        res.append(T('DL_only', sc, sub, 'risk_add_avail', 'DL2'))
        for p in ('IL', 'FP', 'SL2'):
            res.append(T('pillar', sc, sub, 'risk_add_avail', p))
    for sc, sub in scopes.items():
        res.append(T('secondary_S1_V', sc, sub, 'S1_V', 'Y_new2'))
        res.append(T('secondary_S1_V_DL', sc, sub, 'S1_V', 'DL2'))
        if sc != 'VIC_2009':
            res.append(T('secondary_S2_HV', sc, sub, 'S2_HV', 'Y_new2'))
        sb = sub[sub.share_burned >= 0.05]
        res.append(T('sens_a_share_ge5pct', sc, sb, 'risk_add_avail', 'Y_new2', 'descriptive'))
        res.append(T('sens_b_ge2_pillars', sc, sub, 'risk_add_avail', 'Y_new2_ge2pillars', 'descriptive'))
        res.append(T('sens_c_no_FP', sc, sub, 'risk_add_avail', 'Y_new2_noFP', 'descriptive'))
        res.append(T('sens_d_DL_reported_only', sc, sub, 'risk_add_avail', 'DL2_reported_only', 'descriptive'))
        if sc != 'NSW_2013':
            res.append(T('sens_f_vic_IL_biz_only', sc, sub, 'risk_add_avail', 'Y_new2_vic_IL_biz_only', 'descriptive'))
    R = pd.DataFrame(res)
    R.to_csv(OUT / 'TEST_RESULTS_STAGE2.csv', index=False)
    prim = R[R.test == 'PRIMARY_EXPLORATORY'].iloc[0]
    lo, hi = prim.ci_low, prim.ci_high
    verdict = 'CANNOT TELL (not estimable)' if np.isnan(lo) else 'REPLICATED' if lo > 0 else 'NOT REPLICATED' if hi < rf.REPL_UPPER else 'CANNOT TELL'
    F = pd.read_csv(HERE.parent / 'results/frozen_test/TEST_RESULTS.csv')
    json.dump(dict(stage='2 (exploratory, rows already seen)', verdict=verdict, primary=dict(n=int(prim.n), spearman=prim.spearman, ci_low=lo, ci_high=hi),
                   frozen_stage1=dict(verdict=json.load(open(HERE.parent / 'results/frozen_test/VERDICT.json'))['verdict']),
                   rows_pillars=D.pillars_n2.value_counts().to_dict()), open(OUT / 'VERDICT_STAGE2.json', 'w'), indent=1, default=str)
    print(R.round(3).to_string())
    print('STAGE-2 (EXPLORATORY) VERDICT:', verdict)
    rngp = np.random.default_rng(rf.SEED_POWER)
    Pw = D[D.Y_new2.notna()]
    rows = rf.power_table(Pw.risk_add_avail.to_numpy(float), 'pooled primary rows', rngp)
    rows += rf.power_table(Pw[Pw.share_burned >= 0.05].risk_add_avail.to_numpy(float), 'rows with share >= 5%', rngp)
    for nm, g in Pw.groupby('is_vic'):
        rows += rf.power_table(g.risk_add_avail.to_numpy(float), 'VIC rows' if nm else 'NSW rows', rngp)
    pd.DataFrame(rows).to_csv(OUT / 'POWER_CHECK_STAGE2.csv', index=False)
    print(pd.DataFrame(rows).round(3).head(8).to_string())


if __name__ == '__main__':
    main()
