"""Shared helpers for the new-fires test (frozen rules: PRESPEC.md sections 1.1, 4, 6; Amendment 1)."""
import importlib.util
import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MAIN = Path('/Users/ray/Research/AUSSEF')
FED = MAIN / 'fire_event_dataset'
RAW = FED / 'data/raw/extra_fires'
EXTRA = FED / 'data/extra_fires'                      # git-ignored data folder; extra_fire_rows.csv lives here
P1 = Path('/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0/dataset_phase1')
RES = HERE / 'results'
INP = HERE / 'inputs'
WORKBOOK = Path.home() / ('Library/CloudStorage/GoogleDrive-raywang886@gmail.com/My Drive/'
                          'Application Folder - Ray/3. Extracurriculars/AUSSEF/Data/nsw_bushfires_2015_2025_XY.xlsx')


def place(v, ref, higher_is_worse=True):
    """PRESPEC 1.1: percentile of v among the original values `ref`, 1 = worse; = (n_better + n_equal/2 + 1)/(n + 1)."""
    ref = np.asarray(pd.Series(ref).dropna(), float)
    if v is None or pd.isna(v) or len(ref) == 0:
        return np.nan
    eq = np.isclose(ref, v, rtol=0, atol=1e-12)
    n_better = int((((ref < v) if higher_is_worse else (ref > v)) & ~eq).sum())
    return (n_better + eq.sum() / 2 + 1) / (len(ref) + 1)


def place_signed(v, ref):
    """Y indicators are already signed so that higher = worse (PRESPEC section 4)."""
    return place(v, ref, True)


def norm_name(s):
    """Council name key: lower case, drop the ABS type suffix and generic words (matches OLG naming)."""
    s = str(s).lower().replace('&', ' and ')
    s = re.sub(r'\((a|c|s|m|rc|t|nsw)\)', ' ', s)
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'\b(council|city|of|the|shire|municipal|municipality|regional)\b', ' ', s)
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def load_olg_module():
    spec = importlib.util.spec_from_file_location('olg_dataset', FED / 'src/olg.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
