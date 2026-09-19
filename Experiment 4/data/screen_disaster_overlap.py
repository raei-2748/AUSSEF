"""Screen recovered council-years without equating declaration with asset damage."""
import csv,json,sqlite3,hashlib,sys
from pathlib import Path
ROOT=Path('/Users/ray/Research/AUSSEF');OUT=Path(sys.argv[1]);db=sqlite3.connect(OUT/'experiment4.sqlite');db.execute('PRAGMA foreign_keys=ON')
paths={'v2_exposure_overlap_screen':ROOT/'Experiment 2/data/disaster_exposure_v2/NSW_Disaster_Exposure_V2_candidate.csv','supplied_drfa_20260811':ROOT/'Experiment 4/data/raw_extension/drfa_activation_history_by_location_2026_august_11.csv'}
with db:
 for sid,p in paths.items():db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',(sid,None,str(p.relative_to(ROOT)),hashlib.sha256(p.read_bytes()).hexdigest(),'inherited_candidate_panel_not_recertified' if sid.startswith('v2') else 'user_supplied_activation_register_snapshot_provenance_not_independently_recertified',None))
 db.execute('CREATE TABLE council_year_exposure_screen (council_key TEXT REFERENCES councils(council_key),year_start INTEGER,declared_event_ids TEXT,mapped_burn_ha REAL,mapped_burn_status TEXT,physical_flood_status TEXT,screen_status TEXT,source_id TEXT REFERENCES sources(source_id),PRIMARY KEY(council_key,year_start))')
 years=set(db.execute('SELECT DISTINCT p.council_key,b.year_start FROM projects p JOIN budget_snapshots b USING(project_id)'))
 panel={(r['council_key'],int(r['year_start'])):r for r in csv.DictReader(paths['v2_exposure_overlap_screen'].open())}
 for key,y in sorted(years):
  r=panel.get((key,y),{});ids=r.get('all_agrns') or None;burn=r.get('fesm_burned_ha')
  status='positive_declaration_or_mapped_fire_screen_not_certified_untreated' if ids or (burn and float(burn)>0) else 'unknown_no_certified_untreated_status'
  db.execute('INSERT INTO council_year_exposure_screen VALUES (?,?,?,?,?,?,?,?)',(key,y,ids,float(burn) if burn else None,r.get('fesm_status','not_in_inherited_panel'),r.get('physical_flood_status','unknown'),status,'v2_exposure_overlap_screen'))
 for r in csv.DictReader(paths['supplied_drfa_20260811'].open(encoding='utf-8-sig')):
  if r['Location_Name']!='Ballina' or r['STATE']!='New South Wales' or r['agrn'] not in ['943','960','1012']:continue
  did='event:'+r['agrn']
  if not db.execute('SELECT 1 FROM disasters WHERE disaster_id=?',(did,)).fetchone():db.execute('INSERT INTO disasters VALUES (?,?,?)',(did,r['agrn'],'reported_AGRN_from_supplied_activation_register_not_asset_exposure'))
  db.execute('INSERT INTO disaster_observations VALUES (?,?,?,?,?,?,?,?)',('ballina_DRFA_'+r['agrn'],did,'ballina',r['disaster_start_date'],'regional_disaster_start_in_activation_register','Not local inundation onset, declaration publication date, or project damage; register coverage must not imply negative exposure outside listed entries','supplied_drfa_20260811',None))
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
 c=db.execute('SELECT * FROM '+t)
 with (OUT/(t+'.csv')).open('w',newline='') as f:w=csv.writer(f);w.writerow([d[0] for d in c.description]);w.writerows(c)
v=json.loads((OUT/'validation.json').read_text());v['table_counts']={t:db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()};v['event_identity_warning']='Source labels include unresolved aliases; table count is not independent disaster count';v['certified_untreated_council_years']=0
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print(db.execute('SELECT council_key,year_start,declared_event_ids,screen_status FROM council_year_exposure_screen').fetchall())
