"""Record report availability bounds without certifying inherited numeric values."""
import csv,json,sqlite3,hashlib,sys
from pathlib import Path
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists());OUT=Path(sys.argv[1]);RAW=ROOT/'Experiment 4/data/raw_extension'
c=sqlite3.connect(OUT/'experiment4.sqlite');c.execute('PRAGMA foreign_keys=ON')
with c:
 for sid,u in json.loads((RAW/'ballina_financial_presentation_urls.json').read_text()).items():
  p=RAW/(sid+'.pdf');c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',(sid,u,str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'public_exhibition_and_adoption_text_verified',None))
 c.execute('CREATE TABLE fiscal_availability_evidence (evidence_id TEXT PRIMARY KEY,council_key TEXT REFERENCES councils(council_key),fiscal_year_start INTEGER,report_type TEXT,available_by_date TEXT,first_publication_date TEXT,date_basis TEXT,source_id TEXT REFERENCES sources(source_id),source_page TEXT,numeric_value_match_verified INTEGER,limitation TEXT)')
 c.execute('INSERT INTO fiscal_availability_evidence VALUES (?,?,?,?,?,?,?,?,?,?,?)',('ballina2019_public_presentation','ballina',2019,'annual_financial_and_auditor_reports','2020-11-26',None,'resolution261120/12_adopts_reports_as_publicly_exhibited','ballina_nov2020_minutes','PDF7',0,'Agenda PDF94-95 corroborates completed public exhibition. Availability upper bound, not first release date. Individual inherited OLG ratios still require report-page verification.'))
 assert not c.execute('PRAGMA foreign_key_check').fetchall()
for t, in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
 cur=c.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([x[0] for x in cur.description]);w.writerows(cur)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']={t:c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t, in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
