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
PRIMARY_METRIC = "roc_auc"
SECONDARY_METRICS = ["balanced_accuracy"]
CALIBRATION_METRICS = ["brier_score", "ece"]
BENEFIT_METRICS = {"roc_auc", "balanced_accuracy"}
COST_METRICS = {"brier_score", "ece"}
KEY_COLS = ["dataset", "subject", "pipeline", "stressor", "montage", "dropout_fraction"]
OPTIONAL_KEY_COLS = ["region", "session_train", "session_test"]


def effective_key(df: pd.DataFrame) -> list[str]:
    """Condition key including identifiers present in newer benchmark outputs."""
    return KEY_COLS + [c for c in OPTIONAL_KEY_COLS if c in df.columns and df[c].notna().any()]


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
    key = effective_key(df)
    if df.duplicated(key).any():
        dup = df.loc[df.duplicated(key, keep=False), key].head().to_dict("records")
        raise ValueError(f"Subject summary contains duplicate subject-condition rows; examples: {dup}")
    return df


def condition_label(row: pd.Series) -> str:
    if row["stressor"] == "clean":
        return "clean_all_channels"
    if row["stressor"] == "reduced_montage":
        return f"reduced_montage_{row['montage']}"
    frac = float(row["dropout_fraction"])
    if row["stressor"] == "region_dropout" and "region" in row.index and pd.notna(row["region"]):
        region = str(row["region"]).replace(" ", "_")
        return f"region_dropout_{region}_{frac:g}"
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


def _sign_test_p_value(diff: pd.Series | np.ndarray) -> float:
    arr = np.asarray(diff, dtype=float)
    arr = arr[np.isfinite(arr)]
    arr = arr[arr != 0]
    if arr.size == 0:
        return np.nan
    positives = int((arr > 0).sum())
    result = stats.binomtest(positives, arr.size, 0.5, alternative="two-sided")
    return float(result.pvalue)


def _median_ci_sign_free(x: pd.Series | np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """Distribution-free sign-test CI for median using order statistics."""
    arr = np.sort(np.asarray(x, dtype=float))
    arr = arr[np.isfinite(arr)]
    n = arr.size
    if n < 2:
        return np.nan, np.nan
    # smallest k such that central order-statistic interval has coverage >= 1-alpha
    k = 0
    while k <= n // 2 and 2 * stats.binom.cdf(k - 1, n, 0.5) < alpha:
        k += 1
    lo_idx = max(0, k - 1)
    hi_idx = min(n - 1, n - k)
    return float(arr[lo_idx]), float(arr[hi_idx])


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
            med_lo, med_hi = _median_ci_sign_free(diff)
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
                improved = int((diff > 0).sum())
            else:
                worse = int((diff > 0).sum())
                improved = int((diff < 0).sum())
            rows.append(
                {
                    "condition": condition,
                    "stressor": meta["stressor"],
                    "montage": meta["montage"],
                    "dropout_fraction": float(meta["dropout_fraction"]),
                    "metric": metric,
                    "metric_role": "primary" if metric == PRIMARY_METRIC else ("secondary" if metric in SECONDARY_METRICS else "calibration"),
                    "n_subjects": int(len(d)),
                    "clean_mean": float(d["clean"].mean()),
                    "condition_mean": float(d["condition"].mean()),
                    "mean_delta_condition_minus_clean": float(diff.mean()),
                    "delta_ci_low": lo,
                    "delta_ci_high": hi,
                    "median_delta_condition_minus_clean": float(diff.median()),
                    "median_delta_ci_low": med_lo,
                    "median_delta_ci_high": med_hi,
                    "delta_sd": sd,
                    "cohens_dz": float(diff.mean() / sd) if sd > 0 else np.nan,
                    "t_statistic": float(ttest.statistic),
                    "t_p_value": float(ttest.pvalue),
                    "wilcoxon_statistic": wilcoxon_stat,
                    "wilcoxon_p_value": wilcoxon_p,
                    "sign_test_p_value": _sign_test_p_value(diff),
                    "shapiro_p_value_delta": shapiro_p,
                    "n_worse_than_clean": worse,
                    "pct_worse_than_clean": float(worse / len(d)),
                    "n_better_than_clean": improved,
                    "pct_better_than_clean": float(improved / len(d)),
                }
            )
    out = pd.DataFrame(rows)
    for col in ["t_p_value", "wilcoxon_p_value", "sign_test_p_value"]:
        if col in out and out[col].notna().any():
            mask = out[col].notna()
            out.loc[mask, f"{col}_bh_fdr"] = multipletests(out.loc[mask, col], method="fdr_bh")[1]
    return out


def effect_size_interpretation(paired: pd.DataFrame) -> pd.DataFrame:
    if paired.empty:
        return pd.DataFrame()
    out = paired.copy()
    def label_dz(x: float) -> str:
        if pd.isna(x):
            return "not_estimable"
        ax = abs(float(x))
        if ax < 0.2:
            return "negligible"
        if ax < 0.5:
            return "small"
        if ax < 0.8:
            return "medium"
        return "large"
    out["cohens_dz_magnitude"] = out["cohens_dz"].map(label_dz)
    out["direction"] = np.where(out["mean_delta_condition_minus_clean"] < 0, "condition_lower", "condition_higher")
    out["evidence_flag"] = np.select(
        [
            out["n_subjects"] < 5,
            out["shapiro_p_value_delta"].notna() & (out["shapiro_p_value_delta"] < 0.05),
            out["t_p_value_bh_fdr"].notna() & (out["t_p_value_bh_fdr"] < 0.05),
        ],
        ["low_n_interpret_cautiously", "non_normal_delta_check_wilcoxon", "fdr_significant_ttest"],
        default="descriptive_or_not_fdr_significant",
    )
    cols = [
        "condition", "metric", "metric_role", "n_subjects", "mean_delta_condition_minus_clean",
        "delta_ci_low", "delta_ci_high", "median_delta_condition_minus_clean", "median_delta_ci_low",
        "median_delta_ci_high", "cohens_dz", "cohens_dz_magnitude", "n_worse_than_clean",
        "pct_worse_than_clean", "n_better_than_clean", "pct_better_than_clean", "sign_test_p_value_bh_fdr",
        "evidence_flag",
    ]
    return out[[c for c in cols if c in out.columns]].sort_values(["metric_role", "metric", "condition"]).reset_index(drop=True)


def sensitivity_summary(paired: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if paired.empty:
        return pd.DataFrame(rows)
    for condition, g in paired.groupby("condition", dropna=False):
        for metric in [PRIMARY_METRIC] + SECONDARY_METRICS + CALIBRATION_METRICS:
            d = g[g["metric"] == metric]
            if d.empty:
                rows.append({"condition": condition, "metric": metric, "available": False, "role": "calibration" if metric in CALIBRATION_METRICS else "primary_or_secondary"})
                continue
            r = d.iloc[0]
            rows.append({
                "condition": condition,
                "metric": metric,
                "available": True,
                "role": r["metric_role"],
                "n_subjects": int(r["n_subjects"]),
                "mean_delta_condition_minus_clean": float(r["mean_delta_condition_minus_clean"]),
                "pct_worse_than_clean": float(r["pct_worse_than_clean"]),
                "ttest_fdr": float(r["t_p_value_bh_fdr"]) if pd.notna(r.get("t_p_value_bh_fdr", np.nan)) else np.nan,
                "wilcoxon_fdr": float(r["wilcoxon_p_value_bh_fdr"]) if pd.notna(r.get("wilcoxon_p_value_bh_fdr", np.nan)) else np.nan,
                "interpretation": "primary" if metric == PRIMARY_METRIC else ("secondary" if metric in SECONDARY_METRICS else "calibration_optional"),
            })
    return pd.DataFrame(rows)


def overclaim_flags(subj: pd.DataFrame, paired: pd.DataFrame, prefix: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    n_subjects = int(subj["subject"].nunique())
    stressors = set(subj["stressor"].dropna().astype(str))
    rows.append({"flag": "low_subject_count", "triggered": n_subjects < 20, "detail": f"n_subjects={n_subjects}; population-level claims should be cautious below 20 subjects."})
    rows.append({"flag": "development_subset_prefix", "triggered": "dev" in prefix.lower(), "detail": "Prefix contains 'dev'; treat as development output, not final population estimate."})
    missing_cal = [m for m in CALIBRATION_METRICS if subj[m].isna().all()]
    rows.append({"flag": "missing_calibration_metrics", "triggered": bool(missing_cal), "detail": "Missing optional calibration metrics: " + (", ".join(missing_cal) if missing_cal else "none")})
    rows.append({"flag": "cross_session_absent", "triggered": "cross_session" not in stressors, "detail": "Cross-session stressor absent." if "cross_session" not in stressors else "Cross-session stressor present."})
    failed_files = sorted(Path("results").glob(f"{prefix}*failed_subjects*"))
    rows.append({"flag": "skipped_subject_log_present", "triggered": bool(failed_files), "detail": f"Found {len(failed_files)} failed-subject log files matching prefix."})
    if not paired.empty:
        min_n = int(paired["n_subjects"].min())
        rows.append({"flag": "uneven_or_low_paired_n", "triggered": min_n < n_subjects or min_n < 5, "detail": f"minimum paired n={min_n}; total subject n={n_subjects}."})
    return pd.DataFrame(rows)


def channel_dropout_slopes(subj: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    keep = subj[subj["stressor"].isin(["clean", "channel_dropout"])].copy()
    keep["dropout_fraction"] = keep["dropout_fraction"].astype(float)
    for (dataset, pipeline, subject), g in keep.groupby(["dataset", "pipeline", "subject"], dropna=False):
        agg = g.groupby("dropout_fraction", as_index=False)[METRICS].mean(numeric_only=True)
        if agg["dropout_fraction"].nunique() < 3:
            continue
        for metric in METRICS:
            d = agg[["dropout_fraction", metric]].dropna()
            if len(d) < 3:
                continue
            fit = stats.linregress(d["dropout_fraction"], d[metric])
            rows.append({
                "dataset": dataset, "pipeline": pipeline, "subject": subject, "metric": metric,
                "n_conditions": int(len(d)), "slope_per_100pct_dropout": float(fit.slope),
                "slope_per_10pct_dropout": float(fit.slope * 0.10), "intercept": float(fit.intercept),
                "r_value": float(fit.rvalue), "p_value_subject_slope": float(fit.pvalue),
            })
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
        ttest = stats.ttest_1samp(vals, 0.0)
        shapiro_p = float(stats.shapiro(vals).pvalue) if 3 <= len(vals) <= 5000 else np.nan
        harmful = vals < 0 if metric in BENEFIT_METRICS else vals > 0
        rows.append({
            "dataset": dataset, "pipeline": pipeline, "metric": metric, "n_subjects": int(len(vals)),
            "mean_slope_per_10pct_dropout": float(vals.mean()), "slope_ci_low": lo, "slope_ci_high": hi,
            "slope_sd": float(vals.std(ddof=1)), "t_statistic_vs_zero": float(ttest.statistic),
            "t_p_value_vs_zero": float(ttest.pvalue), "shapiro_p_value_slope": shapiro_p,
            "n_harmful_slope": int(harmful.sum()), "pct_harmful_slope": float(harmful.mean()),
        })
    out = pd.DataFrame(rows)
    if not out.empty and out["t_p_value_vs_zero"].notna().any():
        mask = out["t_p_value_vs_zero"].notna()
        out.loc[mask, "t_p_value_vs_zero_bh_fdr"] = multipletests(out.loc[mask, "t_p_value_vs_zero"], method="fdr_bh")[1]
    return out


def methods_audit(subj: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    numeric_metrics = [m for m in METRICS if m in subj.columns]
    key_dups = int(subj.duplicated(effective_key(subj)).sum())
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
    cols = ["condition", "metric", "metric_role", "n_subjects", "clean_mean", "condition_mean",
        "mean_delta_condition_minus_clean", "delta_ci_low", "delta_ci_high", "median_delta_condition_minus_clean",
        "cohens_dz", "t_p_value_bh_fdr", "wilcoxon_p_value_bh_fdr", "sign_test_p_value_bh_fdr",
        "shapiro_p_value_delta", "pct_worse_than_clean"]
    return paired.loc[paired["metric"].isin(["roc_auc", "balanced_accuracy"]), [c for c in cols if c in paired.columns]].sort_values(["metric", "condition"]).reset_index(drop=True)



def escape_latex_cell(value: object) -> str:
    """Escape a scalar for a minimal LaTeX tabular without pandas Styler/Jinja2."""
    if pd.isna(value):
        return ""
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def format_table_for_text(table: pd.DataFrame) -> pd.DataFrame:
    out = table.copy()
    for c in out.select_dtypes(include=[np.number]).columns:
        if c == "n_subjects":
            continue
        out[c] = out[c].map(lambda x: "" if pd.isna(x) else f"{x:.4g}")
    return out


def dataframe_to_latex_tabular(table: pd.DataFrame) -> str:
    """Render a small tabular using only the Python standard library."""
    out = format_table_for_text(table)
    align = "l" * len(out.columns)
    lines = [r"\begin{tabular}{" + align + "}", r"\toprule"]
    lines.append(" & ".join(escape_latex_cell(c) for c in out.columns) + r" \\")
    lines.append(r"\midrule")
    for _, row in out.iterrows():
        lines.append(" & ".join(escape_latex_cell(row[c]) for c in out.columns) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    return "\n".join(lines)


def dataframe_to_markdown(table: pd.DataFrame) -> str:
    """Render a GitHub-flavored markdown table without optional tabulate dependency."""
    out = format_table_for_text(table).fillna("")
    cols = [str(c) for c in out.columns]
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in out.iterrows():
        rows.append("| " + " | ".join(str(row[c]) for c in out.columns) + " |")
    return "\n".join(rows)


def write_latex_table(table: pd.DataFrame, path: Path) -> None:
    path.write_text(dataframe_to_latex_tabular(table), encoding="utf-8")


def write_markdown_summary(audit: pd.DataFrame, paired: pd.DataFrame, slopes_pop: pd.DataFrame, sensitivity: pd.DataFrame, flags: pd.DataFrame, path: Path, prefix: str) -> None:
    key = report_table(paired)
    txt = [
        f"# Statistical reporting pack for `{prefix}`", "",
        "Generated from existing subject-summary CSV files only; no simulated or additional benchmark observations are used.", "",
        "## Methods audit", dataframe_to_markdown(audit), "",
        "## Paired stressor effects vs clean all-channel baseline", dataframe_to_markdown(key), "",
        "## Sensitivity summary", dataframe_to_markdown(sensitivity) if not sensitivity.empty else "No sensitivity table was produced.", "",
        "## Channel-dropout slopes", dataframe_to_markdown(slopes_pop) if not slopes_pop.empty else "No channel-dropout slope table was produced.", "",
        "## Overclaim-risk flags", dataframe_to_markdown(flags) if not flags.empty else "No overclaim flags were produced.", "",
        "## Statistical notes",
        "- Paired effects are computed within subject against the clean all-channel baseline.",
        "- Confidence intervals for mean paired deltas and slopes use Student t intervals.",
        "- Median-delta intervals use a distribution-free sign-test/order-statistic interval.",
        "- Normality of paired deltas/slopes is screened with Shapiro-Wilk where sample size permits.",
        "- Wilcoxon signed-rank and sign tests are reported as sensitivity checks for paired deltas.",
        "- Benjamini-Hochberg false discovery rate correction is applied to paired t-test, Wilcoxon, and sign-test p-values.",
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
    effects = effect_size_interpretation(paired)
    sensitivity = sensitivity_summary(paired)
    flags = overclaim_flags(subj, paired, args.prefix)
    slopes = channel_dropout_slopes(subj)
    slopes_pop = slope_population_summary(slopes)
    table = report_table(paired)

    outputs = {
        "methods_audit": args.results_dir / f"{args.prefix}_statistical_methods_audit.csv",
        "paired_effects": args.results_dir / f"{args.prefix}_statistical_paired_effects.csv",
        "effect_size_interpretation": args.results_dir / f"{args.prefix}_statistical_effect_size_interpretation.csv",
        "sensitivity_summary": args.results_dir / f"{args.prefix}_statistical_sensitivity_summary.csv",
        "overclaim_flags": args.results_dir / f"{args.prefix}_statistical_overclaim_flags.csv",
        "channel_dropout_subject_slopes": args.results_dir / f"{args.prefix}_statistical_channel_dropout_subject_slopes.csv",
        "channel_dropout_slope_summary": args.results_dir / f"{args.prefix}_statistical_channel_dropout_slope_summary.csv",
        "report_table_csv": args.results_dir / f"{args.prefix}_statistical_report_table.csv",
        "report_table_tex": args.reports_dir / f"{args.prefix}_statistical_report_table.tex",
        "markdown_summary": args.reports_dir / f"{args.prefix}_statistical_report_summary.md",
    }
    audit.to_csv(outputs["methods_audit"], index=False)
    paired.to_csv(outputs["paired_effects"], index=False)
    effects.to_csv(outputs["effect_size_interpretation"], index=False)
    sensitivity.to_csv(outputs["sensitivity_summary"], index=False)
    flags.to_csv(outputs["overclaim_flags"], index=False)
    slopes.to_csv(outputs["channel_dropout_subject_slopes"], index=False)
    slopes_pop.to_csv(outputs["channel_dropout_slope_summary"], index=False)
    table.to_csv(outputs["report_table_csv"], index=False)
    write_latex_table(table, outputs["report_table_tex"])
    write_markdown_summary(audit, paired, slopes_pop, sensitivity, flags, outputs["markdown_summary"], args.prefix)

    manifest = {
        "prefix": args.prefix,
        "source_csv": str(args.results_dir / f"{args.prefix}_subject_summary.csv"),
        "n_subjects": int(subj["subject"].nunique()),
        "n_subject_condition_rows": int(len(subj)),
        "outputs": {k: str(v) for k, v in outputs.items()},
        "note": "Derived from existing subject summary CSV only; no simulated data used.",
    }
    manifest_path = args.results_dir / f"{args.prefix}_statistical_report_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
