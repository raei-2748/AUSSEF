"""Experiment 7, step 0: quarterly council panels that the lga_year sheet only has as annual means.

Writes panels/dss_quarter.parquet: working-age income-support recipients by council (ABS LGA 2021 code) and quarter,
harmonised to 2021 councils exactly as the master's SL indicator does (src/vulnerable.council_quarter: pre-merger
councils summed into their successor, Auburn and Holroyd left out). Nothing is modelled here.

Run with the project venv (needs geopandas for the LGA table):
    PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python prep_panels.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATASET = HERE.parent / 'fire_event_dataset'
sys.path.insert(0, str(DATASET))

from src.regions import load_lgas  # noqa: E402
from src.vulnerable import council_quarter  # noqa: E402

lga = load_lgas()
q = council_quarter(lga).reset_index().rename(columns={'code21': 'region_id'})
q['quarter'] = q.quarter.astype(str)
q.to_parquet(HERE / 'panels/dss_quarter.parquet', index=False)
print(q.shape, q.region_id.nunique(), q.quarter.min(), q.quarter.max())
