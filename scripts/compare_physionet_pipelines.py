#!/usr/bin/env python3
"""Subject-paired comparison of full PhysioNet decoder outputs.

Only observed subject-level summaries are used. Named region-dropout conditions are
matched directly between decoders; no regional rows are averaged or imputed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import beta
from statsmodels.stats.multitest import multipletests


def condition_frame(df: pd.DataFrame) -> pd.DataFrame:
    out=df.copy()
    def label(r):
        s=str(r.stressor); f=float(r.dropout_fraction)
        if s=='clean': return 'clean'
        if s=='channel_dropout': return f'dropout_{f:g}'
        if s=='reduced_montage': return str(r.montage)
        if s=='region_dropout':
            if 'region' in r.index and pd.notna(r.get('region')):
                return f"region_{r.region}"
            return f'region_fraction_{f:g}'
        return f'{s}_{f:g}'
    out['condition']=out.apply(label,axis=1)
    return out



def proportion_ci(k,n,alpha=.05):
    if not n: return np.nan,np.nan
    return (0.0 if k==0 else float(beta.ppf(alpha/2,k,n-k+1)),
            1.0 if k==n else float(beta.ppf(1-alpha/2,k+1,n-k)))


def compare(csp,riem):
    csp=condition_frame(csp); riem=condition_frame(riem)
    notes=['Named region-dropout conditions were matched directly; no regional rows were averaged or imputed.']
    key=['subject','condition']
    if csp.duplicated(key).any() or riem.duplicated(key).any(): raise ValueError('Non-unique subject-condition rows after harmonization')
    m=csp[key+['roc_auc']].merge(riem[key+['roc_auc']],on=key,suffixes=('_csp','_riemann'),validate='one_to_one')
    rows=[]
    for cond,g in m.groupby('condition',sort=True):
        g=g.dropna(); d=g.roc_auc_csp-g.roc_auc_riemann; n=len(d)
        if n<2: continue
        mean=float(d.mean()); sd=float(d.std(ddof=1)); se=sd/np.sqrt(n)
        ci=stats.t.interval(.95,n-1,loc=mean,scale=se)
        tt=stats.ttest_rel(g.roc_auc_csp,g.roc_auc_riemann)
        try: w=stats.wilcoxon(d,zero_method='wilcox'); ws,wp=float(w.statistic),float(w.pvalue)
        except ValueError: ws=wp=np.nan
        k=int((d>0).sum()); ties=int((d==0).sum()); lo,hi=proportion_ci(k,n)
        rows.append(dict(condition=cond,n_subjects=n,mean_auc_csp=float(g.roc_auc_csp.mean()),mean_auc_riemann=float(g.roc_auc_riemann.mean()),mean_paired_difference_csp_minus_riemann=mean,ci95_low=float(ci[0]),ci95_high=float(ci[1]),paired_t_statistic=float(tt.statistic),paired_t_p_value=float(tt.pvalue),wilcoxon_statistic=ws,wilcoxon_p_value=wp,cohens_dz=mean/sd if sd>0 else np.nan,n_csp_better=k,n_riemann_better=int((d<0).sum()),n_ties=ties,proportion_csp_better=k/n,proportion_csp_better_ci95_low=lo,proportion_csp_better_ci95_high=hi,shapiro_p_value=float(stats.shapiro(d).pvalue) if 3<=n<=5000 else np.nan))
    out=pd.DataFrame(rows)
    for p in ['paired_t_p_value','wilcoxon_p_value']:
        mask=out[p].notna(); out.loc[mask,p+'_bh_fdr']=multipletests(out.loc[mask,p],method='fdr_bh')[1]
    return out,m,sorted(set(notes))


def difference_in_degradation(pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compare within-subject changes from each decoder's clean baseline.

    Negative values mean CSP-LDA lost more ROC-AUC than Riemann-LR relative
    to the same subject's clean result.
    """
    clean = pairs.loc[pairs["condition"].eq("clean"), ["subject", "roc_auc_csp", "roc_auc_riemann"]].rename(
        columns={"roc_auc_csp": "clean_auc_csp", "roc_auc_riemann": "clean_auc_riemann"}
    )
    nonclean = pairs.loc[~pairs["condition"].eq("clean")].merge(clean, on="subject", validate="many_to_one")
    nonclean["change_csp"] = nonclean["roc_auc_csp"] - nonclean["clean_auc_csp"]
    nonclean["change_riemann"] = nonclean["roc_auc_riemann"] - nonclean["clean_auc_riemann"]
    nonclean["difference_in_degradation_csp_minus_riemann"] = nonclean["change_csp"] - nonclean["change_riemann"]
    rows = []
    for condition, group in nonclean.groupby("condition", sort=True):
        values = group["difference_in_degradation_csp_minus_riemann"].dropna().astype(float)
        n = len(values)
        if n < 2:
            continue
        mean = float(values.mean())
        sd = float(values.std(ddof=1))
        se = sd / np.sqrt(n)
        ci_low, ci_high = stats.t.interval(0.95, n - 1, loc=mean, scale=se)
        t_test = stats.ttest_1samp(values, 0.0)
        try:
            wilcoxon = stats.wilcoxon(values, zero_method="wilcox")
            w_stat, w_p = float(wilcoxon.statistic), float(wilcoxon.pvalue)
        except ValueError:
            w_stat = w_p = np.nan
        rows.append({
            "condition": condition,
            "n_subjects": n,
            "mean_change_csp": float(group.loc[values.index, "change_csp"].mean()),
            "mean_change_riemann": float(group.loc[values.index, "change_riemann"].mean()),
            "mean_difference_in_degradation_csp_minus_riemann": mean,
            "ci95_low": float(ci_low),
            "ci95_high": float(ci_high),
            "cohens_dz": mean / sd if sd > 0 else np.nan,
            "paired_t_statistic": float(t_test.statistic),
            "paired_t_p_value": float(t_test.pvalue),
            "wilcoxon_statistic": w_stat,
            "wilcoxon_p_value": w_p,
            "shapiro_p_value": float(stats.shapiro(values).pvalue) if 3 <= n <= 5000 else np.nan,
        })
    summary = pd.DataFrame(rows)
    for column in ["paired_t_p_value", "wilcoxon_p_value"]:
        mask = summary[column].notna()
        summary.loc[mask, column + "_bh_fdr"] = multipletests(summary.loc[mask, column], method="fdr_bh")[1]
    return summary, nonclean


def tex_table(df):
    cols=['condition','n_subjects','mean_paired_difference_csp_minus_riemann','ci95_low','ci95_high','cohens_dz','paired_t_p_value_bh_fdr','wilcoxon_p_value_bh_fdr','proportion_csp_better']
    x=df[cols].copy()
    for c in cols[2:]: x[c]=x[c].map(lambda v:'NA' if pd.isna(v) else f'{v:.3f}')
    return x.to_latex(index=False,escape=True,caption='Subject-paired ROC-AUC comparison of CSP-LDA and Riemann-LR.',label='tab:pipeline-comparison')


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Render a GitHub-flavored Markdown table without optional dependencies."""
    def cell(value: object) -> str:
        if pd.isna(value):
            return "NA"
        if isinstance(value, (float, np.floating)):
            return f"{float(value):.6g}"
        return str(value).replace("|", "\\|").replace("\n", " ")

    headers = [str(column) for column in df.columns]
    rows = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    rows.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in df.itertuples(index=False, name=None))
    return "\n".join(rows)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--results-dir',type=Path,default=Path('results')); ap.add_argument('--reports-dir',type=Path,default=Path('reports')); ap.add_argument('--csp-prefix',default='PhysionetMI_PhysionetMI_all_csp_lda'); ap.add_argument('--riemann-prefix',default='PhysionetMI_PhysionetMI_all_riemann_lr'); ap.add_argument('--output-prefix',default='PhysionetMI_csp_lda_vs_riemann_lr'); a=ap.parse_args()
    c=pd.read_csv(a.results_dir/f'{a.csp_prefix}_subject_summary.csv'); r=pd.read_csv(a.results_dir/f'{a.riemann_prefix}_subject_summary.csv')
    table,pairs,notes=compare(c,r); degradation,degradation_subjects=difference_in_degradation(pairs); a.reports_dir.mkdir(parents=True,exist_ok=True)
    csv=a.results_dir/f'{a.output_prefix}_paired_comparison.csv'; paircsv=a.results_dir/f'{a.output_prefix}_paired_subject_differences.csv'; degradation_csv=a.results_dir/f'{a.output_prefix}_difference_in_degradation.csv'; degradation_subject_csv=a.results_dir/f'{a.output_prefix}_difference_in_degradation_subjects.csv'; tex=a.reports_dir/f'{a.output_prefix}_paired_comparison.tex'; md=a.reports_dir/f'{a.output_prefix}_paired_comparison.md'; val=a.reports_dir/f'{a.output_prefix}_validation.json'; manifest=a.results_dir/f'{a.output_prefix}_manifest.json'
    table.to_csv(csv,index=False); pairs.assign(paired_difference_csp_minus_riemann=pairs.roc_auc_csp-pairs.roc_auc_riemann).to_csv(paircsv,index=False); degradation.to_csv(degradation_csv,index=False); degradation_subjects.to_csv(degradation_subject_csv,index=False); tex.write_text(tex_table(table),encoding='utf-8')
    limitation=('The comparison is offline and subject-paired. Named left, midline, and right regional-dropout conditions were matched directly; no missing observations were imputed.')
    md.write_text('# Paired decoder comparison\n\nPositive differences favor CSP-LDA. Tests are subject-paired; Benjamini-Hochberg correction is across compared conditions.\n\n'+dataframe_to_markdown(table)+'\n\n## Limitation\n\n'+limitation+'\n',encoding='utf-8')
    validation={'passed':bool(len(table)==10 and table.n_subjects.eq(109).all()),'n_conditions':int(len(table)),'subjects_per_condition':{x.condition:int(x.n_subjects) for x in table.itertuples()},'harmonization_notes':notes,'limitation':limitation}
    val.write_text(json.dumps(validation,indent=2)+'\n'); manifest.write_text(json.dumps({'sources':[str(a.results_dir/f'{a.csp_prefix}_subject_summary.csv'),str(a.results_dir/f'{a.riemann_prefix}_subject_summary.csv')],'outputs':[str(csv),str(paircsv),str(degradation_csv),str(degradation_subject_csv),str(tex),str(md),str(val)],'no_imputation':True,'validation_passed':validation['passed']},indent=2)+'\n')
    print(json.dumps(validation,indent=2));
    if not validation['passed']: raise SystemExit(1)
if __name__=='__main__': main()
