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

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
    csp_keys = pd.MultiIndex.from_frame(csp[key])
    riemann_keys = pd.MultiIndex.from_frame(riem[key])
    missing_from_riemann = csp_keys.difference(riemann_keys)
    missing_from_csp = riemann_keys.difference(csp_keys)
    if len(missing_from_riemann) or len(missing_from_csp):
        raise ValueError(
            'Decoder summaries contain different subject-condition pairs '
            f'(missing from Riemann-LR: {len(missing_from_riemann)}; '
            f'missing from CSP-LDA: {len(missing_from_csp)})'
        )
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


def tex_table(df: pd.DataFrame) -> str:
    """Render the comparison table without pandas' optional Jinja2 dependency."""
    cols = [
        'condition', 'n_subjects', 'mean_paired_difference_csp_minus_riemann',
        'ci95_low', 'ci95_high', 'cohens_dz', 'paired_t_p_value_bh_fdr',
        'wilcoxon_p_value_bh_fdr', 'proportion_csp_better',
    ]

    def escape(value: object) -> str:
        replacements = {
            '\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
            '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
            '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
        }
        return ''.join(replacements.get(char, char) for char in str(value))

    rows = []
    for row in df[cols].itertuples(index=False, name=None):
        cells = []
        for index, value in enumerate(row):
            if pd.isna(value):
                cells.append('NA')
            elif index >= 2:
                cells.append(f'{float(value):.3f}')
            else:
                cells.append(escape(value))
        rows.append(' & '.join(cells) + r' \\')

    header = ' & '.join(escape(column) for column in cols) + r' \\'
    return '\n'.join([
        r'\begin{table}',
        r'\caption{Subject-paired ROC-AUC comparison of CSP-LDA and Riemann-LR.}',
        r'\label{tab:pipeline-comparison}',
        r'\begin{tabular}{lrrrrrrrr}',
        r'\toprule',
        header,
        r'\midrule',
        *rows,
        r'\bottomrule',
        r'\end{tabular}',
        r'\end{table}',
        '',
    ])


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


def paired_comparison_figure(table: pd.DataFrame, output: Path) -> None:
    """Write the manuscript comparison figure from the current paired table."""
    order = [
        "clean", "dropout_0.1", "dropout_0.2", "dropout_0.3", "dropout_0.5",
        "motor_core", "motor_extended", "region_left_motor_strip",
        "region_midline_motor_strip", "region_right_motor_strip",
    ]
    labels = {
        "clean": "Clean", "dropout_0.1": "Dropout 10%",
        "dropout_0.2": "Dropout 20%", "dropout_0.3": "Dropout 30%",
        "dropout_0.5": "Dropout 50%", "motor_core": "Motor core",
        "motor_extended": "Motor extended",
        "region_left_motor_strip": "Left motor strip",
        "region_midline_motor_strip": "Midline motor strip",
        "region_right_motor_strip": "Right motor strip",
    }
    plot = table.set_index("condition").reindex(order).dropna(subset=["mean_paired_difference_csp_minus_riemann"])
    y = np.arange(len(plot))
    mean = plot["mean_paired_difference_csp_minus_riemann"].to_numpy(float)
    low = plot["ci95_low"].to_numpy(float)
    high = plot["ci95_high"].to_numpy(float)
    fig, ax = plt.subplots(figsize=(6.4, 4.8), layout="constrained")
    ax.errorbar(mean, y, xerr=np.vstack([mean - low, high - mean]), fmt="o", color="#1f5a7a",
                ecolor="#444444", elinewidth=1.1, capsize=2.5, markersize=4.5)
    ax.axvline(0.0, color="#777777", linewidth=0.8, linestyle="--")
    ax.set_yticks(y, [labels.get(condition, condition) for condition in plot.index])
    ax.invert_yaxis()
    ax.set_xlabel("Paired ROC-AUC difference (CSP-LDA minus Riemann-LR)")
    ax.grid(axis="x", color="#dddddd", linewidth=0.5)
    ax.spines[["top", "right", "left"]].set_visible(False)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=Path, default=Path("results"))
    ap.add_argument("--reports-dir", type=Path, default=Path("reports"))
    ap.add_argument("--csp-prefix", default="PhysionetMI_PhysionetMI_all_csp_lda")
    ap.add_argument("--riemann-prefix", default="PhysionetMI_PhysionetMI_all_riemann_lr")
    ap.add_argument("--output-prefix", default="PhysionetMI_csp_lda_vs_riemann_lr")
    ap.add_argument("--figure-output", type=Path, default=None)
    args = ap.parse_args()

    csp_path = args.results_dir / f"{args.csp_prefix}_subject_summary.csv"
    riemann_path = args.results_dir / f"{args.riemann_prefix}_subject_summary.csv"
    csp = pd.read_csv(csp_path)
    riemann = pd.read_csv(riemann_path)
    table, pairs, notes = compare(csp, riemann)
    degradation, degradation_subjects = difference_in_degradation(pairs)
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    if args.figure_output is not None:
        paired_comparison_figure(table, args.figure_output)

    csv_path = args.results_dir / f"{args.output_prefix}_paired_comparison.csv"
    pair_path = args.results_dir / f"{args.output_prefix}_paired_subject_differences.csv"
    degradation_path = args.results_dir / f"{args.output_prefix}_difference_in_degradation.csv"
    degradation_subject_path = args.results_dir / f"{args.output_prefix}_difference_in_degradation_subjects.csv"
    tex_path = args.reports_dir / f"{args.output_prefix}_paired_comparison.tex"
    markdown_path = args.reports_dir / f"{args.output_prefix}_paired_comparison.md"
    validation_path = args.reports_dir / f"{args.output_prefix}_validation.json"
    manifest_path = args.results_dir / f"{args.output_prefix}_manifest.json"

    table.to_csv(csv_path, index=False)
    pairs.assign(
        paired_difference_csp_minus_riemann=pairs.roc_auc_csp - pairs.roc_auc_riemann
    ).to_csv(pair_path, index=False)
    degradation.to_csv(degradation_path, index=False)
    degradation_subjects.to_csv(degradation_subject_path, index=False)
    tex_path.write_text(tex_table(table), encoding="utf-8")

    limitation = (
        "The comparison is offline and subject-paired. Named left, midline, and "
        "right regional-dropout conditions were matched directly; no missing "
        "observations were imputed."
    )
    markdown = (
        "# Paired decoder comparison\n\n"
        "Positive differences favor CSP-LDA. Tests are subject-paired; "
        "Benjamini-Hochberg correction is across compared conditions.\n\n"
        f"{dataframe_to_markdown(table)}\n\n"
        f"## Limitation\n\n{limitation}\n"
    )
    markdown_path.write_text(markdown, encoding="utf-8")

    expected_conditions = set(condition_frame(csp)["condition"])
    validation = {
        "passed": bool(
            set(table["condition"]) == expected_conditions
            and table["n_subjects"].nunique() == 1
            and int(table["n_subjects"].iloc[0]) == int(pairs["subject"].nunique())
        ),
        "n_conditions": int(len(table)),
        "subjects_per_condition": {
            row.condition: int(row.n_subjects) for row in table.itertuples()
        },
        "harmonization_notes": notes,
        "limitation": limitation,
    }
    validation_path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "sources": [str(csp_path), str(riemann_path)],
        "outputs": [
            str(csv_path), str(pair_path), str(degradation_path),
            str(degradation_subject_path), str(tex_path), str(markdown_path),
            str(validation_path),
        ],
        "no_imputation": True,
        "validation_passed": validation["passed"],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
