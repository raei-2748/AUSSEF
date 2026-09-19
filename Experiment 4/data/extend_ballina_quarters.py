"""Add image-verified Ballina quarterly estimates; adoption remains unverified."""
import csv,json,sqlite3,hashlib,sys
from pathlib import Path
ROOT=Path('/Users/ray/Research/AUSSEF');OUT=Path(sys.argv[1]);RAW=ROOT/'Experiment 4/data/raw_extension'
db=sqlite3.connect(OUT/'experiment4.sqlite');db.execute('PRAGMA foreign_keys=ON')
common={'2160':440000,'4767':55000,'4768':65000,'4769':50000,'4770':25000,'4771':15000,'5488':28000,'6501':53000,'6503':90000,'6545':94000}
sets=[('Q1','ballina_capital_sept2020','2020-09-30','216',dict(common,**{'6532':973000,'6531':707500,'2372':936000}),3531500),('Q2','ballina_capital_dec2020','2020-12-31','80',dict(common,**{'6532':773000,'6531':400000,'2372':186000}),2274000),('Q3','ballina_capital_march2021','2021-03-31','87',dict(common,**{'6532':903000,'6531':250000,'2372':186000,'4586':75000,'4588':20000,'4589':20000}),2369000)]
urls=json.loads((RAW/'ballina_quarterly_urls.json').read_text())
solved=set()
with db:
 for stage,sid,date,page,values,total in sets:
  assert sum(values.values())==total,(stage,sum(values.values()),total)
  f=RAW/(sid+'.pdf')
  db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',(sid,urls[sid],str(f.relative_to(ROOT)),hashlib.sha256(f.read_bytes()).hexdigest(),'PDF1_image_verified_complete_Open_Spaces_block_subtotal',None))
  for job,amount in values.items():
   pid='ballina:reference:'+job
   c=db.execute("UPDATE budget_snapshots SET amount_aud=?,value_status='reported_review_estimate',reference_period_end=?,decision_status='adoption_not_yet_verified',source_id=?,source_page=?,evidence_limit=? WHERE project_id=? AND year_start=2020 AND stage=? AND amount_aud IS NULL",(amount,date,sid,'PDF1;printed'+page,'Annual estimate includes new proposed variations; meeting adoption not yet verified. Not quarter expenditure. Same official reference across documents; asset scope continuity still subject to audit.',pid,stage))
   assert c.rowcount==1,(pid,stage)
   db.execute("UPDATE projects SET cross_document_link_status='official_reference_matched_across_quarterly_and_year_end_schedules' WHERE project_id=?",(pid,))
   solved.add((pid,stage+'_amount_aud'))
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
 c=db.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:
  w=csv.writer(f);w.writerow([d[0] for d in c.description]);w.writerows(c)
p=OUT/'field_gaps.csv'
with p.open() as f:gaps=list(csv.DictReader(f))
for g in gaps:
 if (g['project_id'],g['required_field']) in solved:
  g.update(status='amount_recovered_adoption_unverified',reason='Quarterly annual estimate image-verified including proposed variations',next_action='Verify council resolution adoption and exact scope; do not treat amount as approved until checked')
with p.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(gaps[0]));w.writeheader();w.writerows(gaps)
v=json.loads((OUT/'validation.json').read_text())
v['table_counts']={t:db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
v.update(observed_project_snapshot_amounts=db.execute('SELECT COUNT(*) FROM budget_snapshots WHERE amount_aud IS NOT NULL').fetchone()[0],ballina_quarterly_subtotals_verified=True,ballina_complete_numeric_chains_adoption_uncertified=13,sqlite_integrity=db.execute('PRAGMA integrity_check').fetchone()[0])
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v,indent=2))
