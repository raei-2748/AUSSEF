import csv,json,sqlite3,hashlib,sys
from pathlib import Path
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists());OUT=Path(sys.argv[1]);c=sqlite3.connect(OUT/'experiment4.sqlite');c.execute('PRAGMA foreign_keys=ON');p=ROOT/'Experiment 4/data/raw_extension/griffith_aug2020.pdf'
with c:
 c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('griffith_aug2020','https://businesspapers.griffith.nsw.gov.au/RedirectToDoc.aspx?URL=Open/2020/08/CO_25082020_AGN_1273_AT.PDF',str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'PDF66_67_named_progress_text_verified',None))
 c.execute('CREATE TABLE comparison_project_leads (lead_id TEXT PRIMARY KEY,council_key TEXT REFERENCES councils(council_key),year_start INTEGER,project_label TEXT,reported_status TEXT,reported_delay_reason TEXT,source_id TEXT REFERENCES sources(source_id),source_page TEXT,limitation TEXT)')
 for n,label,status,reason,page in [('thorne','Southern Industrial Link Road - Thorne Road West','Delayed','Landowner dispute','66'),('lake','Lake Wyangan North Lake sedimentation ponds and wetland','Underway','Unearthed Aboriginal artefacts; permit required','67'),('theatre','Regional Theatre Redevelopment','Complete;June quarter2020',None,'67')]:
  c.execute('INSERT INTO comparison_project_leads VALUES (?,?,?,?,?,?,?,?,?)',('griffith2019_'+n,'griffith',2019,label,status,reason,'griffith_aug2020',page,'Lead only; no stable project ID or linked budget/actual; no exact completion date or verified unaffected status'))
 assert not c.execute('PRAGMA foreign_key_check').fetchall()
with c:
 for kind,status in [('excluded','downloaded_separate_cover1_not_relevant_Q4_bundle'),('plans','PDF2_contents_Q4_at120_to228;scanned_report_requires_OCR')]:
  file=ROOT/('Experiment 4/data/raw_extension/griffith_aug2020_'+kind+'.pdf')
  c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('griffith_aug2020_'+kind,'https://businesspapers.griffith.nsw.gov.au/RedirectToDoc.aspx?URL=Open/2020/08/CO_25082020_ATT_1273_'+kind.upper()+'.PDF',str(file.relative_to(ROOT)),hashlib.sha256(file.read_bytes()).hexdigest(),status,None))
with c:
 p=ROOT/'Experiment 4/data/raw_extension/griffith_june2019_agenda.pdf'
 c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('griffith_june2019_agenda','https://businesspapers.griffith.nsw.gov.au/RedirectToDoc.aspx?URL=Open/2019/06/CO_25062019_AGN_1070_AT.PDF',str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'PDF9_embedded_June11_minutes_resolution19_183',None))
 p=ROOT/'Experiment 4/data/raw_extension/griffith_june11_2019_agenda.pdf'
 c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('griffith_june11_2019_agenda','https://businesspapers.griffith.nsw.gov.au/RedirectToDoc.aspx?URL=Open/2019/06/CO_11062019_AGN_1069_AT.PDF',str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'PDF15_attachment_inventory_and_public_exhibition_dates',None))
 p=ROOT/'Experiment 4/data/raw_extension/griffith_june11_2019_attachments.pdf'
 c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('griffith_june11_2019_attachments','https://businesspapers.griffith.nsw.gov.au/RedirectToDoc.aspx?URL=Open/2019/06/CO_11062019_ATT_1069_EXCLUDED.PDF',str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'PDF2_contents_LTFP3_plan25_submissions308_numeric_extraction_pending',None))
with c:
 c.execute("CREATE TABLE comparison_budget_leads (lead_id TEXT PRIMARY KEY, council_key TEXT REFERENCES councils(council_key), year_start INTEGER, schedule_item TEXT, project_label TEXT, amount_aud REAL, amount_status TEXT, source_id TEXT REFERENCES sources(source_id), source_page TEXT, limitation TEXT)")
 c.execute("INSERT INTO comparison_budget_leads VALUES (?,?,?,?,?,?,?,?,?,?)",('griffith2019_lake_budget','griffith',2019,'35','Lake Wyangan Environmental Strategy Implementation',1000000,'draft_annual_allocation_visually_verified','griffith_june11_2019_attachments','300','2019/20 column, not multiyear project total of 3000000; item35 is a schedule row, not a stable project ID. Budget adoption resolution19/183 requires amendment reconciliation. Broader scope than sedimentation ponds/wetlands progress lead; no certified project match.'))
with c:
 p=ROOT/'Experiment 4/data/raw_extension/griffith_q2_2020.pdf'
 c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('griffith_q2_2020','https://businesspapers.griffith.nsw.gov.au/Open/2020/02/CO_25022020_ATT_1261_EXCLUDED.PDF',str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'PDF2_inventory;PDF5_program_totals_and_PDF18_fund_capital_statement_visually_verified;PDF5_17_OCR_screened',None))
 c.execute("UPDATE comparison_budget_leads SET amount_status=?,limitation=? WHERE lead_id=?",('adopted_program_allocation_inferred_from_resolution_and_amendment_check','PDF300 item35 annual allocation; resolution19/183 in June25 agenda PDF9 adopts June11 plan with attachment(c) amendments. PDF308 and linked community submissions309-312 inspected; no Lake Wyangan allocation change identified. Programme scope remains broader than sedimentation ponds/wetlands; schedule item35 is not stable project ID. Q2 PDF18 reports fund-level capital totals and cannot supply a project revision.','griffith2019_lake_budget'))
with c:
 p=ROOT/'Experiment 4/data/raw_extension/griffith_assetplan2022.pdf'
 c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('griffith_assetplan2022','https://www.griffith.nsw.gov.au/files/sharedassets/public/v/1/cm-documents/asset-management-plan-2022-2032-adopted-28-jun-2022.pdf',str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'PDF69_73_amounts_visually_verified;PDF66_71_section_headers_and_years_text_verified',None))
 c.execute('INSERT INTO comparison_project_leads VALUES (?,?,?,?,?,?,?,?,?)',('griffith2019_boorga','griffith',2019,'Seal Boorga Road - From New Farms Rd to Dickie Rd','Reported carryover from 2019/20 in 2022/23 planned works',None,'griffith_assetplan2022','69;73','Carryover label is explicit; decision date, cause, completion, actual and stable job ID unresolved. Delivery link6.2.2 is not a unique project ID.'))
 for kind,value,page in [('renewal',613009,'69'),('acquisition',1839028,'73')]:
  c.execute('INSERT INTO comparison_budget_leads VALUES (?,?,?,?,?,?,?,?,?,?)',('griffith2022_boorga_'+kind,'griffith',2022,'delivery_link_6.2.2','Seal Boorga Road - From New Farms Rd to Dickie Rd; '+kind+' component',value,'projected_2022_23_component_not_actual','griffith_assetplan2022',page,'Appendix E renewal/replacement and Appendix F acquisition are components of the same named carryover. Do not count as separate projects. Not a quarterly revision or final actual; no inferred decision date or disaster cause.'))
for t in ['sources','comparison_project_leads','comparison_budget_leads']:
 cur=c.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([x[0] for x in cur.description]);w.writerows(cur)
v=json.loads((OUT/'validation.json').read_text())
for t in ['sources','comparison_project_leads','comparison_budget_leads']:v['table_counts'][t]=c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0]
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
