"""Pre-fit checks for defects discovered in V1; never uses test outcomes to tune."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import run_experiment as runner
from eligibility import apply_registry

ROOT = Path(__file__).resolve().parent


def main():
    m = pd.read_csv(ROOT / 'snapshot/master.csv')
    cb = pd.read_csv(ROOT / 'snapshot/codebook.csv').query("sheet == 'master'")
    reg = pd.read_csv(ROOT / 'SOURCE_ELIGIBILITY_REGISTRY.csv').fillna('')
    x, decisions, masked = apply_registry(m, cb)
    checks = {}
    counts = [1,6,8,10]
    a, b = [0,.1,.1,.1], [.2,.05,.05,.05]
    checks['unequal_fold_counterexample_changes_wrong_selection'] = bool(np.mean(a)<np.mean(b) and np.average(a,weights=counts)>np.average(b,weights=counts))
    checks['all_223_X_candidates_have_one_registry_rule'] = len(reg)==223 and reg.column.is_unique and set(reg.column)==set(cb.loc[cb.role_if_Y_sum=='X','column'])
    census = cb[(cb.role_if_Y_sum=='X') & cb.source.astype(str).str.contains('Census|SEIFA',case=False)].column
    rr = reg.set_index('column')
    checks['every_census_source_has_release_rule'] = bool(rr.loc[census,'action'].eq('census_release').all())
    checks['basic_census_exposure_masked_before_2017_release'] = bool(x.loc[pd.to_datetime(m.first_fire_start)<=pd.Timestamp('2017-06-27'), ['X_socio_pop_in_fire','X_socio_pop_within_1km','X_socio_pop_within_5km','X_socio_pop_within_5km_all_councils','X_socio_dwellings_in_fire','X_socio_dwellings_within_1km','X_socio_dwellings_within_5km','X_socio_dwellings_occupied']].isna().all().all())
    checks['both_road_columns_masked_before_2019'] = bool(x.loc[pd.to_datetime(m.first_fire_start)<pd.Timestamp('2019-01-01'),['X_env_road_km_burned','X_env_road_km_within_100m_sum']].isna().all().all())
    checks['remoteness_and_bcarr_removed'] = all(c not in x for c in rr[rr.family.isin(['remoteness_2021','bcarr_2025'])].index)
    altered = m.copy(); altered['Y']=999; altered['Y_class_from_Y']=-3; altered['DL']=-500
    xx,dd,mm = apply_registry(altered,cb)
    checks['target_perturbation_cannot_change_eligibility'] = x.equals(xx) and decisions.equals(dd) and masked.equals(mm)
    unknown = m.copy(); unknown['info_pop_census_year']=np.nan
    ux,_,_ = apply_registry(unknown,cb)
    checks['unknown_census_vintage_masked'] = bool(ux[census.tolist()].isna().all().all())
    checks['deeper_RF_leaf_sizes_and_default_feature_fraction_present'] = {p['min_samples_leaf'] for p in runner.RF_GRID}=={1,2,3,8,15} and {p['max_features'] for p in runner.RF_GRID}=={.33,.7,1.0} and len(runner.RF_GRID)==15
    old_path = ROOT.parent / 'bowen_rf_v1/snapshot/master.csv'
    if not old_path.exists():
        old_path = ROOT.parent / 'experiment_rf_v1/snapshot/master.csv'
    old = pd.read_csv(old_path)
    checks['all_targets_and_rows_identical_to_V1'] = m.equals(old)
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'passed':sum(checks.values()),'total':len(checks),
            'initial_candidates':223,'eligible_after_exclusions':x.shape[1],'masked_cells':len(masked)}
    (ROOT/'PRE_FIT_REPAIR_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
    assert all(checks.values()),result
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
