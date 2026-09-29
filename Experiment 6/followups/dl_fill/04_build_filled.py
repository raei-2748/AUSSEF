"""Step 4a: build the filled DL columns as a NEW file (workbook and aussef.duckdb are never touched).

Inputs
  - the master sheet (read-only): original DL_homes_destroyed_in_council, dwellings_census
  - fill_table.csv (hand-curated from verified sources; one row per council row filled): agrn, region_id, value, flag, ...
  - rules for estimated fills (below), applied only to rows still empty

Flags (column DL_fill_flag), in order of reliability:
  original_sourced           the 90 values already in the dataset (dl_council.py rules)
  reported_new               a NEW source states the homes-destroyed figure (or 'no homes lost') for that fire in that council
  inferred_zero_season       0 because the official RFS season total is used up by attributed fires (residual <= 1 home)
  reported_weak              a figure with a weak match (hedged 'at least', local belief, other date, several councils)
  estimated_area_share       a whole-fire figure split by burned area across councils (the dataset's own proxy; NOT reported)
  estimated_zero_season_budget  0 because the season residual is small (<= 3 homes) but not <= 1 (NOT reported)
  estimated_zero_small_fire  0 by a size rule for small fires with no evidence of loss (NOT reported)
  missing                    still empty
(03_make_fill_table.py writes fill_table.csv with every one of these.)

Cumulative variants (each keeps the earlier flags):
  DL_v1_reported   = original_sourced + reported_new
  DL_v2_inferred   = v1 + inferred_zero_season
  DL_v3_estimated  = v2 + reported_weak + estimated_*
The per-1000 rate and the percentile rank (the DL pillar) are recomputed within each variant, exactly as xy_format.build_y does.
"""
import numpy as np
import pandas as pd

from common import HERE, OUT, load_master

FILL = HERE / 'fill_table.csv'
FLAG_ORDER = ['original_sourced', 'reported_new', 'inferred_zero_season', 'reported_weak', 'estimated_area_share',
              'estimated_zero_season_budget', 'estimated_zero_small_fire', 'missing']


def main():
    m = load_master()
    num = lambda c: pd.to_numeric(m[c], errors='coerce')
    d = pd.DataFrame({'agrn': m.agrn, 'region_id': m.region_id, 'region_name': m.region_name, 'year': m.year,
                      'share': m.share, 'burn_ha': m.burn_ha, 'black_summer': m.agrn == '871',
                      'dwellings': num('X_socio_dwellings_census'),
                      'homes_orig': num('DL_homes_destroyed_in_council'),
                      'DL_orig': num('DL')})
    d['value'] = d.homes_orig
    d['DL_fill_flag'] = np.where(d.homes_orig.notna(), 'original_sourced', 'missing')
    d['fill_source_url'] = ''
    d['fill_source_quote'] = ''
    d['fill_note'] = ''
    d['fill_scope'] = ''

    if FILL.exists():
        f = pd.read_csv(FILL, dtype={'agrn': str})
        f['region_id'] = f.region_id.astype(int)
        key = d.set_index(['agrn', 'region_id']).index
        assert f.set_index(['agrn', 'region_id']).index.isin(key).all(), 'fill_table row not in the 218 rows'
        assert not f.duplicated(['agrn', 'region_id']).any(), 'duplicate fill rows'
        for r in f.itertuples():
            i = d.index[(d.agrn == r.agrn) & (d.region_id == r.region_id)][0]
            assert d.at[i, 'DL_fill_flag'] == 'missing', f'{r.agrn}/{r.region_id} already has a value'
            d.at[i, 'value'] = r.value
            d.at[i, 'DL_fill_flag'] = r.flag
            d.at[i, 'fill_source_url'] = r.url
            d.at[i, 'fill_source_quote'] = r.quote
            d.at[i, 'fill_note'] = r.note
            d.at[i, 'fill_scope'] = r.scope

    # ---- variants and pillar ranks
    tiers = {
        'DL_v0_original': ['original_sourced'],
        'DL_v1_reported': ['original_sourced', 'reported_new'],
        'DL_v2_inferred': ['original_sourced', 'reported_new', 'inferred_zero_season'],
        'DL_v3_estimated': ['original_sourced', 'reported_new', 'inferred_zero_season', 'reported_weak',
                            'estimated_area_share', 'estimated_zero_season_budget', 'estimated_zero_small_fire'],
    }
    for name, flags in tiers.items():
        ok = d.DL_fill_flag.isin(flags) & d.value.notna()
        rate = (d.value / d.dwellings * 1000).where(ok)
        d[name.replace('DL_', 'homes_per_1000_')] = rate
        d[name] = rate.rank(pct=True)
    chk = (d.DL_v0_original - d.DL_orig).abs().max()
    assert chk < 1e-9, f'v0 does not reproduce the workbook DL (max diff {chk})'
    d.to_csv(HERE / 'DL_FILLED.csv', index=False)
    print(d.DL_fill_flag.value_counts().reindex(FLAG_ORDER).fillna(0).astype(int).to_string())
    for name in tiers:
        print(name, 'rows with DL:', int(d[name].notna().sum()), 'of', len(d))
    return d


if __name__ == '__main__':
    main()
