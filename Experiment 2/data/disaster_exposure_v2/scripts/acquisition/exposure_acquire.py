from pathlib import Path
import requests,json,hashlib,re
from urllib.parse import urljoin
R=Path('/Users/ray/Research/AUSSEF'); O=R/'outputs/disaster_exposure_v2';S=O/'sources';S.mkdir(parents=True,exist_ok=True)
if not (O/'frozen_before.json').exists():
 frozen={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in R.rglob('*') if p.is_file() and O not in p.parents and '.git' not in p.parts}
 (O/'frozen_before.json').write_text(json.dumps(frozen,indent=2))
urls={'nema_catalog':'https://data.gov.au/data/organization/national-emergency-management-agency?res_format=CSV','fesm_archive_2012':'https://datasets.seed.nsw.gov.au/api/3/action/package_show?id=historical-fire-extent-and-severity-mapping-fesm-statewide-201213','fesm_reports':'https://www.environment.nsw.gov.au/topics/animals-and-plants/native-vegetation/landcover-science/past-landcover-reporting'}
manifest=[]
for name,u in urls.items():
 r=requests.get(u,timeout=60);f=S/(name+('.json' if 'api/' in u else '.html'));f.write_bytes(r.content);manifest.append(dict(source_id=name,url=u,status=r.status_code,file=str(f.relative_to(O)),sha256=hashlib.sha256(r.content).hexdigest(),retrieved='2026-09-18'));print(name,r.status_code)
 if name=='fesm_archive_2012':
  try:
   j=r.json()['result'];print([(x['name'],x['url']) for x in j['resources']]);print(j.get('metadata_created'))
  except Exception:print(r.text[:100])
 else:
  for href,label in re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',r.text,re.S):
   if any(t in (href+label).lower() for t in ['activation','drfa','2016-17','declaration']):print(urljoin(u,href),re.sub('<[^>]+>','',label)[:100])
(S/'initial_manifest.json').write_text(json.dumps(manifest,indent=2))
