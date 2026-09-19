import requests,json
from pathlib import Path
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists())
S=ROOT/'Experiment 2/data/disaster_exposure_v2/sources'
for slug in ['fire-extent-and-severity-mapping-fesm-2016-2017','fire-extent-and-severity-mapping-fesm']:
 u='https://datasets.seed.nsw.gov.au/api/3/action/package_show?id='+slug;r=requests.get(u,timeout=40);(S/(slug+'.json')).write_text(r.text)
 if r.status_code==200:
  x=r.json()['result'];print(x['name'],x['notes'][:1200]);print([(a['name'],a['url']) for a in x['resources']],flush=True)
