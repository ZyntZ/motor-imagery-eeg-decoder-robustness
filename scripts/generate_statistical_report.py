#!/usr/bin/env python3
"""Statistical reporting summaries for intervention-robust EEG benchmark outputs.

This script intentionally consumes existing benchmark CSV files only. It does not
simulate, resample, or generate new benchmark observations. Outputs are derived
from subject-level summaries and are intended to support manuscript methods,
results tables, and methods-audit reproducibility checks.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

METRICS = ["roc_auc", "balanced_accuracy", "brier_score", "ece"]
BENEFIT_METRICS = {"roc_auc", "balanced_accuracy"}
COST_METRICS = {"brier_score", "ece"}
KEY_COLS = ["dataset", "subject", "pipeline", "stressor", "montage", "dropout_fraction"]


def require_columns(df: pd.DataFrame, columns: set[str], source: Path | str = "dataframe") -> None:
    missing = columns - set(df.columns)
    if missing:
        raise ValueError(f"{source} is missing required columns: {sorted(missing)}")


def load_subject_summary(results_dir: Path, prefix: str) -> pd.DataFrame:
    path = results_dir / f"{prefix}_subject_summary.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    require_columns(df, set(KEY_COLS) | {"roc_auc", "balanced_accuracy"}, path)
    for metric in METRICS:
        if metric not in df.columns:
            df[metric] = np.nan
    if df.duplicated(KEY_COLS).any():
        dup = df.loc[df.duplicated(KEY_COLS, keep=False), KEY_COLS].head().to_dict("records")
        raise ValueError(f"Subject summary contains duplicate subject-condition rows; examples: {dup}")
    return df


def condition_label(row: pd.Series) -> str:
    if row["stressor"] == "clean":
        return "clean_all_channels"
    if row["stressor"] == "reduced_montage":
        return f"reduced_montage_{row['montage']}"
    frac = float(row["dropout_fraction"])
    return f"{row['stressor']}_{frac:g}"


def add_condition(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["condition"] = out.apply(condition_label, axis=1)
    return out


def t_ci_mean(x: pd.Series | np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    arr = np.asarray(x, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size < 2:
        return np.nan, np.nan
    mean = float(arr.mean())
    se = float(arr.std(ddof=1) / np.sqrt(arr.size))
    lo, hi = stats.t.interval(1 - alpha, arr.size - 1, loc=mean, scale=se)
    return float(lo), float(hi)


def paired_condition_effects(subj: pd.DataFrame) -> pd.DataFrame:
    subj = add_condition(subj)
    clean = subj[subj["condition"] == "clean_all_channels"].set_index("subject")
    if clean.empty:
        raise ValueError("No clean all-channel baseline rows found.")
    rows: list[dict[str, object]] = []
    for condition in sorted(c for c in subj["condition"].dropna().unique() if c != "clean_all_channels"):
        cond = subj[subj["condition"] == condition].set_index("subject")
        common = clean.index.intersection(cond.index)
        meta = cond.iloc[0]
        for metric in METRICS:
            d = pd.DataFrame({"clean": clean.loc[common, metric], "condition": cond.loc[common, metric]}).dropna()
            if len(d) < 2:
                continue
            diff = d["condition"] - d["clean"]
            lo, hi = t_ci_mean(diff)
            ttest = stats.ttest_1samp(diff, 0.0)
            try:
                wil = stats.wilcoxon(diff, zero_method="wilcox", alternative="two-sided")
                wilcoxon_stat = float(wil.statistic)
                wilcoxon_p = float(wil.pvalue)
            except ValueError:
                wilcoxon_stat = np.nan
                wilcoxon_p = np.nan
            shapiro_p = float(stats.shapiro(diff).pvalue) if 3 <= len(diff) <= 5000 else np.nan
            sd = float(diff.std(ddof=1))
            if metric in BENEFIT_METRICS:
                worse = int((diff < 0).sum())
            else:
                worse = int((diff > 0).sum())
            rows.append(
                {
                    "condition": condition,
                    "stressor": meta["stressor"],
                    "montage": meta["montage"],
                    "dropout_fraction": float(meta["dropout_fraction"]),
                    "metric": metric,
                    "n_subjects": int(len(d)),
                    "clean_mean": float(d["clean"].mean()),
                    "condition_mean": float(d["condition"].mean()),
                    "mean_delta_condition_minus_clean": float(diff.mean()),
                    "delta_ci_low": lo,
                    "delta_ci_high": hi,
                    "delta_sd": sd,
                    "cohens_dz": float(diff.mean() / sd) if sd > 0 else np.nan,
                    "t_statistic": float(ttest.statistic),
                    "t_p_value": float(ttest.pvalue),
                    "wilcoxon_statistic": wilcoxon_stat,
                    "wilcoxon_p_value": wilcoxon_p,
                    "shapiro_p_value_delta": shapiro_p,
                    "n_worse_than_clean": worse,
                    "pct_worse_than_clean": float(worse / len(d)),
                }
            )
    out = pd.DataFrame(rows)
    for col in ["t_p_value", "wilcoxon_p_value"]:
        if col in out and out[col].notna().any():
            mask = out[col].notna()
            out.loc[mask, f"{col}_bh_fdr"] = multipletests(out.loc[mask, col], method="fdr_bh")[1]
    return out


def channel_dropout_slopes(subj: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    keep = subj[subj["stressor"].isin(["clean", "channel_dropout"])].copy()
    keep["dropout_fraction"] = keep["dropout_fraction"].astype(float)
    for (dataset, pipeline, subject), g in keep.groupby(["dataset", "pipeline", "subject"], dropna=False):
        # One row per fraction is expected in subject summaries. If not, average conservatively.
        agg = g.groupby("dropout_fraction", as_index=False)[METRICS].mean(numeric_only=True)
        if agg["dropout_fraction"].nunique() < 3:
            continue
        for metric in METRICS:
            d = agg[["dropout_fraction", metric]].dropna()
            if len(d) < 3:
                continue
            fit = stats.linregress(d["dropout_fraction"], d[metric])
            rows.append(
                {
                    "dataset": dataset,
                    "pipeline": pipeline,
                    "subject": subject,
                    "metric": metric,
                    "n_conditions": int(len(d)),
                    "slope_per_100pct_dropout": float(fit.slope),
                    "slope_per_10pct_dropout": float(fit.slope * 0.10),
                    "intercept": float(fit.intercept),
                    "r_value": float(fit.rvalue),
                    "p_value_subject_slope": float(fit.pvalue),
                }
            )
    return pd.DataFrame(rows)


def slope_population_summary(slopes: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if slopes.empty:
        return pd.DataFrame(rows)
    for (dataset, pipeline, metric), g in slopes.groupby(["dataset", "pipeline", "metric"], dropna=False):
        vals = g["slope_per_10pct_dropout"].dropna().astype(float)
        if len(vals) < 2:
            continue
        lo, hi = t_ci_mean(vals)
        test = stats.ttest_1samp(vals, 0.0)
        shapiro_p = float(stats.shapiro(vals).pvalue) if 3 <= len(vals) <= 5000 else np.nan
        harmful = vals < 0 if metric in BENEFIT_METRICS else vals > 0
        rows.append(
            {
                "dataset": dataset,
                "pipeline": pipeline,
                "metric": metric,
                "n_subjects": int(len(vals)),
                "mean_slope_per_10pct_dropout": float(vals.mean()),
                "slope_ci_low": lo,
                "slope_ci_high": hi,
                "slope_sd": float(vals.std(ddof=1)),
                "t_statistic_vs_zero": float(test.statistic),
                "t_p_value_vs_zero": float(test.pvalue),
                "shapiro_p_value_slope": shapiro_p,
                "n_harmful_slope": int(harmful.sum()),
                "pct_harmful_slope": float(harmful.mean()),
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty and out["t_p_value_vs_zero"].notna().any():
        mask = out["t_p_value_vs_zero"].notna()
        out.loc[mask, "t_p_value_vs_zero_bh_fdr"] = multipletests(out.loc[mask, "t_p_value_vs_zero"], method="fdr_bh")[1]
    return out


def methods_audit(subj: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    numeric_metrics = [m for m in METRICS if m in subj.columns]
    key_dups = int(subj.duplicated(KEY_COLS).sum())
    rows.append({"check": "n_rows_subject_summary", "value": int(len(subj)), "status": "info"})
    rows.append({"check": "n_subjects", "value": int(subj["subject"].nunique()), "status": "info"})
    rows.append({"check": "n_conditions", "value": int(add_condition(subj)["condition"].nunique()), "status": "info"})
    rows.append({"check": "duplicate_subject_condition_rows", "value": key_dups, "status": "pass" if key_dups == 0 else "fail"})
    for metric in numeric_metrics:
        miss = int(subj[metric].isna().sum())
        rows.append({"check": f"missing_{metric}", "value": miss, "status": "pass" if miss == 0 else "review"})
        out_of_range = int(((subj[metric] < 0) | (subj[metric] > 1)).sum(skipna=True))
        rows.append({"check": f"out_of_range_0_1_{metric}", "value": out_of_range, "status": "pass" if out_of_range == 0 else "fail"})
    counts = add_condition(subj).groupby("condition")["subject"].nunique()
    rows.append({"check": "min_subjects_per_condition", "value": int(counts.min()), "status": "pass" if counts.min() == counts.max() else "review"})
    rows.append({"check": "max_subjects_per_condition", "value": int(counts.max()), "status": "info"})
    return pd.DataFrame(rows)


def report_table(paired: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "condition",
        "metric",
        "n_subjects",
        "clean_mean",
        "condition_mean",
        "mean_delta_condition_minus_clean",
        "delta_ci_low",
        "delta_ci_high",
        "cohens_dz",
        "t_p_value_bh_fdr",
        "wilcoxon_p_value_bh_fdr",
        "shapiro_p_value_delta",
        "pct_worse_than_clean",
    ]
    return paired.loc[paired["metric"].isin(["roc_auc", "balanced_accuracy"]), cols].sort_values(["metric", "condition"]).reset_index(drop=True)


def write_latex_table(table: pd.DataFrame, path: Path) -> None:
    out = table.copy()
    for c in out.select_dtypes(include=[np.number]).columns:
        if c == "n_subjects":
            continue
        out[c] = out[c].map(lambda x: "" if pd.isna(x) else f"{x:.4g}")
    path.write_text(out.to_latex(index=False, escape=True), encoding="utf-8")


def write_markdown_summary(audit: pd.DataFrame, paired: pd.DataFrame, slopes_pop: pd.DataFrame, path: Path, prefix: str) -> None:
    key = report_table(paired)
    txt = [
        f"# Statistical reporting pack for `{prefix}`",
        "",
        "Generated from existing subject-summary CSV files only; no simulated or additional benchmark observations are used.",
        "",
        "## Methods audit",
        audit.to_markdown(index=False),
        "",
        "## Paired stressor effects vs clean all-channel baseline",
        key.to_markdown(index=False),
        "",
        "## Channel-dropout slopes",
        slopes_pop.to_markdown(index=False) if not slopes_pop.empty else "No channel-dropout slope table was produced.",
        "",
        "## Statistical notes",
        "- Paired effects are computed within subject against the clean all-channel baseline.",
        "- Confidence intervals for mean paired deltas and slopes use Student t intervals.",
        "- Normality of paired deltas/slopes is screened with Shapiro-Wilk where sample size permits.",
        "- Wilcoxon signed-rank tests are reported as non-parametric sensitivity checks for paired deltas.",
        "- Benjamini-Hochberg false discovery rate correction is applied to the paired t-test and Wilcoxon p-values.",
    ]
    path.write_text("\n".join(txt), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results-dir", type=Path, default=Path("results"))
    ap.add_argument("--reports-dir", type=Path, default=Path("reports"))
    ap.add_argument("--prefix", default="PhysionetMI_PhysionetMI_all_riemann_lr")
    args = ap.parse_args()

    args.results_dir.mkdir(parents=True, exist_ok=True)
    args.reports_dir.mkdir(parents=True, exist_ok=True)

    subj = load_subject_summary(args.results_dir, args.prefix)
    audit = methods_audit(subj)
    paired = paired_condition_effects(subj)
    slopes = channel_dropout_slopes(subj)
    slopes_pop = slope_population_summary(slopes)
    table = report_table(paired)

    outputs = {
        "methods_audit": args.results_dir / f"{args.prefix}_statistical_methods_audit.csv",
        "paired_effects": args.results_dir / f"{args.prefix}_statistical_paired_effects.csv",
        "channel_dropout_subject_slopes": args.results_dir / f"{args.prefix}_statistical_channel_dropout_subject_slopes.csv",
        "channel_dropout_slope_summary": args.results_dir / f"{args.prefix}_statistical_channel_dropout_slope_summary.csv",
        "report_table_csv": args.results_dir / f"{args.prefix}_statistical_report_table.csv",
        "report_table_tex": args.reports_dir / f"{args.prefix}_statistical_report_table.tex",
        "markdown_summary": args.reports_dir / f"{args.prefix}_statistical_report_summary.md",
    }
    audit.to_csv(outputs["methods_audit"], index=False)
    paired.to_csv(outputs["paired_effects"], index=False)
    slopes.to_csv(outputs["channel_dropout_subject_slopes"], index=False)
    slopes_pop.to_csv(outputs["channel_dropout_slope_summary"], index=False)
    table.to_csv(outputs["report_table_csv"], index=False)
    write_latex_table(table, outputs["report_table_tex"])
    write_markdown_summary(audit, paired, slopes_pop, outputs["markdown_summary"], args.prefix)

    manifest = {
        "prefix": args.prefix,
        "source_csv": str(args.results_dir / f"{args.prefix}_subject_summary.csv"),
        "n_subjects": int(subj["subject"].nunique()),
        "n_subject_condition_rows": int(len(subj)),
        "outputs": {k: str(v) for k, v in outputs.items()},
        "note": "Derived from existing subject summary CSV only; no simulated data used.",
    }
    manifest_path = args.results_dir / f"{args.prefix}_statistical_report_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
