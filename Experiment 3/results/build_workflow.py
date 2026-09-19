"""Experiment 3: measurement audit only. Existing experiments are read-only.
Run this file to rebuild the candidate panel, tables and figures from cached evidence.
No ML, causal estimation, outcome imputation or grant-subtraction is performed.
"""
from pathlib import Path
import json,hashlib,re,sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists())
OUT=ROOT/'Experiment 3/results';S=OUT/'sources';FIG=OUT/'figures';FIG.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((OUT/'frozen_existing_sha256.json').read_text())
def check_frozen():
 changes=[p for p,h in frozen.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
 assert not changes,changes
check_frozen()
fiscal_path=ROOT/'Experiment 2/data/fiscal_panel_v2/NSW_Fiscal_Panel_V2_candidate.csv'
exposure_path=ROOT/'Experiment 2/data/disaster_exposure_v2/NSW_Disaster_Exposure_V2_candidate.csv'
f=pd.read_csv(fiscal_path);d=pd.read_csv(exposure_path)
assert not f.duplicated(['council_key','year_start']).any() and not d.duplicated(['council_key','year_start']).any()
assert set(f.council_key)==set(d.council_key) and f.council_key.nunique()==103
# The comparison routine calculates pre-event distances and screens concurrent exposure.
exec(compile((OUT/'screen_comparisons.py').read_text(),str(OUT/'screen_comparisons.py'),'exec'))
comparisons=pd.read_csv(OUT/'comparison_candidates.csv')
selected=comparisons[comparisons.selected_for_document_review].copy()
evidence=pd.DataFrame(json.loads((OUT/'curated_evidence.json').read_text()))
provenance=pd.DataFrame(json.loads((OUT/'source_provenance.json').read_text()))
provenance['publication_date_verified']='unknown unless an evidence row supplies a document/adoption date'
provenance['http_last_modified_is_publication_date']=False
provenance['review_channel']='cached official PDF or HTML'
provenance.loc[provenance.source_id.isin(['euro_ar2020','euro_roadplan2019','wagga_performance2022']),'review_channel']='official PDF text indexed by web; direct download 403; no visual PDF verification'
provenance.loc[provenance.source_id.eq('lismore_draft2022'),'review_channel']='HTML download landing page only; draft PDF not recovered'
provenance.to_csv(OUT/'source_provenance.csv',index=False)
lookup=provenance.set_index('source_id')
for c in ['url','local_file','sha256']:
 evidence['source_'+c]=evidence.source_id.map(lookup[c])
evidence.to_csv(OUT/'documentary_evidence.csv',index=False)
routine=evidence[evidence.accounting_category.str.contains('routine|maintenance|aggregate')].copy()
routine.to_csv(OUT/'routine_maintenance_evidence.csv',index=False)
reconstruction=evidence[~evidence.index.isin(routine.index)].copy()
reconstruction.to_csv(OUT/'reconstruction_expenditure_evidence.csv',index=False)
# Record all searched PDF pages and distinguish lexical screening from close verification.
search=[]
for p in S.glob('*_pages.json'):
 sid=p.name.removesuffix('_pages.json');pages=json.loads(p.read_text())
 for i,text in enumerate(pages):
  terms=[w for w in ['maintenance','budget','reconstruction','restoration','deferred','postponed','advance'] if w in text.lower()]
  if terms:search.append(dict(source_id=sid,pdf_page=i+1,terms=';'.join(terms),review='keyword screen; only curated evidence rows are close-reviewed transcriptions'))
pd.DataFrame(search).to_csv(OUT/'document_search_audit.csv',index=False)
# Annual panel uses unique council/year keys; repeated use of Wagga as a candidate is not extra data.
events=[('eurobodalla',2019,'black_summer_2019_20'),('lismore',2021,'northern_rivers_floods_2022'),('richmondvalley',2021,'northern_rivers_floods_2022')]
assignments={k:(y,g,'treated') for k,y,g in events}
for r in selected.itertuples():
 assignments[r.candidate_council_key]=(r.event_year,'black_summer_2019_20' if r.event_year==2019 else 'northern_rivers_floods_2022','candidate_comparison')
keep=['council_key','council_name','year_start','financial_year','period_start','period_end','reporting_months','source_file','source_sheet','source_excel_row','actual_maintenance_aud','required_maintenance_aud','maintenance_ratio_pct','maintenance_conflict','maintenance_basis']
exposure_cols=['council_key','year_start','fesm_burned_ha','fesm_status','fesm_source_file','fesm_asof_forecast_status','bushfire_declared','flood_declared','all_declared','bushfire_declaration_status','flood_declaration_status','all_agrns','declaration_inventory_status','declaration_source_files','physical_flood_status','verified_zero_all_disaster_exposure']
prior_cols=['cash_cover_months','operating_ratio_pct','current_ratio','own_source_pct','debt_service_cover','debt_service_cover_requires_review','population','road_km','actual_maintenance_aud','maintenance_ratio_pct']
parts=[]
for key,(year,group,role) in assignments.items():
 x=f[f.council_key.eq(key)&f.year_start.between(year-3,year+2)][keep].copy()
 x=x.merge(d[exposure_cols],on=['council_key','year_start'],validate='one_to_one')
 x['index_event_year']=year;x['event_group']=group;x['role']=role;x['relative_year']=x.year_start-year
 prior=f[f.council_key.eq(key)&f.year_start.eq(year-1)].iloc[0]
 for c in prior_cols:x['pre_'+c]=prior[c]
 if prior.debt_service_cover_requires_review:x['pre_debt_service_cover']=np.nan
 x['pre_fiscal_year']=year-1;x['pre_information_vintage']='prior-period economic values; historical publication availability not certified'
 x['pre_fiscal_source_file']=prior.source_file;x['pre_fiscal_source_sheet']=prior.source_sheet;x['pre_fiscal_source_excel_row']=prior.source_excel_row
 x['low_pre_cash_cover']=np.nan if pd.isna(prior.cash_cover_months) else int(prior.cash_cover_months<3)
 x['weak_pre_operating_position']=np.nan if pd.isna(prior.operating_ratio_pct) else int(prior.operating_ratio_pct<0)
 x['planned_routine_maintenance_aud']=np.nan;x['actual_routine_maintenance_aud']=np.nan
 x['planned_routine_status']='missing_no_complete_certified_scope';x['actual_routine_status']='missing_no_separated_matching_actual'
 x['disaster_reconstruction_expenditure_aud']=np.nan;x['disaster_reconstruction_status']='unknown_no_pure_actual_reconstruction_total'
 x['maintenance_deviation']=np.nan;x['primary_outcome_eligible']=False
 x['primary_exclusion_reason']='No same-year, same-scope pre-disaster routine plan and separated actual pair; component candidates retained in evidence ledger'
 x['secondary_only']=True;x['causal_eligible']=False
 x['routine_separation_status']='unknown';x['price_basis']='nominal AUD; aggregate trend is a diagnostic, not a real expenditure effect'
 x['evidence_ids']=[';'.join(evidence.loc[evidence.council_key.eq(key)&evidence.year_start.eq(yr),'evidence_id']) for yr in x.year_start]
 parts.append(x)
panel=pd.concat(parts,ignore_index=True).sort_values(['council_key','year_start'])
assert not panel.duplicated(['council_key','year_start']).any()
panel.to_csv(OUT/'experiment3_panel.csv',index=False)
# Value-level provenance for the inherited measurements and fixed pre-event characteristics.
inventory=json.loads((ROOT/'Experiment 2/data/fiscal_panel_v2/source_inventory.json').read_text())
urls={Path(r.get('file','')).name:r.get('url','') for r in inventory}
units={'cash_cover_months':'months','operating_ratio_pct':'percentage points','current_ratio':'multiple','own_source_pct':'percentage points','debt_service_cover':'multiple','population':'persons','road_km':'km','actual_maintenance_aud':'AUD','required_maintenance_aud':'AUD','maintenance_ratio_pct':'percentage points','fesm_burned_ha':'hectares'}
value_rows=[]
for r in panel.itertuples():
 for field in ['actual_maintenance_aud','required_maintenance_aud','maintenance_ratio_pct']+['pre_'+c for c in prior_cols if c!='debt_service_cover_requires_review']+['fesm_burned_ha','bushfire_declared','flood_declared']:
  val=getattr(r,field);base=field.removeprefix('pre_');prior=field.startswith('pre_');hazard=base in ['fesm_burned_ha','bushfire_declared','flood_declared']
  sf=r.pre_fiscal_source_file if prior else r.source_file;sy=r.pre_fiscal_year if prior else r.year_start
  value_rows.append(dict(council_key=r.council_key,year_start=r.year_start,field=field,value=val,value_status='unknown' if hazard and pd.isna(val) else ('missing' if pd.isna(val) else (('verified_zero_mapped_scope' if str(r.fesm_status).startswith('verified') else 'recorded_zero_scope_unverified') if base=='fesm_burned_ha' and val==0 else ('recorded_no_listed_event' if hazard and val==0 else 'observed'))),unit=units.get(base,'binary listed declaration'),source_document=str(exposure_path if hazard else fiscal_path),source_url='' if hazard else urls.get(Path(sf).name,''),source_year=sy,source_table='V2 CSV; council_key/year_start join; column '+base,original_file=(r.fesm_source_file if base=='fesm_burned_ha' else r.declaration_source_files) if hazard else sf,original_sheet='' if hazard else r.pre_fiscal_source_sheet if prior else r.source_sheet,original_excel_row='' if hazard else r.pre_fiscal_source_excel_row if prior else r.source_excel_row,raw_value_in_v2=val,raw_value_stage='harmonised V2 value, not a new raw workbook transcription',scope_note='Mapped/declaration scope only; no physical flood zero certified' if hazard else ('council-estimated aggregate; not routine budget' if 'maintenance' in field else 'prior economic state; no post-disaster controls')))
pd.DataFrame(value_rows).to_csv(OUT/'backbone_value_provenance.csv',index=False)
# Explicit missingness register: do not fabricate routine zeroes for years not documented.
missing=[]
for r in panel.itertuples():
 for field in ['planned_routine_maintenance_aud','actual_routine_maintenance_aud','disaster_reconstruction_expenditure_aud','maintenance_deviation']:
  missing.append(dict(council_key=r.council_key,year_start=r.year_start,field=field,value=np.nan,status='unknown' if field=='disaster_reconstruction_expenditure_aud' else 'missing',reason=r.primary_exclusion_reason if field!='disaster_reconstruction_expenditure_aud' else r.disaster_reconstruction_status,evidence_ids=r.evidence_ids,review_status='targeted document review' if r.evidence_ids else 'backbone only; no direct year-specific documentary measurement recovered'))
pd.DataFrame(missing).to_csv(OUT/'measurement_missingness.csv',index=False)
# Reconstruct three pre-years of AGGREGATE maintenance only. No routine outcome is inferred.
trends=[]
for r in selected.itertuples():
 t=panel[panel.council_key.eq(r.treated_council_key)&panel.relative_year.lt(0)].set_index('relative_year')
 c=panel[panel.council_key.eq(r.candidate_council_key)&panel.relative_year.lt(0)].set_index('relative_year')
 for lag in [-3,-2,-1]:
  a=t.loc[lag];b=c.loc[lag]
  valid=not a.maintenance_conflict and not b.maintenance_conflict and pd.notna(a.actual_maintenance_aud) and pd.notna(b.actual_maintenance_aud)
  ai=100*a.actual_maintenance_aud/t.loc[-3].actual_maintenance_aud if valid else np.nan
  bi=100*b.actual_maintenance_aud/c.loc[-3].actual_maintenance_aud if valid else np.nan
  trends.append(dict(treated_council_key=r.treated_council_key,candidate_council_key=r.candidate_council_key,index_event_year=r.event_year,year_start=int(a.year_start),relative_year=lag,treated_aggregate_actual_aud=a.actual_maintenance_aud,candidate_aggregate_actual_aud=b.actual_maintenance_aud,treated_adequacy_pct=a.maintenance_ratio_pct,candidate_adequacy_pct=b.maintenance_ratio_pct,treated_index=ai,candidate_index=bi,index_gap=ai-bi,treated_prior_declared=a.all_declared,candidate_prior_declared=b.all_declared,aggregate_quality_pass=valid,routine_pretrend_available=False,parallel_trends_established=False,verdict='NO-GO: only aggregate trajectories; routine definitions unavailable; no statistical pretrend test'))
pretrend=pd.DataFrame(trends);pretrend.to_csv(OUT/'pretrend_audit.csv',index=False)
# Funding clocks: a receipt window is not an exact first payment date.
funding=pd.DataFrame([
 dict(council_key='lismore',disaster='Northern Rivers floods February/March 2022',announcement_date='2024-03-29',agreement_effective_date='',first_payment_date='',receipt_date_lower='2023-07-01',receipt_date_upper='2024-06-30',receipt_amount_aud=86000000,receipt_precision='financial year; not certified first payment',project='TfNSW road disaster works portfolio; individual project IDs not recovered',source_evidence_id=';'.join(evidence.loc[evidence.field.eq('advance_funding_received_in_year'),'evidence_id']),exact_timing_project_link_verified=False,analysis_eligible=False),
 *[dict(council_key=k,disaster=g,announcement_date='',agreement_effective_date='',first_payment_date='',receipt_date_lower='',receipt_date_upper='',receipt_amount_aud=np.nan,receipt_precision='unknown; no inferred zero',project='unknown',source_evidence_id='',exact_timing_project_link_verified=False,analysis_eligible=False) for k,g in [('richmondvalley','Northern Rivers floods February/March 2022'),('eurobodalla','Black Summer and subsequent floods')]]
]);funding.to_csv(OUT/'advance_funding_audit.csv',index=False)
coverage=panel.groupby('role').agg(councils=('council_key','nunique'),council_years=('year_start','size'),primary_pairs=('primary_outcome_eligible','sum'),observed_aggregate_maintenance=('actual_maintenance_aud','count')).reset_index();coverage.to_csv(OUT/'coverage_summary.csv',index=False)
# Figures are honest about unavailable outcomes; no zero-height bars stand in for unknown actuals.
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(12,6))
plot=evidence[(evidence.field.eq('planned_routine_component_candidate'))&evidence.value.gt(0)]
import textwrap
labels=[textwrap.fill(f"{'Richmond Valley' if r.council_key=='richmondvalley' else r.council_key.title()}: {r.asset_scope}", width=42) for r in plot.itertuples()]
y=np.arange(len(plot));ax.barh(y,plot.value/1e6,color='#276c8e',label='Reported plan component')
ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlabel('Budget component (AUD million, nominal)');ax.set_title('2021–22 maintenance plan components\nMatching actual expenditure unavailable', fontsize=12)
for i,v in enumerate(plot.value/1e6):ax.text(v+.04,i,'actual: missing',va='center',fontsize=9)
ax.set_xlim(0,3.4);ax.grid(axis='x',alpha=.15)
fig.text(.01,.01,'Different asset scopes: do not add these lines or treat them as complete council routine budgets.',fontsize=9)
fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(FIG/'planned_vs_actual_routine.png',dpi=150);plt.close(fig)
fig,axes=plt.subplots(1,3,figsize=(13.5,4.5),sharey=True)
for ax,(key,year,_) in zip(axes,events):
 p=pretrend[pretrend.treated_council_key.eq(key)];a=p.drop_duplicates('relative_year').sort_values('relative_year')
 ax.plot(a.relative_year,a.treated_index,'o-',color='#9e382c',lw=2,label=key)
 for candidate,g in p.groupby('candidate_council_key'):ax.plot(g.relative_year,g.candidate_index,'s--',label=candidate)
 ax.set(title=f'{key}: event FY {year}–{str(year+1)[-2:]}',xlabel='Years before disaster');ax.set_xticks([-3,-2,-1]);ax.grid(alpha=.2);ax.legend(fontsize=9)
axes[0].set_ylabel('Aggregate actual maintenance (first pre-year = 100)')
fig.suptitle('Pre-trend diagnostic: aggregate maintenance, NOT routine maintenance',fontsize=13)
fig.tight_layout();fig.savefig(FIG/'treated_comparison_pretrends.png',dpi=150);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,3.5));ax.axis('off')
ax.set_title('Post-disaster routine-maintenance deviation: not estimable',pad=18)
for j,(key,year,_) in enumerate(events):
 ax.text(.02,.78-j*.25,f'{key} ({year}–{str(year+1)[-2:]})',weight='bold',transform=ax.transAxes)
 ax.text(.39,.78-j*.25,'No certified planned/actual pair at event year or +1/+2',transform=ax.transAxes)
ax.text(.02,.02,'Blank deviations are missing measurements, not zero effects. No causal or fiscal-interaction model fitted.',transform=ax.transAxes,fontsize=10)
fig.tight_layout();fig.savefig(FIG/'post_disaster_deviation_status.png',dpi=150);plt.close(fig)
# Do not create statistical_results.csv: the user requested it only if modelling is defensible.
checks=dict(existing_files_checked=len(frozen),existing_files_changed=[],fiscal_backbone_councils=103,panel_rows=len(panel),panel_councils=panel.council_key.nunique(),treated_councils=3,independent_selected_event_groups=2,comparison_screen_rows=len(comparisons),selected_comparison_links=len(selected),selected_unique_comparisons=selected.candidate_council_key.nunique(),certified_primary_outcomes=int(panel.primary_outcome_eligible.sum()),causal_control_rows=int(panel.causal_eligible.sum()),documentary_observations=len(evidence),models_fitted=0,source_panels_unchanged=True,unknown_not_filled_with_zero=True,source_access_attempts=len(provenance))
check_frozen();(OUT/'validation_checks.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
