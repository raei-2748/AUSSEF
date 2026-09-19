from pathlib import Path
import requests,json,hashlib,datetime,sys,concurrent.futures
from bs4 import BeautifulSoup
from pypdf import PdfReader
O=Path('/Users/ray/Research/AUSSEF/Experiment 3/results');S=O/'sources'
items=json.loads(Path(sys.argv[1]).read_text())
def fetch(x):
 sid,url=x['source_id'],x['url'];row=dict(x,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:
  r=requests.get(url,timeout=55);row.update(http_status=r.status_code,resolved_url=r.url,last_modified_header=r.headers.get('Last-Modified',''))
  ispdf=r.content.startswith(b'%PDF');ext='.pdf' if ispdf else '.html';p=S/(sid+ext);p.write_bytes(r.content)
  row.update(local_file=str(p.relative_to(O)),sha256=hashlib.sha256(r.content).hexdigest(),status='retrieved' if r.ok else 'http_error')
  if ispdf:
   pages=[p.extract_text() or '' for p in PdfReader(p).pages];(S/(sid+'_pages.json')).write_text(json.dumps(pages));row['pages']=len(pages)
  else:
   soup=BeautifulSoup(r.text,'html.parser');text=soup.get_text(' ',strip=True);(S/(sid+'.txt')).write_text(text)
   from urllib.parse import urljoin
   links=[{'label':a.get_text(' ',strip=True),'url':urljoin(r.url,a['href'])} for a in soup.find_all('a',href=True)]
   (S/(sid+'_links.json')).write_text(json.dumps(links,indent=2))
 except Exception as e:row.update(status='access_failed',error=str(e))
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:rows=list(ex.map(fetch,items))
f=O/'source_provenance.json';old=json.loads(f.read_text()) if f.exists() else []; ids={r['source_id'] for r in rows};f.write_text(json.dumps([r for r in old if r['source_id'] not in ids]+rows,indent=2))
for r in rows:print(r['source_id'],r['status'],r.get('pages',''),r.get('http_status',''))
