import sqlite3,csv,json,hashlib,sys
from pathlib import Path
ROOT=Path('/Users/ray/Research/AUSSEF');OUT=Path(sys.argv[1]);c=sqlite3.connect(OUT/'experiment4.sqlite');c.execute('PRAGMA foreign_keys=ON')
p=ROOT/'Experiment 4/data/raw_extension/richmondvalley_ar202324.pdf'
with c:
 c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('richmondvalley_ar202324','https://richmondvalley.nsw.gov.au/wp-content/uploads/2024/11/RVC-Annual-Report-2023-2024.pdf',str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'PDF19_printed34_text_verified_distinct_road_scopes',None))
 c.execute('CREATE TABLE project_linkage_audit (audit_id TEXT PRIMARY KEY,project_id TEXT REFERENCES projects(project_id),source_id TEXT REFERENCES sources(source_id),source_page TEXT,reported_scope TEXT,link_status TEXT,damage_transfer_allowed INTEGER,completion_transfer_allowed INTEGER,required_resolution TEXT)')
 c.execute('INSERT INTO project_linkage_audit VALUES (?,?,?,?,?,?,?,?,?)',('RV_Naughtons_scope','richmondvalley:candidate:P008','richmondvalley_ar202324','PDF19;printed34','Landslip reconstruction and separately completed 400m northern-section Fixing Local Roads betterment','same_road_different_scopes_candidate_link_unresolved',0,0,'Obtain contract/project number, chainage and original scope for P008; distinguish road reopening from completion of northern-section works'))
 c.execute("UPDATE projects SET cross_document_link_status='same_road_different_work_scopes_requires_chainage_contract_match' WHERE project_id='richmondvalley:candidate:P008'")
 assert not c.execute('PRAGMA foreign_key_check').fetchall()
with c:
 p=ROOT/'Experiment 4/data/raw_extension/richmond_naughtons_aug2024.pdf'
 c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('richmond_naughtons_aug2024','https://richmondvalley.nsw.gov.au/wp-content/uploads/2024/08/Agenda-of-Extraordinary-Council-Meeting-Tuesday-6-August-2024.pdf',str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'PDF10_printed9_text_verified_scope_completion',None))
 c.execute('INSERT INTO project_linkage_audit VALUES (?,?,?,?,?,?,?,?,?)',('RV_Naughtons_location','richmondvalley:candidate:P008','richmond_naughtons_aug2024','PDF10;printed9;item6.2','Approx300m; southern boundary92 to northern boundary925 Naughtons Gap Road as printed; funded2020; construction completed April2024','candidate_match_name_funding_only_length_conflicts_with_400m_report',0,0,'Verify cadastral plan Lot1DP1307756 and original contract; retain300m_vs400m difference and address text; do not assign exact completion day'))
 c.execute("UPDATE damage_status SET damage_status='landslip_reported_as_project_deferral_reason',source_id='richmond_q3',evidence_status='Q3_2022_PDF12_explicit_deferral_reason;physical_section_assessment_event_identity_and_date_unresolved' WHERE project_id='richmondvalley:candidate:P008'")
with c:
 p=ROOT/'Experiment 4/data/raw_extension/ballina_may2020_minutes_scope.pdf'
 c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('ballina_may2020_minutes_scope','https://www.ballina.nsw.gov.au/files/assets/public/v/1/council/documents/agenda-and-minutes/2020/ordinary-minutes-28-april-2020.pdf',str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'PDF3_content_date28May2020_resolution280520_3;URL_month_mislabelled',None))
 pid='ballina:reference:2160'
 for aid,sid,page,scope in [('BA_skate_2018_site','ballina_apr2018_agenda','PDF35;printed31','DA2017/554; skate park at Elvery Lane, Alstonville; pending government referrals'),('BA_skate_2020_site','ballina_may2020_minutes_scope','PDF3;280520/3','DA2020/23; district park including skate park; approved Lot32 viaDA2018/753;93Rifle Range Road and55Avalon Avenue, Wollongbar')]:
  c.execute('INSERT INTO project_linkage_audit VALUES (?,?,?,?,?,?,?,?,?)',(aid,pid,sid,page,scope,'different_planning_applications_and_site_descriptions_crossyear_continuity_unverified',0,0,'Obtain relocation/redesign decision, cadastral crosswalk and ledger transfer between DA2017/554 andDA2020/23; do not transfer damage or completion across sites'))
 c.execute("UPDATE projects SET cross_document_link_status='different_DA_site_descriptions_requires_scope_and_ledger_crosswalk' WHERE project_id=?",(pid,))
for t in ['sources','projects','project_linkage_audit','damage_status']:
 cur=c.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([x[0] for x in cur.description]);w.writerows(cur)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']['sources']=c.execute('SELECT COUNT(*) FROM sources').fetchone()[0];v['table_counts']['project_linkage_audit']=c.execute('SELECT COUNT(*) FROM project_linkage_audit').fetchone()[0]
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
