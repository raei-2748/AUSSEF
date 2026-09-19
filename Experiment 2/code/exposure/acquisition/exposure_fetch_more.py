from pathlib import Path
import requests,json,hashlib,re
from urllib.parse import urljoin

ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists())
O=ROOT/'Experiment 2/data/disaster_exposure_v2';S=O/'sources';S.mkdir(parents=True,exist_ok=True)
manifest=[]
def get(name,u):
 r=requests.get(u,timeout=90);r.raise_for_status();f=S/name;f.write_bytes(r.content);manifest.append(dict(source_id=name,url=u,file=str(f.relative_to(O)),bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest(),retrieved='2026-09-18'));return r
j=get('nema_metadata.json','https://data.gov.au/data/api/3/action/package_show?id=drfa-activation-history-by-lga').json()['result']
print('NEMA notes',j['notes']);print('resources',[(x['name'],x['url']) for x in j['resources']])
for r in j['resources']:
 if r.get('format','').lower()=='csv':get('nema_drfa.csv',r['url']);break
get('fesm_2016_17.xlsx','https://www.environment.nsw.gov.au/sites/default/files/2024-09/fire-extent-severity-mapping-results-2016-17.xlsx')
for year in range(2012,2016):
 slug=f'historical-fire-extent-and-severity-mapping-fesm-statewide-{year}{str(year+1)[-2:]}'
 try:
  j=get(f'fesm_metadata_{year}.json','https://datasets.seed.nsw.gov.au/api/3/action/package_show?id='+slug).json()['result']
  print('FESM',year,j.get('metadata_created'),[(x['name'],x.get('size'),x['url']) for x in j['resources']])
  for r in j['resources']:
   if 'Wildfires' in r['name']:get(f'fesm_wildfires_{year}.zip',r['url'])
  if year==2012:
   for r in j['resources']:
    if 'Quality' in r['name']:get('fesm_historical_quality.pdf',r['url'])
 except Exception as e:print('ERROR',year,str(e));manifest.append(dict(source_id=str(year),status='failed',error=str(e)))
(S/'download_manifest.json').write_text(json.dumps(manifest,indent=2))
