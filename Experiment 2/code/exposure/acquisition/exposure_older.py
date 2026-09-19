from pathlib import Path
import requests,json,hashlib
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists())
O=ROOT/'Experiment 2/data/disaster_exposure_v2';S=O/'sources'
urls={'nema_2024.csv':'https://data.gov.au/data/dataset/10ba7303-e3af-41b4-98b5-e04db77caea8/resource/462acfff-f2e0-4446-a0fb-f20f8a19f487/download/drfa_activation_history_by_location_2024_may_01.csv','nema_old_resource.json':'https://data.gov.au/data/api/3/action/resource_show?id=462acfff-f2e0-4446-a0fb-f20f8a19f487','nema_dataset.html':'https://data.gov.au/data/dataset/drfa-activation-history-by-lga'}
a=[]
for n,u in urls.items():
 try:
  r=requests.get(u,timeout=60);(S/n).write_bytes(r.content);a.append(dict(file='sources/'+n,url=u,status=r.status_code,sha256=hashlib.sha256(r.content).hexdigest()));print(n,r.status_code,len(r.content),r.text[:80])
 except Exception as e:print(e)
(S/'older_manifest.json').write_text(json.dumps(a,indent=2))
