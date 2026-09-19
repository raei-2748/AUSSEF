"""Document the exposure extension and verify invariants; does not fit models."""
from pathlib import Path
import pandas as pd,numpy as np,json,hashlib,re,datetime,importlib.metadata
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists());O=R/'Experiment 2/data/disaster_exposure_v2';S=O/'sources'
p=pd.read_csv(O/'NSW_Disaster_Exposure_V2_candidate.csv');h=p[p.historical_extension];cov=pd.read_csv(O/'coverage_by_year.csv');ev=pd.read_csv(O/'declaration_event_ledger.csv');links=pd.read_csv(O/'declaration_council_links.csv')
cs=pd.read_csv(R/'Experiment 2/data/fiscal_panel_v2/council_selection.csv');cs[cs.included].to_csv(O/'council_subset_103.csv',index=False)
# A complete dictionary for the candidate panel, with no undocumented output columns.
def row(c,definition,unit,missing='Blank means unknown or not supplied; never replace with zero.',scope='All years; see provenance and status columns.'):
 return dict(variable=c,definition=definition,unit=unit,missingness_rule=missing,scope=scope)
d=[row('council_key','Stable identifier inherited without changing membership from fiscal V2 council_selection.csv','identifier','Never missing'),row('council_name','Display label from fiscal V2; never used as join key','text','Never missing'),row('year_start','First calendar year of July-June financial year','year','Never missing'),row('financial_year','July-June reference year; not publication year','YYYY-YY','Never missing'),row('historical_extension','True for newly reconstructed 2012-13 through 2016-17','boolean','Never missing'),row('exposure_provenance','New historical reconstruction or frozen original panel','category','Never missing'),row('fesm_burned_ha','Mapped low+moderate+high+extreme wildfire area (classes 2-5); hectares calculated from actual raster pixel dimensions for historical extension','hectares','Zero is no mapped burn in the stated inventory, not no fire','Historical: wildfire events >100 ha; fixed ABS2023 boundaries; later original values unchanged'),row('fesm_burned_pct_raw','Historical: 100 x mapped hectares / council polygon hectares; later: original raw workbook field, including inequality strings','percent of council area','Zero may be a rounded source percentage in original years; inspect hectares','Historical recalculated in EPSG3308; later raw reported percentage not revalidated'),row('fesm_extent_only_ha','Mapped class 1/extent-only area, separate from classified burn area','hectares','Historical zero only after pixel-class audit; original missing retained'),row('fesm_min_fire_size_ha_exclusive','Inventory minimum event size: strict greater-than threshold, not a council-area cutoff','hectares'),row('fesm_status','Distinguishes positive mapped burn, source-scoped mapped zero, and unavailable values','category'),row('fesm_sensor','Satellite sensor regime; 2012-17 Landsat, 2017-18 onward Sentinel 2','text'),row('fesm_boundary_vintage','Boundary geometry vintage used for spatial summary','year or status'),row('fesm_area_method','How mapped area was measured','text'),row('fesm_source_file','Cached spatial source for historical years; unchanged original source name for later years','filename'),row('fesm_source_member','Raster inside ZIP, or original table reference','archive member / sheet'),row('fesm_excel_total_row','Original workbook total-row locator where table used; blank for raster-derived historical measures','1-based spreadsheet row','Blank is not applicable for raster-derived values'),row('fesm_asof_forecast_status','Whether retrieved product vintage supports an historical real-time forecast','category'),row('declaration_inventory_status','Completeness of the source inventory, separate from observed event presence','category'),row('declaration_regime','Assistance/declaration system; agricultural-only records excluded from historical primary measures','text'),row('declaration_source_files','Evidence used to reconstruct each reference year','filenames'),row('declaration_asof_forecast_status','Availability of announcement/revision dates before forecast cutoff','category'),row('physical_flood_status','Physical flood-area coverage; declaration records are not inundation measurements','category'),row('flood_inundated_ha','Reserved for verified physical inundated area; no values populated','hectares','All blank = unknown, never zero'),row('verified_zero_all_disaster_exposure','Whether absence of all disaster exposure has been verified','boolean','False throughout; false does not imply positive exposure')]
for hazard in ['bushfire','flood','all']:
 scope='Bushfire-labelled events' if hazard=='bushfire' else ('Events explicitly labelled flood/flooding, including compound storm-flood events; storm-only not automatically flood' if hazard=='flood' else 'All non-agricultural-only natural-disaster event records, including other hazards')
 d.extend([row(f'{hazard}_declared','1 = at least one listed council event; 0 = no listed event in scoped complete source; blank = unknown','0 / 1 / blank','Unlisted councils in partial inventories are blank, not zero',scope),row(f'{hazard}_declared_event_count','Event count only where source inventory supports a scoped total; distinct source entries, not independent physical disasters or necessarily unique AGRNs','count','Entirely blank for 2013-14 to 2016-17 because full counts are uncertified',scope),row(f'{hazard}_observed_event_count','Count of distinct recovered event entries naming council; lower bound when inventory incomplete','count','Blank if no positive evidence in an incomplete inventory; zero only in scoped complete source',scope),row(f'{hazard}_count_is_lower_bound','True means observed count must not be treated as a complete annual event count','boolean','True even for unknown cells in partial years; false in later years only denotes inherited V1 count semantics, not fresh certification',scope),row(f'{hazard}_declaration_status','Explicit evidence/status accompanying declaration measures','category','Never infer physical absence from administrative absence',scope),row(f'{hazard}_event_ids','Internal source-row identifiers for reconstructed records; AGRN-prefixed original identifiers later','semicolon-delimited identifiers','Blank for no recovered event, including unknown cells; consult status',scope),row(f'{hazard}_agrns','Actual Australian Government Reference Numbers only','identifiers','Historical reports omit AGRNs; all historical cells blank; internal IDs are not invented AGRNs',scope)])
df=pd.DataFrame(d);assert set(df.variable)==set(p.columns);df.to_csv(O/'variable_dictionary.csv',index=False)
# Source register: core accepted inputs and unused alternatives are clearly distinguished.
manifest=[];urlmap={}
for f in S.glob('*.json'):
 if 'manifest' not in f.name and 'attempt' not in f.name:continue
 try:x=json.loads(f.read_text());xs=x if isinstance(x,list) else [x]
 except Exception:continue
 for a in xs:
  if isinstance(a,dict) and a.get('url'):
   filename=a.get('file','');filename=Path(filename).name if filename else ''
   if filename:urlmap[filename]=a['url']
   manifest.append(dict(attempt_manifest=f.name,url=a['url'],file=filename,status=a.get('status',''),error=a.get('error','')))
pd.DataFrame(manifest).to_csv(O/'source_access_attempts.csv',index=False)
for y in range(2012,2016):
 x=json.loads((S/f'fesm_metadata_{y}.json').read_text())['result'];urlmap[f'fesm_metadata_{y}.json']='https://datasets.seed.nsw.gov.au/api/3/action/package_show?id='+x['name'];urlmap[f'fesm_wildfires_{y}.zip']=next(r['url'] for r in x['resources'] if r['name'].endswith('Wildfires'))
for source,u in ev[['source_id','source_url']].drop_duplicates().itertuples(index=False,name=None):urlmap[source+'.pdf']=u
urlmap['raa_2016.pdf']=json.loads((S/'raa_2016_redirect_manifest.json').read_text())['url'];urlmap['raa_2017.pdf']=json.loads((S/'raa_2017_attempt.json').read_text())['url']
urlmap['lga_2023.zip']='https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/LGA_2023_AUST_GDA94.zip'
urlmap['lga_2015.zip']='https://www.ausstats.abs.gov.au/ausstats/subscriber.nsf/0/54F1418AFBEDD91CCA257E8400143B95/$File/1270055003_lga_2015_aust_shape.zip'
core={**{f'fesm_wildfires_{y}.zip':'accepted historical mapped wildfire raster' for y in range(2012,2016)},'fesm_2016_vector.zip':'accepted historical mapped wildfire raster package (cache filename does not describe format)','fesm_2016_17.xlsx':'audit only; area-percent inconsistency; not used for candidate area','mpes_2012.pdf':'accepted 2012-13 complete published declaration list, PDF pp23-24','raa_2013.pdf':'accepted partial declaration inventory; agricultural-only rows excluded; PDF pp10-11','raa_2014.pdf':'accepted partial declaration inventory; PDF pp14-15','raa_2015.pdf':'accepted partial declaration inventory; PDF pp15-16','raa_2016.pdf':'accepted partial declaration inventory; PDF pp12-13','raa_2017.pdf':'checked for prior-year carryovers; none found in tables PDF pp13-14','lga_2023.zip':'accepted fixed spatial denominator and council polygons','lga_2015.zip':'boundary sensitivity only','fesm_v3_factsheet.pdf':'class-code reference, PDF p2; generic sensor statement overridden by year-specific metadata','fesm_2016_report.pdf':'sensor and retrospective publication evidence, May2022','nema_drfa.csv':'not used to backfill: actual records start2017 despite catalogue description'}
register=[]
for name,role in core.items():
 f=S/name;assert f.exists();register.append(dict(file='sources/'+name,source_url=urlmap.get(name,''),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size,role=role,acquisition_date_utc='2026-09-18',publication_date='2022-05 (month precision)' if name=='fesm_2016_report.pdf' else '',publication_status='See metadata and temporal availability audit; acquisition is not publication'))
assert all(r['source_url'] for r in register),[r for r in register if not r['source_url']]
pd.DataFrame(register).to_csv(O/'source_register.csv',index=False)
cache=[]
for f in sorted(S.iterdir()):
 if f.is_file():cache.append(dict(file='sources/'+f.name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),source_url=urlmap.get(f.name,''),role=core.get(f.name,'supporting metadata, search evidence or unsuccessful retrieval; not automatically valid input')))
pd.DataFrame(cache).to_csv(O/'source_cache_inventory.csv',index=False)
# Measurement disagreement is reported, never resolved by overwriting either measure.
rows=[]
for r in h.itertuples():
 if pd.notna(r.bushfire_declared):rows.append(dict(council_key=r.council_key,year_start=r.year_start,mapped_fire_positive=r.fesm_burned_ha>0,bushfire_declared=r.bushfire_declared,mapped_zero_but_declared=(r.fesm_burned_ha==0 and r.bushfire_declared==1),mapped_positive_but_no_listed_declaration=(r.fesm_burned_ha>0 and r.bushfire_declared==0),interpretation='Different scopes: mapped vegetation burn versus assistance eligibility; neither overwrites the other'))
pd.DataFrame(rows).to_csv(O/'fire_declaration_scope_comparison.csv',index=False)
# Numeric/unit flags for the new spatial years.
area=pd.read_csv(O/'spatial_council_crosswalk.csv');histarea=h.merge(area,on='council_key',validate='many_to_one');assert ((histarea.fesm_burned_ha>=0)&(histarea.fesm_burned_ha<=histarea.area_ha_3308*1.00001)).all()
# Exact preservation of all original exposure values, including quality flags, in the snapshot.
v1=pd.read_csv(R/'NSW Data Panel.csv');snap=pd.read_csv(O/'original_exposure_snapshot_2017_2024.csv');expected=v1[v1.council_key.isin(p.council_key.unique())][snap.columns].reset_index(drop=True);pd.testing.assert_frame_equal(expected,snap,check_dtype=False)
qa=json.loads((O/'validation_checks.json').read_text());qa.update(original_exposure_snapshot_cellwise_equal=True,all_historical_burned_areas_within_council_area=True,all_46_panel_columns_documented=len(df)==len(p.columns),historical_fire_positive=int((h.fesm_burned_ha>0).sum()),historical_fire_scoped_zero=int((h.fesm_burned_ha==0).sum()),historical_bushfire_binary_known=int(h.bushfire_declared.notna().sum()),historical_flood_binary_known=int(h.flood_declared.notna().sum()))
qa['preexisting_files_changed']=[str(f) for f,sha in json.loads((O/'frozen_before.json').read_text()).items() if hashlib.sha256((R/f).read_bytes()).hexdigest()!=sha];assert not qa['preexisting_files_changed'];(O/'validation_checks.json').write_text(json.dumps(qa,indent=2))
# A compact coverage chart distinguishes known positive, scoped zero, and unknown.
fig,axes=plt.subplots(1,3,figsize=(12,4.8),sharey=True);colors=['#bd5b36','#477e75','#dce0e5'];labels=['Positive evidence','Scoped zero','Unknown']
for ax,var,title in zip(axes,['fesm_burned_ha','bushfire_declared','flood_declared'],['Mapped wildfire area','Bushfire declaration','Flood-labelled declaration']):
 data=cov[(cov.variable==var)&(cov.year_start<2017)].sort_values('year_start');left=np.zeros(len(data))
 for field,color,label in zip(['positive','zero','unknown'],colors,labels):
  bars=ax.barh(data.financial_year,data[field],left=left,color=color,label=label)
  for j,v in enumerate(data[field]):
   if v>=12:ax.text(left[j]+v/2,j,str(v),ha='center',va='center',fontsize=10,color='white' if field!='unknown' else '#344054')
  left+=data[field].to_numpy()
 ax.set_title(title,fontsize=11);ax.set_xlim(0,103);ax.set_xlabel('Councils (fixed subset = 103)');ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0)
axes[0].invert_yaxis();fig.suptitle('Historical exposure extension: evidence coverage',fontsize=16,x=.06,ha='left');fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.5,.02));fig.text(.06,.005,'Mapped zero means no mapped burn in the stated >100 ha wildfire inventory. Unknown is never coded as zero.',fontsize=9,color='#475467');fig.tight_layout(rect=(0,.13,1,.91));fig.savefig(O/'historical_coverage.png',dpi=180);plt.close(fig)
# Reproducibility manifest for cached-source reconstruction.
versions={}
for pkg in ['pandas','numpy','geopandas','shapely','rasterio','pypdf','matplotlib','pyproj','openpyxl']:
 try:versions[pkg]=importlib.metadata.version(pkg)
 except importlib.metadata.PackageNotFoundError:versions[pkg]='rasterio 1.5.1 installed in temporary runtime; see requirements.txt' if pkg=='rasterio' else 'not detected'
(O/'runtime_versions.json').write_text(json.dumps(versions,indent=2))
print(json.dumps(qa,indent=2))
