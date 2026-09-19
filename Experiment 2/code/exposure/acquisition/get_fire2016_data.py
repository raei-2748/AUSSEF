import requests,json,hashlib,zipfile
from pathlib import Path
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists())
S=ROOT/'Experiment 2/data/disaster_exposure_v2/sources';x=json.loads((S/'fire-extent-and-severity-mapping-fesm-2016-2017.json').read_text())['result'];m=[]
for r in x['resources']:
 if r['url'].endswith('fire_fesm_2016_17.zip') or 'factsheet' in r['url']:
  u=r['url'];resp=requests.get(u,timeout=120);f=S/('fesm_2016_vector.zip' if u.endswith('.zip') else 'fesm_v3_factsheet.pdf');f.write_bytes(resp.content);m.append(dict(url=u,file=f.name,status=resp.status_code,bytes=len(resp.content),sha256=hashlib.sha256(resp.content).hexdigest()));print(m[-1],flush=True)
  if u.endswith('.zip') and zipfile.is_zipfile(f):print(zipfile.ZipFile(f).namelist()[:40],flush=True)
(S/'fesm2016_spatial_manifest.json').write_text(json.dumps(m,indent=2))
