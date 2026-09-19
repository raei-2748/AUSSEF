from pathlib import Path
import requests,json,hashlib
from concurrent.futures import ThreadPoolExecutor
S=Path('/Users/ray/Research/AUSSEF/outputs/disaster_exposure_v2/sources')
urls=[('nla_2014.html','https://webarchive.nla.gov.au/awa/20170101000000/http://www.emergency.nsw.gov.au/publications/natural-disaster-declarations/2014-2015.html'),('mpes_2014_retry.pdf','https://wayback.archive-it.org/22771/20240423201346/https://www.opengov.nsw.gov.au/download/15231'),('semc_2016_retry.pdf','https://wayback.archive-it.org/22771/20240423201346/https://www.opengov.nsw.gov.au/download/19365')]
def get(t):
 n,u=t
 try:
  r=requests.get(u,timeout=45);(S/n).write_bytes(r.content);print(n,r.status_code,len(r.content),r.url,flush=True);return dict(file='sources/'+n,url=u,final_url=r.url,status=r.status_code,sha256=hashlib.sha256(r.content).hexdigest())
 except Exception as e:return dict(url=u,error=str(e))
a=list(ThreadPoolExecutor(max_workers=2).map(get,urls));(S/'archive_retry_manifest.json').write_text(json.dumps(a,indent=2))
