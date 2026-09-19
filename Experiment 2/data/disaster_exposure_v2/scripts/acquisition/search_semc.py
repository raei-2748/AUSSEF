import requests,json,hashlib
from pathlib import Path
from pypdf import PdfReader
S=Path('/Users/ray/Research/AUSSEF/outputs/disaster_exposure_v2/sources');records=[]
for y in range(2013,2017):
 u='https://data.nsw.gov.au/data/api/3/action/package_search';q=f'State Emergency Management Committee {y}';r=requests.get(u,params={'q':q,'rows':10},timeout=40);(S/f'semc_search_{y}.json').write_text(r.text)
 for x in r.json()['result']['results']:
  if 'Emergency Management Committee' in x['title'] and str(y) in x['title'] and str(y+1) in x['title']:
   url=x['resources'][0]['url'];print(x['title'],url,flush=True);r=requests.get(url,timeout=60);f=S/f'semc_{y}.pdf';f.write_bytes(r.content);records.append(dict(year=y,url=url,status=r.status_code,file=f'sources/semc_{y}.pdf',sha256=hashlib.sha256(r.content).hexdigest()))
   if r.content.startswith(b'%PDF'):
    pages=[p.extract_text() for p in PdfReader(f).pages];(S/f'semc_{y}_pages.json').write_text(json.dumps(pages))
    for i,p in enumerate(pages):
     if 'declar' in p.lower():print('YEAR/PAGE',y,i+1,p[:1500],flush=True)
   else:print('download',r.status_code,len(r.content))
   break
(S/'semc_manifest.json').write_text(json.dumps(records,indent=2))
