import requests,json
from pathlib import Path
S=Path('/Users/ray/Research/AUSSEF/outputs/disaster_exposure_v2/sources')
for slug in ['fire-extent-and-severity-mapping-fesm-2016-2017','fire-extent-and-severity-mapping-fesm']:
 u='https://datasets.seed.nsw.gov.au/api/3/action/package_show?id='+slug;r=requests.get(u,timeout=40);(S/(slug+'.json')).write_text(r.text)
 if r.status_code==200:
  x=r.json()['result'];print(x['name'],x['notes'][:1200]);print([(a['name'],a['url']) for a in x['resources']],flush=True)
