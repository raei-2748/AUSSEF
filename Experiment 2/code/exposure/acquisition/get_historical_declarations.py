from pathlib import Path
import requests,json,hashlib
from concurrent.futures import ThreadPoolExecutor
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists())
S=ROOT/'Experiment 2/data/disaster_exposure_v2/sources'
base='https://www.nsw.gov.au/departments-and-agencies/nsw-reconstruction-authority/about-us/recovery/natural-disaster-declarations/'
jobs=[(f'nsw_fy_{y}.html',base+f'fy-{y}-{str(y+1)[-2:]}') for y in range(2012,2018)]
jobs += [('emergency_old_2014.html','https://www.emergency.nsw.gov.au/publications/natural-disaster-declarations/2014-2015.html'),('archive_cdx.json','https://web.archive.org/cdx/search/cdx?url=data.gov.au/data/dataset/10ba7303-e3af-41b4-98b5-e04db77caea8/resource/462acfff-f2e0-4446-a0fb-f20f8a19f487/download/*&output=json&filter=statuscode:200&collapse=digest')]
def fetch(t):
 n,u=t
 try:
  r=requests.get(u,timeout=40);(S/n).write_bytes(r.content);print(n,r.status_code,len(r.content),flush=True);return dict(file='sources/'+n,url=u,status=r.status_code,sha256=hashlib.sha256(r.content).hexdigest())
 except Exception as e:return dict(url=u,status='failed',error=str(e))
a=list(ThreadPoolExecutor(max_workers=3).map(fetch,jobs));(S/'historical_links_manifest.json').write_text(json.dumps(a,indent=2))
