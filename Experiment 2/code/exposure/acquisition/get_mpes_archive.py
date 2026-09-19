from pathlib import Path
import requests,json,hashlib
from pypdf import PdfReader
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists())
S=ROOT/'Experiment 2/data/disaster_exposure_v2/sources';a=[]
for y,id in [(2012,14743),(2013,14741),(2014,15231)]:
 u=f'https://wayback.archive-it.org/22771/20240423201346/https://www.opengov.nsw.gov.au/download/{id}'
 try:
  r=requests.get(u,timeout=60);f=S/f'mpes_{y}.pdf';f.write_bytes(r.content);print(y,r.status_code,len(r.content),r.content[:8]);a.append(dict(year=y,url=u,status=r.status_code,sha256=hashlib.sha256(r.content).hexdigest()))
  if r.content.startswith(b'%PDF'):
   texts=[x.extract_text() for x in PdfReader(f).pages];(S/f'mpes_{y}_pages.json').write_text(json.dumps(texts))
   for i,t in enumerate(texts):
    if 'Natural Disaster Declarations' in t or ('AGRN' in t and 'Local' in t):print('YEAR/PAGE',y,i+1,t[:6500])
 except Exception as e:print(str(e))
(S/'mpes_manifest.json').write_text(json.dumps(a,indent=2))
