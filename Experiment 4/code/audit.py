from pathlib import Path
import hashlib,json,re,zipfile
import pandas as pd
import numpy as np
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists()); OUT=ROOT/'Experiment 4/audit/results'
NOTE=ROOT/'Experiment 4/audit/experiment.ipynb'
files=[p for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and p!=NOTE]
OUT.mkdir(parents=True,exist_ok=True)
freeze=OUT/'frozen_existing_sha256.json'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if not freeze.exists(): freeze.write_text(json.dumps({str(p.relative_to(ROOT)):digest(p) for p in files},indent=2))
hashes=json.loads(freeze.read_text()); assert all(digest(ROOT/p)==h for p,h in hashes.items())
def save(d,name):d.to_csv(OUT/f'{name}.csv',index=False)
# Whole-repository inventory and schema search; generated mirrors are not independent evidence.
inv=[]; schema=[]
for p in files:
 rel=str(p.relative_to(ROOT));inv.append(dict(path=rel,extension=p.suffix,bytes=p.stat().st_size,sha256=hashes.get(rel),role='generated_index_not_independent_source' if 'generated/graph' in rel else 'existing_repository_file'))
 if p.suffix=='.csv':
  try:
   d=pd.read_csv(p,low_memory=False)
   hits=[c for c in d if re.search(r'budget|revis|defer|project|quarter|planned|actual|maintenance|date|capacity',c,re.I)]
   schema.append(dict(path=rel,rows=len(d),columns=len(d.columns),column_names='|'.join(d.columns),candidate_columns='|'.join(hits),read_status='read'))
  except Exception as e:schema.append(dict(path=rel,read_status=type(e).__name__+': '+str(e)[:150]))
save(pd.DataFrame(inv),'repository_inventory');save(pd.DataFrame(schema),'csv_schema_inventory')
E=ROOT/'Experiment 3/results'; S=E/'sources'; F=ROOT/'Experiment 2/data/fiscal_panel_v2'; D=ROOT/'Experiment 2/data/disaster_exposure_v2'
paths={'fiscal':F/'NSW_Fiscal_Panel_V2_candidate.csv','e3_panel':E/'experiment3_panel.csv','evidence':E/'documentary_evidence.csv','events_historical':D/'declaration_event_ledger.csv','exposure':D/'NSW_Disaster_Exposure_V2_candidate.csv','activation':ROOT/'Experiment 4/related/funding_access/results/inputs/drfa_activation_history_by_location_2026_august_11.csv'}
tables={k:pd.read_csv(v) for k,v in paths.items()};profiles=[];fields=[]
for k,d in tables.items():
 profiles.append(dict(dataset=k,path=str(paths[k].relative_to(ROOT)),rows=len(d),columns=len(d.columns),councils=d.council_key.nunique() if 'council_key' in d else np.nan,year_min=d.year_start.min() if 'year_start' in d else np.nan,year_max=d.year_start.max() if 'year_start' in d else np.nan,duplicate_council_year_rows=int(d.duplicated(['council_key','year_start']).sum()) if {'council_key','year_start'}<=set(d) else np.nan))
 for c in d:fields.append(dict(dataset=k,column=c,dtype=str(d[c].dtype),nonmissing=int(d[c].notna().sum()),missing=int(d[c].isna().sum()),missing_pct=d[c].isna().mean()*100,distinct=d[c].nunique()))
save(pd.DataFrame(profiles),'dataset_profile');save(pd.DataFrame(fields),'field_quality_profile')
# Scan cached E3 PDF extractions. Normalize whitespace so split PDF headers are not missed.
hits=[]
for p in S.glob('*_pages.json'):
 for i,t in enumerate(json.loads(p.read_text()),1):
  t=re.sub(r'\s+',' ',t)
  for kind,pattern in [('quarterly','quarterly budget|quarterly review|quarterly financial|QBRS'),('revision','revised budget'),('deferral','defer|postpon|carry.?forward|delayed'),('annual_pair','Original unaudited budget')]:
   m=re.search(pattern,t,re.I)
   if m:hits.append(dict(source_file=str(p.relative_to(ROOT)),pdf_page=i,topic=kind,context=t[max(0,m.start()-100):m.end()+240],interpretation='Search hit only; not a verified outcome or complete document series'))
save(pd.DataFrame(hits),'cached_document_search')
prov=pd.read_csv(E/'source_provenance.csv').set_index('source_id'); ev=tables['evidence']
# New descriptive transcriptions from original cached PDFs, not existing model outputs.
ann=[]
for council,yr,sid,pg,b,a in [('richmondvalley',2021,'richmond_fs2022',10,43690000,26431000),('lismore',2021,'lismore_fs2022',9,64888000,32656000),('griffith',2019,'griffith_fs2020',9,40933000,22210000),('lismore',2023,'lismore_fs2024',9,235791000,122821000)]:
 ann.append(dict(council_key=council,year_start=yr,financial_year=f'{yr}-{str(yr+1)[-2:]}',measure='Gross IPPE cash payments; all capital scope',original_budget_aud=b,actual_aud=a,deviation_aud=a-b,deviation_pct=100*(a-b)/b,source_file=f'Experiment 3/results/sources/{sid}.pdf',source_url=prov.loc[sid,'url'] if 'url' in prov else ev[ev.source_id.eq(sid)].source_url.iloc[0],pdf_page=pg,unit_conversion='source AUD thousands x1000; parenthesised outflows represented as positive spending',ordinary_scope_verified=False,primary_outcome_eligible=False,limitation='All IPPE, not fixed ordinary infrastructure portfolio; no quarterly revisions; cash basis. Lismore FY2023–24 baseline postdates 2022 flood.',verification='PDF text; page image inspected'))
save(pd.DataFrame(ann),'annual_deviation_examples')
q=[]
for label,b,r in [('Footpath Maintenance',197100,197100),('Urban Sealed Road Maintenance',2450600,3008921),('Rural Sealed Roads Maintenance',2295400,3337000),('Rural Unsealed Roads Maintenance',1026300,626300),('State Roads Routine Maintenance Works',541700,541700),('Regional Roads Block Grant Maintenance',1150600,1200600)]:
 q.append(dict(council_key='lismore',financial_year='2022-23',program=label,original_budget_aud=b,revised_full_year_budget_aud=r,revision_asof='2023-03-31',revision_aud=r-b,revision_pct=100*(r-b)/b,earlier_quarter_snapshots_recovered=False,original_adoption_date='',revision_approval_date='',source_url=ev[ev.source_id.eq('lismore_budget2024')].source_url.iloc[0],source_file='Experiment 3/results/sources/lismore_budget2024.pdf',pdf_page=17,printed_page=15,verification='PDF text and page image inspected',primary_eligible_for_feb2022=False,reason='Original FY2022–23 budget postdates February 2022 flood; no causal attribution, no quarter-on-quarter series; disaster cost separation unverified'))
save(pd.DataFrame(q),'quarterly_revision_examples')
# Preserve project narratives, without pretending they provide a complete deferral register.
projects=ev[ev.evidence_id.isin(['E024','E033','E032'])].copy();projects['original_planned_completion_date']=pd.NA;projects['revised_completion_date']=pd.NA;projects['stable_project_id']=pd.NA;projects['certified_delay_days']=np.nan;projects['undamaged_accessible_asset_verified']=False
save(projects,'project_deferral_audit')
# Fiscal data are annual measurements; last completed year is not necessarily an available publication.
fiscal=tables['fiscal'];capacity=['operating_ratio_pct','cash_cover_months','current_ratio','own_source_pct','grants_pct','debt_service_cover','debt_service_ratio_pct','population','road_km']
cov=[]
for yr,g in fiscal.groupby('year_start'):
 for c in capacity:cov.append(dict(year_start=yr,financial_year=g.financial_year.iloc[0],feature=c,councils=len(g),usable_numeric=int(pd.to_numeric(g[c],errors='coerce').notna().sum()),missing=int(g[c].isna().sum()),qualifier='Numeric coverage only; definition, vintage and event timing gates remain'))
save(pd.DataFrame(cov),'capacity_coverage_by_year')
selected=tables['e3_panel'].query("role == 'treated'").drop_duplicates('council_key')
cols=['council_key','event_group','pre_fiscal_year','pre_cash_cover_months','pre_operating_ratio_pct','low_pre_cash_cover','weak_pre_operating_position']
save(selected[cols],'pilot_capacity_contrast')
raw=tables['activation'];nsw=raw[raw.STATE.eq('New South Wales') & raw.Location_Type.eq('LGA')].copy();nsw['source_csv_row']=nsw.index+2
nsw['parsed_start']=pd.to_datetime(nsw.disaster_start_date,errors='coerce');nsw['fy_start']=nsw.parsed_start.dt.year-(nsw.parsed_start.dt.month<7).astype(int);nsw['nsw_fy_quarter']=((nsw.parsed_start.dt.month-7)%12//3+1).astype('Int64')
# Explicit normalised exact-name lookup, retaining unresolved joins; no fuzzy matching.
lookup=fiscal[['council_key','council_name']].drop_duplicates();lookup['norm']=lookup.council_name.str.lower().str.replace(r'[^a-z0-9]','',regex=True)
assert lookup.norm.is_unique
nsw['norm']=nsw.Location_Name.str.lower().str.replace(r'[^a-z0-9]','',regex=True)
nsw=nsw.merge(lookup[['norm','council_key']],on='norm',how='left',validate='many_to_one');nsw['join_status']=np.where(nsw.council_key.notna(),'EXACT_NORMALISED_NAME; boundary vintage not verified','UNMATCHED; do not assign exposure zero')
nsw['local_impact_onset_verified']=False;nsw['quarter_note']='Event-wide listed start quarter, not council-specific impact or budget decision quarter; current activation snapshot incomplete as event universe'
save(nsw.drop(columns=['norm']),'nsw_disaster_timing_audit')
# Last full FY strictly before event start, no modelling and no publication-date claim.
frows=[]
for _,r in nsw[nsw.council_key.notna()].iterrows():
 eligible=fiscal[fiscal.council_key.eq(r.council_key)&pd.to_datetime(fiscal.period_end).lt(r.parsed_start)]
 if eligible.empty:continue
 prior=eligible.sort_values('period_end').iloc[-1]
 frows.append(dict(source_csv_row=r.source_csv_row,council_key=r.council_key,agrn=r.agrn,event_start=r.disaster_start_date,capacity_financial_year=prior.financial_year,capacity_period_end=prior.period_end,lag_days=(r.parsed_start-pd.Timestamp(prior.period_end)).days,publication_before_event_verified=False,**{c:prior[c] for c in capacity}))
save(pd.DataFrame(frows),'candidate_pre_event_capacity_links')
checks={'pre_existing_files_unchanged':len(hashes),'csv_files_profiled':len(schema),'csv_read_failures':sum(x['read_status']!='read' for x in schema),'fiscal_rows':len(fiscal),'fiscal_councils':fiscal.council_key.nunique(),'fiscal_years':fiscal.year_start.nunique(),'existing_e3_rows':len(tables['e3_panel']),'e3_certified_routine_outcomes':int(tables['e3_panel'].primary_outcome_eligible.sum()),'annual_broad_IPPE_examples':len(ann),'quarterly_component_examples':len(q),'quarterly_council_years':1,'complete_quarterly_sequences_certified':0,'certified_ordinary_infrastructure_outcomes':0,'nsw_activation_rows':len(nsw),'nsw_activation_councils':nsw.Location_code.nunique(),'nsw_activation_events':nsw.agrn.nunique(),'nsw_activation_missing_dates':int(nsw.parsed_start.isna().sum()),'nsw_activation_duplicate_council_event':int(nsw.duplicated(['Location_code','agrn']).sum()),'activation_exact_name_joined_rows':int(nsw.council_key.notna().sum()),'activation_exact_name_joined_councils':nsw.council_key.nunique(),'candidate_pre_event_links':len(frows),'models_fitted':0}
(OUT/'validation_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
