from pathlib import Path
import json,requests,hashlib,io
import pandas as pd
S=Path('/Users/ray/Research/AUSSEF/outputs/disaster_exposure_v2/sources');js=json.loads((S/'nema_activity.json').read_text())['result'];urls=[]
for act in js:
 for r in act.get('data',{}).get('package',{}).get('resources',[]):
  if '462acfff' in r['url'] and r['url'] not in urls:urls.append(r['url'])
print('Unique old resources',len(urls));print('\n'.join(urls[:4]));records=[]
for i,u in enumerate(urls[:3]):
 r=requests.get(u,timeout=60);print(i,r.status_code,len(r.content),r.content[:30]);(S/f'nema_old_attempt_{i}.csv').write_bytes(r.content);records.append(dict(url=u,status=r.status_code,file=f'sources/nema_old_attempt_{i}.csv',sha256=hashlib.sha256(r.content).hexdigest()))
 if r.status_code==200 and not r.content.startswith(b'<'):
  d=pd.read_csv(io.BytesIO(r.content));print(d.shape,d.columns.tolist());print(d.iloc[:2].to_string())
u='https://data.gov.au/data/api/3/action/datastore_search?resource_id=462acfff-f2e0-4446-a0fb-f20f8a19f487&limit=1';r=requests.get(u,timeout=60);(S/'nema_old_datastore.json').write_text(r.text);print(r.text[:500]);records.append(dict(url=u,status=r.status_code,file='sources/nema_old_datastore.json'))
(S/'nema_old_attempts_manifest.json').write_text(json.dumps(records,indent=2))
