"""Create typed candidate capacity observations; no publication assumptions."""
import sqlite3,csv,json,sys,math
from pathlib import Path
OUT=Path(sys.argv[1]);db=sqlite3.connect(OUT/'experiment4.sqlite');db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
variables={'operating_ratio_pct':('percent','Prior operating balance relative to revenue'),'cash_cover_months':('months','Liquidity buffer; preserve cash definition caveat'),'current_ratio':('ratio','Short-term financial obligations coverage'),'own_source_pct':('percent','Locally controlled revenue share'),'grants_pct':('percent','Grant reliance; denominator must be harmonised'),'debt_service_cover':('ratio','Debt servicing capacity; preserve quality flags'),'population':('persons','Council service scale'),'road_km':('kilometres','Infrastructure network scale')}
with db:
 db.execute('CREATE TABLE capacity_candidates (council_key TEXT REFERENCES councils(council_key),budget_year_start INTEGER,fiscal_year_start INTEGER,variable TEXT,value REAL,unit TEXT,period_end TEXT,lag_years INTEGER,known_original_decision_date TEXT,period_precedes_known_original_decision INTEGER,publication_date TEXT,availability_status TEXT,definition_status TEXT,inclusion_reason TEXT,model_eligible INTEGER,source_id TEXT REFERENCES sources(source_id),PRIMARY KEY(council_key,budget_year_start,fiscal_year_start,variable))')
 pairs=db.execute('SELECT DISTINCT p.council_key,b.year_start FROM projects p JOIN budget_snapshots b USING(project_id)').fetchall()
 for key,y in pairs:
  dates=[r[0] for r in db.execute("SELECT DISTINCT b.decision_date FROM budget_snapshots b JOIN projects p USING(project_id) WHERE p.council_key=? AND b.year_start=? AND b.stage='B0' AND b.decision_date IS NOT NULL",(key,y))]
  date=min(dates) if dates else None
  for lag in [1,2]:
   fy=y-lag;r=db.execute('SELECT * FROM fiscal_annual WHERE council_key=? AND year_start=?',(key,fy)).fetchone()
   for var,(unit,reason) in variables.items():
    raw=r[var] if r else None;value=None if raw in [None,''] else float(raw)
    assert value is None or math.isfinite(value)
    end=r['period_end'] if r else None
    precedes=int(end<date) if end and date else None
    status='missing_council_fiscal_record' if not r else 'not_pre_adoption_period' if precedes==0 else 'economic_period_only_publication_unverified'
    definition=r['cash_definition_status'] if r and var=='cash_cover_months' else r['operating_definition_regime'] if r and var=='operating_ratio_pct' else 'debt_review_flag='+str(r['debt_service_cover_requires_review']) if r and var=='debt_service_cover' else 'inherited_definition_requires_comparability_check'
    db.execute('INSERT INTO capacity_candidates VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(key,y,fy,var,value,unit,end,lag,date,precedes,r['publication_date'] if r else None,status,definition,reason,0,r['source_id'] if r else None))
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
c=db.execute('SELECT * FROM capacity_candidates ORDER BY council_key,budget_year_start,lag_years,variable')
with (OUT/'capacity_candidates.csv').open('w',newline='') as f:w=csv.writer(f);w.writerow([d[0] for d in c.description]);w.writerows(c)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']['capacity_candidates']=db.execute('SELECT COUNT(*) FROM capacity_candidates').fetchone()[0];v['certified_capacity_observations']=0
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print('Capacity rows',v['table_counts']['capacity_candidates']);print('Observed values',db.execute('SELECT COUNT(*) FROM capacity_candidates WHERE value IS NOT NULL').fetchone()[0])
