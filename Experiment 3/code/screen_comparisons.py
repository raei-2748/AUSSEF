from pathlib import Path
import pandas as pd,numpy as np
R=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists());O=R/'Experiment 3/results'
f=pd.read_csv(R/'Experiment 2/data/fiscal_panel_v2/NSW_Fiscal_Panel_V2_candidate.csv');d=pd.read_csv(R/'Experiment 2/data/disaster_exposure_v2/NSW_Disaster_Exposure_V2_candidate.csv');raw=pd.read_csv(R/'NSW Data Panel.csv')
rows=[];feature_rows=[]
for treated,event in [('eurobodalla',2019),('lismore',2021),('richmondvalley',2021)]:
 records=[]
 for key,g in f.groupby('council_key'):
  pre=g[g.year_start.between(event-3,event-1)].sort_values('year_start');prior=pre[pre.year_start==event-1]
  if len(prior)!=1:continue
  p=prior.iloc[0];m=pre.actual_maintenance_aud.where(~pre.maintenance_conflict)
  pp=d[(d.council_key==key)&d.year_start.between(event-3,event-1)]
  cls=raw[(raw.council_key==key)&(raw.year_start==event-1)].classification
  r={'council_key':key,'classification':cls.iloc[0] if len(cls) else 'unknown','prior_year':event-1,'pre_maintenance_years':int(m.notna().sum()),'maintenance_level_log':np.log1p(p.actual_maintenance_aud) if not p.maintenance_conflict else np.nan,'maintenance_trend_log_per_year':(np.log1p(m.iloc[-1])-np.log1p(m.iloc[0]))/2 if len(m)==3 and m.notna().all() else np.nan,'cash_cover_months':p.cash_cover_months,'operating_ratio_pct':p.operating_ratio_pct,'current_ratio':p.current_ratio,'own_source_pct':p.own_source_pct,'debt_service_cover':p.debt_service_cover if not p.debt_service_cover_requires_review else np.nan,'population_log':np.log1p(p.population),'road_km_log':np.log1p(p.road_km),'prior_burn_log':np.log1p(pp.fesm_burned_ha.sum()) if len(pp)==3 and pp.fesm_burned_ha.notna().all() else np.nan,'prior_declared_years':pp.all_declared.sum() if len(pp)==3 and pp.all_declared.notna().all() else np.nan}
  records.append(r)
 x=pd.DataFrame(records).set_index('council_key');cols=[c for c in x if c not in ['classification','prior_year','pre_maintenance_years']];anchor=x.loc[treated]
 # Feature scales use pre-event observations only; no outcome or current exposure enters distance.
 scale=(x[cols].quantile(.75)-x[cols].quantile(.25)).replace(0,np.nan)
 use=[c for c in cols if pd.notna(anchor[c]) and pd.notna(scale[c])]
 complete=x[use].notna().all(axis=1);distance=((x[use]-anchor[use])/scale[use]).abs().mean(axis=1).where(complete)
 for key,r in x.iterrows():
  if key==treated:continue
  exposure=d[(d.council_key==key)&d.year_start.eq(event)].iloc[0]
  future=d[(d.council_key==key)&d.year_start.between(event,event+2)]
  concurrent=exposure.all_declared==1 or (pd.notna(exposure.fesm_burned_ha) and exposure.fesm_burned_ha>0)
  same=r.classification==anchor.classification
  status='exclude_documented_concurrent_exposure' if concurrent else ('exclude_scale_class_mismatch' if not same else ('exclude_missing_pre_features' if pd.isna(distance[key]) else 'candidate_only_hazard_and_outcome_unverified'))
  row=dict(treated_council_key=treated,event_year=event,candidate_council_key=key,pre_only_distance=distance[key],distance_features=';'.join(use),feature_count=len(use),same_prior_classification=same,screen_status=status,event_declared=exposure.all_declared,event_burned_ha=exposure.fesm_burned_ha,event_fire_status=exposure.fesm_status,event_physical_flood_status=exposure.physical_flood_status,post_window_any_declared=bool(future.all_declared.eq(1).any()),post_window_coverage_years=len(future),region_status='not_in_backbone; classification is not geography',primary_outcome_comparable=False,causal_control_eligible=False)
  for c in x:row['candidate_pre_'+c]=r[c];row['treated_pre_'+c]=anchor[c]
  rows.append(row)
  if key==treated:pass
 out=pd.DataFrame([r for r in rows if r['treated_council_key']==treated]);c=out[out.screen_status.str.startswith('candidate_only')].sort_values('pre_only_distance')
 print(treated,'pre-features',len(use),'remaining',len(c));print(c[['candidate_council_key','pre_only_distance','post_window_any_declared']].head(5).to_string(index=False))
out=pd.DataFrame(rows);out['candidate_rank']=out[out.screen_status.str.startswith('candidate_only')].groupby('treated_council_key').pre_only_distance.rank(method='first');out['selected_for_document_review']=out.candidate_rank.le(2);out.to_csv(O/'comparison_candidates.csv',index=False)
