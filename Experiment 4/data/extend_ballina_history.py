"""Import prior-year observations for references already in the candidate store."""
import csv,json,sqlite3,hashlib,sys
from pathlib import Path
ROOT=Path('/Users/ray/Research/AUSSEF');OUT=Path(sys.argv[1]);RAW=ROOT/'Experiment 4/data/raw_extension'
db=sqlite3.connect(OUT/'experiment4.sqlite');db.execute('PRAGMA foreign_keys=ON')
def ins(t,r):db.execute('INSERT INTO '+t+' ('+','.join(r)+') VALUES ('+','.join('?' for _ in r)+')',list(r.values()))
# year, reference, original annual estimate, expended this year: image-verified page1
rows=[(2018,'2160',450000,16300),(2018,'5488',26000,0),(2018,'6501',20000,0),(2018,'6503',90000,0),(2018,'2372',0,154100),(2019,'2160',450000,10100),(2019,'6532',1002000,28800),(2019,'5488',27000,73700),(2019,'6501',20000,5200),(2019,'6503',90000,0),(2019,'6531',25000,6600),(2019,'2372',845000,25100)]
u={r['year']:r['links'][0] for r in json.loads((RAW/'ballina_history_discovery.json').read_text()) if r.get('links')}
with db:
 for y,url in u.items():
  sid=f'ballina_capital_june{y}';f=RAW/(sid+'.pdf')
  ins('sources',dict(source_id=sid,url=url,local_file=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),evidence_status='PDF1_selected_existing_reference_rows_image_verified_not_full_block',publication_date=None))
 for year,job,b0,actual in rows:
  pid='ballina:reference:'+job;sid=f'ballina_capital_june{year+1}';page='PDF1;printed'+('127' if year==2018 else '31')
  for stage in ['B0','Q1','Q2','Q3','ACTUAL']:
   amount=b0 if stage=='B0' else actual if stage=='ACTUAL' else None
   ins('budget_snapshots',dict(snapshot_id=f'{pid}:{year}:{stage}',project_id=pid,year_start=year,stage=stage,amount_aud=amount,value_status='retrospective_review_amount_scope_unverified' if amount is not None else 'unknown_not_recovered',amount_basis='reported_expended_this_year_accounting_basis_unverified' if stage=='ACTUAL' else 'annual_budget',reference_period_end=f'{year+1}-06-30' if stage=='ACTUAL' else None,decision_date=None,decision_status='unknown',source_id=sid if amount is not None else None,source_page=page if amount is not None else None,decision_source_id=None,evidence_limit='Same reference and compatible name; recurrent or staged scope not certified. Original adoption and expenditure accounting basis require verification. Do not infer undamaged or untreated status.',model_eligible=0))
  db.execute("UPDATE projects SET cross_document_link_status='reference_repeats_across_years_asset_scope_not_certified' WHERE project_id=?",(pid,))
 ins('project_milestones',dict(milestone_id='BA2018_2372_complete',project_id='ballina:reference:2372',asof_date='2019-06-30',milestone_type='reported_completion_status',reported_value='Complete',date_interpretation='Status at annual review; exact completion date unknown. Later same-reference spending indicates possible phases or changed scope.',source_id='ballina_capital_june2019',source_page='PDF1;printed127'))
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
 c=db.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([d[0] for d in c.description]);w.writerows(c)
p=OUT/'field_gaps.csv'
with p.open() as f:gaps=list(csv.DictReader(f))
for year,job,*_ in rows:
 for field in ['Q1_amount_aud','Q2_amount_aud','Q3_amount_aud','original_adoption_document','expenditure_accounting_basis','crossyear_asset_scope','damage_access_assessment','event_overlap_screen']:
  gaps.append(dict(project_id='ballina:reference:'+job,year_start=year,required_field=field,status='not_recovered_search_incomplete',reason='Historical annual schedule does not establish this field',next_action='Retrieve contemporaneous quarterly reviews and original plan; verify project phases and disaster overlap'))
with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(gaps[0]));w.writeheader();w.writerows(gaps)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']={t:db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()};v.update(field_gaps=len(gaps),observed_project_snapshot_amounts=db.execute('SELECT COUNT(*) FROM budget_snapshots WHERE amount_aud IS NOT NULL').fetchone()[0],ballina_historical_project_years_added=12)
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n');print(v['observed_project_snapshot_amounts'])

# Direct plan corroboration; exact adoption resolutions remain to be checked.
with db:
 for y,name,page in [(2018,'2018_19-delivery-program-and-operational-plan-adopted-280618.pdf',38),(2019,'dp-op-2019_2023-adopted-version-web-resized.pdf',48)]:
  f=RAW/f'ballina_final_plan{y}.pdf'
  db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',(f'ballina_final_plan{y}','https://www.ballina.nsw.gov.au/files/assets/public/v/1/council/documents/council-documents/'+name,str(f.relative_to(ROOT)),hashlib.sha256(f.read_bytes()).hexdigest(),f'PDF{page}_annual_column_visually_verified;adopted_version_listed_by_council_archive',None))
 checks={2018:{'2160':450000,'5488':26000,'6501':20000,'6503':90000},2019:{'2160':450000,'6532':1002000,'5488':27000,'6501':20000,'6503':90000,'6531':25000,'2372':845000}}
 for y,jobs in checks.items():
  for job,value in jobs.items():
   pid='ballina:reference:'+job
   assert db.execute("SELECT amount_aud FROM budget_snapshots WHERE project_id=? AND year_start=? AND stage='B0'",(pid,y)).fetchone()[0]==value
   db.execute("UPDATE budget_snapshots SET source_id=?,source_page=?,value_status='original_plan_amount_corroborated',decision_status='council_archive_adopted_version_exact_resolution_unverified',evidence_limit='Annual allocation visually verified in original-year plan and matches later original-estimate column. No project job ID in plan; named scope match only. Exact adoption/publication evidence and stable asset scope remain to verify.' WHERE project_id=? AND year_start=? AND stage='B0'",(f'ballina_final_plan{y}',f'PDF{38 if y==2018 else 48};annual_{y}/{str(y+1)[-2:]}_column',pid,y))
for t in ['sources','budget_snapshots']:
 cur=db.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:
  w=csv.writer(f);w.writerow([x[0] for x in cur.description]);w.writerows(cur)
p=OUT/'field_gaps.csv'
with p.open() as f:gaps=list(csv.DictReader(f))
for g in gaps:
 y=int(g['year_start']);job=g['project_id'].split(':')[-1]
 if g['project_id'].startswith('ballina:reference:') and job in checks.get(y,{}) and g['required_field']=='original_adoption_document':
  g.update(status='plan_recovered_exact_adoption_resolution_unverified',reason='Original-year plan allocation corroborated against retrospective original estimate',next_action='Verify contemporaneous adoption resolution and publication date; retain scope checks')
with p.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(gaps[0]));w.writeheader();w.writerows(gaps)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']['sources']=db.execute('SELECT COUNT(*) FROM sources').fetchone()[0];v['ballina_historical_baselines_plan_corroborated']=11
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')

with db:
 docs=[('ballina_ar2018','https://www.ballina.nsw.gov.au/files/assets/public/v/1/council/documents/council-documents/annual-report-2017_2018.pdf','PDF173_visual_verified_skate_row_and_duplicate_reference'),('ballina_june2017_minutes','https://www.ballina.nsw.gov.au/files/assets/public/v/1/council/documents/agenda-and-minutes/2017/22-june-2017/2ordinary_minutes_22_june_2017.pdf','PDF8_resolution220617_9_adopts_plan_with_amendments'),('ballina_june2017_agenda','https://www.ballina.nsw.gov.au/files/assets/public/v/1/council/documents/agenda-and-minutes/2017/22-june-2017/220617_ordinary_agenda_22_june_2017.pdf','adoption_report_located_original_exhibited_plan_not_reproduced')]
 for sid,url,status in docs:
  f=RAW/(sid+'.pdf');db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',(sid,url,str(f.relative_to(ROOT)),hashlib.sha256(f.read_bytes()).hexdigest(),status,None))
 pid='ballina:reference:2160'
 for stage in ['B0','Q1','Q2','Q3','ACTUAL']:
  amount=450000 if stage=='B0' else 34900 if stage=='ACTUAL' else None
  ins('budget_snapshots',dict(snapshot_id=f'{pid}:2017:{stage}',project_id=pid,year_start=2017,stage=stage,amount_aud=amount,value_status='retrospective_review_amount_scope_unverified' if amount is not None else 'unknown_not_recovered',amount_basis='reported_expended_this_year_accounting_basis_unverified' if stage=='ACTUAL' else 'annual_budget',reference_period_end='2018-06-30' if stage=='ACTUAL' else None,decision_date=None,decision_status='unknown',source_id='ballina_ar2018' if amount is not None else None,source_page='PDF173;Open Spaces and Reserves;Wollongbar Skate Park' if amount is not None else None,decision_source_id=None,evidence_limit='Reference2160 is reused on the same page for East Ballina Cemetery Master Plan. Match uses category and skate-park name, not reference alone. Original450000 plus carryover50000 and approved variations-450000 equals latest50000. Annual approved variations have no verified quarter/date; latest50000 is not Q3. Completion31Dec2018 is a future target, not actual.',model_eligible=0))
 db.execute("UPDATE projects SET identifier_status='reference_nonunique_requires_category_and_name',cross_document_link_status='category_name_match_only_scope_not_certified' WHERE project_id=?",(pid,))
 ins('project_milestones',dict(milestone_id='BA2017_2160_status',project_id=pid,asof_date='2018-06-30',milestone_type='reported_progress_status',reported_value='Awaiting development application determination; future completion target31December2018',date_interpretation='Status at annual review; no exact deferral decision or completed date established',source_id='ballina_ar2018',source_page='PDF173'))
for t in ['sources','projects','budget_snapshots','project_milestones']:
 cur=db.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([x[0] for x in cur.description]);w.writerows(cur)
p=OUT/'field_gaps.csv'
with p.open() as f:gaps=list(csv.DictReader(f))
for field in ['Q1_amount_aud','Q2_amount_aud','Q3_amount_aud','original_adoption_document','expenditure_accounting_basis','crossyear_asset_scope','damage_access_assessment','event_overlap_screen']:
 gaps.append(dict(project_id='ballina:reference:2160',year_start=2017,required_field=field,status='not_recovered_search_incomplete',reason='Annual report only; reference2160 also labels cemetery project. Initial adoption resolution found but original allocation attachment not yet verified.',next_action='Retrieve original exhibited plan and quarterly capital schedules; match category and name and audit exposure'))
with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(gaps[0]));w.writeheader();w.writerows(gaps)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']={t:db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'")};v['field_gaps']=len(gaps);v['observed_project_snapshot_amounts']=db.execute('SELECT COUNT(*) FROM budget_snapshots WHERE amount_aud IS NOT NULL').fetchone()[0];v['ballina_historical_project_years_added']=13
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')

with db:
 u=json.loads((RAW/'ballina2017_quarter_urls.json').read_text())
 for q,date,printed in [('q1','2017-09-30','217'),('q2','2017-12-31','198')]:
  sid='ballina_2017_'+q;f=RAW/(sid+'.pdf')
  db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',(sid,u[q],str(f.relative_to(ROOT)),hashlib.sha256(f.read_bytes()).hexdigest(),'PDF1_Open_Spaces_named_skate_row_image_verified',None))
  db.execute("UPDATE budget_snapshots SET amount_aud=500000,value_status='reported_quarterly_estimate_approval_unverified',amount_basis='annual_budget_including_50000_carryover',reference_period_end=?,source_id=?,source_page=?,evidence_limit='Skate park identified by Open Spaces category and name; reference2160 also labels cemetery. Original450000 plus carryover50000 equals latest500000; no new skate variation shown. Agenda attachment is not adoption minutes. No inferred damage status or actual completion.' WHERE project_id='ballina:reference:2160' AND year_start=2017 AND stage=?",(date,sid,'PDF1;printed'+printed,q.upper()))
 ins('project_milestones',dict(milestone_id='BA2017_2160_q2_status',project_id='ballina:reference:2160',asof_date='2017-12-31',milestone_type='reported_progress_status',reported_value='Development application lodged; consultants providing additional information',date_interpretation='Status at Q2 review; not a disaster-cause statement or completion date',source_id='ballina_2017_q2',source_page='PDF1;printed198'))
for t in ['sources','budget_snapshots','project_milestones']:
 cur=db.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([x[0] for x in cur.description]);w.writerows(cur)
p=OUT/'field_gaps.csv'
with p.open() as f:gaps=list(csv.DictReader(f))
for g in gaps:
 if g['project_id']=='ballina:reference:2160' and g['year_start']=='2017' and g['required_field'] in ['Q1_amount_aud','Q2_amount_aud']:
  g.update(status='amount_recovered_approval_unverified',reason='Named quarterly capital schedule reports latest annual estimate500000 including carryover50000',next_action='Verify meeting decision and retain scope/damage checks')
with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(gaps[0]));w.writeheader();w.writerows(gaps)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']={t:db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'")};v['observed_project_snapshot_amounts']=db.execute('SELECT COUNT(*) FROM budget_snapshots WHERE amount_aud IS NOT NULL').fetchone()[0];(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')

with db:
 u=json.loads((RAW/'ballina2018apr_urls.json').read_text())
 for sid,url in u.items():
  f=RAW/(sid+'.pdf');db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',(sid,url,str(f.relative_to(ROOT)),hashlib.sha256(f.read_bytes()).hexdigest(),'Q3_attachment_PDF1_image_verified;minutes_PDF9_and_agenda_PDF72_76_text_checked',None))
 pid='ballina:reference:2160'
 db.execute("UPDATE budget_snapshots SET amount_aud=50000,value_status='approved_quarterly_allocation_verified',reference_period_end='2018-03-31',decision_date='2018-04-26',decision_status='adopted_resolution260418_18',source_id='ballina_2017_q3',source_page='PDF1;printed73',decision_source_id='ballina_apr2018_minutes',evidence_limit='Minutes PDF9 approve500000 to50000 and450000 transfer to2018/19. Agenda PDF76 has350000 variation typo, retained in source_conflicts. Category/name match only; reference2160 is nonunique. Damage, original adoption allocation and stable scope unresolved.' WHERE project_id=? AND year_start=2017 AND stage='Q3'",(pid,))
 db.execute('INSERT INTO project_revisions VALUES (?,?,?,?,?,?,?,?,?,?)',('BA2017_Q3_2160',pid,2017,'Q3',-450000,500000,50000,'Transfer to2018/19; planning consent pending per agendaPDF72','ballina_apr2018_minutes','PDF9;260418/18'))
 db.execute('INSERT INTO review_decisions VALUES (?,?,?,?,?,?,?,?,?,?,?)',('BA2017_Q3','ballina',2017,'Q3','2018-03-31','2018-04-26','listed_amendments_approved','ballina_apr2018_minutes','PDF9','260418/18','Approval verified for listed skate-park amendment; no blanket inference for unlisted projects'))
 db.execute('INSERT INTO source_conflicts VALUES (?,?,?,?,?,?,?,?)',('BA2017_Q3_variation_typo',pid,'revision_aud','ballina_apr2018_agenda','PDF76;printed72','ballina_apr2018_minutes','Agenda variation-350000 conflicts with500000 to50000 arithmetic; minutesPDF9 and attachmentPDF1 specify-450000','resolved_use_adopted_minutes_preserve_agenda_discrepancy'))
 ins('project_milestones',dict(milestone_id='BA2017_2160_deferral',project_id=pid,asof_date='2018-04-26',milestone_type='approved_partial_budget_deferral',reported_value='450000 transferred to2018/19; planning consent pending',date_interpretation='Exact council decision date; not an actual completion date or proof of no disaster exposure',source_id='ballina_apr2018_minutes',source_page='PDF9;260418/18'))
for t in ['sources','budget_snapshots','project_revisions','review_decisions','source_conflicts','project_milestones']:
 cur=db.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([x[0] for x in cur.description]);w.writerows(cur)
p=OUT/'field_gaps.csv'
with p.open() as f:gaps=list(csv.DictReader(f))
for g in gaps:
 if g['project_id']=='ballina:reference:2160' and g['year_start']=='2017' and g['required_field']=='Q3_amount_aud':g.update(status='amount_and_decision_verified',reason='50000 adopted26April2018 in resolution260418/18',next_action='Retain original allocation, scope, damage and accounting checks')
with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(gaps[0]));w.writeheader();w.writerows(gaps)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']={t:db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'")};v['observed_project_snapshot_amounts']=db.execute('SELECT COUNT(*) FROM budget_snapshots WHERE amount_aud IS NOT NULL').fetchone()[0];(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')

with db:
 u=json.loads((RAW/'ballina2017_decision_urls.json').read_text())
 for sid,date,q,page,res in [('ballina_oct2017_minutes','2017-10-26','Q1','18','261017/25'),('ballina_jan2018_minutes','2018-01-25','Q2','10','250118/17')]:
  f=RAW/(sid+'.pdf');db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',(sid,u[sid],str(f.relative_to(ROOT)),hashlib.sha256(f.read_bytes()).hexdigest(),'review_resolution_notes_report_and_approves_listed_other_amendments',None))
  db.execute('INSERT INTO review_decisions VALUES (?,?,?,?,?,?,?,?,?,?,?)',('BA2017_'+q,'ballina',2017,q,'2017-09-30' if q=='Q1' else '2017-12-31',date,'status_report_noted_listed_amendments_only',sid,'PDF'+page,res,'Skate park not a listed budget amendment; no inference of a new approval for its500000 reported estimate'))
  db.execute("UPDATE budget_snapshots SET decision_date=?,decision_status='status_report_noted_no_new_skate_allocation_approval',decision_source_id=? WHERE project_id='ballina:reference:2160' AND year_start=2017 AND stage=?",(date,sid,q))
for t in ['sources','review_decisions','budget_snapshots']:
 cur=db.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([x[0] for x in cur.description]);w.writerows(cur)
p=OUT/'field_gaps.csv'
with p.open() as f:gaps=list(csv.DictReader(f))
for g in gaps:
 if g['project_id']=='ballina:reference:2160' and g['year_start']=='2017' and g['required_field'] in ['Q1_amount_aud','Q2_amount_aud']:
  g.update(status='amount_recovered_report_noted_no_new_approval',reason='Minutes note report and approve listed other amendments; skate estimate is reported not newly approved',next_action='Trace original/carryover authorisation; retain scope and damage checks')
with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(gaps[0]));w.writeheader();w.writerows(gaps)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']={t:db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'")};(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
