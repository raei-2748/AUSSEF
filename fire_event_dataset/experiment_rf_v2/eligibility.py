"""Explicit source-based eligibility registry; no target values enter any rule."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent


def apply_registry(master, codebook):
    candidates = codebook.loc[codebook.role_if_Y_sum == 'X', 'column'].tolist()
    registry = pd.read_csv(ROOT / 'SOURCE_ELIGIBILITY_REGISTRY.csv').fillna('')
    assert registry.column.is_unique and set(registry.column) == set(candidates)
    x = master[candidates].copy().mask(master[candidates].eq('N/A'))
    starts = pd.to_datetime(master.first_fire_start)
    vintage = pd.to_numeric(master.info_pop_census_year, errors='coerce')
    decisions, masked, exclude = [], [], []
    for rule in registry.itertuples(index=False):
        column = rule.column
        bad = pd.Series(False, index=master.index)
        if rule.action == 'exclude':
            exclude.append(column)
            bad[:] = True
        elif rule.action == 'census_release':
            dates = pd.to_datetime(vintage.map({2016: rule.date_2016, 2021: rule.date_2021}), errors='coerce')
            bad = dates.isna() | starts.le(dates)
        elif rule.action == 'not_before':
            bad = starts.lt(pd.Timestamp(rule.not_before))
        elif rule.action != 'retain':
            raise ValueError(f'Unreviewed eligibility action: {rule.action}')
        observed_bad = bad & x[column].notna()
        for i in master.index[observed_bad]:
            masked.append({'row_id': master.row_id[i], 'column': column,
                           'first_fire_start': master.first_fire_start[i], 'reason': rule.reason})
        decisions.append({'column': column, 'rule': rule.reason, 'action': rule.action,
                          'source_family': rule.family, 'masked_cells': int(observed_bad.sum()),
                          'release_status': rule.release_status})
        x.loc[bad, column] = np.nan
    return x.drop(columns=exclude), pd.DataFrame(decisions), pd.DataFrame(masked)
