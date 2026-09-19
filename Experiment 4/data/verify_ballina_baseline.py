"""Verify thirteen Ballina B0 allocations against the final plan and adopted amendments."""
import csv,json,sqlite3,hashlib,sys
from pathlib import Path
ROOT=Path('/Users/ray/Research/AUSSEF');OUT=Path(sys.argv[1]);RAW=ROOT/'Experiment 4/data/raw_extension'
db=sqlite3.connect(OUT/'experiment4.sqlite');db.execute('PRAGMA foreign_keys=ON')
u=json.loads((RAW/'ballina_original_urls.json').read_text())
with db:
 for sid,url in u.items():
  f=RAW/(sid+'.pdf');status='adoption_supporting_attachments_not_full_original_plan' if sid=='ballina_original2020' else 'adoption_report_table19_image_verified' if sid.endswith('agenda') else 'resolution250620_4_clauses1_18_text_verified'
  db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',(sid,url,str(f.relative_to(ROOT)),hashlib.sha256(f.read_bytes()).hexdigest(),status,None))
 for job,amount in [('6545',94000),('2372',945000)]:
  pid='ballina:reference:'+job
  assert db.execute("SELECT amount_aud FROM budget_snapshots WHERE project_id=? AND stage='B0'",(pid,)).fetchone()[0]==amount
  db.execute("UPDATE budget_snapshots SET value_status='original_adopted_allocation_verified',decision_date='2020-06-25',decision_status='adopted_table19_by_resolution250620_4_clause18',source_id='ballina_june2020_agenda',source_page='PDF85;printed81;Table19',decision_source_id='ballina_june2020_minutes',evidence_limit='Minutes PDF4 and PDF6 adopt amended Table19. Matched by project name and allocation; original table has no project reference. Full asset-scope continuity and event alignment remain unverified.' WHERE project_id=? AND stage='B0'",(pid,))
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
with db:
 f=ROOT/'Experiment 4/data/raw_extension/ballina_final_plan2020.pdf'
 db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('ballina_final_plan2020','https://www.ballina.nsw.gov.au/files/assets/public/v/1/council/documents/council-documents/dp-op-2020_2024-final.pdf',str(f.relative_to(ROOT)),hashlib.sha256(f.read_bytes()).hexdigest(),'PDF45_original_open_spaces_allocations_visually_verified;final_plan_matches_June_amendments',None))
 allocations={'2160':400000,'6532':952000,'4767':55000,'4768':65000,'4769':50000,'4770':25000,'4771':15000,'5488':28000,'6501':53000,'6503':90000,'6531':707500}
 assert sum(allocations.values())+94000+945000==3479500
 for job,amount in allocations.items():
  pid='ballina:reference:'+job
  assert db.execute("SELECT amount_aud FROM budget_snapshots WHERE project_id=? AND stage='B0' AND year_start=2020",(pid,)).fetchone()[0]==amount
  db.execute("UPDATE budget_snapshots SET value_status='original_adopted_allocation_verified',decision_date='2020-06-25',decision_status='adopted_plan_resolution250620_4',source_id='ballina_final_plan2020',source_page='PDF45;printed45;2020/21_column',decision_source_id='ballina_june2020_minutes',evidence_limit='Final council-hosted plan; amounts and project names visually matched. Open Spaces total3479500 matches all13 positive baseline allocations and adopted amendments. Plan has no job IDs; link to quarterly references by name and amount only. Scope continuity, damage and causal eligibility remain unverified.' WHERE project_id=? AND stage='B0' AND year_start=2020",(pid,))
for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
 c=db.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([d[0] for d in c.description]);w.writerows(c)
p=OUT/'field_gaps.csv'
with p.open() as f:gaps=list(csv.DictReader(f))
for g in gaps:
 if g['project_id'] in ['ballina:reference:'+j for j in list(allocations)+['6545','2372']] and g['year_start']=='2020' and g['required_field']=='original_adoption_document':g.update(status='resolved_adopted_plan',reason='Final plan PDF45 and adopted June25 amendments verify original2020/21 allocation',next_action='Retain independent asset-scope and event checks')
with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(gaps[0]));w.writeheader();w.writerows(gaps)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']['sources']=db.execute('SELECT COUNT(*) FROM sources').fetchone()[0];v['ballina_original_allocations_adoption_verified']=13
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print('Verified thirteen adopted original allocations; model eligibility unchanged.')
