"""Add verified quarterly timing, revisions and unresolved event-overlap evidence."""
from pathlib import Path
import csv,hashlib,json,sqlite3,sys
ROOT=Path('/Users/ray/Research/AUSSEF');OUT=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'Experiment 4/data'
db=sqlite3.connect(OUT/'experiment4.sqlite');db.execute('PRAGMA foreign_keys=ON')
def ins(table,d):db.execute('INSERT INTO '+table+' ('+','.join(d)+') VALUES ('+','.join('?' for _ in d)+')',list(d.values()))
assert not db.execute("SELECT 1 FROM sources WHERE source_id='snowy_q3_2022'").fetchone(),'Already applied'
sources=[
 ('snowy_q3_2022','https://www.snowyvalleys.nsw.gov.au/files/assets/public/meeting-minutes-amp-agendas/council-meetings/20220519/10.4-attachment-1-quarterly-budget-review-quarter-3-31-march-2022.pdf','snowy_q3_2022.pdf','OCR_all_15_pages_page_images_7_10_verified'),
 ('snowy_may_minutes','https://www.snowyvalleys.nsw.gov.au/files/assets/public/v/4/meeting-minutes-amp-agendas/council-meetings/20220519/20220519-signed-minutes-ordinary-council-meeting.pdf','snowy_may_minutes.pdf','signed_minutes_page9_image_verified_conflict_retained'),
 ('snowy_march2022','https://www.snowyvalleys.nsw.gov.au/files/assets/public/v/1/meeting-minutes-amp-agendas/council-meetings/20220317/00-20220317-business-paper-ordinary-council.pdf','snowy_march2022.pdf','embedded_February_minutes_PDF13_printed10_text_verified'),
 ('snowy_may2022','https://www.snowyvalleys.nsw.gov.au/files/assets/public/meeting-minutes-amp-agendas/council-meetings/20220519/00-20220519-business-paper-ordinary-council.pdf','snowy_may2022.pdf','agenda_PDF43_printed38_text_verified'),
]
with db:
 for sid,url,file,status in sources:
  local='Experiment 4/data/raw_extension/'+file
  ins('sources',dict(source_id=sid,url=url,local_file=local,sha256=hashlib.sha256((ROOT/local).read_bytes()).hexdigest(),evidence_status=status,publication_date=None))
 db.execute('CREATE TABLE review_decisions (decision_id TEXT PRIMARY KEY,council_key TEXT REFERENCES councils(council_key),year_start INTEGER,stage TEXT,reference_period_end TEXT,decision_date TEXT,status TEXT,source_id TEXT REFERENCES sources(source_id),source_page TEXT,resolution TEXT,limitation TEXT)')
 for st,ref,date,status,sid,page,res,lim in [
  ('Q2','2021-12-31','2022-02-17','review_adopted_minutes_verified','snowy_march2022','PDF13;printed10','M50/22','Whole-review adoption does not prove individual project allocations'),
  ('Q3','2022-03-31','2022-05-19','March_review_adopted_clause2_names_September_conflict','snowy_may_minutes','9','M145/22','Clause1 adopts March review; clause2 names September adjustments; ambiguity retained')]:
  ins('review_decisions',dict(decision_id='snowy2021'+st,council_key='snowyvalleys',year_start=2021,stage=st,reference_period_end=ref,decision_date=date,status=status,source_id=sid,source_page=page,resolution=res,limitation=lim))
  db.execute("UPDATE budget_snapshots SET reference_period_end=?,decision_date=?,decision_status=?,decision_source_id=?,evidence_limit=? WHERE project_id LIKE 'snowyvalleys:%' AND year_start=2021 AND stage=?",(ref,date,status,sid,lim+'; project amount remains unknown',st))
 # Normalise reduction in expenditure to a negative revision. Source effect-on-budget
 # signs describe funding benefit, so they must not be copied as spending increases.
 for code,amount,reason in [
  ('snowview',-950000,'Design delayed by resource constraints; dedicated project manager obtained. Source note52, no disaster causation asserted.'),
  ('batlow_caravan',-2700000,'Candidate name match to Itinerant Worker Accommodation; land claim, contaminated ground and industry delivery shortages; scope join unverified. Source note48/4.')]:
  pid='snowyvalleys:candidate:'+code
  ins('project_revisions',dict(revision_id='SV_Q3_'+code,project_id=pid,year_start=2021,stage='Q3',revision_aud=amount,before_revision_aud=None,after_revision_aud=None,reason=reason+' Negative means reduced annual expenditure; minutes adoption clause conflict retained.',source_id='snowy_q3_2022',source_page='10'))
  db.execute('UPDATE projects SET rephased_to_fy=?,cross_document_link_status=? WHERE project_id=?',('2022-23','candidate_name_match_quarterly_to_annual_no_stable_id',pid))
 # Event mentions have month precision only; no invented day or inferred AGRN.
 for code,label,lim in [
  ('jan2022','January 2022 Storm & Flood Event','Reported month January 2022; exact onset and AGRN unknown'),
  ('nov_unknown','November Flood Event','Year not printed in this note; do not silently assign November 2021'),
  ('feb2021','February 2021 Storms & Floods','Earlier-event emergency works; payment recognition in Q3 is not occurrence date'),
  ('oct2020','October 2020 Storm Event','Earlier-event emergency works; exact day and AGRN unknown')]:
  eid='snowy_q3_mention:'+code
  ins('disasters',dict(disaster_id=eid,reported_event_id=label,identity_status='provisional_source_mention_not_deduplicated_to_AGRN'))
  ins('disaster_observations',dict(observation_id='SV_'+code,disaster_id=eid,council_key='snowyvalleys',date=None,date_type='reported_event_month_or_name_only',limitation=lim+'; QBR PDF page7; not asset-level damage evidence',source_id='snowy_q3_2022',underlying_source_url=sources[0][1]))
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
with db:
 urls=json.loads((ROOT/'Experiment 4/data/raw_extension/snowy_q12_urls.json').read_text())
 for sid,url in urls.items():
  local='Experiment 4/data/raw_extension/'+sid+'.pdf'
  ins('sources',dict(source_id=sid,url=url,local_file=local,sha256=hashlib.sha256((ROOT/local).read_bytes()).hexdigest(),evidence_status='downloaded_Q1_page9_Q2_page8_image_verified_other_pages_text_or_OCR_screen_only',publication_date=None))
 db.execute('CREATE TABLE source_conflicts (conflict_id TEXT PRIMARY KEY,project_id TEXT REFERENCES projects(project_id),field TEXT,source_id TEXT REFERENCES sources(source_id),source_page TEXT,conflicting_source_id TEXT REFERENCES sources(source_id),finding TEXT,resolution_status TEXT)')
 for code,amount,note in [('fitzroy_toilets',300000,'13'),('khancoban_toilets',161818,'16')]:
  pid='snowyvalleys:candidate:'+code
  ins('project_revisions',dict(revision_id='SV_Q2_'+code,project_id=pid,year_start=2021,stage='Q2',revision_aud=amount,before_revision_aud=None,after_revision_aud=None,reason='Recognition of capital expenditure in Q2; source funding-effect sign reversed to positive spending addition; original-baseline conflict',source_id='snowy_q2_2021',source_page='PDF8;note'+note))
  ins('source_conflicts',dict(conflict_id='SV_B0_'+code,project_id=pid,field='B0_amount_aud',source_id='snowy_q2_2021',source_page='PDF8;note'+note,conflicting_source_id='snowy_ar2122',finding='Annual report calls amount June-adopted budget; Q2 review adds same amount as recognition of expenditure. Original adopted capital authority not established.',resolution_status='unresolved_recover_June_adopted_project_schedule'))
  db.execute("UPDATE budget_snapshots SET value_status='reported_original_conflicts_with_Q2_addition',evidence_limit='Original amount retained as reported; Q2 recognises same capital expenditure. Not a certified adopted baseline.' WHERE project_id=? AND stage='B0'",(pid,))
 ins('project_revisions',dict(revision_id='SV_Q1_tumut_aerodrome',project_id='snowyvalleys:candidate:tumut_aerodrome',year_start=2021,stage='Q1',revision_aud=-3500000,before_revision_aud=None,after_revision_aud=None,reason='Partial works deferred to next year due to CASA technical approval delays; candidate name match; not evidence of disaster-caused displacement',source_id='snowy_q1_2021',source_page='PDF9;note25'))
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
for table, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
 cur=db.execute('SELECT * FROM '+table)
 with (OUT/(table+'.csv')).open('w',newline='') as f:
  w=csv.writer(f);w.writerow([d[0] for d in cur.description]);w.writerows(cur)
v=json.loads((OUT/'validation.json').read_text())
v['table_counts']={n:db.execute('SELECT COUNT(*) FROM '+n).fetchone()[0] for n, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
v['sqlite_integrity']=db.execute('PRAGMA integrity_check').fetchone()[0]
v['unresolved_original_budget_conflicts']=db.execute('SELECT COUNT(*) FROM source_conflicts').fetchone()[0]
v['event_identity_warning']='11 source labels are not 11 independently verified disasters; four new mentions await AGRN reconciliation'
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v,indent=2))
