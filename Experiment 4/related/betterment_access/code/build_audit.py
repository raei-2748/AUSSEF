"""Experiment 4B: descriptive reconstruction only. Unknown decisions never become controls."""
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib,json,re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'NSW Data Panel.csv').exists())
OUT=ROOT/'Experiment 4/related/betterment_access/results';S=OUT/'sources';FIG=OUT/'figures'
def save(frame,name):frame.to_csv(OUT/(name+'.csv'),index=False)
def frozen_check():
 hashes=json.loads((OUT/'frozen_existing_sha256.json').read_text())
 assert all((ROOT/p).is_file() and hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items()),'Pre-existing file changed'
 return len(hashes)
frozen_check()
prov=pd.DataFrame(json.loads((OUT/'source_provenance.json').read_text()));urls=prov.set_index('source_id').url.to_dict();save(prov,'source_provenance')
def council_key(name):
 # Stable within this audit; not represented as an official ABS code. No fuzzy matching.
 name=name.replace('Council of the City of Gold Coast','City of Gold Coast')
 name=re.sub(r'\b(Aboriginal|Regional|Shire|City|Council|of|the)\b','',name)
 return 'QLD_'+re.sub('[^a-z0-9]+','_',name.lower()).strip('_')
rows=[]
for ti,tab in enumerate(BeautifulSoup((S/'qra2022.html').read_text(),'html.parser').find_all('table'),1):
 for ri,row in enumerate(tab.find_all('tr')[1:],1):
  vals=[c.get_text(' ',strip=True) for c in row.find_all(['td','th'])]
  assert len(vals)==3
  stream,applicant,project=vals
  rows.append(dict(public_record_id=f'QRA2022_T{ti}_R{ri:03d}',funding_round='2022 / 2021–22 event season',funding_stream=stream[-1],applicant=applicant,council_key=council_key(applicant) if 'Department' not in applicant else '',applicant_type='STATE_AGENCY' if 'Department' in applicant else 'LOCAL_GOVERNMENT',project_asset_label=project,application_id='',project_id='',source_id='qra2022',source_url=urls['qra2022'],source_locator=f'Successful projects; Category {stream[-1]} table, data row {ri}',source_version_date='2024-07-24',status='APPROVED_REPORTED',eligibility_status='ACCEPTED_UNDER_PROGRAM_BY_OFFICIAL_AWARD_LIST; individual assessment file unavailable',label_confidence='HIGH for public award; project identity/eligibility details unresolved',submission_date='',decision_date='',amount_requested_aud=np.nan,amount_approved_aud=np.nan,event='',asset_type='UNVERIFIED: retain original project/asset label',assessment_score=np.nan,recommendation='',bcr=np.nan,quality_note='Published asset/works row; not certified one application or one unique project'))
projects=pd.DataFrame(rows);keys=['funding_stream','applicant','project_asset_label'];projects['repeated_label']=projects.duplicated(keys,keep=False);projects['same_label_row_count']=projects.groupby(keys).public_record_id.transform('size')
# Supplement only exact council + named-asset matches; retain coarse dates as text.
mask=(projects.applicant.eq('Scenic Rim Regional Council')&projects.project_asset_label.eq('Teviotville Road'))
projects.loc[mask,['submission_date','decision_date','event']]=['2022-12','early 2023','South East Queensland Rainfall and Flooding, 22 February – 5 April 2022']
projects['supplemental_source_ids']='';projects.loc[mask,'supplemental_source_ids']='scenic_ar2023_attachment; scenic_drfa2024'
mask2=(projects.applicant.eq('Scenic Rim Regional Council')&projects.project_asset_label.eq('Allandale Road'))
projects.loc[mask2,'event']='Southern Queensland Flooding, 6–20 May 2022';projects.loc[mask2,'supplemental_source_ids']='scenic_drfa2024'
save(projects,'published_approved_projects');save(projects.loc[projects.repeated_label],'repeated_project_labels')
lg=projects[projects.applicant_type.eq('LOCAL_GOVERNMENT')].copy()
summary=lg.groupby(['council_key','applicant']).agg(published_rows=('public_record_id','size'),distinct_asset_labels=('project_asset_label','nunique'),streams=('funding_stream',lambda s:';'.join(sorted(set(s))))).reset_index();save(summary,'council_cluster_audit')
# This ledger contains evidence observations, not a deduplicated application register.
cases=pd.DataFrame(json.loads((OUT/'case_evidence.json').read_text()));cases['source_url']=cases.source_id.map(urls);cases['council_key']=cases.applicant.map(lambda x:council_key(x) if 'Department' not in x else '')
save(cases,'decision_evidence');assert not cases.usable_eligible_negative.any()
counts=pd.DataFrame([
 ['Reported submissions',123,'Submission; may contain multiple projects','QRA program status; not project denominator'],['Reported council applicants',39,'Councils','TMR also submitted; identities of all submitters not published'],['Published approved asset/works rows',len(projects),'Public-list rows','Keep repeats; does not equal unique projects'],['Published local-government approved rows',len(lg),'Public-list rows','Excludes state agency'],['Distinct approved council names',lg.council_key.nunique(),'Councils','Not the number of independent applications'],['Distinct stream/applicant/asset labels',len(projects.drop_duplicates(keys)),'Labels','Not certified deduplicated project count'],['Verified eligible unsuccessful local-government applications',0,'Cases recovered by this audit','Unknown population count; not evidence all applications succeeded'],['Application IDs recovered',0,'Official IDs','Public row IDs are audit references only'],['Model-ready application observations',0,'Certified observations','No valid two-class risk set or need block']
],columns=['quantity','value','unit','caveat']);counts['source_url']=urls['qra2022'];save(counts,'decision_universe_reconciliation')
# Queensland-only capacity baseline: deliberately no NSW source is loaded.
qao=pd.read_csv(OUT/'qao_capacity_transcription.csv');qao['council_key']=qao.council_name.map(council_key);assert qao.council_key.is_unique
core=['grant_share_5yr_pct','operating_surplus_pct','net_financial_liabilities_pct'];capacity=[]
for r in qao.to_dict('records'):
 for f in core:
  capacity.append(dict(council_key=r['council_key'],council_name=r['council_name'],feature=f,value=r[f],unit='percent',measurement_date=r['period_end'],publication_date=r['publication_date'],audit_date='',source_id=r['source_id'],source_url=urls[r['source_id']],source_locator=f"Figure I4; printed p{r['printed_page']} / PDF p{r['pdf_page']}",scope='council; QAO-published ratio',quality_note=r['quality_note']+('; '+r['grant_period_note'] if f=='grant_share_5yr_pct' else ''),timing_status='PRE_2021_22_DISASTER_MEASUREMENT; application-specific publication cutoff still required',confidence=r['confidence']))
# A concrete extraction pilot demonstrates additional Queensland financial components; not full coverage.
pilot=[('cash_and_equivalents',183955,'AUD thousands','PDF p96 / printed p94','Total cash includes restricted money; not unrestricted cash'),('borrowings',391176,'AUD thousands','PDF p96 / printed p94','Borrowings, not net financial liabilities'),('property_plant_equipment',2886422,'AUD thousands','PDF p96 / printed p94','Book value includes asset classes; valuation bases require harmonisation'),('total_assets',3613521,'AUD thousands','PDF p96 / printed p94','Council scope, not consolidated group'),('rates_levies_charges',214766,'AUD thousands','PDF p95 / printed p93','One own-source component; not all own-source revenue'),('fees_charges',31643,'AUD thousands','PDF p95 / printed p93','Own-source component'),('sales_revenue',3676,'AUD thousands','PDF p95 / printed p93','Own-source component'),('grants_contributions_total',137871,'AUD thousands','PDF p95 / printed p93','Includes capital/contributed assets; do not call operating grant dependence'),('interest_investment_revenue',2091,'AUD thousands','PDF p95 / printed p93','Own-source component'),('employee_expenses',109509,'AUD thousands','PDF p95 / printed p93','Expense scale, not staffing FTE'),('finance_costs',17286,'AUD thousands','PDF p95 / printed p93','Includes refinancing costs; no simple comparable debt-service ratio'),('headcount',1290,'people','PDF p68 / printed p66','Headcount at 30 June 2021; not FTE')]
for f,value,unit,loc,note in pilot:
 capacity.append(dict(council_key='QLD_ipswich',council_name='Ipswich City Council',feature=f,value=value,unit=unit,measurement_date='2021-06-30',publication_date='',audit_date='2021-10-12' if unit=='AUD thousands' else '',source_id='ipswich_ar2021_current',source_url=urls['ipswich_ar2021_current'],source_locator=loc,scope='council, not consolidated group',quality_note=note,timing_status='PRE_DISASTER_MEASUREMENT; original release date not certified; audit date is not publication',confidence='HIGH: annual report component; comparability not yet certified'))
capacity.append(dict(council_key='QLD_ipswich',council_name='Ipswich City Council',feature='population_council_reported',value=234614,unit='people',measurement_date='2021-06-30',publication_date='2021-09-11',audit_date='',source_id='ipswich_population',source_url=urls['ipswich_population'],source_locator='News article, first paragraph',scope='council-reported annual growth estimate',quality_note='Use consistent dated ABS ERP for full panel; not harmonised population coverage',timing_status='PRE_2021_22_DISASTER_MEASUREMENT; application dates not recovered',confidence='HIGH for reported value'))
capacity=pd.DataFrame(capacity);save(capacity,'queensland_capacity_values')
coverage=summary.merge(qao[['council_key','period_end','publication_date',*core]],on='council_key',how='left',validate='one_to_one');assert coverage[core].notna().all().all();save(coverage,'capacity_council_coverage')
# Strict joins are not invented for the public list's undated applications.
temporal=lg[['public_record_id','council_key','applicant','project_asset_label','submission_date','decision_date']].merge(qao[['council_key','period_end','publication_date','quality_note']],on='council_key',how='left',validate='many_to_one')
temporal['capacity_measurement_before_known_submission']=pd.Series(pd.NA,index=temporal.index,dtype='boolean');temporal['capacity_publication_before_known_submission']=pd.Series(pd.NA,index=temporal.index,dtype='boolean')
known=temporal.submission_date.eq('2022-12');temporal.loc[known,'capacity_measurement_before_known_submission']=pd.to_datetime(temporal.loc[known,'period_end']).lt(pd.Timestamp('2022-12-01'));temporal.loc[known,'capacity_publication_before_known_submission']=pd.to_datetime(temporal.loc[known,'publication_date']).lt(pd.Timestamp('2022-12-01'))
temporal['timing_verdict']=np.where(known,'QAO baseline predates earliest day of reported submission month','APPLICATION/DECISION DATE UNKNOWN; no strict as-of join certified');save(temporal,'temporal_availability_audit')
cap_avail=[
 ('operating position','QAO current operating surplus ratio',39,'qao_appendixI','Pre-event values recovered; report published 11 May 2022; application cutoffs unresolved'),
 ('liquidity/cash','Annual report cash; restricted balances/current liabilities needed',1,'ipswich_ar2021_current','Pilot only; unrestricted liquidity not yet comparable'),
 ('own-source revenue','Rates/fees/sales/interest components',1,'ipswich_ar2021_current','Pilot components; no complete comparable own-source ratio constructed'),
 ('grant dependence','QAO five-year total grant funding share',39,'qao_appendixI','Recovered proxy; differs from current operating-grant dependence'),
 ('debt burden/capacity','QAO net financial liabilities ratio',39,'qao_appendixI','Recovered; Brisbane concession accounting and two older audits flagged'),
 ('staffing/administrative scale','Annual report headcount, staff expenses; comparative personnel source',1,'ipswich_ar2021_current','Pilot only; headcount is not FTE or dedicated grant-team capacity'),
 ('population/infrastructure scale','Council population estimate and asset book values',1,'ipswich_population','Pilot only; ABS ERP, road length and consistent valuation basis needed'),
 ('prior disaster/grant experience','Dated earlier application/approval histories',0,'rti_log','No complete pre-cutoff application history recovered; later snapshots not substituted')]
cap_avail=pd.DataFrame(cap_avail,columns=['capacity_block','candidate_measure','councils_with_pilot_values','source_id','remaining_gap']);cap_avail['source_url']=cap_avail.source_id.map(urls);cap_avail['coverage_denominator']='39 identified councils: 38 award-list councils + Boulia evidence; not a certified applicant universe';save(cap_avail,'capacity_data_availability')
need_rows=[
 ('damage_reconstruction_estimate','Eligibility §§6–7; funding §11','Original independently documented damage/site assessment; Category B restore-to-function estimate before review','None across certified application universe; Boulia REPA totals are not project-level Betterment baselines','AUD; source engineer/date/asset IDs'),
 ('requested_betterment_and_total_cost','Funding §§11–17; assessment b','Separate initial Betterment increment, base REPA, total cost, co-contribution and GST','Ipswich bundled requested REPA value only; not a separable Betterment request','AUD; original submission version'),
 ('hazard_risk_options','Assessment a','Pre-decision hazard/risk assessment, options and inaction case','Application dossiers not public in reviewed sources','Hazard-specific measures; no generic index'),
 ('cost_benefit_bcr','Assessment b','Submitted CBA/BCR with horizon, discount rate, assumptions, avoided costs and nonfinancial benefits','No application-specific BCR or assessor score recovered','Ratio and component AUD; do not use realised avoided costs'),
 ('community_benefit','Assessment c','Quantified affected users/access/service benefits at application','Retrospective selected-success narratives only; no comparable baseline','Original quantified measures with units'),
 ('vulnerability_remoteness','Prioritisation §19','Contemporaneous vulnerable groups/diverse populations and geographic remoteness','No project footprints/beneficiary records; council-wide proxies alone insufficient','Counts, shares or ABS category separately'),
 ('asset_project_type','Eligibility §7; assessment a/d','Original asset class and scope','221 public asset labels; formal class/scope and negative cases missing','Categorical; no guess from names in main data'),
 ('deliverability_technical_evidence','Assessment d; application §27; §28 is post-approval and excluded','Pre-decision investigation, consultation, engineering/options evidence; readiness and approvals','No full original application evidence for both outcomes','Dated checklist; not later construction progress'),
 ('innovation','Assessment e','Original innovative design/resilience evidence','Not recovered consistently','Assessed dimension; optional according to guideline'),
 ('regional_balance_other_funding','Prioritisation §19','Alternative funding, duplication and local/regional balance considered at assessment','Not recovered at application level','Context and decision batch, distinct from capacity'),
 ('assessment_scores_recommendation','Assessment and final approval §§19–21','Criteria-level assessor scores/recommendation, overrides, timestamps','No public scored register recovered','Keep recommendation as audit label; not a direct predictor of approval')]
need=pd.DataFrame(need_rows,columns=['variable','policy_locator','required_pre_decision_measure','public_recovery_status','unit_or_boundary']);need['source_url']=urls['guideline2022'];need['complete_two_outcome_coverage']=False;need['independence_warning']='Applicant submission quality may itself reflect capacity; separate underlying damage from presentation/assessor judgement. No causal interpretation.';save(need,'project_need_quality_audit')
policy=pd.DataFrame([
 ['2022 D','150000000','5000000','3 events in June; May flooding added in July','annex_july','2022-07','Verify guideline/annex version at each decision'],
 ['2022 E','20000000','3000000','9 listed 2021–22 events','annex_july','2022-07','Separate stream, allocation pool and project cap'],
 ['Both','','','CEO QRA final project approval; unsuccessful projects retained for reconsideration','guideline2022','2022-06-06','Do not treat temporary non-approval as final outcome'],
 ['Both','','','Co-contribution normally required; Indigenous councils exempt','guideline2022','2022-06-06','Record rule; council capacity and contribution policy differ'],
 ['Both','','','MARS withdrawal/re-lodgement can be an administrative revision','lodgement2022','2022-06','Track parent/revision identifiers; do not count revision as withdrawal outcome'],
 ['2022 fund','7200000','','Later funding reallocation reported','treasury2025','2025-11-19','Not initial allocation or project approval; need dated decision history']
],columns=['stream','reported_pool_aud','ordinary_project_cap_aud','rule_or_change','source_id','document_date','analytical_implication']);policy['source_url']=policy.source_id.map(urls);save(policy,'policy_and_unit_audit')
gates=pd.DataFrame([
 [1,'Eligible approved applications identifiable','PARTIAL','Official award labels for 194 council asset/works rows across 38 councils; no unique application IDs or separate eligibility files'],
 [2,'Eligible unsuccessful applications identifiable','NOT PASSED','Zero verified eligible unsuccessful 2022 local-government applications; Boulia ineligible, TMR outside population, Somerset wrong round'],
 [3,'Consistent outcome across applications','NOT PASSED','Need unique projects, eligibility, decision cutoff and revision/reconsideration histories; published row is not application'],
 [4,'Enough outcomes across distinct councils','NOT PASSED','No certified negative councils; 38 award councils cannot establish effective two-class sample size'],
 [5,'Independent need/project quality adequate','NOT PASSED','Criteria known, application-level damage/CBA/quality evidence absent for both outcome classes'],
 [6,'Comparable pre-decision capacity available','PARTIAL','Three QAO measures recovered for 39 identified councils; additional components pilot-only, dates and scope unresolved']
],columns=['gate','question','verdict','evidence']);save(gates,'feasibility_gates')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
def finish(fig,name):fig.tight_layout();fig.savefig(FIG/(name+'.png'),dpi=145,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(10,9));v=summary.sort_values('published_rows');ax.barh(v.applicant.str.replace(' Council','',regex=False),v.published_rows,color='#286d82');ax.set(title='Published approved asset rows are clustered within councils',xlabel='Rows in QRA list (not unique applications or independent decisions)');finish(fig,'01_council_clustering')
fig,ax=plt.subplots(figsize=(10,4));x=cap_avail.iloc[::-1];ax.barh(x.capacity_block,x.councils_with_pilot_values,color='#286d82');ax.set(xlim=(0,42),xlabel='Identified councils with some recovered values (out of 39)',title='Capacity construction: core ratios versus limited pilots');
for i,n in enumerate(x.councils_with_pilot_values):ax.text(n+.4,i,str(n),va='center')
finish(fig,'02_capacity_coverage')
fig,ax=plt.subplots(figsize=(10,4));labels=['Approved list: council asset rows','Councils named in approved list','Verified eligible unsuccessful cases','Certified model-ready applications'];vals=[len(lg),len(summary),0,0];ax.barh(labels[::-1],vals[::-1],color=['#aa543f','#aa543f','#286d82','#286d82']);ax.set(xlim=(0,220),xlabel='Count — different units explicitly labelled; not a success rate',title='The public list does not supply the eligible comparison group');
for i,n in enumerate(vals[::-1]):ax.text(n+2,i,str(n),va='center')
finish(fig,'03_decision_gap')
checks=dict(existing_files_unchanged=frozen_check(),reported_submissions=123,reported_council_applicants=39,published_rows=len(projects),published_D_rows=int(projects.funding_stream.eq('D').sum()),published_E_rows=int(projects.funding_stream.eq('E').sum()),public_local_government_rows=len(lg),public_state_agency_rows=len(projects)-len(lg),award_councils=len(summary),repeated_label_groups=int(projects.loc[projects.repeated_label].groupby(keys).ngroups),distinct_published_labels=len(projects.drop_duplicates(keys)),capacity_councils=len(qao),capacity_numeric_values=len(capacity),known_eligible_unsuccessful_localgov_2022=0,model_ready_applications=0,models_fitted=0,overall_verdict='CONDITIONAL GO — data acquisition only')
(OUT/'validation_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
