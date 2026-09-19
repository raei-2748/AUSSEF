from pathlib import Path
import requests,json,hashlib
from pypdf import PdfReader
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists())
S=ROOT/'Experiment 2/data/disaster_exposure_v2/sources';records=[]
for y in range(2013,2017):
 r=requests.get('https://data.nsw.gov.au/data/api/3/action/package_search',params={'q':f'Rural Assistance Authority {y}','rows':10},timeout=40);(S/f'raa_search_{y}.json').write_text(r.text)
 for x in r.json()['result']['results']:
  if 'Rural Assistance Authority' in x['title'] and str(y) in x['title'] and (str(y+1) in x['title'] or str(y+1)[-2:] in x['title']):
   url=x['resources'][0]['url'];r=requests.get(url,timeout=60);f=S/f'raa_{y}.pdf';f.write_bytes(r.content);records.append(dict(year=y,url=url,status=r.status_code,file='sources/'+f.name,sha256=hashlib.sha256(r.content).hexdigest()));print(y,url,r.status_code,len(r.content),flush=True)
   if r.content.startswith(b'%PDF'):
    pages=[p.extract_text() for p in PdfReader(f).pages];(S/f'raa_{y}_pages.json').write_text(json.dumps(pages))
    for i,t in enumerate(pages):
     if 'Natural Disaster Events' in t or ('Area Affected' in t):print('YEAR/PAGE',y,i+1,t[:5500],flush=True)
   break
(S/'raa_manifest.json').write_text(json.dumps(records,indent=2))
