"""Rebuild the candidate evidence store in a NEW directory; never fit models."""
import sys,subprocess,sqlite3,csv,json,hashlib
from pathlib import Path
BASE=Path('/Users/ray/Research/AUSSEF/Experiment 4/data')
STAGES=['build_candidate_store','extend_verified_sources','audit_snowy_quarterly','extend_ballina','extend_ballina_quarters','verify_ballina_decisions','verify_ballina_baseline','extend_ballina_history','screen_disaster_overlap','audit_capacity_alignment','add_capacity_availability','audit_ballina_fiscal_values','audit_damage_linkage','extend_richmond_followon','extend_griffith_leads']
def check(folder):
 db=sqlite3.connect(folder/'experiment4.sqlite');assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not db.execute('PRAGMA foreign_key_check').fetchall()
 counts={}
 for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall():
  c=db.execute('SELECT * FROM '+t);cols=[x[0] for x in c.description];rows=c.fetchall();counts[t]=len(rows)
  with (folder/(t+'.csv')).open(newline='') as f:
   reader=csv.reader(f);assert next(reader)==cols,t;export=list(reader)
  norm=lambda row:tuple('' if x is None else str(x) for x in row)
  assert sorted(map(norm,rows))==sorted(map(tuple,export)),('CSV divergence',t)
 assert not db.execute('SELECT project_id,year_start,stage,COUNT(*) FROM budget_snapshots GROUP BY 1,2,3 HAVING COUNT(*)>1').fetchall()
 assert db.execute('SELECT COUNT(*) FROM budget_snapshots WHERE model_eligible=1').fetchone()[0]==0
 return db,counts
if __name__=='__main__':
 out=Path(sys.argv[1]);assert not out.exists(),'Choose a new directory';out.mkdir(parents=True)
 for stage in STAGES:
  r=subprocess.run([sys.executable,str(BASE/(stage+'.py')),str(out)],capture_output=True,text=True)
  if r.returncode:raise RuntimeError(stage+'\n'+r.stdout+'\n'+r.stderr)
  print('Passed',stage,flush=True)
 db,counts=check(out);old,_=check(BASE);differences=[]
 for t in counts:
  a=db.execute('SELECT * FROM '+t).fetchall();b=old.execute('SELECT * FROM '+t).fetchall()
  canon=lambda rows:sorted(json.dumps(r) for r in rows)
  if canon(a)!=canon(b):differences.append(t)
 report=dict(sqlite_integrity='ok',foreign_key_errors=0,csv_database_match=True,table_counts=counts,canonical_table_differences=differences,model_rows=0)
 (out/'rebuild_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
