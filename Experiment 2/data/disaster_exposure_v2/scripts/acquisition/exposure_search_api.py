import requests,json
from pathlib import Path
S=Path('/Users/ray/Research/AUSSEF/outputs/disaster_exposure_v2/sources')
for year in ['2012-13','2013-14']:
 u='https://data.nsw.gov.au/data/api/3/action/package_search';r=requests.get(u,params={'q':'Ministry Police '+year,'rows':20},timeout=60);(S/f'mpes_search_{year}.json').write_text(r.text)
 try:
  for x in r.json()['result']['results']:
   print(x['title'],[(a['url']) for a in x['resources']])
 except Exception as e:print(r.status_code,str(e))
# Public CKAN activity history can retain prior resource URLs.
u='https://data.gov.au/data/api/3/action/package_activity_list?id=10ba7303-e3af-41b4-98b5-e04db77caea8&limit=100';r=requests.get(u,timeout=60);(S/'nema_activity.json').write_text(r.text);print('activity',r.status_code,r.text[:100])
