import requests,json,hashlib
from pathlib import Path
from pypdf import PdfReader
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists())
S=ROOT/'Experiment 2/data/disaster_exposure_v2/sources';m=[]
for label,q in [('2014','"RAA" "2014-15"'),('2016','"Rural Assistance" "2016-2017"')]:
 r=requests.get('https://data.nsw.gov.au/data/api/3/action/package_search',params={'q':q,'rows':100},timeout=40);(S/f'raa_exact_{label}.json').write_text(r.text)
 for x in r.json()['result']['results']:
  print(label,x['title'],[v['url'] for v in x['resources']],flush=True)
  if ('RAA' in x['title'] and label=='2014') or ('Rural Assistance' in x['title'] and '2016' in x['title'] and '2017' in x['title']):
   u=x['resources'][0]['url'];r=requests.get(u,timeout=60);f=S/f'raa_{label}.pdf';f.write_bytes(r.content);m.append(dict(file=f.name,url=u,status=r.status_code,sha256=hashlib.sha256(r.content).hexdigest()))
   if r.content.startswith(b'%PDF'):(S/f'raa_{label}_pages.json').write_text(json.dumps([p.extract_text() for p in PdfReader(f).pages]))
u='https://www.environment.nsw.gov.au/sites/default/files/2025-01/fire-extent-severity-mapping-2020-21-2016-17-220206.pdf';r=requests.get(u,timeout=60);(S/'fesm_2016_report.pdf').write_bytes(r.content);m.append(dict(file='fesm_2016_report.pdf',url=u,status=r.status_code))
(S/'finish_sources_manifest.json').write_text(json.dumps(m,indent=2))
