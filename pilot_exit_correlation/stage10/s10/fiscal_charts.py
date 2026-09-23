"""Part D: council road spending and grants indexed to 2018-19, by Black Summer exposure group, with a go/no-go gate."""
import numpy as np
import pandas as pd

BASE_YEAR = 2018
PRE_YEARS, POST_YEARS = (2016, 2017), (2019, 2020)


def index_panel(df, value_col, key="lga_key"):
    base = df[df.year_start == BASE_YEAR].set_index(key)[value_col]
    out = df.join(base.rename("base"), on=key)
    out["index"] = np.where(out.base > 0, 100 * out[value_col] / out.base, np.nan)
    return out


def gap_by_year(indexed, group_col="group"):
    med = indexed.groupby(["year_start", group_col])["index"].median().unstack(group_col)
    if "cut off" not in med or "burned only" not in med:
        return med, pd.Series(dtype=float)
    return med, med["cut off"] - med["burned only"]


def gate(gaps):
    pre = gaps.reindex(list(PRE_YEARS)).abs().max()
    post = gaps.reindex(list(POST_YEARS)).max()
    ok = pd.notna(pre) and pd.notna(post) and post > pre
    return bool(ok), (float(pre) if pd.notna(pre) else np.nan), (float(post) if pd.notna(post) else np.nan)
