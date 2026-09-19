"""Build a conservative, source-linked candidate store. No estimation or imputation."""
from pathlib import Path
import csv, hashlib, json, sqlite3, sys

ROOT = Path('/Users/ray/Research/AUSSEF')
BASE = ROOT/'Experiment 4'
PILOT = BASE/'results'
OUT = Path(sys.argv[1]) if len(sys.argv)>1 else BASE/'data'
OUT.mkdir(exist_ok=True)
assert not (OUT/'experiment4.sqlite').exists(), 'Use a new output folder; existing evidence database will not be overwritten'

def read(path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

tables = {}
sources = {}
def source(sid, url='', local='', status='inherited_curated_evidence'):
    if not sid:
        return None
    if sid not in sources:
        p = ROOT/local if local else None
        sources[sid] = dict(source_id=sid, url=url, local_file=local,
            sha256=hashlib.sha256(p.read_bytes()).hexdigest() if p and p.is_file() else '',
            evidence_status=status, publication_date=None)
    elif url and not sources[sid]['url']:
        sources[sid]['url']=url
    return sid

for r in read(PILOT/'source_index.csv'):
    source(r['source_id'], r['url'])
for r in json.loads((PILOT/'source_provenance.json').read_text()):
    sid=source(r['source_id'],r.get('url',''))
    local=r.get('local_file','')
    if local:
        p=PILOT/local
        if p.is_file():
            sources[sid]['local_file']=str(p.relative_to(ROOT))
            sources[sid]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()

fpath=ROOT/'Experiment 2/data/fiscal_panel_v2/NSW_Fiscal_Panel_V2_candidate.csv'
fiscal=read(fpath)
source('inherited_fiscal_v2',local=str(fpath.relative_to(ROOT)),status='derived_candidate_panel_not_publication_vintage_certified')
councils={r['council_key']:dict(council_key=r['council_key'],council_name=r['council_name'],
    jurisdiction='NSW',universe='inherited_V2_continuing_council_screen') for r in fiscal}
tables['councils']=list(councils.values())
fcols=['council_key','year_start','financial_year','period_start','period_end','reporting_months',
 'operating_ratio_pct','cash_cover_months','cash_cover_reported_months','current_ratio','own_source_pct',
 'grants_pct','debt_service_cover','debt_service_ratio_pct','population','road_km',
 'total_revenue_including_capital_aud','total_expenses_aud','operating_revenue_ex_capital_aud',
 'cash_definition_status','operating_definition_regime','debt_service_cover_requires_review',
 'source_file','source_sheet','source_excel_row']
tables['fiscal_annual']=[{**{k:r[k] or None for k in fcols},'source_id':'inherited_fiscal_v2',
    'publication_date':None,'strict_pre_event_available':0,
    'availability_status':'economic_period_known_publication_vintage_unverified'} for r in fiscal]

# Keep date observations separate: a regional start, ignition and local peak are not equivalent.
events=read(PILOT/'event_timeline.csv')
tables['disasters']=[]
tables['disaster_observations']=[]
for i,r in enumerate(events,1):
    event_id=r['event_id'] or 'unresolved_event_'+str(i)
    key='event:'+event_id
    if key not in {x['disaster_id'] for x in tables['disasters']}:
        tables['disasters'].append(dict(disaster_id=key,reported_event_id=event_id,
            identity_status='inherited_label_requires_cross_source_identity_audit'))
    sid=source('event_timeline',local=str((PILOT/'event_timeline.csv').relative_to(ROOT)),status='derived_dated_evidence_ledger')
    tables['disaster_observations'].append(dict(observation_id='D'+str(i),disaster_id=key,
        council_key=r['council_key'],date=r['date'] or None,date_type=r['date_type'],
        limitation=r['limitation'],source_id=sid,underlying_source_url=r['source_url']))

register=read(PILOT/'project_revision_register.csv')
decisions={(r['council_key'],r['year_start'],r['stage']):r for r in read(PILOT/'decision_dates.csv')}
tables['projects']=[]; tables['budget_snapshots']=[];tables['damage_status']=[];tables['project_revisions']=[]
gaps=[]
for r in register:
    official=r['official_project_id']
    if official.endswith('.0'): official=official[:-2]
    # Analyst IDs identify evidence candidates only, never certified physical assets.
    pid=r['council_key']+':'+('job:'+official if official else 'candidate:'+r['project_record_id'])
    sid=source(r['source_id'],r['source_url'])
    tables['projects'].append(dict(project_id=pid,council_key=r['council_key'],official_project_id=official or None,
        analyst_record_id=r['project_record_id'],project_label=r['project_label'],
        unit_status='project_or_program_scope_requires_verification',identifier_status=r['identifier_status'],
        spending_class=r['spending_class'],cross_document_link_status=r['cross_document_link_status'],
        original_completion_date=None,actual_completion_date=None,deferral_decision_date=None,
        rephased_to_fy=r['rephased_to_fy'] or None,completion_status=r['year_end_completion_status'],
        fixed_pre_event_portfolio_verified=0,source_id=sid,source_page=r['source_page']))
    tables['damage_status'].append(dict(damage_record_id=pid+':unresolved',project_id=pid,
        disaster_id=None,assessment_date=None,damage_status=r['asset_damage_status'],
        access_status=r['asset_access_status'],source_id=sid,
        evidence_status='inherited_unknown_not_evidence_of_no_damage'))
    tables['project_revisions'].append(dict(revision_id=r['project_record_id'],project_id=pid,
        year_start=int(r['year_start']),stage=r['revision_stage'],
        revision_aud=float(r['budget_revision_aud']) if r['budget_revision_aud'] else None,
        before_revision_aud=float(r['pre_revision_budget_aud']) if r['pre_revision_budget_aud'] else None,
        after_revision_aud=float(r['post_revision_budget_aud']) if r['post_revision_budget_aud'] else None,
        reason=r['reason'],source_id=sid,source_page=r['source_page']))
    for st in ['B0','Q1','Q2','Q3','ACTUAL']:
        val=''; ssid=None; page=None
        if st=='B0' and r['original_budget_aud']:
            val=r['original_budget_aud'];ssid=source(r['original_source_id'],r['original_source_url']);page=r['original_source_page']
        elif st==r['revision_stage'] and r['post_revision_budget_aud']:
            val=r['post_revision_budget_aud'];ssid=sid;page=r['source_page']
        elif st=='ACTUAL' and r['year_end_actual_aud']:
            val=r['year_end_actual_aud'];ssid=sid;page=r['source_page']
        d=decisions.get((r['council_key'],r['year_start'],st),{})
        tables['budget_snapshots'].append(dict(snapshot_id=pid+':'+r['year_start']+':'+st,
            project_id=pid,year_start=int(r['year_start']),stage=st,
            amount_aud=float(val) if val else None,value_status='reported_candidate' if val else 'unknown_not_recovered',
            amount_basis='annual_actual' if st=='ACTUAL' else 'annual_budget',
            reference_period_end=d.get('reference_period_end') or None,
            decision_date=d.get('decision_date') or None,
            decision_status=d.get('decision_status','unknown'),source_id=ssid,source_page=page,
            decision_source_id=source(d.get('source_id'),d.get('source_url','')),
            evidence_limit='Review-level date; project-level adoption and scope need verification',model_eligible=0))
        if not val:
            gaps.append(dict(project_id=pid,year_start=r['year_start'],required_field=st+'_amount_aud',
                status='not_recovered_search_incomplete',reason='Selected revision evidence does not report a same-scope full-year level at this stage',
                next_action='Inspect adopted project schedule and quarterly/year-end project ledger; never infer level from a change alone'))
    for field in ['stable_asset_scope','damage_access_assessment','completion_dates','three_pre_event_budget_years']:
        gaps.append(dict(project_id=pid,year_start=r['year_start'],required_field=field,
            status='not_certified_search_incomplete',reason='Current project register lacks dated linked evidence',
            next_action='Recover project or asset records with explicit identifiers and contemporaneous dates'))

tables['comparisons']=[]
for r in read(PILOT/'comparison_screen.csv'):
    for treated in r['comparison_for'].split(';'):
        tables['comparisons'].append(dict(comparison_id=r['council_key']+':'+treated+':'+r['year_start'],
            council_key=r['council_key'],treated_council_key=treated,year_start=int(r['year_start']),
            certified_pre_event_budget_years=0,matched_control_eligible=0,
            mapped_burn_status=r['mapped_burn_status'],physical_flood_status=r['physical_flood_status'],
            subsequent_exposure=r['subsequent_exposure'],spillover_screen=r['spillover_screen'],
            source_id=source('comparison_screen',local=str((PILOT/'comparison_screen.csv').relative_to(ROOT))),
            verdict=r['verdict']))
pending_source=source('wagga_adopted_ltfp_2021_22',
 'https://www.ipart.nsw.gov.au/sites/default/files/cm9_documents/Wagga-Wagga-City-Council-Attachment---1--2021-22-Adopted-Long-Term-Fin-Plan.PDF',
 'Experiment 4/data/raw_extension/wagga_adopted_ltfp_2021_22.pdf',
 'official_host_pdf_page_66_text_and_image_verified')
tables['project_evidence']=[dict(evidence_id='wagga45049_pending_original_2021',
 project_id='waggawagga:job:45049',year_start=2021,source_id=pending_source,source_page='66',
 measure='original_annual_pending_allocation',amount_aud=331341,
 funding_status='pending_not_confirmed',verification='PDF printed page 66 visually inspected',
 limitation='Not accepted as confirmed funded B0; same job number but scope and adoption date still need checking')]
tables['sources']=list(sources.values())

def write(name,rows):
    assert rows,name
    with (OUT/(name+'.csv')).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

for name,rows in tables.items():write(name,rows)
write('field_gaps',gaps)

# SQLite uses explicit primary and foreign keys; CSV blank values become SQL NULL.
keys={'councils':['council_key'],'sources':['source_id'],'disasters':['disaster_id'],
 'projects':['project_id'],'budget_snapshots':['snapshot_id'],'fiscal_annual':['council_key','year_start'],
 'damage_status':['damage_record_id'],'comparisons':['comparison_id'],
 'disaster_observations':['observation_id'],'project_revisions':['revision_id'],'project_evidence':['evidence_id']}
db=sqlite3.connect(OUT/'experiment4.sqlite')
db.execute('PRAGMA foreign_keys=ON')
assert not db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(), 'Refuse to overwrite existing database; build into a new version'
for name in ['sources','councils','disasters','projects','fiscal_annual','budget_snapshots','damage_status','comparisons','disaster_observations','project_revisions','project_evidence']:
    rows=tables[name];cols=list(rows[0]);defs=[]
    for col in cols:
        typ='REAL' if col.endswith('_aud') else ('INTEGER' if col in ['year_start','model_eligible','matched_control_eligible','certified_pre_event_budget_years','fixed_pre_event_portfolio_verified','strict_pre_event_available'] else 'TEXT')
        defs.append('"'+col+'" '+typ)
    defs.append('PRIMARY KEY ('+','.join(keys[name])+')')
    for col,target in [('council_key','councils(council_key)'),('treated_council_key','councils(council_key)'),('project_id','projects(project_id)'),('source_id','sources(source_id)'),('decision_source_id','sources(source_id)'),('disaster_id','disasters(disaster_id)')]:
        if col in cols and col not in keys[name]:defs.append('FOREIGN KEY ('+col+') REFERENCES '+target)
    if name=='budget_snapshots':defs.append('UNIQUE(project_id,year_start,stage)')
    db.execute('CREATE TABLE '+name+' ('+','.join(defs)+')')
    db.executemany('INSERT INTO '+name+' VALUES ('+','.join('?' for _ in cols)+')',[[r[c] if r[c]!='' else None for c in cols] for r in rows])
db.commit()
assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert not db.execute('PRAGMA foreign_key_check').fetchall()
checks=dict(table_counts={n:len(r) for n,r in tables.items()},foreign_key_errors=0,
    observed_project_snapshot_amounts=sum(r['amount_aud'] is not None for r in tables['budget_snapshots']),
    certified_model_rows=0,field_gaps=len(gaps),status='candidate_store_search_in_progress_not_model_ready',
    original_source_sha256=hashlib.sha256((ROOT/'NSW Data Panel.csv').read_bytes()).hexdigest())
(OUT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
db.close()
print(json.dumps(checks,indent=2))
