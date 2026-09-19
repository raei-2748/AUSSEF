"""Validate curated source transcriptions and rebuild descriptive pilot outputs. No models."""
from pathlib import Path
import json,hashlib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=next(p for p in [Path(__file__).resolve().parent,*Path(__file__).resolve().parents] if (p/'NSW Data Panel.csv').exists())
DEFAULT_OUTPUT=ROOT/'Experiment 4/results'

def build(folder=None):
    out=Path(folder) if folder else DEFAULT_OUTPUT
    chains=pd.read_csv(out/'budget_chains.csv')
    projects=pd.read_csv(out/'project_revision_register.csv')
    decisions=pd.read_csv(out/'decision_dates.csv')
    assert not chains.duplicated(['council_key','year_start','category_id']).any()
    assert not projects.project_record_id.duplicated().any()
    assert not chains.causal_eligible.any()
    assert chains.ACTUAL_aud.isna().all()  # Never insert unrelated annual cash totals.
    stages=['B0','Q1','Q2','Q3','ACTUAL']
    long=[]
    for _,r in chains.iterrows():
        for stage in stages:
            long.append(dict(council_key=r.council_key,financial_year=r.financial_year,year_start=r.year_start,
                category_id=r.category_id,category_label=r.category_label,stage=stage,
                amount_aud=r[stage+'_aud'],value_status=r[stage+'_status'],
                source_id=r[stage+'_source_id'],source_page=r[stage+'_page'],source_url=r[stage+'_source_url'],
                quality_status=r.quality_status,scope_class=r.scope_class,causal_eligible=False))
    long=pd.DataFrame(long)
    long=long.merge(decisions[['council_key','year_start','stage','reference_period_end','decision_date','decision_status']],
                    on=['council_key','year_start','stage'],how='left',validate='many_to_one')
    long.loc[long.stage=='B0','decision_status']='original_column_reproduced_in_review_adoption_not_fully_audited'
    long.to_csv(out/'budget_stages_clean.csv',index=False)
    summary=chains[chains.category_label.str.contains('Total|Consolidated')].copy()
    for after,before in [('Q2','Q1'),('Q3','Q2'),('Q3','B0')]:
        summary[f'{after}_minus_{before}_aud']=summary[after+'_aud']-summary[before+'_aud']
    summary['ordinary_causal_interpretation_permitted']=False
    summary[['council_key','financial_year','category_label','B0_aud','Q1_aud','Q2_aud','Q3_aud','ACTUAL_aud',
             'Q2_minus_Q1_aud','Q3_minus_Q2_aud','Q3_minus_B0_aud','quality_status',
             'ordinary_causal_interpretation_permitted']].to_csv(out/'quarterly_summary.csv',index=False)
    coverage=[]
    for c,g in chains.groupby('council_key'):
        z={'council_key':c,'category_chains':len(g),'ordinary_scope_certified':int(g.ordinary_scope_verified.sum()),
           'complete_ordinary_chains':0,'excluded_from_causal_modelling':len(g),
           'exclusion':'No certified fixed ordinary portfolio with matched year-end actual; other issues in cleaning log'}
        for st in stages:z[st+'_observed']=int(g[st+'_aud'].notna().sum());z[st+'_missing']=int(g[st+'_aud'].isna().sum())
        coverage.append(z)
    pd.DataFrame(coverage).to_csv(out/'coverage_and_exclusions.csv',index=False)
    pd.DataFrame(columns=['council_key','project_id','financial_year','stage','ordinary_budget_aud',
                          'ordinary_actual_aud','pre_event_capacity','event_date']).to_csv(out/'model_ready_ordinary_panel.csv',index=False)
    # Sum checks compare mutually exclusive categories with reported total.
    checks=[]
    for c,g in chains.groupby('council_key'):
        total=g[g.category_label.str.contains('Total|Consolidated')].iloc[0]
        detail=g[~g.category_label.str.contains('Total|Consolidated')]
        for st in stages[:4]:
            observed=total[st+'_aud']
            residual=detail[st+'_aud'].sum(min_count=1)-observed
            checks.append(dict(check='category_sum',council_key=c,stage=st,residual_aud=residual,
              status='not_testable' if pd.isna(observed) else ('pass' if residual==0 else ('rounding_flag' if abs(residual)<=1 else 'fail_retained'))))
    euro=pd.read_csv(out/'eurobodalla_source_transcription.csv')
    for _,r in euro.iterrows():
        residual=r.reported_Q3-(r.B0+r.carryover+r.Sep_change+r.Dec_change+r.Mar_change)
        if residual:
            checks.append(dict(check='euro_rollforward_'+r.code,council_key='eurobodalla',stage='Q3',residual_aud=residual,status='rounding_flag' if abs(residual)<=1 else 'fail_retained'))
    checks.append(dict(check='reported_oneoff_movement',council_key='waggawagga',stage='Q1',residual_aud=100965860-97965275-2000585,status='fail_retained'))
    checks.append(dict(check='QBR_original_vs_audited_original',council_key='griffith',stage='B0',residual_aud=40933000-40932455,status='fail_retained'))
    pd.DataFrame(checks).to_csv(out/'reconciliation_checks.csv',index=False)
    # Data are descriptive and have different scopes. Do not draw lines to annual cash actuals.
    names={'richmondvalley':'Richmond Valley','lismore':'Lismore','eurobodalla':'Eurobodalla','griffith':'Griffith','waggawagga':'Wagga Wagga'}
    fig,axes=plt.subplots(2,3,figsize=(13,7))
    for ax,(_,r) in zip(axes.flat,summary.iterrows()):
        vals=np.array([r.B0_aud,r.Q1_aud,r.Q2_aud,r.Q3_aud])/1e6
        ax.plot(range(4),vals,'o--' if r.council_key=='lismore' else 'o-',color='#247383')
        ax.set_xticks(range(4),['Original','Q1','Q2','Q3'])
        ax.set_title(names[r.council_key]+' '+r.financial_year)
        ax.set_ylabel('Reported budget (AUD million)');ax.grid(axis='y',alpha=.2)
        ax.text(.03,.04,'Provisional units / source conflicts' if r.council_key=='lismore' else
                ('Q3 proposal; approval unverified' if r.council_key=='eurobodalla' else
                 ('Original same-basis budget missing' if r.council_key=='waggawagga' else 'Mixed capital scope')),
                transform=ax.transAxes,fontsize=8)
    axes.flat[-1].axis('off')
    axes.flat[-1].text(0,.8,'Descriptive source budgets only\n\nDifferent council scopes.\nNo matched ordinary year-end actuals.\nNo causal effect estimated.\nQBR adoption occurs after quarter end.',va='top')
    fig.suptitle('Budget revisions can be recovered; ordinary-spending outcomes remain unverified')
    fig.tight_layout();fig.savefig(out/'budget_paths.png',dpi=160);plt.close(fig)
    # Check every pre-existing file against pre-pilot hash; additions allowed.
    # The repository was later grouped into Experiment 1-4 folders, so legacy
    # manifest paths are translated to their current locations before hashing.
    frozen=json.loads((out/'frozen_existing_sha256.json').read_text())
    moved_prefixes={
        'outputs/experiment3_crowdout/':'Experiment 3/results/',
        'outputs/experiment4_budget_deviation_audit/':'Experiment 4/audit/results/',
        'outputs/experiment4_funding_access_feasibility/':'Experiment 4/related/funding_access/results/',
        'outputs/experiment4b_betterment_access/':'Experiment 4/related/betterment_access/results/',
    }
    moved_files={
        '05_experiment3_crowdout.ipynb':'Experiment 3/experiment.ipynb',
        '06_experiment4_funding_access_feasibility.ipynb':'Experiment 4/related/funding_access/experiment.ipynb',
        '07_experiment4b_betterment_access.ipynb':'Experiment 4/related/betterment_access/experiment.ipynb',
        '08_experiment4_budget_deviation_audit.ipynb':'Experiment 4/audit/experiment.ipynb',
    }
    def current_path(rel):
        if rel in moved_files:
            return ROOT/moved_files[rel]
        for old,new in moved_prefixes.items():
            if rel.startswith(old):
                return ROOT/(new+rel[len(old):])
        return ROOT/rel
    changed=[]
    for rel,digest in frozen.items():
        p=current_path(rel)
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(rel)
    expected_path_updates={
        'README.md',
        '05_experiment3_crowdout.ipynb',
        '06_experiment4_funding_access_feasibility.ipynb',
        '07_experiment4b_betterment_access.ipynb',
        '08_experiment4_budget_deviation_audit.ipynb',
        'outputs/experiment3_crowdout/README.md',
        'outputs/experiment3_crowdout/acquire_sources.py',
        'outputs/experiment3_crowdout/build_workflow.py',
        'outputs/experiment3_crowdout/screen_comparisons.py',
        'outputs/experiment4_budget_deviation_audit/README.md',
        'outputs/experiment4_budget_deviation_audit/audit.py',
        'outputs/experiment4_funding_access_feasibility/README.md',
        'outputs/experiment4_funding_access_feasibility/build_audit.py',
        'outputs/experiment4b_betterment_access/README.md',
        'outputs/experiment4b_betterment_access/build_audit.py',
    }
    unexpected_changes=sorted(set(changed)-expected_path_updates)
    manifest=[{'file':str(p.relative_to(out)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
              for p in sorted((out/'sources').iterdir()) if p.is_file()]
    pd.DataFrame(manifest).to_csv(out/'source_hashes.csv',index=False)
    result={'councils':int(chains.council_key.nunique()),'category_chains':len(chains),'stage_records':len(long),
            'observed_stage_values':int(long.amount_aud.notna().sum()),'missing_stage_values':int(long.amount_aud.isna().sum()),
            'project_revision_records':len(projects),'certified_ordinary_model_rows':0,'models_fitted':0,
            'frozen_files_checked':len(frozen),'frozen_path_updates':sorted(set(changed)&expected_path_updates),
            'frozen_files_changed':unexpected_changes,'source_files_hashed':len(manifest),
            'known_source_errors_retained':2,'verdict':'NO-GO for causal modelling/scaling on current reconstructed data'}
    (out/'validation_checks.json').write_text(json.dumps(result,indent=2))
    assert not unexpected_changes,unexpected_changes
    return result
if __name__=='__main__':
    print(json.dumps(build(),indent=2))
