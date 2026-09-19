"""Build a retrospective exposure extension only. No modelling or imputation.
Run from any directory. Inputs and existing fiscal/model outputs remain read-only.
"""
from pathlib import Path
import re,json,calendar,hashlib,sys
import pandas as pd
import numpy as np
from pypdf import PdfReader
R=Path(__file__).resolve().parents[3];O=R/'outputs/disaster_exposure_v2';S=O/'sources'
def norm(x):
 return re.sub('[^a-z0-9]','',re.sub(r'\b(the|city|of|shire|regional|council|municipality)\b','',str(x).lower()))
cs=pd.read_csv(R/'outputs/fiscal_panel_v2/council_selection.csv');selected=cs[cs.included].copy();keys=set(selected.council_key);assert len(keys)==103
look={norm(r.council_name):r.council_key for r in selected.itertuples()}
look.update({norm(r.council_key):r.council_key for r in selected.itertuples()})
aliases={'portmacquarie':'portmacquariehastings','portmacquairehastings':'portmacquariehastings','moree':'moreeplains','bega':'begavalley','eurobodala':'eurobodalla','sellharbour':'shellharbour','kurringgai':'kuringgai'}
for a,b in aliases.items():assert b in keys;look[a]=b
excluded=set(norm(x) for x in cs.loc[~cs.included,'council_name'])|set(norm(x) for x in cs.loc[~cs.included,'council_key'])
excluded.update(map(norm,['Armidale Dumaresq','Gloucester','Gosford','Greater Taree','Great Lakes','Guyra','Wyong','Boorowa','Cooma-Monaro','Conargo','Cootamundra','Corowa','Deniliquin','Dubbo','Gundagai','Harden','Jerilderie','Murray','Palerang','Queanbeyan','Snowy River','Tumbarumba','Tumut','Urana','Wakool','Wellington','Young','Bombala','Ashfield','Auburn','Bankstown','Canterbury','Holroyd','Hurstville','Kogarah','Leichhardt','Marrickville','Pittwater','Rockdale','Warringah','The Unincorporated Area','Unincorporated Area of NSW','Unincorporated Area','Western Plains','Snowy Valley','Mid Coast']))
urls={'mpes_2012':'https://wayback.archive-it.org/22771/20240423201346/https://www.opengov.nsw.gov.au/download/14743','raa_2013':'https://wayback.archive-it.org/22771/20240423201346/https://www.opengov.nsw.gov.au/download/14785','raa_2014':'https://wayback.archive-it.org/22771/20240423201346/https://www.opengov.nsw.gov.au/download/15213','raa_2015':'https://wayback.archive-it.org/22771/20240423201346/https://www.opengov.nsw.gov.au/download/15718','raa_2016':'https://www.parliament.nsw.gov.au/tp/files/72400/NSW%20Rural%20Assistance%20Authority%20Annual%20Report.PDF'}
events=[]
def add(source,page,ordinal,date,hazard,area,agri=False):
 events.append(dict(record_id=f'{source}_p{page}_r{ordinal:02d}',source_id=source,source_file=f'sources/{source}.pdf',source_url=urls[source],pdf_page=page,reported_event_date=date,reported_hazard=hazard,reported_area=area,agricultural_only=agri,agrn='',declaration_announcement_date='',source_first_publication_date='',publication_date_status='not_verified; annual report date is not event announcement date'))
pages=json.loads((S/'mpes_2012_pages.json').read_text());n=0
for pi in [22,23]:
 t=pages[pi].split('\nGrants')[0];matches=list(re.finditer(r'(?m)^\s*((?:Storms|Severe|Bushfire)[^\n]*?)\s+-\s+([^\n]+)',t))
 for i,m in enumerate(matches):
  end=matches[i+1].start() if i+1<len(matches) else len(t);area=' '.join(t[m.end():end].split()).strip();n+=1;add('mpes_2012',pi+1,n,m.group(2).strip(),m.group(1).strip(),area)
assert n==29,n
hazards=['Severe storms, Flooding & Landslides','Severe weather & tornadoes','Severe weather & storms','Hail Storm and Flooding','Severe Thunderstorms','Severe thunderstorm','Hail and Wind Storm','Storms and Flooding','Storms and Floods','Storms & Floods','Hail & Wind Storm','Severe Weather','Severe Storm','Thunderstorms','Hail Storms','Hail Storm','Snow Storm','Bushfire','Flooding','Floods','Storms']
hazards.sort(key=len,reverse=True)
for y,indices in [(2013,[9,10]),(2014,[13,14]),(2015,[14,15]),(2016,[11,12])]:
 p=json.loads((S/f'raa_{y}_pages.json').read_text());n=0
 for pi in indices:
  t=p[pi];t=re.split(r'(?m)^\s*[*#]\s+Indicates',t)[0]
  matches=list(re.finditer(r'(?m)^\s*(\d[\d/ \-]*?20\d{2})[ \t]+',t))
  for i,m in enumerate(matches):
   end=matches[i+1].start() if i+1<len(matches) else len(t);body=' '.join(t[m.end():end].split()).strip();agri=body.startswith('#');body=body.lstrip('# ').strip()
   h=next((h for h in hazards if body.lower().startswith(h.lower())),None);assert h,(y,pi,body)
   area=body[len(h):].strip();agri=agri or area.startswith(('*','#'));area=area.lstrip('*# ').strip();n+=1
   add(f'raa_{y}',pi+1,n,m.group(1).strip(),body[:len(h)],area,agri)
 # Raw rows checked against the original table layout, including agricultural rows.
 assert n=={2013:25,2014:13,2015:16,2016:28}[y],(y,n)

def dates(s):
 s=s.strip();nums=re.findall(r'\d+',s)
 if '/' in s and re.search(r'\d/\d',s):
  if re.fullmatch(r'\d{1,2}/\d{1,2}/\d{4}',s):d,m,y=map(int,s.split('/'));lo=hi=f'{y:04d}-{m:02d}-{d:02d}';precision='day'
  elif re.fullmatch(r'\d{1,2}-\d{1,2}/\d{1,2}/\d{4}',s):d,e,m,y=map(int,nums);lo=f'{y:04d}-{m:02d}-{d:02d}';hi=f'{y:04d}-{m:02d}-{e:02d}';precision='reported_range'
  elif s=='30/04 - 2/05/2015':lo='2015-04-30';hi='2015-05-02';precision='reported_range'
  else:raise ValueError(s)
 else:
  y=int(nums[-1]);months=[i for i in range(1,13) if calendar.month_name[i].lower() in s.lower()];assert months,s
  if len(nums)==1:lo=f'{y}-{min(months):02d}-01';hi=f'{y}-{max(months):02d}-{calendar.monthrange(y,max(months))[1]}';precision='month_or_month_range_bounds_not_exact_dates'
  else:
   d=int(nums[0]);e=int(nums[1]) if len(nums)>2 else d
   lo=f'{y}-{min(months):02d}-{d:02d}';hi=f'{y}-{max(months):02d}-{e:02d}';precision='open_ended_onset' if s.lower().startswith('from') else ('reported_range' if len(nums)>2 else 'day')
 dt=pd.Timestamp(lo);fy=dt.year-(dt.month<7);assert pd.Timestamp(hi).year-(pd.Timestamp(hi).month<7)==fy,(s,lo,hi)
 return lo,hi,precision,fy
links=[];cross=[]
for e in events:
 lo,hi,precision,fy=dates(e['reported_event_date']);e.update(onset_date_lower_bound=lo,onset_date_upper_bound=lo if precision=='reported_range' else hi,reported_end_date=hi if precision=='reported_range' else '',date_precision=precision,year_start=fy,financial_year=f'{fy}-{str(fy+1)[-2:]}',hazard_group='bushfire' if 'bushfire' in e['reported_hazard'].lower() else ('flood' if 'flood' in e['reported_hazard'].lower() else 'other'),event_id=e['record_id'],include_in_historical_panel=not e['agricultural_only'] and 2012<=fy<=2016,exclusion_reason='agricultural_only' if e['agricultural_only'] else '')
 if e['record_id']=='raa_2013_p10_r01':e['event_id']='mpes_2012_p23_r01';e['include_in_historical_panel']=False;e['exclusion_reason']='corroborating_duplicate_of_MPES_June2013_event'
 if e['agricultural_only']:
  if e['source_id']=='raa_2013' and fy==2014:e['exclusion_reason']+='; source date 21/12/2014 is outside reporting year; not silently corrected'
  continue
 area=e['reported_area']
 if '(' in area:area=area[area.index('(')+1:area.rindex(')')]
 area=re.sub(r'^(South Eastern NSW|Eastern NSW|NSW East Coast Storms and Floods|East Coast Storms and Floods|North Coast)\s*[-–]\s*','',area)
 names=[n.strip() for n in area.split(',') if n.strip()]
 for name in names:
  k=look.get(norm(name));assert k or norm(name) in excluded,('unresolved council',e['record_id'],name,norm(name))
  status='included_fixed_103' if k else 'excluded_not_in_fixed_103';cross.append(dict(source_name=name,normalised_name=norm(name),council_key=k or '',match_status=status,alias_rule='explicit_spelling_or_short_name_alias' if norm(name) in aliases else 'normalise_punctuation_and_council_suffixes'))
  links.append(dict(record_id=e['record_id'],event_id=e['event_id'],council_name_source=name,council_key=k or '',in_fixed_103=bool(k),year_start=fy,hazard_group=e['hazard_group'],include_in_historical_panel=e['include_in_historical_panel'],source_file=e['source_file'],pdf_page=e['pdf_page']))
ev=pd.DataFrame(events);lk=pd.DataFrame(links);cr=pd.DataFrame(cross).drop_duplicates().sort_values('source_name')
assert len(lk[lk.record_id.str.startswith('mpes_2012')])==181
assert not lk[lk.in_fixed_103].duplicated(['record_id','council_key']).any()
ev.to_csv(O/'declaration_event_ledger.csv',index=False);lk.to_csv(O/'declaration_council_links.csv',index=False);cr.to_csv(O/'declaration_name_crosswalk.csv',index=False)
print('Event records',len(ev),'nonagri included',ev.include_in_historical_panel.sum(),'agri',ev.agricultural_only.sum(),flush=True)
print(ev[ev.include_in_historical_panel].groupby(['year_start','hazard_group']).size().to_string(),flush=True)

# Retain mapped-burn values, while avoiding the unsupported claim that class 0 is inside a fire footprint.
z=pd.read_csv(O/'historical_fire_zonal_statistics.csv').rename(columns={'fesm_unburnt_within_mapped_footprint_ha':'fesm_class0_ha','fesm_reserved_class1_ha':'fesm_extent_only_ha'})
assert len(z)==515 and z.fesm_extent_only_ha.eq(0).all()
z.to_csv(O/'historical_fire_zonal_statistics.csv',index=False)
f16=pd.read_excel(S/'fesm_2016_17.xlsx',sheet_name='Tab 2 - LGA',header=1);f16['LGA']=f16['LGA'].ffill();f16['council_key']=f16.LGA.map(lambda a:look.get(norm(a)));f16['source_excel_row']=f16.index+3
cells=f16[f16.council_key.notna()].copy();cells.to_csv(O/'fesm_2016_source_cells.csv',index=False)
tot=cells[cells['Total Area'].notna()];assert len(tot)==103
r16=[]
for r in tot.to_dict('records'):
 sev=cells[(cells.council_key==r['council_key']) & cells['Severity Class'].isin(['low','moderate','high','extreme'])]
 assert abs(sev['Area (Ha)'].sum()-r['Total Area'])<0.04
 r16.append(dict(council_key=r['council_key'],year_start=2016,financial_year='2016-17',fesm_burned_ha=r['Total Area'],fesm_burned_pct_raw=r['Total % of LGA'],fesm_high_extreme_ha=sev.loc[sev['Severity Class'].isin(['high','extreme']),'Area (Ha)'].sum(),fesm_extent_only_ha=np.nan,fesm_status='observed_positive_mapped_burn_within_source_scope' if r['Total Area']>0 else 'verified_zero_mapped_burn_within_source_scope',source_file='fesm_2016_17.xlsx',source_member='Tab 2 - LGA',source_excel_row=r['source_excel_row'],source_pixel_width_m=30,source_pixel_height_m=30,area_method='Published LGA total; source percentage retained including rounded zeros',boundary_vintage='not_stated_in_workbook',sensor='Landsat 8',minimum_fire_size_ha_exclusive=100,fire_type='wildfire_only',source_catalogue_created_utc='',ex_ante_eligible_for_historical_forecast=False,physical_all_fire_zero_verified=False))
# Spatial data determine all five historical years. The 2016 table is retained only for audit.
comparison=z[z.year_start.eq(2016)].merge(pd.DataFrame(r16)[['council_key','fesm_burned_ha','fesm_burned_pct_raw']],on='council_key',suffixes=('_raster','_workbook'),validate='one_to_one')
comparison['raster_to_workbook_ha_ratio']=comparison.fesm_burned_ha_raster/comparison.fesm_burned_ha_workbook.replace(0,np.nan)
comparison['zero_positive_agreement']=comparison.fesm_burned_ha_raster.eq(0)==comparison.fesm_burned_ha_workbook.eq(0)
comparison['decision']='Use raster pixel area; retain reported workbook area only as discrepant source evidence'
assert comparison.zero_positive_agreement.all()
comparison.to_csv(O/'fesm_2016_workbook_reconciliation.csv',index=False)
fire=z.copy()
fire.loc[fire.year_start.eq(2016),'sensor']='Landsat 8'

assert len(fire)==515
base=pd.read_csv(R/'outputs/fiscal_panel_v2/NSW_Fiscal_Panel_V2_candidate.csv')[['council_key','council_name','year_start','financial_year']]
assert len(base)==1339
hist=base[base.year_start<2017].merge(fire.drop(columns='financial_year'),on=['council_key','year_start'],validate='one_to_one')
hist=hist.rename(columns={'source_file':'fesm_source_file','source_member':'fesm_source_member','source_excel_row':'fesm_excel_total_row','minimum_fire_size_ha_exclusive':'fesm_min_fire_size_ha_exclusive','sensor':'fesm_sensor','boundary_vintage':'fesm_boundary_vintage','area_method':'fesm_area_method'})
hist['historical_extension']=True;hist['exposure_provenance']='new_primary_source_historical_reconstruction';hist['physical_flood_status']='unknown_no_complete_inundation_inventory';hist['flood_inundated_ha']=np.nan;hist['verified_zero_all_disaster_exposure']=False
hist['declaration_inventory_status']=np.where(hist.year_start.eq(2012),'complete_list_as_published_MPES_annual_report','partial_reconstruction_RAA_annual_reports')
hist['declaration_regime']='NDRRA; agricultural-only assistance excluded'
hist['declaration_asof_forecast_status']='unknown_announcement_and_revision_dates_not_verified';hist['fesm_asof_forecast_status']='ineligible_retrospective_product_postdates_historical_targets'
hist['declaration_source_files']=hist.year_start.map({2012:'mpes_2012.pdf',2013:'raa_2013.pdf;raa_2014.pdf',2014:'raa_2014.pdf;raa_2015.pdf',2015:'raa_2015.pdf;raa_2016.pdf',2016:'raa_2016.pdf;raa_2017.pdf_checked_no_prior_FY_rows'})
used=lk[lk.in_fixed_103 & lk.include_in_historical_panel].drop_duplicates(['event_id','council_key'])
for hazard in ['bushfire','flood','all']:
 sub=used if hazard=='all' else used[used.hazard_group.eq(hazard)]
 group=sub.groupby(['council_key','year_start']).event_id.agg(list).to_dict()
 ids=[group.get((r.council_key,r.year_start),[]) for r in hist.itertuples()];cnt=np.array([len(x) for x in ids]);complete=hist.year_start.eq(2012).to_numpy()
 hist[f'{hazard}_declared_event_count']=np.where(complete,cnt,np.nan)
 hist[f'{hazard}_observed_event_count']=np.where(complete|(cnt>0),cnt,np.nan)
 hist[f'{hazard}_count_is_lower_bound']=~complete
 hist[f'{hazard}_declared']=np.where(cnt>0,1,np.where(complete,0,np.nan))
 hist[f'{hazard}_event_ids']=[';'.join(x) for x in ids]
 hist[f'{hazard}_agrns']=''
 hist[f'{hazard}_declaration_status']=np.where(complete,np.where(cnt>0,'observed_positive_in_complete_published_list','no_listed_event_in_complete_published_list_not_physical_zero'),np.where(cnt>0,'observed_positive_partial_inventory_count_lower_bound','unknown_incomplete_inventory_no_positive_record'))
# Frozen original exposure fields for later years are copied, not recalculated.
v1=pd.read_csv(R/'NSW Data Panel.csv');v1=v1[v1.council_key.isin(keys)].copy();excols=['council_key','year_start','financial_year']+v1.columns[v1.columns.get_loc('fesm_burned_ha'):].tolist()
v1[excols].to_csv(O/'original_exposure_snapshot_2017_2024.csv',index=False)
later=base[base.year_start>=2017].merge(v1[excols].drop(columns='financial_year'),on=['council_key','year_start'],validate='one_to_one');assert len(later)==824
later['historical_extension']=False;later['exposure_provenance']='frozen_NSW_Data_Panel_v1_exposure';later['fesm_sensor']='Sentinel 2 (original mapping scope varies by year)';later['fesm_boundary_vintage']='original_workbook_vintage_not_reaudited';later['fesm_area_method']='Original published LGA summary, unchanged';later['fesm_source_member']='Original source sheet; see V1 documentation';later['declaration_inventory_status']='original_inventory_status_retained_not_recertified';later['declaration_regime']='NDRRA/DRFA transition; inherited V1';later['declaration_asof_forecast_status']='not_reaudited_in_this_extension';later['fesm_asof_forecast_status']='not_reaudited_in_this_extension';later['declaration_source_files']='NSW Data Panel.csv; underlying V1 evidence';later['flood_inundated_ha']=np.nan
for hazard in ['bushfire','flood','all']:
 c=pd.to_numeric(later[f'{hazard}_declared_event_count'],errors='coerce');later[f'{hazard}_observed_event_count']=c;later[f'{hazard}_count_is_lower_bound']=False;later[f'{hazard}_declared']=np.where(c.notna(),(c>0).astype(int),np.nan);later[f'{hazard}_event_ids']=later[f'{hazard}_agrns'].fillna('').map(lambda x:';'.join('AGRN:'+a.strip() for a in str(x).split(';') if a.strip()))
# Keep only documented fields in the combined exposure table; original extras remain in the snapshot.
common=['council_key','council_name','year_start','financial_year','historical_extension','exposure_provenance','fesm_burned_ha','fesm_burned_pct_raw','fesm_extent_only_ha','fesm_min_fire_size_ha_exclusive','fesm_status','fesm_sensor','fesm_boundary_vintage','fesm_area_method','fesm_source_file','fesm_source_member','fesm_excel_total_row','fesm_asof_forecast_status','declaration_inventory_status','declaration_regime','declaration_source_files','declaration_asof_forecast_status','physical_flood_status','flood_inundated_ha','verified_zero_all_disaster_exposure']
for h in ['bushfire','flood','all']:common += [f'{h}_{c}' for c in ['declared','declared_event_count','observed_event_count','count_is_lower_bound','declaration_status','event_ids','agrns']]
panel=pd.concat([hist.reindex(columns=common),later.reindex(columns=common)],ignore_index=True).sort_values(['council_key','year_start']);assert len(panel)==1339 and not panel.duplicated(['council_key','year_start']).any();assert panel.groupby('year_start').size().eq(103).all()
panel.to_csv(O/'NSW_Disaster_Exposure_V2_candidate.csv',index=False);panel[panel.historical_extension].to_csv(O/'historical_extension_2012_2016.csv',index=False)
coverage=[]
for year,g in panel.groupby('year_start'):
 for col in ['fesm_burned_ha','bushfire_declared','flood_declared','all_declared','bushfire_declared_event_count','flood_declared_event_count','flood_inundated_ha']:
  vals=pd.to_numeric(g[col],errors='coerce');coverage.append(dict(year_start=year,financial_year=g.financial_year.iloc[0],variable=col,councils=103,positive=int((vals>0).sum()),zero=int((vals==0).sum()),unknown=int(vals.isna().sum()),provenance=g.exposure_provenance.iloc[0]))
coverage=pd.DataFrame(coverage);coverage.to_csv(O/'coverage_by_year.csv',index=False)
covc=[]
for key,g in panel.groupby('council_key'):
 d=dict(council_key=key,council_name=g.council_name.iloc[0])
 for col in ['fesm_burned_ha','bushfire_declared','flood_declared']:
  h=g[g.historical_extension];d[col+'_historical_observed_years']=int(h[col].notna().sum());d[col+'_historical_positive_years']=int((pd.to_numeric(h[col],errors='coerce')>0).sum())
 covc.append(d)
pd.DataFrame(covc).to_csv(O/'coverage_by_council.csv',index=False)
# Every reconstructed cell has separate event-time and real-time availability fields.
av=[]
for r in panel.itertuples():
 for variable in ['fesm_burned_ha','bushfire_declared','flood_declared']:
  isfire=variable=='fesm_burned_ha';historical=r.year_start<2017
  status=r.fesm_asof_forecast_status if isfire else r.declaration_asof_forecast_status
  evidence='FESM catalogue created February 2025; exact first historical public release not independently established' if isfire and r.year_start<2016 else ('FESM report May 2022, PDF p2 and 2016-17 workbook' if isfire and r.year_start==2016 else ('Annual reports recovered retrospectively; no event-level announcement date verified' if historical else 'V1 source timing not recertified'))
  av.append(dict(council_key=r.council_key,exposure_year_start=r.year_start,target_year_start=r.year_start+1,target_financial_year=f'{r.year_start+1}-{str(r.year_start+2)[-2:]}',forecast_cutoff=f'{r.year_start+1}-07-01',variable=variable,value=getattr(r,variable),reference_period_end=f'{r.year_start+1}-06-30',availability_status=status,ex_ante_certified=False,evidence=evidence,decision='exclude_from_claim_of_real_time_forecast_until_asof_evidence_verified'))
pd.DataFrame(av).to_csv(O/'temporal_availability_audit.csv',index=False)
recon=[]
for y in range(2012,2017):
 s=ev[ev.include_in_historical_panel & ev.year_start.eq(y)]
 recon.append(dict(year_start=y,bushfire_events_observed=int(s.hazard_group.eq('bushfire').sum()),flood_labelled_events_observed=int(s.hazard_group.eq('flood').sum()),other_events_observed=int(s.hazard_group.eq('other').sum()),source_list_completeness='published_complete_MPES_list_only' if y==2012 else 'not_established; RAA list is assistance-oriented',absent_council_cells='scoped_zero' if y==2012 else 'unknown',announcement_dates_verified=0))
pd.DataFrame(recon).to_csv(O/'declaration_inventory_audit.csv',index=False)
qa={'panel_rows':len(panel),'councils':len(keys),'historical_rows_added':515,'years':sorted(panel.year_start.unique().tolist()),'historical_mapped_fire_cells':int(hist.fesm_burned_ha.notna().sum()),'mpes_2012_event_rows':29,'mpes_2012_council_event_links':181,'event_records':len(ev),'agricultural_records_excluded':int(ev.agricultural_only.sum()),'later_exposure_rows_copied':824,'models_fitted':0,'duplicate_panel_keys':0,'historical_fire_pixels_class1':0,'fesm_2016_zero_positive_agreement_all103':True,'flood_area_cells_known':0,'ex_ante_certified_historical_cells':0}
changed=[]
for file,sha in json.loads((O/'frozen_before.json').read_text()).items():
 if not (R/file).exists() or hashlib.sha256((R/file).read_bytes()).hexdigest()!=sha:changed.append(file)
qa['preexisting_files_checked']=len(json.loads((O/'frozen_before.json').read_text()));qa['preexisting_files_changed']=changed;assert not changed,changed
(O/'validation_checks.json').write_text(json.dumps(qa,indent=2));print(json.dumps(qa,indent=2),flush=True)
