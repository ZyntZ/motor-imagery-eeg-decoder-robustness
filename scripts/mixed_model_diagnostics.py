#!/usr/bin/env python3
"""Machine-readable mixed-model assumption and influence diagnostics."""
from __future__ import annotations
import argparse, json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.formula.api import mixedlm, ols
from statsmodels.stats.diagnostic import het_breuschpagan, linear_reset


def condition_label(r):
    if r.stressor=='clean': return 'clean'
    if r.stressor=='reduced_montage': return str(r.montage)
    if r.stressor=='channel_dropout': return f'dropout_{float(r.dropout_fraction):g}'
    region=r.get('region',np.nan)
    return f"{r.stressor}_{region if pd.notna(region) else float(r.dropout_fraction):g}" if isinstance(region,float) else f'{r.stressor}_{region}'


def fit_diagnostics(df,model_id,formula):
    rows=[]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            fit=mixedlm(formula,df,groups=df.subject).fit(reml=False,method='lbfgs',maxiter=1000,disp=False)
            resid=np.asarray(fit.resid,float); fitted=np.asarray(fit.fittedvalues,float)
            exog=np.asarray(fit.model.exog,float)
            bp=het_breuschpagan(resid,exog)
            sh=stats.shapiro(resid) if 3<=len(resid)<=5000 else None
            random_var=float(np.asarray(fit.cov_re).ravel()[0]); singular=random_var < 1e-8
            rows += [
              dict(model_id=model_id,diagnostic='convergence',statistic=np.nan,p_value=np.nan,passed=bool(fit.converged),detail=f'converged={fit.converged}'),
              dict(model_id=model_id,diagnostic='singularity',statistic=random_var,p_value=np.nan,passed=not singular,detail=f'random_intercept_variance={random_var:.8g}'),
              dict(model_id=model_id,diagnostic='residual_normality_shapiro',statistic=float(sh.statistic) if sh else np.nan,p_value=float(sh.pvalue) if sh else np.nan,passed=bool(sh and sh.pvalue>=.05),detail='Diagnostic only; mixed-model inference does not require raw outcomes to be normal.'),
              dict(model_id=model_id,diagnostic='homoscedasticity_breusch_pagan',statistic=float(bp[0]),p_value=float(bp[1]),passed=bool(bp[1]>=.05),detail='Null hypothesis: constant residual variance.'),
            ]
            # Subject-cluster influence: largest deletion change relative to full coefficient.
            terms=[t for t in fit.fe_params.index if t!='Intercept']; target=terms[-1] if terms else 'Intercept'; full=float(fit.fe_params[target]); changes=[]
            for subject in sorted(df.subject.unique()):
                try:
                    loo=mixedlm(formula,df[df.subject.ne(subject)],groups=df.loc[df.subject.ne(subject),'subject']).fit(reml=False,method='lbfgs',maxiter=500,disp=False)
                    changes.append((subject,abs(float(loo.fe_params[target])-full)))
                except Exception: pass
            if changes:
                sid,delta=max(changes,key=lambda z:z[1]); scale=abs(full) if abs(full)>1e-12 else 1.0
                rows.append(dict(model_id=model_id,diagnostic='leave_one_subject_out_influence',statistic=float(delta),p_value=np.nan,passed=bool(delta/scale<.2),detail=f'max coefficient change for {target}; subject={sid}; relative_change={delta/scale:.4g}'))
            if caught:
                rows.append(dict(model_id=model_id,diagnostic='fit_warnings',statistic=len(caught),p_value=np.nan,passed=False,detail=' | '.join(sorted(set(str(w.message) for w in caught)))))
        except Exception as exc:
            rows.append(dict(model_id=model_id,diagnostic='model_fit',statistic=np.nan,p_value=np.nan,passed=False,detail=f'{type(exc).__name__}: {exc}'))
    return rows


def diagnose(df):
    df=df[np.isfinite(df.roc_auc)].copy(); df['condition']=df.apply(condition_label,axis=1)
    rows=fit_diagnostics(df,'all_conditions',"roc_auc ~ C(condition, Treatment(reference='clean'))")
    dose=df[df.stressor.isin(['clean','channel_dropout'])].copy(); dose.dropout_fraction=dose.dropout_fraction.astype(float)
    rows+=fit_diagnostics(dose,'channel_dropout_linear','roc_auc ~ dropout_fraction')
    # Formal linearity sensitivity: quadratic term and RESET on subject-demeaned outcomes.
    dose['roc_auc_within_subject']=dose.roc_auc-dose.groupby('subject').roc_auc.transform('mean')
    dose['dropout_within_subject']=dose.dropout_fraction-dose.groupby('subject').dropout_fraction.transform('mean')
    quad=ols('roc_auc_within_subject ~ dropout_within_subject + I(dropout_within_subject ** 2)',dose).fit(cov_type='cluster',cov_kwds={'groups':dose.subject})
    qp=float(quad.pvalues['I(dropout_within_subject ** 2)'])
    lin=ols('roc_auc_within_subject ~ dropout_within_subject',dose).fit(cov_type='cluster',cov_kwds={'groups':dose.subject})
    reset=linear_reset(lin,power=2,use_f=True,cov_type='HC3')
    rows += [dict(model_id='channel_dropout_linearity',diagnostic='quadratic_term',statistic=float(quad.tvalues['I(dropout_within_subject ** 2)']),p_value=qp,passed=qp>=.05,detail='Cluster-robust subject-demeaned quadratic sensitivity test.'),dict(model_id='channel_dropout_linearity',diagnostic='ramsey_reset',statistic=float(reset.fvalue),p_value=float(reset.pvalue),passed=float(reset.pvalue)>=.05,detail='RESET test of linear functional form; sensitivity diagnostic.')]
    return pd.DataFrame(rows)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--results-dir',type=Path,default=Path('results')); ap.add_argument('--prefix',required=True); a=ap.parse_args()
    df=pd.read_csv(a.results_dir/f'{a.prefix}_subject_summary.csv'); out=diagnose(df); csv=a.results_dir/f'{a.prefix}_mixed_model_diagnostics.csv'; js=a.results_dir/f'{a.prefix}_mixed_model_diagnostics_summary.json'; out.to_csv(csv,index=False)
    summary={'prefix':a.prefix,'n_diagnostics':len(out),'n_failed_diagnostics':int((~out.passed).sum()),'all_models_fit':not out.diagnostic.eq('model_fit').any(),'interpretation':'Failed assumption diagnostics require robust/sensitivity interpretation; they do not automatically invalidate observed paired effects.','output':str(csv)}; js.write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
