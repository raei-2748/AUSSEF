from pathlib import Path
import json,requests,hashlib
from concurrent.futures import ThreadPoolExecutor
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists())
S=ROOT/'Experiment 2/data/disaster_exposure_v2/sources';a=json.loads((S/'nema_activity.json').read_text())['result'];rs={}
for x in a:
 for r in x.get('data',{}).get('package',{}).get('resources',[]):rs.setdefault(r['id'],r)
def get(r):
 u=r['url'];rec=dict(url=u,id=r['id'])
 try:
  x=requests.get(u,timeout=30);rec['status']=x.status_code
  if x.status_code==200 and not x.content.lstrip().startswith(b'<'):
   n='nema_archive_'+r['id']+('.xlsx' if u.endswith('.xlsx') else '.csv');(S/n).write_bytes(x.content);rec.update(file='sources/'+n,sha256=hashlib.sha256(x.content).hexdigest());print('RECOVERED',n,len(x.content),flush=True)
 except Exception as e:rec.update(error=str(e))
 return rec
out=list(ThreadPoolExecutor(max_workers=3).map(get,list(rs.values())[2:]));(S/'nema_recovery_attempts.json').write_text(json.dumps(out,indent=2));print([(x['id'],x.get('status')) for x in out])
