"""Import the complete Open Spaces block from Ballina's June2021 review (page1)."""
import csv,json,hashlib,sqlite3,sys
from pathlib import Path
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists());OUT=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'Experiment 4/data'
db=sqlite3.connect(OUT/'experiment4.sqlite');db.execute('PRAGMA foreign_keys=ON')
def ins(t,r):db.execute('INSERT INTO '+t+' ('+','.join(r)+') VALUES ('+','.join('?' for _ in r)+')',list(r.values()))
assert not db.execute("SELECT 1 FROM sources WHERE source_id='ballina_capital_june2021'").fetchone(),'Already imported'
rows=[
 ('2160','Wollongbar Skate Park',400000,440000,352000,'Complete'),
 ('6532','Wollongbar District Park',952000,903000,234500,'Dec-21'),
 ('4586','Various Shelters and BBQs',0,75000,15700,'Oct-21'),
 ('4588','Fawcett Park Shelters and BBQs',0,20000,22200,'Complete'),
 ('4589','Missingham Park Shelters and BBQs',0,20000,18400,'Complete'),
 ('4767','Condon Park Ballina Surface',55000,55000,29200,'Complete'),
 ('4768','Coastal Grove Ballina Heights Surface',65000,65000,51500,'Complete'),
 ('4769','Meldrum Park Ballina Shade Shelter',50000,50000,6800,'Aug-21'),
 ('4770','Missingham Park Ballina Design',25000,25000,8800,'Uncertain'),
 ('4771','Compton Drive Ballina Dog Exercise Area',15000,15000,10600,'Jun-21'),
 ('5488','Crown Reserve Improvements',28000,28000,18700,'On-going'),
 ('6501','Killen Falls Plan of Management',53000,53000,58900,'Complete'),
 ('6503','Ocean Breeze Reserve Lennox Head Equipment',90000,90000,1400,'Aug-21'),
 ('6531','Ross Park Lennox Head Redevelopment',707500,250000,8500,'Sep-21'),
 ('6545','Riverview Park Ballina Equipment',94000,94000,500,'Aug-21'),
 ('2372','Pop Denison Ballina Master Plan',945000,186000,164000,'Dec-21'),
 ('2544','Elizabeth Anne Brown Park Alstonville Monument',0,10000,11800,'Complete')]
assert sum(r[2] for r in rows)==3479500
assert sum(r[3] for r in rows)==2379000
assert sum(r[4] for r in rows)==1013500
source_defs=[
 ('ballina_capital_june2021','https://www.ballina.nsw.gov.au/files/assets/public/v/1/council/documents/agenda-and-minutes/2021/220721-item-9-20-capital-expenditure-program-30-june-2021-review.pdf','page1_image_verified_Open_Spaces_block'),
 ('ballina_july2021','https://www.ballina.nsw.gov.au/files/assets/public/v/1/council/documents/agenda-and-minutes/2021/220721-ordinary-agenda-22-july-2021.pdf','PDF161_printed155_basis_definition_text_verified'),
 ('snowy_original2021','https://www.snowyvalleys.nsw.gov.au/files/assets/public/reports-amp-strategies/202122-ipampr/20210617-2021-22-operational-and-capital-budget-resolution-m113-21-17-june-2021-council-meeting.pdf','PDF11_printed49_image_verified'),
 ('snowy_june2021_minutes','https://www.snowyvalleys.nsw.gov.au/files/assets/public/v/3/meeting-minutes-amp-agendas/council-meetings/20210617/20210617-signed-minutes-ordinary-council.pdf','page3_OCR_verified_adoption_subject_to_feedback'),
 ('snowy_june2021_feedback','https://www.snowyvalleys.nsw.gov.au/files/assets/public/meeting-minutes-amp-agendas/council-meetings/20210617/10.1-attachment-1-ipr-feedback-summary.pdf','downloaded_amendment_audit_pending')]
with db:
 for sid,url,verification in source_defs:
  path='Experiment 4/data/raw_extension/'+sid+'.pdf'
  ins('sources',dict(source_id=sid,url=url,local_file=path,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),evidence_status=verification,publication_date=None))
 db.execute('CREATE TABLE project_milestones (milestone_id TEXT PRIMARY KEY,project_id TEXT REFERENCES projects(project_id),asof_date TEXT,milestone_type TEXT,reported_value TEXT,date_interpretation TEXT,source_id TEXT REFERENCES sources(source_id),source_page TEXT)')
 for job,label,b0,end,actual,completion in rows:
  pid='ballina:reference:'+job
  scope='ordinary_candidate' if b0 else 'not_in_original_annual_allocation'
  if job in ['4586','5488','6501','4770','2372']:scope+=';scope_or_program_review'
  ins('projects',dict(project_id=pid,council_key='ballina',official_project_id=job,analyst_record_id='BA2020_'+job,project_label=label,unit_status='reported_reference_project_or_program_crossyear_continuity_unverified',identifier_status='official_review_reference_not_certified_asset_id',spending_class=scope,cross_document_link_status='single_year_end_schedule',original_completion_date=None,actual_completion_date=None,deferral_decision_date=None,rephased_to_fy=None,completion_status='reported_complete_date_unknown' if completion=='Complete' else 'target_or_status_only',fixed_pre_event_portfolio_verified=0,source_id='ballina_capital_june2021',source_page='PDF1;printed375'))
  for stage in ['B0','Q1','Q2','Q3','ACTUAL']:
   val=b0 if stage=='B0' else actual if stage=='ACTUAL' else None
   ins('budget_snapshots',dict(snapshot_id=pid+':2020:'+stage,project_id=pid,year_start=2020,stage=stage,amount_aud=val,value_status='reported_year_end_review' if val is not None else 'unknown_not_recovered',amount_basis='annual_cash_excludes_accruals_commitments' if stage=='ACTUAL' else 'annual_budget',reference_period_end='2021-06-30' if stage=='ACTUAL' else None,decision_date=None,decision_status='unknown',source_id='ballina_capital_june2021' if val is not None else None,source_page='PDF1;printed375' if val is not None else None,decision_source_id=None,evidence_limit='Original estimate retrospectively reproduced; final cash actual rounded to reported dollars; no event or damage join',model_eligible=0))
  ins('project_evidence',dict(evidence_id='BA_finalbudget_'+job,project_id=pid,year_start=2020,source_id='ballina_capital_june2021',source_page='PDF1;printed375',measure='year_end_revised_annual_estimate',amount_aud=end,funding_status='reported_estimate',verification='page_image_and_complete_block_subtotal_checked',limitation='Not Q3; cannot disaggregate cumulative changes by quarter'))
  ins('project_milestones',dict(milestone_id='BA_completion_'+job,project_id=pid,asof_date='2021-06-30',milestone_type='construction_complete_column',reported_value=completion,date_interpretation='Target month or status at review; not an exact actual completion date',source_id='ballina_capital_june2021',source_page='PDF1;printed375'))
  ins('damage_status',dict(damage_record_id=pid+':unknown',project_id=pid,disaster_id=None,assessment_date=None,damage_status='unknown',access_status='unknown',source_id='ballina_capital_june2021',evidence_status='No damage determination in capital schedule; no absence inference'))
 for code,amount in [('fitzroy_toilets',300000),('khancoban_toilets',161818)]:
  pid='snowyvalleys:candidate:'+code
  ins('project_evidence',dict(evidence_id='SV_original_document_'+code,project_id=pid,year_start=2021,source_id='snowy_original2021',source_page='PDF11;printed49',measure='original_plan_project_allocation',amount_aud=amount,funding_status='adoption_resolution_identified_amendment_audit_pending',verification='PDF_page_image_verified',limitation='CB05 is a category code not unique project ID; Q2 expenditure recognition still unresolved'))
  db.execute("UPDATE source_conflicts SET finding=finding || ' Original-plan document independently confirms same allocation; Q2 accounting/revision meaning remains unresolved.',resolution_status='original_plan_amount_corroborrated_Q2_recognition_unresolved' WHERE project_id=?",(pid,))
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
 c=db.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([d[0] for d in c.description]);w.writerows(c)
p=OUT/'field_gaps.csv'
with p.open() as f:gaps=list(csv.DictReader(f))
for job,*_ in rows:
 for field in ['Q1_amount_aud','Q2_amount_aud','Q3_amount_aud','original_adoption_document','damage_access_assessment','exact_completion_dates','three_pre_event_budget_years','event_overlap_screen']:
  gaps.append(dict(project_id='ballina:reference:'+job,year_start=2020,required_field=field,status='not_recovered_search_incomplete',reason='Year-end schedule alone cannot establish this field',next_action='Retrieve earlier capital reviews and original plan; join dated disaster and asset records'))
with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(gaps[0]));w.writeheader();w.writerows(gaps)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']={t:db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
v.update(field_gaps=len(gaps),observed_project_snapshot_amounts=db.execute('SELECT COUNT(*) FROM budget_snapshots WHERE amount_aud IS NOT NULL').fetchone()[0],ballina_block_subtotals_verified=True,sqlite_integrity=db.execute('PRAGMA integrity_check').fetchone()[0])
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
