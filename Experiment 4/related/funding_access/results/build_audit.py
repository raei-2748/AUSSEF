"""Descriptive feasibility audit. No predictive or causal models; Experiments 1–3 are read-only."""
from pathlib import Path
import json, hashlib, re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'NSW Data Panel.csv').exists())
OUT=ROOT/'Experiment 4/related/funding_access/results'; FIG=OUT/'figures'; S=OUT/'sources'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(x,name):x.to_csv(OUT/(name+'.csv'),index=False)
def check_frozen():
 frozen=json.loads((OUT/'frozen_existing_sha256.json').read_text())
 assert all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in frozen.items()),'Existing files changed'
 return len(frozen)
frozen_count=check_frozen()
ip=json.loads((OUT/'input_provenance.json').read_text());assert sha(Path(ip['original']))==ip['sha256']==sha(Path(ip['copy']))
d=pd.read_csv(ip['copy'],dtype={'Location_code':str,'agrn':str});d.insert(0,'source_csv_row',np.arange(len(d))+2)
d['onset']=pd.to_datetime(d.disaster_start_date,errors='raise');binary=['cat_A','cat_B','cat_C','cat_D','AGDRP','DRA']
assert all(d[c].isin([0,1]).all() for c in binary)
assert not d.duplicated(['agrn','STATE','Location_Type','Location_code']).any()
lga=d[d.Location_Type.eq('LGA')].copy()
g=lga.groupby('agrn',sort=False).agg(n_lga_rows=('cat_C','size'),cat_C_positive=('cat_C','sum'),cat_D_positive=('cat_D','sum'),state=('STATE','first'),event_name=('event_name','first'),disaster_start_date=('disaster_start_date','first'),hazard_type=('hazard_type','first')).reset_index()
for c in ['C','D']:
 g['cat_'+c+'_zero']=g.n_lga_rows-g['cat_'+c+'_positive'];g['cat_'+c+'_proportion']=g['cat_'+c+'_positive']/g.n_lga_rows
 g['cat_'+c+'_pattern']=np.select([g['cat_'+c+'_positive'].eq(0),g['cat_'+c+'_positive'].eq(g.n_lga_rows)],['no-'+c,'all-'+c],default='mixed-'+c)
g['descriptive_event_scope']=np.where(g.cat_C_pattern.eq('all-C'),'All listed LGA rows flagged; does not prove one decision','Measure-specific decision scope unresolved')
g=g.sort_values(['disaster_start_date','agrn']);cevents=set(g.loc[g.cat_C_positive.gt(0),'agrn'])
lga['recorded_any_DRFA']=lga[['cat_A','cat_B','cat_C','cat_D']].any(axis=1)
save(lga.loc[lga.agrn.isin(set(g.loc[g.cat_C_pattern.eq('mixed-C'),'agrn'])),['source_csv_row','agrn','Location_Name','Location_code','STATE','cat_A','cat_B','cat_C','cat_D','highest_drfa_category_group','AGDRP','DRA','recorded_any_DRFA']],'mixed_event_case_review')
profile={'exact_duplicate_rows':int(d.drop(columns=['source_csv_row']).duplicated().sum()),'duplicate_LGA_event_keys':int(lga.duplicated(['agrn','STATE','Location_code']).sum()),'missing_hazard_rows':int(d.hazard_type.isna().sum()),'earliest_onset':d.disaster_start_date.min(),'latest_onset':d.disaster_start_date.max(),'LGA_rows_without_any_DRFA_flag':int((~lga.recorded_any_DRFA).sum()),'SAL_C_or_D_flags':int(d.loc[d.Location_Type.eq('SAL'),['cat_C','cat_D']].sum().sum()),'group_values':d.highest_drfa_category_group.value_counts().to_dict(),'events_with_conflicting_onset':int(d.groupby('agrn').disaster_start_date.nunique().gt(1).sum()),'events_with_multiple_states':int(d.groupby('agrn').STATE.nunique().gt(1).sum())}
(OUT/'backbone_checks.json').write_text(json.dumps(profile,indent=2))
candidates=lga[lga.agrn.isin(cevents)].copy();candidates['council_entity_candidate']=~candidates.Location_Name.str.contains('Unincorporated',case=False)
candidates['natural_disaster_candidate']=~candidates.event_name.str.contains('Terrorist',case=False)
# Preserve raw values and characterize actual fields; dictionary separates policy meaning from unverified encoding.
dictionary=json.loads((OUT/'field_definitions.json').read_text())
audit=[]
for c in d.columns[1:-1]:
 vals=d[c];entry=dictionary[c]
 audit.append(dict(field=c,dtype=str(vals.dtype),rows=len(d),missing=int(vals.isna().sum()),distinct=int(vals.nunique()),observed_values='; '.join(map(str,sorted(vals.dropna().unique()))) if vals.nunique()<=15 else '',**entry))
save(pd.DataFrame(audit),'activation_backbone_audit')
prov=pd.DataFrame(json.loads((OUT/'source_provenance.json').read_text()));prov['local_access_status']=np.where(prov.http_status.eq(200),'retrieved','failed_http')
for r in prov.itertuples():
 if pd.notna(getattr(r,'local_file',None)):
  assert sha(OUT/r.local_file)==r.sha256
  if r.local_file.endswith('.html'):
   t=(OUT/r.local_file).read_text(errors='replace')
   if 'Just a moment...' in t or '<title>File Not Found' in t:prov.loc[prov.source_id.eq(r.source_id),'local_access_status']='blocked_or_missing_content'
prov['review_channel']='cached official document'
prov.loc[prov.source_id.isin(['raa_declarations','sa1209','vic1166','tas1144','vic1037_business']),'review_channel']='official web indexed text reviewed; local copy blocked/missing'
save(prov,'source_provenance');urlmap=prov.set_index('source_id').url.to_dict()
measures=pd.DataFrame(json.loads((OUT/'curated_measures.json').read_text()));measures.agrn=measures.agrn.astype(str);measures['source_url']=measures.source_id.map(urlmap)
assert measures.source_url.notna().all();assert set(measures.agrn)==cevents
measures['verification_status']=np.where(measures.category_verified,'CATEGORY_VERIFIED_SCOPE_PARTIAL','EVENT_PROGRAM_FOUND_CATEGORY_UNRESOLVED')
measures.loc[measures.source_id.str.startswith('1046_'),'verification_status']='CATEGORY_AND_NAMED_GEOGRAPHIC_SCOPE_VERIFIED'
export=measures.copy();export.verified_geographic_locations=export.verified_geographic_locations.apply(lambda x:';'.join(x));save(export,'category_c_measure_audit')
counts=measures[measures.category.eq('C')].groupby('agrn').size();g['distinct_C_measures_recovered_minimum']=g.agrn.map(counts).astype('Int64');g['C_measure_inventory_complete']=False
g['independent_funding_decision_count']=pd.NA;g['usable_positive_negative_contrasts']=0;save(g,'event_category_summary')
variation=pd.concat([g[['agrn','state','event_name','n_lga_rows','cat_'+c+'_positive','cat_'+c+'_zero','cat_'+c+'_proportion','cat_'+c+'_pattern']].rename(columns={'cat_'+c+'_positive':'positive_rows','cat_'+c+'_zero':'zero_rows','cat_'+c+'_proportion':'positive_proportion','cat_'+c+'_pattern':'pattern'}).assign(category=c) for c in ['C','D']],ignore_index=True);save(variation,'category_variation_audit')
# Named geography is eligibility for a program's availability, NOT actual recipient payment.
case_rows=[]
for m in measures.itertuples():
 if m.category!='C' or not m.verified_geographic_locations:continue
 for r in candidates[candidates.agrn.eq(m.agrn)].itertuples():
  inside=r.Location_Name in m.verified_geographic_locations
  case_rows.append(dict(agrn=r.agrn,Location_code=r.Location_code,Location_Name=r.Location_Name,measure_id=m.measure_id,measure_name=m.measure_name,raw_cat_C=r.cat_C,status='VERIFIED_POSITIVE' if inside else 'OUTSIDE_MEASURE_SCOPE',status_definition='Verified named geographic availability; no payment or selection-risk-set claim' if inside else 'Not named in this published measure scope; NOT a verified eligible negative',verified_eligible_negative=False,receipt_verified=False,source_id=m.source_id,source_url=m.source_url,category_source='activation_1046 PDF p6' if m.agrn=='1046' else m.page_or_section,snapshot_conflict=inside and r.cat_C==0))
cases=pd.DataFrame(case_rows);save(cases,'positive_negative_case_audit')
verified_keys=set(zip(cases.loc[cases.status.eq('VERIFIED_POSITIVE'),'agrn'],cases.loc[cases.status.eq('VERIFIED_POSITIVE'),'Location_code']))
conflict_keys=set(zip(cases.loc[cases.snapshot_conflict,'agrn'],cases.loc[cases.snapshot_conflict,'Location_code']))
risk=lga.copy();risk['candidate_C_event']=risk.agrn.isin(cevents);risk['status']='UNKNOWN_ELIGIBILITY'
risk['reason']='No measure-specific eligibility/consideration record; raw zero is not a denial'
risk.loc[risk.cat_C.eq(1),['status','reason']]=['AMBIGUOUS_RECORD','C flag recorded, but exact measure and common risk set not certified']
for i,r in risk.iterrows():
 k=(r.agrn,r.Location_code)
 if k in verified_keys:risk.loc[i,['status','reason']]=['VERIFIED_POSITIVE','At least one named Category C geographic scope verified; not a payment']
 if k in conflict_keys:risk.loc[i,['status','reason']]=['AMBIGUOUS_RECORD','Raw C=0 conflicts with official named Category C tourism eligibility; retain raw flag']
 if 'Unincorporated' in r.Location_Name:risk.loc[i,['status','reason']]=['NOT_LGA_DECISION','Statistical unincorporated area is not an ordinary council administrative-capacity unit']
 if 'Terrorist' in r.event_name:risk.loc[i,['status','reason']]=['NOT_COMPARABLE','Terrorist attack excluded from proposed natural-disaster study']
risk['verified_eligible_negative']=False;risk['model_ready']=False;risk['funding_receipt']=np.nan
noab=~risk[['cat_A','cat_B']].any(axis=1)&risk.cat_C.eq(0)&risk.candidate_C_event
risk.loc[noab&risk.status.eq('UNKNOWN_ELIGIBILITY'),'reason']='No A/B activation recorded; C prerequisite not established. AGDRP/DRA-only inclusion is not a valid C-eligible denominator.'
risk['measure_audit_ids']=risk.agrn.map(measures.groupby('agrn').measure_id.apply(';'.join)).fillna('')
risk['source_dataset']=str(Path(ip['copy']).relative_to(ROOT));risk['source_url']=urlmap['official_csv'];save(risk.drop(columns='onset'),'candidate_risk_set')
valid=[]
for r in g[g.agrn.isin(cevents)].itertuples():
 a=risk[risk.agrn.eq(r.agrn)];m=measures[measures.agrn.eq(r.agrn)];p=cases[cases.agrn.eq(r.agrn)]
 valid.append(dict(agrn=r.agrn,state=r.state,event_name=r.event_name,raw_C_positive=r.cat_C_positive,raw_C_zero=r.cat_C_zero,raw_pattern=r.cat_C_pattern,verified_geographic_positive_locations=p.loc[p.status.eq('VERIFIED_POSITIVE'),'Location_code'].nunique(),verified_eligible_negatives=0,conflicting_zero_rows=p.loc[p.snapshot_conflict,'Location_code'].nunique(),measure_reviews=len(m),verified_C_measures=int(m.category.eq('C').sum()),complete_measure_inventory=False,complete_need_bundle=False,decision_count_certified=False,usable_contrasts=0,verdict='NO-GO',source_urls=';'.join(m.source_url.unique()),reason='No documented eligible-but-unselected denominator; category flag aggregates heterogeneous programs' if r.agrn not in ['1209','1240'] else 'Unit outside ordinary council natural-disaster study'))
validation=pd.DataFrame(valid);save(validation,'risk_set_validation')
# Exact NSW names/keys only, with small explicit alias map. No fuzzy or cross-state matching.
fpath=ROOT/'Experiment 2/data/fiscal_panel_v2/NSW_Fiscal_Panel_V2_candidate.csv';f=pd.read_csv(fpath);f['measurement_end']=pd.to_datetime(f.period_end)
norm=lambda x:re.sub('[^a-z0-9]','',str(x).lower())
name_to_key={norm(r.council_name):r.council_key for r in f.drop_duplicates('council_key').itertuples()};name_to_key.update({k:k for k in f.council_key.unique()});aliases={'campbelltownnsw':'campbelltown'};name_to_key.update(aliases)
cols=['cash_cover_months','current_ratio','operating_ratio_pct','own_source_pct','grants_pct','debt_service_cover','debt_service_ratio_pct','population','road_km']
units=['months','multiple','percent','percent','percent','multiple','percent','persons','km'];cap=[];cross=[]
for r in candidates.itertuples():
 key=name_to_key.get(norm(r.Location_Name)) if r.STATE=='New South Wales' else None
 prior=f[f.council_key.eq(key)&f.measurement_end.lt(r.onset)].sort_values('measurement_end') if key else f.iloc[:0]
 row=prior.iloc[-1] if len(prior) else None
 cross.append(dict(agrn=r.agrn,Location_code=r.Location_code,Location_Name=r.Location_Name,STATE=r.STATE,council_key=key,join_rule='exact normalized name/key; NSW only' if key else 'unmatched; outside frozen 103 councils',boundary_vintage_verified=False))
 common=dict(agrn=r.agrn,Location_code=r.Location_code,Location_Name=r.Location_Name,STATE=r.STATE,council_key=key,disaster_start_date=r.disaster_start_date)
 for col,unit in zip(cols,units):
  val=row[col] if row is not None else np.nan;review=bool(row.debt_service_cover_requires_review) if row is not None and col=='debt_service_cover' else False
  cap.append(dict(**common,feature=col,original_value=val,usable_value=val if not review else np.nan,unit=unit,source_year=row.financial_year if row is not None else '',measurement_date=row.period_end if row is not None else '',publication_date='',lag_days=(r.onset-row.measurement_end).days if row is not None else np.nan,missingness_status='OUTSIDE_FISCAL_PANEL' if key is None else 'NO_PRE_ONSET_PERIOD' if row is None else 'QUALITY_FLAG_EXCLUDED' if review else 'MISSING' if pd.isna(val) else 'OBSERVED_PRE_ONSET',source_dataset=str(fpath.relative_to(ROOT)),source_file=row.source_file if row is not None else '',source_sheet=row.source_sheet if row is not None else '',source_excel_row=row.source_excel_row if row is not None else '',retrospective_eligible=bool(row is not None and pd.notna(val) and not review),strict_ex_ante_certified=False,leakage_note='Prior full financial year only; current retrieved vintage may be revised; first publication not certified',definition_status=row.cash_definition_status if row is not None and col=='cash_cover_months' else row.operating_definition_regime if row is not None and col=='operating_ratio_pct' else 'see frozen V2 dictionary'))
 # Do not mistake a final snapshot's historical flags for what was known before onset.
 prior=d[(d.STATE==r.STATE)&(d.Location_Type=='LGA')&(d.Location_code==r.Location_code)&(d.onset<r.onset)]
 for feature,val in [('prior_recorded_activation_events',prior.loc[prior[['cat_A','cat_B','cat_C','cat_D']].any(axis=1),'agrn'].nunique()),('prior_recorded_disaster_events',prior.agrn.nunique()),('prior_recorded_C_events',prior.loc[prior.cat_C.eq(1),'agrn'].nunique()),('prior_recorded_D_events',prior.loc[prior.cat_D.eq(1),'agrn'].nunique())]:
  cap.append(dict(**common,feature=feature,original_value=val,usable_value=np.nan,unit='events',source_year='snapshot 2026-08-11',measurement_date=prior.disaster_start_date.max() if len(prior) else '',publication_date='2026-08-11',lag_days=np.nan,missingness_status='LOWER_BOUND_BACKFILLED_HISTORY',source_dataset=str(Path(ip['copy']).relative_to(ROOT)),source_file=Path(ip['copy']).name,source_sheet='',source_excel_row='',retrospective_eligible=False,strict_ex_ante_certified=False,leakage_note='Earlier onset is not earlier C/D decision; decision dates missing; left-truncated history. Count is descriptive only; 0 means none recorded, not no prior experience.',definition_status='not a pre-onset certified predictor'))
 for feature in ['staffing_FTE','remoteness','prior_funding_receipt_experience']:
  cap.append(dict(**common,feature=feature,original_value=np.nan,usable_value=np.nan,unit='not recovered',source_year='',measurement_date='',publication_date='',lag_days=np.nan,missingness_status='NOT_IN_BACKBONE',source_dataset='',source_file='',source_sheet='',source_excel_row='',retrospective_eligible=False,strict_ex_ante_certified=False,leakage_note='Requires separately dated source; activation is not receipt',definition_status='unavailable'))
capacity=pd.DataFrame(cap);save(capacity,'capacity_linkage_audit');save(pd.DataFrame(cross),'council_crosswalk_audit')
assert pd.to_datetime(capacity.loc[capacity.retrospective_eligible,'measurement_date']).lt(pd.to_datetime(capacity.loc[capacity.retrospective_eligible,'disaster_start_date'])).all()
# Availability investigation, not a fabricated merged need panel. Metadata availability is not usable observation coverage.
needs=json.loads((OUT/'need_catalogue.json').read_text());needrows=[]
for e in g[g.agrn.isin(cevents)].itertuples():
 for n in needs:
  v=dict(n);sid=v.pop('source_id');v['source_url']=urlmap.get(sid,'');v.update(agrn=e.agrn,event_name=e.event_name,disaster_start_date=e.disaster_start_date,source_id=sid,observed_values_joined=0,eligible_LGA_coverage_fraction=np.nan,missingness='NOT_EXTRACTED_OR_NOT_CERTIFIED',pre_decision_coverage_verified=False)
  if e.agrn=='1240':v['event_applicability']='NOT_COMPARABLE: terrorist attack outside natural hazard design'
  elif v['variable']=='fire_extent_severity':v['event_applicability']='Hazard relevance requires event fire record; NSW FESM is NSW only; other states need their own product'
  elif v['variable']=='cyclone_wind':v['event_applicability']='Cyclone components only; no claim that track alone measures local wind damage'
  else:v['event_applicability']='Candidate source; event extraction, coverage and cutoff certification still required'
  if e.agrn=='950' and v['variable']=='houses_damaged_destroyed':v.update(source_id='wa950',source_url=urlmap['wa950'],missingness='EVENT_AGGREGATE_ONLY: 86 properties destroyed; no certified pre-decision LGA vector',availability_date='2020–21 annual report; exact first release unknown',spatial_unit='Swan + Mundaring event aggregate')
  needrows.append(v)
need=pd.DataFrame(needrows);save(need,'need_data_availability')
temporal=capacity[['agrn','Location_code','Location_Name','feature','measurement_date','publication_date','disaster_start_date','retrospective_eligible','strict_ex_ante_certified','leakage_note']].copy();temporal['funding_decision_date']='';temporal['block']='capacity'
nt=need[['agrn','variable','measurement_date','availability_date','disaster_start_date','timing_risk']].rename(columns={'variable':'feature','availability_date':'publication_date','timing_risk':'leakage_note'});nt['retrospective_eligible']=False;nt['strict_ex_ante_certified']=False;nt['funding_decision_date']='';nt['block']='need'
mt=measures[['agrn','measure_name','document_date','first_approval_date']].rename(columns={'measure_name':'feature','document_date':'publication_date','first_approval_date':'funding_decision_date'});mt['block']='outcome_measure';mt['measurement_date']='';mt['disaster_start_date']=mt.agrn.map(g.set_index('agrn').disaster_start_date);mt['retrospective_eligible']=False;mt['strict_ex_ante_certified']=False;mt['leakage_note']='Document/version date is not first approval or payment. Outcome metadata, not predictor.'
save(pd.concat([temporal,nt,mt],ignore_index=True),'temporal_leakage_audit')
policy=pd.DataFrame(json.loads((OUT/'policy_eras.json').read_text()));policy['source_url']=policy.source_id.map(urlmap);save(policy,'policy_era_audit')
# Descriptive plots only.
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
def finish(fig,name):fig.tight_layout();fig.savefig(FIG/(name+'.png'),dpi=145,bbox_inches='tight');plt.close(fig)
p=g[g.cat_C_positive.gt(0)|g.cat_D_positive.gt(0)].copy();y=np.arange(len(p));fig,ax=plt.subplots(figsize=(11,12));ax.barh(y-.18,p.cat_C_proportion,height=.35,label='C',color='#246c87');ax.barh(y+.18,p.cat_D_proportion,height=.35,label='D',color='#d68a42');ax.set_yticks(y,p.agrn);ax.invert_yaxis();ax.set(xlabel='Fraction of listed LGA rows flagged (not funding receipt)',ylabel='AGRN',title='C/D prevalence in events with any C or D flag');ax.legend();finish(fig,'01_event_prevalence')
p=validation.copy();y=np.arange(len(p));fig,ax=plt.subplots(figsize=(11,10));ax.barh(y,p.raw_C_positive,label='CSV C-positive rows',color='#bacbd3');ax.scatter(p.verified_geographic_positive_locations,y,label='Named C availability verified',color='#246c87');ax.scatter(np.zeros(len(p)),y,label='Verified eligible negatives: zero',color='#ae4a37',marker='x');ax.set_yticks(y,p.agrn);ax.invert_yaxis();ax.set(xlabel='Locations (different evidence stages; not independent decisions)',ylabel='AGRN',title='Recorded positives versus verified measure scope and negatives');ax.legend(loc='lower right');finish(fig,'02_positives_negatives')
fig,ax=plt.subplots(figsize=(8,4));tab=pd.crosstab(variation.category,variation.pattern);plot=pd.DataFrame({c:[int((g['cat_'+c+'_pattern']==k+'-'+c).sum()) for k in ['no','all','mixed']] for c in ['C','D']},index=['No positive','All listed LGAs positive','Mixed']);plot.plot.bar(ax=ax,color=['#246c87','#d68a42'],rot=0);ax.set(title='Within-event variation across all 378 AGRNs',ylabel='Events');finish(fig,'03_within_event_variation')
stages=pd.DataFrame({'stage':['All CSV rows','LGA rows','Rows in C-positive events','Natural disaster / council candidates','Model-ready LGA–measure observations'], 'count':[len(d),len(lga),len(candidates),int((candidates.council_entity_candidate&candidates.natural_disaster_candidate).sum()),0]});save(stages,'eligibility_filter_counts');fig,ax=plt.subplots(figsize=(10,4));ax.barh(stages.stage[::-1],stages['count'][::-1],color='#246c87');ax.set(title='Feasibility funnel: no model-ready observations',xlabel='Count');
for i,v in enumerate(stages['count'][::-1]):ax.text(v+20,i,str(v),va='center')
finish(fig,'04_eligibility_filters')
fig,ax=plt.subplots(figsize=(9,4));tmp=g.assign(year=g.disaster_start_date.str[:4]).groupby('year').agg(all_events=('agrn','size'),C_events=('cat_C_positive',lambda s:int(s.gt(0).sum())),D_events=('cat_D_positive',lambda s:int(s.gt(0).sum())));tmp.plot(ax=ax,marker='o');ax.set(title='Event history: no C/D-positive records before 2021',ylabel='AGRN events',xlabel='Disaster onset year');finish(fig,'05_event_timing')
coverage=capacity.groupby('feature').agg(candidate_rows=('agrn','size'),observed_retrospective=('retrospective_eligible','sum'),strict_certified=('strict_ex_ante_certified','sum')).reset_index();save(coverage,'capacity_coverage');fig,axes=plt.subplots(1,2,figsize=(13,6));c=coverage[coverage.feature.isin(cols)];axes[0].barh(c.feature,100*c.observed_retrospective/c.candidate_rows,color='#246c87');axes[0].set(xlim=(0,100),xlabel='% of all C-event LGA candidates',title='Capacity: pre-onset numeric values linked');axes[1].barh(['Independent need bundles','Capacity publication dates','Eligible negative cases'],[0,0,0]);axes[1].set(xlim=(0,100),xlabel='% certified',title='Certification gaps remain');axes[1].text(5,1,'0 certified; unknown is not unavailable',fontsize=10);finish(fig,'06_measurement_coverage')
checks=dict(frozen_files_checked=check_frozen(),existing_files_changed=[],input_sha256=ip['sha256'],publisher_download_identical=sha(S/'official_csv.csv')==ip['sha256'],rows=len(d),lga_rows=len(lga),sal_rows=int(d.Location_Type.eq('SAL').sum()),events=len(g),C_rows=int(d.cat_C.sum()),D_rows=int(d.cat_D.sum()),C_events=len(cevents),mixed_C_events=int(g.cat_C_pattern.eq('mixed-C').sum()),D_events=int(g.cat_D_positive.gt(0).sum()),mixed_D_events=int(g.cat_D_pattern.eq('mixed-D').sum()),candidate_C_event_rows=len(candidates),measure_review_rows=len(measures),verified_named_scope_case_rows=int(cases.status.eq('VERIFIED_POSITIVE').sum()),conflicting_C_zero_locations=len(conflict_keys),verified_eligible_negatives=0,usable_contrasts=0,capacity_matched_candidate_rows=int(pd.DataFrame(cross).council_key.notna().sum()),capacity_retrospective_values=int(capacity.retrospective_eligible.sum()),strict_ex_ante_complete_bundles=0,models_fitted=0)
(OUT/'validation_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
