"""Import explicit Ballina resolutions, preserving proposal/approval distinctions."""
import csv,json,sqlite3,hashlib,sys
from pathlib import Path
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists());OUT=Path(sys.argv[1]);RAW=ROOT/'Experiment 4/data/raw_extension'
db=sqlite3.connect(OUT/'experiment4.sqlite');db.execute('PRAGMA foreign_keys=ON')
def ins(t,r):db.execute('INSERT INTO '+t+' ('+','.join(r)+') VALUES ('+','.join('?' for _ in r)+')',list(r.values()))
urls=json.loads((RAW/'ballina_minutes_urls.json').read_text())
reviews=[('Q1','ballina_minutes_oct2020','2020-09-30','2020-10-22','13','221020/23'),('Q2','ballina_minutes_jan2021','2020-12-31','2021-01-28','13','280121/20'),('Q3','ballina_minutes_apr2021','2021-03-31','2021-04-22','11','220421/18')]
changes=[('Q2','6532',973000,-200000,773000,'Deferral to 2021/22'),('Q2','6531',800000,-400000,400000,'Deferral to 2021/22'),('Q2','2372',936000,-750000,186000,'Deferral to 2021/22'),('Q3','6532',773000,130000,903000,'Transfer from Amenities'),('Q3','4586',175000,-100000,75000,'LRCI deferral to 2021/22'),('Q3','6531',400000,-150000,250000,'Deferral to 2021/22')]
with db:
 for stage,sid,period,date,page,res in reviews:
  f=RAW/(sid+'.pdf')
  ins('sources',dict(source_id=sid,url=urls[sid],local_file=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),evidence_status='resolution_text_verified;Q2_Q3_numeric_rows_image_verified',publication_date=None))
  ins('review_decisions',dict(decision_id='BA2020_'+stage,council_key='ballina',year_start=2020,stage=stage,reference_period_end=period,decision_date=date,status='report_noted_and_listed_amendments_approved',source_id=sid,source_page=page,resolution=res,limitation='Approval applies to listed amendments; noting the report is not independent original-budget adoption evidence. Meeting date is not verified first publication date.'))
  db.execute("UPDATE budget_snapshots SET decision_date=?,decision_source_id=?,decision_status='report_noted_prior_authority_not_independently_verified' WHERE project_id LIKE 'ballina:%' AND stage=? AND amount_aud IS NOT NULL",(date,sid,stage))
  for st,job,before,delta,after,reason in changes:
   if st!=stage:continue
   assert before+delta==after
   pid='ballina:reference:'+job
   assert db.execute('SELECT amount_aud FROM budget_snapshots WHERE project_id=? AND stage=?',(pid,stage)).fetchone()[0]==after
   ins('project_revisions',dict(revision_id='BA2020_'+stage+'_'+job,project_id=pid,year_start=2020,stage=stage,revision_aud=delta,before_revision_aud=before,after_revision_aud=after,reason=reason,source_id=sid,source_page=page))
   db.execute("UPDATE budget_snapshots SET decision_status='explicit_revised_amount_approved',evidence_limit='Revised annual amount explicitly approved in resolution; decision after reference quarter end. Original adoption and asset scope still require verification.' WHERE project_id=? AND stage=?",(pid,stage))
   if delta<0:
    ins('project_milestones',dict(milestone_id='BA_deferral_'+stage+'_'+job,project_id=pid,asof_date=date,milestone_type='approved_partial_budget_deferral',reported_value='2021/22',date_interpretation='Date of resolution approving partial expenditure deferral; not actual completion or first operational delay',source_id=sid,source_page=page))
    db.execute("UPDATE projects SET deferral_decision_date=COALESCE(deferral_decision_date,?),rephased_to_fy='2021/22' WHERE project_id=?",(date,pid))
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
 c=db.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:
  w=csv.writer(f);w.writerow([d[0] for d in c.description]);w.writerows(c)
p=OUT/'field_gaps.csv'
with p.open() as f:gaps=list(csv.DictReader(f))
for g in gaps:
 for stage,job,*_ in changes:
  if g['project_id']=='ballina:reference:'+job and g['required_field']==stage+'_amount_aud':g.update(status='resolved_explicit_revised_amount_approved',reason='Schedule amount matches council resolution',next_action='Retain original adoption, event alignment and other separate gates')
with p.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(gaps[0]));w.writeheader();w.writerows(gaps)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']={t:db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()};v['ballina_explicit_quarterly_approvals']=6;v['ballina_dated_partial_deferral_decisions']=5
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
