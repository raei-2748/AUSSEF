"""DL_insurance_loss_raw: Insurance Council of Australia (ICA) catastrophe insured losses, linked to fires by date.

ICA reports losses per catastrophe (often several fires and several states), not per fire. A fire is linked when it is a
NSW fire starting between 3 days before the catastrophe start and its finish, and the catastrophe is a bushfire event
that includes NSW. DL_insurance_loss_raw is the whole catastrophe's original loss (the same value on every linked fire);
an area-share allocation is given separately and is an assumption, not an ICA figure.
Run with: uv run --no-sync --with openpyxl python -m src.ica
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from src.common import DATA, record_source

XLSX = DATA / "ica/ica_catastrophes.xlsx"
URL = "https://insurancecouncil.com.au/wp-content/uploads/2024/07/ICA-Historical-Normalised-Catastrophe-June-2024.xlsx"
LEAD_DAYS = 3


def events():
    d = pd.read_excel(XLSX, "ICA_CAT_Historical", header=9)
    d = d[d.Type.astype(str).str.contains("Bushfire", case=False) & d.State.astype(str).str.contains("NSW")]
    d["start"] = pd.to_datetime(d["Event Start"], errors="coerce")
    d["finish"] = pd.to_datetime(d["Event Finish"], errors="coerce").fillna(d.start)
    d = d[d.start >= "2014-07-01"]
    # CAT194 was amalgamated into CAT195 and has no separate loss; keep the carrying event only
    d = d[~d["Event Name"].astype(str).str.contains("Amalgamated", case=False)]
    return d


def run(ev, out_path):
    cats = events()
    rows = []
    for c in cats.itertuples():
        m = ev[(ev.start >= c.start - pd.Timedelta(days=LEAD_DAYS)) & (ev.start <= c.finish)]
        for r in m.itertuples():
            rows.append(dict(event_id=r.event_id, ica_cat=c._1, ica_event_name=c._2, ica_event_start=c.start.date(),
                             ica_event_finish=c.finish.date(), ica_states=c.State,
                             DL_insurance_loss_raw=c._13, ica_normalised_loss_2022=c._14, ica_claims_count=c._15,
                             burn_area_ha=r.burn_area_ha))
    out = pd.DataFrame(rows)
    out = out.sort_values("ica_event_start").drop_duplicates("event_id", keep="last")
    tot = out.groupby("ica_cat").burn_area_ha.transform("sum")
    out["ica_linked_fires"] = out.groupby("ica_cat").event_id.transform("count")
    out["DL_insurance_loss_area_share_proxy"] = out.DL_insurance_loss_raw * out.burn_area_ha / tot
    out = out.drop(columns="burn_area_ha")
    out.to_parquet(out_path)
    doc = {
        "ica_cat": ["ICA catastrophe code linked by date", "str", "ICA Historical Catastrophe List (June 2024)", ""],
        "ica_event_name": ["ICA catastrophe name", "str", "ICA", ""],
        "ica_event_start": ["ICA catastrophe start", "date", "ICA", ""],
        "ica_event_finish": ["ICA catastrophe finish", "date", "ICA", ""],
        "ica_states": ["States covered by the catastrophe", "str", "ICA", "loss may include other states"],
        "ica_normalised_loss_2022": ["Catastrophe loss normalised to 2022 (AUD)", "AUD", "ICA", "event level"],
        "ica_claims_count": ["Catastrophe claim count", "count", "ICA", "event level"],
        "ica_linked_fires": ["NSW fires linked to this catastrophe", "count", "", ""],
        "DL_insurance_loss_area_share_proxy": ["Catastrophe loss × this fire's share of linked burned area", "AUD", "computed",
                                               "ASSUMPTION: loss proportional to area; includes other states' losses"],
    }
    Path(str(out_path).replace(".parquet", ".doc.json")).write_text(json.dumps(doc, indent=1))
    record_source("ICA Historical Normalised Catastrophe List, June 2024", URL, XLSX, "© Insurance Council of Australia, public",
                  "bushfire catastrophes including NSW since July 2014")
    return out


if __name__ == "__main__":
    ev = gpd.read_parquet(DATA / "cache/fires.parquet")
    out = run(ev, DATA / "enrich/ica.parquet")
    print(out.groupby(["ica_cat", "ica_event_name"]).agg(fires=("event_id", "count"), loss=("DL_insurance_loss_raw", "first")))
