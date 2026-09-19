import csv,json,sqlite3,hashlib,sys
from pathlib import Path
ROOT=Path('/Users/ray/Research/AUSSEF');OUT=Path(sys.argv[1]);c=sqlite3.connect(OUT/'experiment4.sqlite');c.execute('PRAGMA foreign_keys=ON');p=ROOT/'Experiment 4/data/raw_extension/richmond_q1_202223.pdf'
with c:
 c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('richmond_q1_202223','https://richmondvalley.nsw.gov.au/wp-content/uploads/2022/11/Quarterly-Budget-Review-Statement-for-the-quarter-ended-30-September-2022.pdf',str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'PDF14_printed12_capital_variation_image_verified',None))
 c.execute('INSERT INTO project_revisions VALUES (?,?,?,?,?,?,?,?,?,?)',('RV_P008_2022Q1','richmondvalley:candidate:P008',2022,'Q1',-483772,None,None,'Reported recommended capital expenditure transfer to2023/24; weather and contractor availability; adoption not verified','richmond_q1_202223','PDF13-14;printed11-12'))
 assert not c.execute('PRAGMA foreign_key_check').fetchall()
for t in ['sources','project_revisions']:
 cur=c.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([x[0] for x in cur.description]);w.writerows(cur)
v=json.loads((OUT/'validation.json').read_text())
for t in ['sources','project_revisions']:v['table_counts'][t]=c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0]
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
