"""Apply visually checked source findings to the Experiment 4 candidate store."""
import csv,hashlib,json,sqlite3,sys
from pathlib import Path
ROOT=Path('/Users/ray/Research/AUSSEF')
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'Experiment 4/data'
db=sqlite3.connect(OUT/'experiment4.sqlite');db.row_factory=sqlite3.Row
db.execute('PRAGMA foreign_keys=ON')
def insert(table,record):
    cols=list(record)
    db.execute('INSERT INTO '+table+' ('+','.join(cols)+') VALUES ('+','.join('?' for _ in cols)+')',list(record.values()))
def src(sid,url,file):
    local='Experiment 4/data/raw_extension/'+file
    insert('sources',dict(source_id=sid,url=url,local_file=local,
        sha256=hashlib.sha256((ROOT/local).read_bytes()).hexdigest(),
        evidence_status='official_pdf_text_and_page_image_verified',publication_date=None))

assert not db.execute("SELECT 1 FROM sources WHERE source_id='snowy_ar2122'").fetchone(),'Already applied; refusing duplicate import'
with db:
    src('snowy_ar2122','https://www.snowyvalleys.nsw.gov.au/files/assets/public/reports-amp-strategies/202122-ipampr/2021-22-annual-report-adopted-17-novemeber-2022.pdf','snowy_ar2122.pdf')
    src('wagga_capital_july2020','https://meetings.wagga.nsw.gov.au/Open/2020/08/OC_24082020_AGN_3743_AT_files/OC_24082020_AGN_3743_AT_Attachment_18700_3.PDF','wagga_capital_july2020.pdf')
    if not db.execute("SELECT 1 FROM councils WHERE council_key='snowyvalleys'").fetchone():
        insert('councils',dict(council_key='snowyvalleys',council_name='Snowy Valleys',jurisdiction='NSW',universe='extension_candidate_outside_103_continuing_councils_entity_history_requires_audit'))
    rows=[
      ('bombowlee_land','Bombowlee Land Acquisition',100000,67378,79,'underway','ordinary_candidate'),
      ('tintaldra_culvert','Tintaldra Road Culvert Replacement',264521,597670,79,'underway','ordinary_candidate'),
      ('withers_bridge','Withers Bridge',300000,417540,79,'completed_reported','ordinary_candidate'),
      ('bombowlee_complex','Bombowlee Creek/Taradale Complex',9900000,8295532,79,'underway','ordinary_candidate'),
      ('tumbarumba_generator','Generator for SVC Tumbarumba Office',21600,5992,81,'underway','ordinary_candidate_scope_overlap_flag'),
      ('tumbarumba_solar','Solar Panels for SVC Tumbarumba Office',24500,2805,81,'underway','ordinary_candidate'),
      ('khancoban_toilets','Khancoban Toilets (LRCI Phase 2)',161818,153274,81,'completed_reported','ordinary_candidate'),
      ('fitzroy_toilets','Fitzroy Street Toilets (LRCI Phase 2)',300000,165033,81,'underway','ordinary_candidate'),
      ('ournie_hall','Ournie Community Hall',800000,313501,81,'underway','ordinary_candidate'),
      ('office_refurbishment','Office Buildings Refurbishment',500000,97710,81,'underway','ordinary_candidate_bundle'),
      ('snowview','Snow View Estate Stage 3 Civil Works',1000000,59226,81,'underway','ordinary_candidate'),
      ('batlow_caravan','Batlow Caravan Park (NSW Bushfire Recovery)',3500000,1632675,81,'underway','disaster_recovery_labelled'),
      ('tumut_aerodrome','Tumut Aerodrome (NSW Bushfire Recovery)',6000000,482190,81,'underway','disaster_recovery_labelled_scope_overlap_flag'),
    ]
    for code,label,b0,actual,page,status,scope in rows:
        pid='snowyvalleys:candidate:'+code
        insert('projects',dict(project_id=pid,council_key='snowyvalleys',official_project_id=None,
            analyst_record_id='SV_'+code,project_label=label,unit_status='named_work_candidate_scope_not_certified',
            identifier_status='analyst_label_no_official_project_ID',spending_class=scope,
            cross_document_link_status='same_annual_report_row_only',original_completion_date=None,
            actual_completion_date=None,deferral_decision_date=None,rephased_to_fy=None,
            completion_status=status,fixed_pre_event_portfolio_verified=0,source_id='snowy_ar2122',source_page=str(page)))
        insert('damage_status',dict(damage_record_id=pid+':unknown',project_id=pid,disaster_id=None,
            assessment_date=None,damage_status='unknown',access_status='unknown',source_id='snowy_ar2122',
            evidence_status='no_asset_damage_assessment_in_budget_row_recovery_label_is_not_damage_measure'))
        for stage in ['B0','Q1','Q2','Q3','ACTUAL']:
            value=b0 if stage=='B0' else actual if stage=='ACTUAL' else None
            insert('budget_snapshots',dict(snapshot_id=pid+':2021:'+stage,project_id=pid,year_start=2021,stage=stage,
                amount_aud=value,value_status='reported_retrospective_same_row' if value is not None else 'unknown_not_recovered',
                amount_basis='annual_report_actual_basis_requires_audit' if stage=='ACTUAL' else 'annual_budget',
                reference_period_end='2022-06-30' if stage=='ACTUAL' else None,decision_date=None,
                decision_status='June_2021_adoption_reported_exact_date_not_verified' if stage=='B0' else 'unknown',
                source_id='snowy_ar2122' if value is not None else None,source_page=str(page) if value is not None else None,
                decision_source_id=None,evidence_limit='Retrospective report; quarterly continuity and event alignment unverified; not pre-2019-fire baseline',model_eligible=0))
    for measure,value in [('combined_annual_allocation',384787),('confirmed_component',24940),('estimated_prior_year_carryover',28506),('pending_component',331341)]:
        insert('project_evidence',dict(evidence_id='wagga45049_july2020_'+measure,project_id='waggawagga:job:45049',
            year_start=2020,source_id='wagga_capital_july2020',source_page='8',measure=measure,amount_aud=value,
            funding_status='separate_components_not_original_or_quarter_end',verification='PDF page 8 image verified',
            limitation='July review attachment; adoption and relation to original budget unverified'))
    assert 24940+28506+331341==384787
    assert not db.execute('PRAGMA foreign_key_check').fetchall()

for table in [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]:
    cursor=db.execute('SELECT * FROM '+table);cols=[x[0] for x in cursor.description]
    with (OUT/(table+'.csv')).open('w',newline='') as f:
        w=csv.writer(f);w.writerow(cols);w.writerows(cursor)
gpath=OUT/'field_gaps.csv'
with gpath.open() as f: gaps=list(csv.DictReader(f))
for code,*_ in rows:
    for field in ['Q1_amount_aud','Q2_amount_aud','Q3_amount_aud','official_project_id','original_adoption_document','damage_access_assessment','exact_completion_dates','three_pre_event_budget_years','pre_event_fiscal_capacity','event_overlap_screen']:
        gaps.append(dict(project_id='snowyvalleys:candidate:'+code,year_start='2021',required_field=field,
            status='not_recovered_search_incomplete',reason='Annual report budget/actual pair cannot establish this field',
            next_action='Recover adopted plan quarterly reviews and project/asset records; audit entity and disaster histories'))
with gpath.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(gaps[0]));w.writeheader();w.writerows(gaps)
checks=json.loads((OUT/'validation.json').read_text())
checks['table_counts']={r[0]:db.execute('SELECT COUNT(*) FROM '+r[0]).fetchone()[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
checks.update(observed_project_snapshot_amounts=db.execute('SELECT COUNT(*) FROM budget_snapshots WHERE amount_aud IS NOT NULL').fetchone()[0],field_gaps=len(gaps),certified_model_rows=0,foreign_key_errors=0,sqlite_integrity=db.execute('PRAGMA integrity_check').fetchone()[0])
(OUT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
