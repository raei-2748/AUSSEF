"""Build a candidate fiscal panel and audit eligibility. No models or imputation.
Run from AUSSEF with pandas, numpy, openpyxl, xlrd, matplotlib installed.
All writes are confined to `Experiment 2/data/fiscal_panel_v2`; earlier data remain frozen.
"""
from pathlib import Path
import json,re,hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists())
OUT=ROOT/'Experiment 2/data/fiscal_panel_v2'
OLD=ROOT/'Experiment 1/audit/operating_ratio_audit'
S=OLD/'sources'
FROZEN=json.loads((OUT/'frozen_before.json').read_text())
def freeze_check():
    changed=[f for f,h in FROZEN.items() if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h]
    assert not changed,changed
freeze_check()
original=pd.read_csv(ROOT/'NSW Data Panel.csv')
manifest=json.loads((OLD/'source_downloads.json').read_text())
source_map={Path(x['file']).name:x for x in manifest if x['status']=='retrieved'}
def norm(s):
    s=re.sub(r'\b(the|council|of|city|shire|municipality|municipal|regional)\b','',str(s).lower())
    return re.sub('[^a-z0-9]','',s)
aliases={'thehills':'hills','nambuccavalley':'nambucca'}
name_keys={aliases.get(norm(r.council),norm(r.council)):r.council_key for r in original.drop_duplicates('council_key').itertuples()}
def key_for(s):return name_keys.get(aliases.get(norm(s),norm(s)))
def colname(n):
    s='';n+=1
    while n:n,k=divmod(n-1,26);s=chr(65+k)+s
    return s
# Explicit source years, including the original panel's 2024–25 row with uncollected ratios.
config={2012:('time-series-data-1994-2015.xls','2012-13 DATA',0),2013:('time-series-data-1994-2015.xls','2013-14 DATA',1),2014:('time-series-data-2014-15_1.xls','2014-15 Time Series Data',2),2015:('time-series-data-2015-16.xls','2015-16 DATA',2),2016:('time-series-data-2016-17.xls','2016-17 DATA',2)}
for y in range(2017,2025):
    r=original[original.year_start==y].iloc[0];f=r.fiscal_source_file
    if f not in source_map:
        options=[n for n in source_map if f'{y}-{y+1}' in n or f'{y}-{str(y+1)[-2:]}' in n];assert len(options)==1;f=options[0]
    config[y]=(f,r.fiscal_source_sheet,2)
books={};cross=[]
for y,(fn,sh,hr) in config.items():
    b=pd.read_excel(S/fn,sheet_name=sh,header=None);headers=[re.sub(r'\s+',' ',str(v)).strip() for v in b.iloc[hr]]
    gc=next(i for i,v in enumerate(headers) if re.fullmatch('(OLG |DLG )?Group',v,re.I))
    nc=1 if y==2012 else 0
    mask=pd.to_numeric(b.iloc[:,gc],errors='coerce').between(1,11)
    books[y]=(b,headers,mask,nc)
    for j in b.index[mask]:
        name=b.iloc[j,nc];key=key_for(name)
        cross.append(dict(year_start=y,source_name=name,council_key=key,excel_row=j+1,source_file=fn,sheet=sh,source_url=source_map[fn]['url'],match_method='Reviewed legal-name token normalisation; membership independently checked against continuing-council list' if key else 'Unmatched predecessor/new name; never auto-aggregated'))
cross=pd.DataFrame(cross)
assert not cross.dropna(subset=['council_key']).duplicated(['year_start','council_key']).any()
continuing=set(cross.loc[cross.year_start==2015,'council_key'].dropna())
assert len(continuing)==108, f'Investigate continuing-council crosswalk: {len(continuing)}'
known_boundary={'hills':'2016 transfer to Parramatta; continuing legal entity is not constant boundary','hornsby':'2016 transfer to Parramatta; continuing legal entity is not constant boundary'}
flagged=set(original.loc[original.boundary_change_flag==True,'council_key'])
exclusions={**known_boundary,**{k:'Original source boundary-change flag: conservative exclusion pending transfer/period reconciliation' for k in flagged}}
# Require presence in every extension year; this criterion concerns identity, not favourable fiscal outcomes.
identity_complete=set.intersection(*(set(cross.loc[cross.year_start==y,'council_key'].dropna()) for y in range(2012,2018)))
subset=sorted((continuing & identity_complete)-set(exclusions))
selection=[]
for r in original.drop_duplicates('council_key').itertuples():
    reason='Included: OLG full-year continuing list; all historical names matched; no identified transfer/flag'
    if r.council_key not in continuing:reason='Excluded: absent from official 2015–16 full-year continuing-council list; do not splice amalgamated predecessors'
    elif r.council_key in exclusions:reason='Excluded: '+exclusions[r.council_key]
    elif r.council_key not in identity_complete:reason='Excluded: incomplete stable-identity crosswalk'
    selection.append(dict(council_key=r.council_key,council_name=r.council,included=r.council_key in subset,in_2015_full_year_list=r.council_key in continuing,reason=reason,boundary_certification='Conservative legal/entity screen; not cadastral polygon identity certification',evidence='2015–16 DATA A3; Audit Office 2017 amalgamation appendix; Parramatta/Hornsby/The Hills official boundary records; original boundary flags'))
selection=pd.DataFrame(selection);selection.to_csv(OUT/'council_selection.csv',index=False)
cross['included_council']=cross.council_key.isin(subset);cross.to_csv(OUT/'council_crosswalk.csv',index=False)
# Raw header matching is year-aware to avoid accidentally using comparative columns.
patterns={
'operating_ratio_pct':r'operating performance ratio','cash_cover_reported_months':r'cash expense cover ratio','current_ratio':r'unrestricted current ratio','own_source_pct':r'own source revenue','grants_pct':r'grants.*revenue','debt_service_cover':r'debt service cover','debt_service_ratio_pct':r'^debt service ratio',
'actual_maintenance_aud':r'actual asset maintenance expenditure','required_maintenance_aud':r'required asset maintenance expenditure','maintenance_reported_pct':r'^asset maintenance ratio',
'total_revenue_including_capital_aud':r'total revenue from continuing operations','total_expenses_aud':r'total expenses from continuing operations','result_before_capital_aud':r'net operating result before capital',
'residential_rates_aud':r'total residential (rating|rates) revenue','farmland_rates_aud':r'total farmland rates revenue','business_rates_aud':r'total business rates revenue','mining_rates_aud':r'total mining rates revenue',
'population':r'^population( \(?20\d\d\)?)?$','area_km2':r'council area','road_reported_km':r'total road length'}
lineage=[];rows=[];unitrules=[]
def locate(headers,pattern,y):
    js=[i for i,h in enumerate(headers) if re.search(pattern,h,re.I)]
    if len(js)>1:
        ys=[i for i in js if re.search(f'{y}[/–-](?:{y+1}|{str(y+1)[-2:]})',headers[i])]
        if ys:return ys[0] # Prefer main financial-summary block over duplicate maintenance-schedule expense column.
    assert len(js)<=1,(y,pattern,[(i,headers[i]) for i in js])
    return js[0] if js else None
for y,(b,headers,mask,nc) in books.items():
    fn,sh,hr=config[y];src=source_map[fn]
    columns={v:locate(headers,p,y) for v,p in patterns.items()}
    for v,c in columns.items():
        if c is None:unitrules.append(dict(year_start=y,variable=v,header='',excel_column='',factor=np.nan,source_unit='not present',source_file=fn));continue
        h=headers[c];factor=1
        if v.endswith('_aud'):factor=1000 if re.search(r"['’,]000",h) else 1
        if y==2012 and v=='maintenance_reported_pct':factor=100
        if y==2023 and v in ['operating_ratio_pct','own_source_pct','grants_pct','maintenance_reported_pct']:factor=100
        if y==2024 and v=='grants_pct':factor=100
        unitrules.append(dict(year_start=y,variable=v,header=h,excel_column=colname(c),factor=factor,source_unit='AUD thousands' if v.endswith('_aud') and factor==1000 else ('fraction' if factor==100 else 'header/raw units'),source_file=fn))
    rules={v:next(r for r in unitrules if r['year_start']==y and r['variable']==v) for v in patterns}
    for j in b.index[mask]:
        key=key_for(b.iloc[j,nc])
        if key not in subset:continue
        r=dict(council_key=key,council_name=original.loc[original.council_key==key,'council'].iloc[0],year_start=y,financial_year=f'{y}-{str(y+1)[-2:]}',period_start=f'{y}-07-01',period_end=f'{y+1}-06-30',reporting_months=12,reporting_period_evidence='OLG annual reporting-year header; continuing-entity screen, individual opinion not certified for all rows',source_file=fn,source_sheet=sh,source_excel_row=j+1,historical_extension=y<2017)
        for v,c in columns.items():
            raw=b.iloc[j,c] if c is not None else np.nan
            numeric=pd.to_numeric(raw,errors='coerce');factor=rules[v]['factor']
            val=numeric*factor if pd.notna(numeric) else np.nan;r[v]=val
            status='observed_numeric' if pd.notna(val) else ('not_collected_2024_25' if c is not None and 'not collected' in headers[c].lower() else ('column_unavailable' if c is None else 'source_missing_or_nonnumeric'))
            lineage.append(dict(council_key=key,year_start=y,variable=v,raw_value=raw,normalized_value=val,normalization_factor=factor,source_status=status,source_file=fn,source_sheet=sh,source_cell=f'{colname(c)}{j+1}' if c is not None else '',source_header=headers[c] if c is not None else '',source_url=src['url'],source_sha256=src['sha256'],release_date='',current_vintage_availability='Historical first-release values not certified from current archive',retrieved_date='2026-09-18'))
        r['cash_cover_months']=r['cash_cover_reported_months'] if y>=2013 else np.nan
        r['cash_definition_status']='Earlier measure excludes term deposits and uses different expense denominator; not converted' if y==2012 else 'Includes term deposits; cash-flow-based measure, detailed vintage exclusions remain subject to audit'
        r['operating_definition_regime']='Early OLG/TCorp definitions; revaluation exclusions described' if y<=2013 else ('Pre-AASB15/1058' if y<=2018 else ('AASB15/1058 and lease regime' if y<=2023 else 'Six fiscal ratios not collected by OLG'))
        r['debt_service_cover_requires_review']=pd.notna(r['debt_service_cover']) and r['debt_service_cover']==0
        r['road_scope']='local_regional_state' if 'state' in (headers[columns['road_reported_km']] if columns['road_reported_km'] is not None else '').lower() else 'local_regional'
        r['road_km']=r['road_reported_km'] if r['road_scope']=='local_regional' else np.nan
        r['maintenance_gap_aud']=r['actual_maintenance_aud']-r['required_maintenance_aud']
        r['maintenance_calculated_pct']=100*r['actual_maintenance_aud']/r['required_maintenance_aud'] if pd.notna(r['required_maintenance_aud']) and r['required_maintenance_aud']>0 else np.nan
        r['maintenance_difference_pp']=r['maintenance_calculated_pct']-r['maintenance_reported_pct']
        r['maintenance_conflict']=pd.notna(r['maintenance_difference_pp']) and abs(r['maintenance_difference_pp'])>1
        r['maintenance_ratio_pct']=r['maintenance_calculated_pct'] if not r['maintenance_conflict'] else np.nan
        r['maintenance_basis']='Council-estimated requirement; early special schedules unaudited, not a harmonised engineering need'
        rows.append(r)
lineage=pd.DataFrame(lineage);panel=pd.DataFrame(rows).sort_values(['council_key','year_start']).reset_index(drop=True)
assert len(panel)==len(subset)*13
pd.DataFrame(unitrules).to_csv(OUT/'unit_conversion_rules.csv',index=False)
lineage.to_csv(OUT/'cell_lineage.csv',index=False)
panel.loc[panel.maintenance_conflict,['council_key','financial_year','actual_maintenance_aud','required_maintenance_aud','maintenance_reported_pct','maintenance_calculated_pct','maintenance_difference_pp']].to_csv(OUT/'maintenance_conflicts.csv',index=False)
# Compare overlap against frozen panel; discrepancies remain visible rather than silently overwriting V1.
overlap=panel.merge(original,on=['council_key','year_start'],suffixes=('_v2','_v1'))
comp=[]
for v in ['operating_ratio_pct','cash_cover_months','current_ratio','own_source_pct','debt_service_cover','actual_maintenance_aud','required_maintenance_aud','maintenance_ratio_pct']:
    for r in overlap.itertuples():
        x=getattr(r,v+'_v2');z=getattr(r,v+'_v1')
        if pd.isna(x)!=pd.isna(z):comp.append(dict(council_key=r.council_key,year_start=r.year_start,variable=v,v1_value=z,v2_value=x,difference=np.nan,status='Availability change from explicit V2 eligibility rules; see maintenance_conflicts.csv'))
        if pd.notna(x) and pd.notna(z) and not np.isclose(x,z,rtol=1e-9,atol=.011):comp.append(dict(council_key=r.council_key,year_start=r.year_start,variable=v,v1_value=z,v2_value=x,difference=x-z,status='Documented source reconstruction difference; frozen V1 unchanged'))
pd.DataFrame(comp,columns=['council_key','year_start','variable','v1_value','v2_value','difference','status']).to_csv(OUT/'v1_overlap_differences.csv',index=False)
# Physical/declaration history has NOT been extended. Never create historical zeros.
exposure=[c for c in original.columns if c.startswith(('fesm_','bushfire_','flood_','all_decl','physical_','verified_zero','source_list','open_ended','known_prior','prior_fy','direct_infra','boundary_'))]
panel=panel.merge(original[['council_key','year_start']+exposure],on=['council_key','year_start'],how='left',validate='one_to_one')
panel['exposure_coverage_status']=np.where(panel.year_start<2017,'not_extended_unknown','inherited_V1_scope_and_flags')
# Detailed statement components already transcribed in audit03; retain only continuing councils.
components=pd.read_csv(OLD/'accounting_component_audit.csv')
components=components[(components.evidence_type=='Manual audited-statement transcription') & components.council_key.isin(subset)].copy()
# Historical audited income statement, Albury 2013–14, PDF p4 ($000).
# Comparative 2012–13 belongs to the later report, not a certified original release.
albury_url='https://eservice.alburycity.nsw.gov.au/ACCPublicDocs/DocumentViewer.aspx?DocID=1072745'
albury_values={
'rates_annual_charges':(53508,48963),'user_charges_fees':(37188,36388),
'interest_investment':(2457,2412),'other_revenue':(2620,2132),
'operating_grants':(6115,9207),'capital_grants':(19248,9850),
'net_joint_venture_income':(30,15),'employee_cost':(33231,32173),
'borrowing_cost':(3535,3968),'materials_services':(22846,22664),
'depreciation_amortisation':(25354,25615),'impairment':(16,55),
'depreciation_impairment':(25370,25670),'other_expense':(14052,14921),
'net_disposal_loss':(1642,191),'total_revenue_including_capital':(121166,108967),
 'total_expenses':(100676,99587),'result_before_capital':(1242,-470)}
extra=[]
for component,values in albury_values.items():
    for year,value in zip([2013,2012],values):
        extra.append(dict(council_key='albury',year_start=year,financial_year=f'{year}-{str(year+1)[-2:]}',component=component,raw_value=value,source_unit='AUD thousands',value_aud=value*1000,source_id='albury_fs_2013',source_url=albury_url,source_location='PDF p4, printed p3; authorisation p2',source_header=component,report_vintage=2014,definition_caveat='2012 comparative in 2014 report; authorisation is not publication. Depreciation_impairment sums separately reported depreciation and impairment.',evidence_type='Manual audited-statement transcription',authorised_for_issue_date='2014-10-27',exact_publication_date=''))
components=pd.concat([components,pd.DataFrame(extra)],ignore_index=True)
for year in [2012,2013]:
    v={r['component']:r['value_aud'] for r in extra if r['year_start']==year}
    assert sum(v[k] for k in ['rates_annual_charges','user_charges_fees','interest_investment','other_revenue','operating_grants','capital_grants','net_joint_venture_income'])==v['total_revenue_including_capital']
    assert sum(v[k] for k in ['employee_cost','borrowing_cost','materials_services','depreciation_impairment','other_expense','net_disposal_loss'])==v['total_expenses']
    assert v['total_revenue_including_capital']-v['total_expenses']-v['capital_grants']==v['result_before_capital']
vintage=[]
for variable,later in [('operating_ratio_pct',-.94),('own_source_pct',82.52)]:
    archived=float(panel.loc[(panel.council_key=='albury')&(panel.year_start==2012),variable].iloc[0])
    vintage.append(dict(council_key='albury',year_start=2012,variable=variable,olg_archive_value=archived,later_comparative_value=later,later_report_vintage=2014,source_url=albury_url,source_location='PDF p50, note13a(i)',resolution='Unresolved definition/vintage discrepancy; retain archive candidate and do not silently substitute comparative'))
pd.DataFrame(vintage).to_csv(OUT/'vintage_discrepancies.csv',index=False)

# Preserve original source vintage; do not merge historical comparative revisions as if first-release observations.
component_mapping={'rates_annual_charges':'rates_annual_charges_aud','user_charges_fees':'user_charges_fees_aud','other_revenue':'other_revenue_aud','operating_grants':'operating_grants_aud','capital_grants':'capital_grants_aud','interest_investment':'interest_investment_aud','employee_cost':'employee_cost_aud','materials_services':'materials_services_aud','borrowing_cost':'borrowing_cost_aud','depreciation_impairment':'depreciation_impairment_aud','other_expense':'other_expense_aud','total_revenue_including_capital':'statement_total_revenue_aud','total_expenses':'statement_total_expenses_aud'}
for old,new in component_mapping.items():
    c=components[components.component==old]
    assert not c.duplicated(['council_key','year_start']).any()
    panel=panel.merge(c[['council_key','year_start','value_aud']].rename(columns={'value_aud':new}),on=['council_key','year_start'],how='left',validate='one_to_one')
components.to_csv(OUT/'detailed_component_lineage.csv',index=False)
panel['operating_revenue_ex_capital_aud']=panel.statement_total_revenue_aud-panel.capital_grants_aud
# This is only a published income-statement total excluding capital; NOT the adjusted OP denominator.
# Add demonstrably dated advance-policy information in a separate ex-ante feature table.
policy=[
(2017,'2017-06-08',50,'https://www.olg.nsw.gov.au/wp-content/uploads/2020/12/GC-145.pdf','GC145, p1','First two instalments announced; 50% approximation, not final entitlement'),
(2018,'2018-06-21',50,'https://www.olg.nsw.gov.au/wp-content/uploads/GC-147-2018-19-Financial-Assistance-Grants-FAGs-%E2%80%93-advance-payment-and-transition-to-implement-improvements-to-the-existing-allocation-model.pdf','GC147, p1','Approximate advance, balance adjusted later'),
(2019,'2019-06-18',52,'https://www.olg.nsw.gov.au/wp-content/uploads/2020/12/GC-148.pdf','GC148, p1','Approximately 52%, not 50%; final entitlement pending'),
(2020,'2020-05-27',50,'https://www.olg.nsw.gov.au/sites/default/files/2026-03/grants-commission-circular-gc-149-2020-21-financial-assistance-grants-advance-payment.pdf','GC149, p1','Approximately 50%; final entitlement pending'),
(2021,'2021-06-09',50,'https://www.olg.nsw.gov.au/sites/default/files/2026-03/council-circular-gc-150-2021-22-financial-assistance-grants-advance-payment.pdf','GC150, p1','Approximately 50%; final entitlement pending'),
(2022,'2022-04-12',75,'https://www.olg.nsw.gov.au/sites/default/files/2026-03/council-circular-gc-150-2022-23-financial-assistance-grants-advance-payment.pdf','GC151, p1; filename incorrectly says150','Approximately 75%; announced before target starts'),
(2023,'2023-06-28',100,'https://www.olg.nsw.gov.au/sites/default/files/2026-03/grants-commission-circular-gc-152-2023-24-financial-assistance-grants-advance-payment.pdf','GC152, p1','Approximately 100%; final adjustment pending')]
policy.append((2024,'2024-06-28',85,'https://www.olg.nsw.gov.au/sites/default/files/2026-01/grants-commission-circular-gc-153-2024-25-financial-assistance-grants–advance-payment.pdf','GC153, p1; visually inspected','Approximately 85%; announcement verified but primary target uncollected'))
# Resolve cached URLs from the manifest where possible, preserving browser-read official links otherwise.
new_sources=json.loads((OUT/'source_manifest.json').read_text())+json.loads((OUT/'source_manifest_additional.json').read_text())
for i,t in enumerate(policy):
    y,date,pct,url,loc,note=t
    for src in new_sources:
        if src.get('status')=='retrieved' and str(y)+'_'+str(y+1)[-2:] in src['source_id'] and 'grants' in src['source_id']:url=src['url']
    policy[i]=(y,date,pct,url,loc,note)
policy_df=pd.DataFrame(policy,columns=['target_year','announcement_date','announced_target_fag_advance_pct','source_url','source_location','caveat'])
policy_df['available_before_target']=pd.to_datetime(policy_df.announcement_date)<pd.to_datetime(policy_df.target_year.astype(str)+'-07-01')
assert policy_df.available_before_target.all();policy_df.to_csv(OUT/'dated_ex_ante_policy.csv',index=False)
# Release date is NOT a PDF modification timestamp, an accounting year or a statutory deadline.
release=[]
for y in range(2012,2025):
    upper='';evidence='';status='First release date not verified; current download is not historical vintage'
    if y==2012:upper='2014-06-30';evidence='comparative_2013.pdf cover: June2014';status='Report release month verified; spreadsheet revision vintage not certified'
    if y==2013:upper='2015-06-30';evidence='profile_2015.pdf cover and OLG annual2014–15 PDF p17: released June2015';status='Report release month verified; spreadsheet revision vintage not certified'
    release.append(dict(measurement_year=y,period_end=f'{y+1}-06-30',report_release_upper_bound=upper,exact_publication_date='',evidence=evidence,status=status,current_archive_retrieval_date='2026-09-18',current_upload_path_not_release_date=True))
release=pd.DataFrame(release);release.to_csv(OUT/'publication_date_audit.csv',index=False)
# Build a complete candidate predictor availability ledger for t−1 values at the start of t+1.
financial_vars=['operating_ratio_pct','cash_cover_months','current_ratio','own_source_pct','debt_service_cover','debt_service_ratio_pct','maintenance_ratio_pct','population','road_km','total_revenue_including_capital_aud','total_expenses_aud','residential_rates_aud','operating_grants_aud','capital_grants_aud','employee_cost_aud','materials_services_aud','depreciation_impairment_aud']
financial_vars=list(dict.fromkeys(financial_vars+list(component_mapping.values())+['operating_revenue_ex_capital_aud','result_before_capital_aud','required_maintenance_aud','actual_maintenance_aud','farmland_rates_aud','business_rates_aud','mining_rates_aud','grants_pct']))
av=[];design=[];pi=panel.set_index(['council_key','year_start'])
for key in subset:
    for target in range(2014,2025):
        prior=target-2;event=target-1;pr=pi.loc[(key,prior)];ta=pi.loc[(key,target)];er=pi.loc[(key,event)];cutoff=pd.Timestamp(f'{target}-07-01')
        for v in financial_vars:
            value=pr[v];status='missing_value' if pd.isna(value) else 'historical_value_exists_but_publication_vintage_unverified'
            if v=='cash_cover_months' and prior==2012:status='incompatible_pre2013_cash_definition'
            if v=='road_km' and prior<=2013:status='incompatible_state_road_scope'
            pub=release.loc[release.measurement_year==prior].iloc[0]
            source_file=pr.source_file;source_location=f'{pr.source_sheet}, row {pr.source_excel_row}; cell_lineage.csv';release_bound=pub.report_release_upper_bound
            if v in component_mapping.values() or v=='operating_revenue_ex_capital_aud':
                component='capital_grants' if v=='operating_revenue_ex_capital_aud' else next(k for k,val in component_mapping.items() if val==v)
                detail=components[(components.council_key==key)&(components.year_start==prior)&(components.component==component)]
                source_file='';source_location='';release_bound=''
                if len(detail):
                    d=detail.iloc[0];source_file=d.source_url;source_location=d.source_location
                    auth=d.get('authorised_for_issue_date','')
                    if pd.notna(auth) and str(auth) and pd.Timestamp(auth)>=cutoff:status='retrieved_report_authorised_after_forecast_cutoff'

            av.append(dict(council_key=key,target_year=target,forecast_cutoff=cutoff.date(),measurement_year=prior,variable=v,value=value,availability_status=status,verified_ex_ante=False,report_release_upper_bound=release_bound,source_file=source_file,source_location=source_location,reason='Do not use unknown availability as observed-before-cutoff. A later archive or restated comparative is not a certified first-release feature.'))
        for variable in ['fesm_burned_ha','bushfire_declared_event_count','flood_declared_event_count']:
            value=er[variable]
            av.append(dict(council_key=key,target_year=target,forecast_cutoff=cutoff.date(),measurement_year=event,variable=variable,value=value,availability_status='exposure_history_not_extended' if event<2017 else ('missing_value' if pd.isna(value) else 'exposure_product_publication_vintage_unverified'),verified_ex_ante=False,report_release_upper_bound='',source_file='Frozen NSW Data Panel.csv',source_location='Original source/coverage flags retained in candidate panel',reason='Occurrence year does not certify when declarations or mapped exposure were available; no historical zeros inferred.'))
        p=policy_df[policy_df.target_year==target]
        pv=p.iloc[0] if len(p) else None
        av.append(dict(council_key=key,target_year=target,forecast_cutoff=cutoff.date(),measurement_year=event,variable='announced_target_fag_advance_pct',value=pv.announced_target_fag_advance_pct if pv is not None else np.nan,availability_status='verified_dated_announcement' if pv is not None else 'announcement_not_verified',verified_ex_ante=pv is not None,report_release_upper_bound=pv.announcement_date if pv is not None else '',source_file=pv.source_url if pv is not None else '',source_location=pv.source_location if pv is not None else '',reason='Applies to target entitlement paid in advance before target starts. Does NOT predict next target-end advance announcement, realised grant income or council damage.'))
        fiscal_ok=pd.notna(pr.operating_ratio_pct) and pd.notna(ta.operating_ratio_pct)
        exposure_ok=event>=2017 and pd.notna(er.fesm_burned_ha) and pd.notna(er.bushfire_declared_event_count) and pd.notna(er.flood_declared_event_count)
        design.append(dict(council_key=key,prior_year=prior,event_year=event,target_year=target,forecast_cutoff=cutoff.date(),fiscal_pair_available=fiscal_ok,cash_pair_available=pd.notna(pr.cash_cover_months) and pd.notna(ta.cash_cover_months),maintenance_pair_available=pd.notna(pr.maintenance_ratio_pct) and pd.notna(ta.maintenance_ratio_pct),event_exposure_values_available=exposure_ok,fiscal_and_exposure_candidate=fiscal_ok and exposure_ok,strict_ex_ante_ready=False,prior_financial_vintage_verified=False,exposure_publication_date_verified=False,reason='Fiscal vintage unverified; early exposure years not extended; physical occurrence date does not establish mapped-product availability'))
av=pd.DataFrame(av);design=pd.DataFrame(design)
av.to_csv(OUT/'temporal_availability_audit.csv',index=False);design.to_csv(OUT/'forecast_design_eligibility.csv',index=False)
# Verified-only features contain policy announcements; all unavailable years remain blank.
verified=av[av.verified_ex_ante].pivot(index=['council_key','target_year','forecast_cutoff'],columns='variable',values='value').reset_index()
verified.to_csv(OUT/'verified_ex_ante_features.csv',index=False)
panel['candidate_only']=True;panel['strict_asof_predictor_panel']=False
panel.to_csv(OUT/'NSW_Fiscal_Panel_V2_candidate.csv',index=False)
# Coverage: retain year/variable/denominator and reason, not only counts of complete rows.
metrics=list(patterns)+['cash_cover_months','maintenance_ratio_pct','road_km']+list(component_mapping.values())+['operating_revenue_ex_capital_aud']
cov=[]
for y,g in panel.groupby('year_start'):
    for v in metrics:cov.append(dict(year_start=y,financial_year=g.financial_year.iloc[0],variable=v,councils_in_subset=len(g),observed=int(g[v].notna().sum()),missing=int(g[v].isna().sum()),extension=y<2017))
pd.DataFrame(cov).to_csv(OUT/'coverage_by_year_variable.csv',index=False)
cc=panel.groupby('council_key').agg(total_years=('year_start','size'),operating_years=('operating_ratio_pct','count'),cash_comparable_years=('cash_cover_months','count'),maintenance_eligible_years=('maintenance_ratio_pct','count'),new_years=('historical_extension','sum'))
cc.to_csv(OUT/'coverage_by_council.csv')
annual=design.groupby('target_year').agg(councils=('council_key','size'),fiscal_pairs=('fiscal_pair_available','sum'),cash_pairs=('cash_pair_available','sum'),maintenance_pairs=('maintenance_pair_available','sum'),fiscal_exposure_pairs=('fiscal_and_exposure_candidate','sum'),strict_ex_ante_pairs=('strict_ex_ante_ready','sum'))
annual.to_csv(OUT/'coverage_by_forecast_year.csv')
folds=[]
for scenario,minprior,require_exposure in [('V1_period_same_subset',2017,True),('V2_fiscal_only_upper_bound',2012,False),('V2_fiscal_plus_inherited_exposure',2012,True)]:
    q=design[(design.prior_year>=minprior)&design.fiscal_pair_available]
    if require_exposure:q=q[q.event_exposure_values_available]
    for test in sorted(design.target_year.unique()):
        tr=q[q.target_year<test-1];te=q[q.target_year==test]
        folds.append(dict(scenario=scenario,test_target_year=test,training_rows=len(tr),training_distinct_target_years=tr.target_year.nunique(),test_rows=len(te),passes_existing_100_train_rows=len(tr)>=100 and len(te)>=2,strict_asof_ready=False,caveat='Structural count only; no model fitted, no publication-vintage or old-exposure certification'))
folds=pd.DataFrame(folds);folds.to_csv(OUT/'potential_forward_folds.csv',index=False)
# Dictionary contains every panel column and explicitly distinguishes aliases/raw versus common definitions.
definition={
'operating_ratio_pct':('percent','Published operating-performance ratio after explicit source scaling; exact adjusted numerator exclusions not fully reconstructed across vintages','Candidate; AASB and definition-regime flags required'),
'cash_cover_reported_months':('months','Reported cash expense cover, including incompatible2012 definition','Do not pool2012 with later cash cover'),
'cash_cover_months':('months','Reported cash cover from2013 onward;2012 withheld because term deposits/denominator differ','Candidate common definition from2013–14; publication vintage unresolved'),
'current_ratio':('times','Unrestricted current assets/current liabilities after specified restrictions','Core definition broadly consistent; original exclusions retained'),
'own_source_pct':('percent','Own-source share of continuing revenue including capital grants in denominator','Later adjusted exclusions can differ; not simply one minus grants_pct'),
'debt_service_cover':('times','Operating resources before interest/depreciation divided by principal and interest','Not debt_service_ratio_pct; zero/debt-free denominator requires review'),
'debt_service_ratio_pct':('percent','Debt interest and principal relative to continuing operating revenue excluding capital','Unavailable2012; kept separate from debt cover'),
'maintenance_reported_pct':('percent','Published actual/required maintenance ratio;2012fraction x100','Council-estimated denominator; historical unaudited schedule'),
'maintenance_calculated_pct':('percent','100 times actual/required maintenance, only for positive denominator','Arithmetic does not harmonise engineering need'),
'maintenance_ratio_pct':('percent','Calculated adequacy if reported/calculated difference <=1pp; conflicts withheld','Threshold accommodates integer rounding; no favourable-outcome trimming'),
'maintenance_gap_aud':('nominal AUD','Actual less required maintenance; negative is shortfall','No inflation adjustment; not a causal crowd-out measure'),
'road_reported_km':('km','Road length as reported; early years include state roads','Scope changes; retain road_scope'),
'road_km':('km','Local and regional road length only; earlier broader-scope measure withheld','No invented conversion from all roads'),
'operating_revenue_ex_capital_aud':('nominal AUD','Audited-statement total revenue less capital grants from the same statement vintage','Not adjusted OP denominator'),
'residential_rates_aud':('nominal AUD','Residential rating category revenue','Not total rates and annual charges'),
'result_before_capital_aud':('nominal AUD','Reported net operating result before capital grants','Not necessarily adjusted OP numerator')}
dictrows=[]
for v in panel.columns:
    unit,meaning,caveat=definition.get(v,('nominal AUD' if v.endswith('_aud') else ('percent' if v.endswith('_pct') else 'source/metadata'),v.replace('_',' '),'See cell_lineage.csv, unit_conversion_rules.csv and definition_changes.md; metadata/flags are not automatically predictors'))
    if v=='total_revenue_including_capital_aud':meaning='Total continuing revenue INCLUDING capital grants; not operating-only income'
    if v=='total_expenses_aud':meaning='Total continuing expenses, including depreciation; not cash payments'
    if v in component_mapping.values():caveat='Sparse audited-statement transcription; publication date unverified; realised target values would leak'
    dictrows.append(dict(variable=v,unit=unit,definition=meaning,caveat=caveat,measurement_role='Fiscal-year observation; shift to t−1 only after availability validation' if v in metrics else 'Identity, provenance, eligibility or inherited exposure',predictor_approval='not approved by default',source='Cell lineage for workbook variables; detailed component lineage for statement variables; frozen V1 for inherited exposure'))
pd.DataFrame(dictrows).to_csv(OUT/'variable_dictionary.csv',index=False)
# Compact standalone visuals.
plt.rcParams.update({'figure.dpi':140,'font.size':10})
coverage=pd.DataFrame(cov);focus=['operating_ratio_pct','cash_cover_months','current_ratio','own_source_pct','debt_service_cover','maintenance_ratio_pct','operating_grants_aud']
heat=coverage[coverage.variable.isin(focus)].pivot(index='variable',columns='year_start',values='observed').reindex(focus)
fig,ax=plt.subplots(figsize=(12,4));im=ax.imshow(heat,vmin=0,vmax=len(subset),cmap='Blues',aspect='auto');ax.set_xticks(range(len(heat.columns)),[f'{y}–{str(y+1)[-2:]}' for y in heat.columns],rotation=45,ha='right');ax.set_yticks(range(len(heat)),heat.index)
for i in range(len(heat)):
    for j in range(len(heat.columns)):ax.text(j,i,int(heat.iloc[i,j]),ha='center',va='center',color='white' if heat.iloc[i,j]>len(subset)*.6 else 'black',fontsize=8)
ax.set_title('V2 candidate coverage: numeric availability is not ex-ante certification');fig.colorbar(im,ax=ax,label='Councils');fig.tight_layout();fig.savefig(OUT/'coverage_heatmap.png');plt.close(fig)
summary={'continuing_councils_in_2015_16':len(continuing),'selected_councils':len(subset),'candidate_rows':len(panel),'new_historical_rows':int(panel.historical_extension.sum()),'new_fiscal_years':5,'cash_earliest_candidate_year':2013,'operating_nonmissing':int(panel.operating_ratio_pct.notna().sum()),'maintenance_conflicts':int(panel.maintenance_conflict.sum()),'verified_policy_target_years':policy_df.target_year.tolist(),'verified_policy_council_target_rows':len(verified),'strict_ex_ante_ready_forecast_rows':int(design.strict_ex_ante_ready.sum()),'prior_files_hash_checked':len(FROZEN),'all_prior_files_unchanged':True,'new_models_fitted':0}
summary['new_historical_statement_council_years']=2
summary['audited_component_council_years']=int(components[['council_key','year_start']].drop_duplicates().shape[0])
summary['vintage_discrepancies']=len(vintage)
summary['potential_folds']={s:int(g.passes_existing_100_train_rows.sum()) for s,g in folds.groupby('scenario')}
(OUT/'validation_summary.json').write_text(json.dumps(summary,indent=2));freeze_check();print(json.dumps(summary,indent=2))
