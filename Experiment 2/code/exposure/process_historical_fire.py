"""Historical wildfire extraction; no models. All original inputs remain read-only."""
from pathlib import Path
import zipfile,json,re,hashlib,shutil,sys
import pandas as pd,numpy as np,geopandas as gpd,rasterio
from rasterio.windows import Window,bounds
from rasterio.features import rasterize
from shapely.geometry import box
R=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists());O=R/'Experiment 2/data/disaster_exposure_v2';S=O/'sources'
def norm(s):return re.sub('[^a-z0-9]','',re.sub(r'\b(the|city|shire|regional|council|municipality)\b','',str(s).lower()))
cs=pd.read_csv(R/'Experiment 2/data/fiscal_panel_v2/council_selection.csv');cs=cs[cs.included].sort_values('council_key');keys=cs.council_key.tolist();look={norm(r.council_name):r.council_key for r in cs.itertuples()};look['nambuccavalley']=look['nambucca']
for yr in [2015,2023]:
 f=S/f'lga_{yr}.zip'
 assert f.exists(),f'Cached ABS boundary source required: {f}'
# A fixed 2023 boundary provides a declared standard geography; 2015 is sensitivity only.
g=gpd.read_file('zip://'+str(S/'lga_2023.zip')).to_crs(3308)
g['council_key']=g.LGA_NAME23.str.replace(r'\s*\([^)]*\)','',regex=True).map(lambda x:look.get(norm(x)))
g=g[g.council_key.notna() & (g.STE_NAME21=='New South Wales')].sort_values('council_key').reset_index(drop=True)
assert set(g.council_key)==set(keys),(set(keys)-set(g.council_key));assert len(g)==103
assert g.geometry.is_valid.all();g['zone_id']=np.arange(1,104);g['area_ha_3308']=g.area/10000
g[['council_key','LGA_CODE23','LGA_NAME23','area_ha_3308']].to_csv(O/'spatial_council_crosswalk.csv',index=False)
g[['council_key','LGA_CODE23','geometry']].to_file(O/'continuing_councils_2023.geojson',driver='GeoJSON')
years=list(map(int,sys.argv[1:])) if len(sys.argv)>1 else list(range(2012,2017))
records=pd.read_csv(O/'historical_fire_zonal_statistics.csv').query('year_start not in @years').to_dict('records') if len(sys.argv)>1 else []
metadata=[a for a in json.loads((O/'raster_audit.json').read_text()) if a['year_start'] not in years] if len(sys.argv)>1 else []
for yr in years:
 f=S/(f'fesm_wildfires_{yr}.zip' if yr<2016 else 'fesm_2016_vector.zip');entry=next(n for n in zipfile.ZipFile(f).namelist() if n.endswith('.img'))
 counts=np.zeros((104,256),dtype='int64');whole=np.zeros(256,dtype='int64')
 with rasterio.open('zip://'+str(f)+'!'+entry) as src:
  assert src.crs.to_epsg()==3308 and src.count==1
  if yr<2016:assert box(*src.bounds).covers(g.geometry.union_all()),'Raster extent excludes council geometry'
  # 2016 is a bounded statewide inventory mosaic; areas outside its extent are not imaged-zero.
  # Zero mapped-burn results must separately agree with explicit workbook zeros.
  step=2048
  for row in range(0,src.height,step):
   for col in range(0,src.width,step):
    win=Window(col,row,min(step,src.width-col),min(step,src.height-row));arr=src.read(1,window=win)
    bc=np.bincount(arr.ravel(),minlength=256);whole+=bc
    if bc[:255].sum()==0:continue
    inds=g.sindex.query(box(*bounds(win,src.transform)),predicate='intersects')
    if len(inds)==0:continue
    labels=rasterize([(g.geometry.iloc[i],int(g.zone_id.iloc[i])) for i in inds],out_shape=arr.shape,transform=src.window_transform(win),fill=0,dtype='uint16')
    valid=(arr!=255)&(labels!=0)
    if valid.any():counts+=np.bincount(labels[valid].astype('int32')*256+arr[valid],minlength=104*256).reshape(104,256)
  pixel_ha=abs(src.transform.a*src.transform.e)/10000
  assert whole[6:255].sum()==0,('unexpected classes',np.where(whole)[0])
  for r in g.itertuples():
   c=counts[r.zone_id];burn=int(c[2:6].sum());extent=int(c[1]);records.append(dict(council_key=r.council_key,year_start=yr,financial_year=f'{yr}-{str(yr+1)[-2:]}',fesm_burned_ha=burn*pixel_ha,fesm_burned_pct_raw=100*burn*pixel_ha/r.area_ha_3308,fesm_high_extreme_ha=int(c[4:6].sum())*pixel_ha,fesm_class0_ha=int(c[0])*pixel_ha,fesm_extent_only_ha=extent*pixel_ha,fesm_status='unknown_unclassified_pixels_present' if extent else ('observed_positive_mapped_burn_within_source_scope' if burn else 'verified_zero_mapped_burn_within_source_scope'),source_file=f.name,source_member=entry,source_pixel_width_m=src.transform.a,source_pixel_height_m=abs(src.transform.e),area_method='Pixel centres within ABS2023 LGA; projected EPSG3308 grid-cell area, approximate hectares',boundary_vintage=2023,sensor='Landsat',minimum_fire_size_ha_exclusive=100,fire_type='wildfire_only',source_catalogue_created_utc=json.loads((S/(f'fesm_metadata_{yr}.json' if yr<2016 else 'fire-extent-and-severity-mapping-fesm-2016-2017.json')).read_text())['result']['metadata_created'],ex_ante_eligible_for_historical_forecast=False,physical_all_fire_zero_verified=False,raster_bbox_council_area_fraction=r.geometry.intersection(box(*src.bounds)).area/r.geometry.area))
  metadata.append(dict(year_start=yr,width=src.width,height=src.height,crs=str(src.crs),nodata=src.nodata,pixel_area_ha=pixel_ha,global_class_counts={str(i):int(v) for i,v in enumerate(whole) if v},selected_council_class_counts={str(i):int(v) for i,v in enumerate(counts.sum(axis=0)) if v}))
 print('Processed',yr,'positive',sum(r['fesm_burned_ha']>0 for r in records if r['year_start']==yr),flush=True)
 pd.DataFrame(records).to_csv(O/'historical_fire_zonal_statistics.csv',index=False);(O/'raster_audit.json').write_text(json.dumps(metadata,indent=2))
# Boundary sensitivity: quantify shape differences without claiming identical historic boundaries.
h=gpd.read_file('zip://'+str(S/'lga_2015.zip')).to_crs(3308)
namecol=next(c for c in h.columns if c.startswith('LGA_NAME'));h['council_key']=h[namecol].str.replace(r'\s*\([^)]*\)','',regex=True).map(lambda x:look.get(norm(x)));h=h[h.council_key.notna() & h.LGA_CODE15.astype(str).str.startswith('1')].set_index('council_key');diff=[]
for r in g.itertuples():
 old=h.loc[r.council_key].geometry if r.council_key in h.index else None
 diff.append(dict(council_key=r.council_key,abs2015_match=old is not None,symmetric_difference_ha=r.geometry.symmetric_difference(old).area/10000 if old is not None else np.nan,relative_symmetric_difference_pct=100*r.geometry.symmetric_difference(old).area/r.geometry.area if old is not None else np.nan,status='Diagnostic geometry difference includes coastline/generalisation; not a legal boundary-change test'))
pd.DataFrame(diff).to_csv(O/'boundary_sensitivity.csv',index=False)
