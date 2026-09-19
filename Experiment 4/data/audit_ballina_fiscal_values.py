import csv,json,sqlite3,hashlib,sys
from pathlib import Path
ROOT=Path('/Users/ray/Research/AUSSEF');OUT=Path(sys.argv[1]);c=sqlite3.connect(OUT/'experiment4.sqlite');c.execute('PRAGMA foreign_keys=ON')
f=ROOT/'Experiment 4/data/raw_extension/ballina_ar201920.pdf'
rows=[('operating_ratio_pct',2.76,'percent'),('own_source_pct',69.43,'percent'),('current_ratio',2.59,'ratio'),('debt_service_cover',2.54,'ratio'),('cash_cover_months',9.99,'months')]
with c:
 c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('ballina_ar201920','https://www.ballina.nsw.gov.au/files/assets/public/v/1/council/documents/council-documents/annual-report-2019_2020_web-version.pdf',str(f.relative_to(ROOT)),hashlib.sha256(f.read_bytes()).hexdigest(),'PDF267_printed89_note28a_image_verified',None))
 c.execute('CREATE TABLE fiscal_value_audit (council_key TEXT REFERENCES councils(council_key),fiscal_year_start INTEGER,variable TEXT,reported_value REAL,inherited_value REAL,unit TEXT,match_status TEXT,source_id TEXT REFERENCES sources(source_id),source_page TEXT,availability_link_status TEXT,PRIMARY KEY(council_key,fiscal_year_start,variable))')
 for var,value,unit in rows:
  old=float(c.execute('SELECT '+var+" FROM fiscal_annual WHERE council_key='ballina' AND year_start=2019").fetchone()[0]);match=abs(old-value)<1e-9
  c.execute('INSERT INTO fiscal_value_audit VALUES (?,?,?,?,?,?,?,?,?,?)',('ballina',2019,var,value,old,unit,'matches_report' if match else 'discrepancy_definition_or_vintage_unresolved','ballina_ar201920','PDF267;financial_statements89;note28a','Report-year presentation known; exact archived public-version equivalence still unverified'))
  if not match:c.execute("UPDATE capacity_candidates SET definition_status=definition_status || ';direct_report_value_conflict',availability_status='value_conflict_requires_reconciliation' WHERE council_key='ballina' AND fiscal_year_start=2019 AND variable=?",(var,))
 assert not c.execute('PRAGMA foreign_key_check').fetchall()
with c:
 p=ROOT/'Experiment 4/data/raw_extension/ballina_oct2020_statements.pdf'
 c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',('ballina_oct2020_statements','https://www.ballina.nsw.gov.au/files/assets/public/v/1/council/documents/agenda-and-minutes/2020/221020-item-9_8-attachment-3-draft-annual-financial-statements.pdf',str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'PDF98_note28a_image_verified_matches_annual_report_five_ratios',None))
 c.execute('ALTER TABLE fiscal_value_audit ADD COLUMN corroborating_source_id TEXT REFERENCES sources(source_id)')
 c.execute('ALTER TABLE fiscal_value_audit ADD COLUMN corroborating_source_page TEXT')
 c.execute("UPDATE fiscal_value_audit SET corroborating_source_id='ballina_oct2020_statements',corroborating_source_page='PDF98;printed89;note28a',availability_link_status='October2020_agenda_statement_and_annual_report_match;public_exhibition_by_Nov26;OLG_difference_unresolved' WHERE council_key='ballina' AND fiscal_year_start=2019")
for t in ['sources','fiscal_value_audit','capacity_candidates']:
 cur=c.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([x[0] for x in cur.description]);w.writerows(cur)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']['sources']=c.execute('SELECT COUNT(*) FROM sources').fetchone()[0];v['table_counts']['fiscal_value_audit']=5;v['ballina_fiscal_value_discrepancies']=3
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
