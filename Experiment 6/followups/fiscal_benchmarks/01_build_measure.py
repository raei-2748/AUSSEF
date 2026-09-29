"""Step 1 (no Y): build the benchmark-count fiscal measure for every council x fire row and every council-year.
Definitions are pre-specified in the header of bench_common.py. Writes BENCHMARK_YEAR_TABLE.csv and
BENCHMARK_MEASURE_ROWS.csv. Reads only master keys (agrn, region_id, first_fire_start, burned share).
Run: python3 01_build_measure.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

from bench_common import (BENCH, MIN_YEARS, N_PRE, OLD_F_ITEMS, pct, window_measure, year_table)

HERE = Path(__file__).resolve().parent
WORKBOOK = Path.home() / ('Library/CloudStorage/GoogleDrive-raywang886@gmail.com/My Drive/'
                          'Application Folder - Ray/3. Extracurriculars/AUSSEF/Data/'
                          'nsw_bushfires_2015_2025_XY.xlsx')
OLG_WIDE = Path('/Users/ray/Research/AUSSEF/fire_event_dataset/data/olg/olg_wide.parquet')


def check_year_convention(ly):
    """lga_year.year must equal the OLG financial-year START year (year 2014 = FY2014-15)."""
    w = pd.read_parquet(OLG_WIDE)
    a = ly[ly.region_name == 'Albury'].set_index('year').fiscal_operating_ratio_pct_fy
    b = w[w.council_name_norm == 'albury'].set_index('fy_start').operating_performance_ratio_pct
    j = pd.concat([a, b], axis=1, keys=['lga_year', 'olg_fy_start']).dropna()
    assert len(j) >= 8 and np.allclose(j.lga_year, j.olg_fy_start, atol=0.01), j
    print('year convention OK: lga_year.year == OLG fy_start on', len(j), 'Albury years')


def main():
    ly = pd.read_excel(WORKBOOK, sheet_name='lga_year', header=1, keep_default_na=False, na_values=[''])
    check_year_convention(ly)
    ly = ly[(ly.year >= 2014) & (ly.year <= 2023)].copy()
    yt = year_table(ly)
    # old six-ratio F block recomputed within each financial year (time-matched comparator F_tm)
    f_items = pd.DataFrame(index=yt.index)
    for col, sign in OLD_F_ITEMS.items():
        f_items[col] = yt.groupby('year')[col].transform(lambda s, sg=sign: pct(s, sg))
    yt['F_year'] = f_items.mean(axis=1, skipna=True)
    keep = (['region_id', 'region_name', 'year'] + [c for c, *_ in BENCH.values()] + ['fiscal_debt_service_ratio_pct_fy'] +
            [f'{k}_met' for k in BENCH] + ['n_measurable', 'n_met', 'usable', 'F_year'])
    yt[keep].to_csv(HERE / 'BENCHMARK_YEAR_TABLE.csv', index=False)
    print('council-years', len(yt), 'usable', int(yt.usable.sum()))

    m = pd.read_excel(WORKBOOK, sheet_name='master', header=2, keep_default_na=False, na_values=[''],
                      usecols=['agrn', 'region_id', 'region_name', 'first_fire_start',
                               'X_fire_share_of_council_burned'])
    m['agrn'] = m.agrn.astype(str)
    m['region_id'] = m.region_id.astype(int)
    d0 = pd.to_datetime(m.first_fire_start)
    m['fire_fy_start'] = np.where(d0.dt.month >= 7, d0.dt.year, d0.dt.year - 1)
    rows = []
    for _, r in m.iterrows():
        yrs = [int(r.fire_fy_start) - k for k in range(1, N_PRE + 1)]
        out = window_measure(yt, r.region_id, yrs)
        fy = yt[(yt.region_id == r.region_id) & yt.year.isin(yrs)].F_year.dropna()
        out['F_tm'] = fy.mean() if len(fy) >= MIN_YEARS else np.nan
        rows.append(out)
    res = pd.concat([m.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    res['stress_bench'] = 1 - res.bench_share
    res['stress_years'] = 1 - res.years_share
    res['stress_avg3'] = 1 - res.avg3_share
    res['stress_fin5'] = 1 - res.fin5_share
    res['stress_infra3'] = 1 - res.infra3_share
    res.rename(columns={'X_fire_share_of_council_burned': 'share'}).to_csv(HERE / 'BENCHMARK_MEASURE_ROWS.csv',
                                                                            index=False)
    print('rows', len(res), 'with bench_share', int(res.bench_share.notna().sum()))
    print('rows by fire FY start:'); print(res.groupby('fire_fy_start').agg(
        rows=('agrn', 'size'), with_measure=('bench_share', lambda s: int(s.notna().sum()))).T.to_string())
    print(res.bench_share.describe().round(3).to_string())
    print(res.bench_n_met_of8.describe().round(2).to_string())


if __name__ == '__main__':
    main()
