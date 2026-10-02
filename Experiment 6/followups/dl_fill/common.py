"""Shared loaders for the DL-fill follow-up. Read-only: the workbook and aussef.duckdb are never written."""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MAIN = Path('/Users/ray/Research/AUSSEF - Local')            # main checkout holds Experiment 6 results and fire_event_dataset
E6_RESULTS = MAIN / 'Experiment 6' / 'results'
FED = MAIN / 'fire_event_dataset'
WORKBOOK = Path('/Users/ray/Research/AUSSEF - Local/data/master_workbook/nsw_bushfires_2015_2025_XY.xlsx')
OUT = HERE / 'out'
OUT.mkdir(exist_ok=True)


def load_master():
    """master sheet, 218 declared-event x council rows. 'N/A' is text, so numeric columns go through to_numeric."""
    m = pd.read_excel(WORKBOOK, sheet_name='master', header=2, keep_default_na=False, na_values=[''])
    m['agrn'] = m.agrn.astype(str)
    m['region_id'] = m.region_id.astype(int)
    m['year'] = pd.to_datetime(m.first_fire_start).dt.year
    m['share'] = pd.to_numeric(m.X_fire_share_of_council_burned, errors='coerce')
    m['burn_ha'] = pd.to_numeric(m.X_fire_burn_area_in_council_ha, errors='coerce')
    return m


def load_key_events():
    ke = pd.read_excel(WORKBOOK, sheet_name='key_events', header=1, keep_default_na=False, na_values=[''])
    ke['agrn'] = ke.agrn.astype(str)
    return ke
