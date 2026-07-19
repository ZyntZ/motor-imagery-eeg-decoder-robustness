#!/usr/bin/env python3
"""Final subject-level statistics for benchmark CSV outputs.

Fold/repeat outputs are first collapsed to subject-level summaries before
population-level inference.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import beta
from statsmodels.formula.api import mixedlm
from statsmodels.stats.multitest import multipletests


def exact_binom_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if n <= 0:
        return np.nan, np.nan
    lo = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return float(lo), float(hi)


def bootstrap_ci(x: np.ndarray, n_resamples: int = 5000, seed: int = 42) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size < 2:
        return np.nan, np.nan
    res = stats.bootstrap((x,), np.mean, n_resamples=n_resamples, random_state=seed, method="BCa")
    return float(res.confidence_interval.low), float(res.confidence_interval.high)


def ensure_metric_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in ["brier_score", "ece"]:
        if c not in out.columns:
            out[c] = np.nan
    return out


def load_subject_level(results_dir: Path, prefix: str) -> pd.DataFrame:
    path = results_dir / f"{prefix}_subject_summary.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = ensure_metric_columns(pd.read_csv(path))
    needed = {"dataset", "subject", "pipeline", "stressor", "montage", "dropout_fraction", "roc_auc", "balanced_accuracy"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"Missing required subject-summary columns: {sorted(missing)}")
    # Confirm one inferential row per subject/condition after aggregation.
    key = ["dataset", "subject", "pipeline", "stressor", "montage", "dropout_fraction"]
    key += [c for c in ["region", "session_train", "session_test"] if c in df.columns and df[c].notna().any()]
    if df.duplicated(key).any():
        raise ValueError("Subject summary contains duplicate subject-condition rows; aggregate before inference.")
    return df


def population_metrics(subj: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    group_cols = ["dataset", "pipeline", "stressor", "montage", "dropout_fraction"]
    group_cols += [c for c in ["region", "session_train", "session_test"] if c in subj.columns and subj[c].notna().any()]
    rows = []
    for keys, g in subj.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        row["n_subjects"] = int(g["subject"].nunique())
        for metric in ["roc_auc", "balanced_accuracy", "brier_score", "ece"]:
            lo, hi = bootstrap_ci(g[metric].to_numpy(), seed=seed)
            row[f"mean_{metric}"] = float(g[metric].mean()) if g[metric].notna().any() else np.nan
            row[f"{metric}_ci_low"] = lo
            row[f"{metric}_ci_high"] = hi
        rows.append(row)
    return pd.DataFrame(rows).sort_values(group_cols).reset_index(drop=True)


def condition_label(row: pd.Series) -> str:
    """Return a stable, analysis-safe label for one benchmark condition."""
    stressor = str(row["stressor"])
    if stressor == "clean":
        return "clean"
    if stressor == "reduced_montage":
        return str(row["montage"])
    fraction = float(row["dropout_fraction"])
    if stressor == "channel_dropout":
        return f"dropout_{fraction:g}"
    # Region names and session IDs are retained when available. Older subject
    # summaries do not contain them, so dropout fraction remains a deterministic
    # discriminator for those archived outputs.
    suffix = []
    for column in ("region", "session_train", "session_test"):
        if column in row.index and pd.notna(row[column]):
            suffix.append(str(row[column]).replace(" ", "_"))
    suffix.append(f"{fraction:g}")
    return "_".join([stressor, *suffix])


def wide_auc(subj: pd.DataFrame) -> pd.DataFrame:
    """Pivot every stressor condition for paired subject-level inference."""
    work = subj.copy()
    work["condition"] = work.apply(condition_label, axis=1)
    if work.duplicated(["subject", "condition"]).any():
        duplicates = work.loc[work.duplicated(["subject", "condition"], keep=False), ["subject", "condition"]]
        raise ValueError(f"Condition labels are not unique within subject: {duplicates.head().to_dict('records')}")
    auc = work.pivot(index="subject", columns="condition", values="roc_auc").add_prefix("auc_")
    bal = work.pivot(index="subject", columns="condition", values="balanced_accuracy").add_prefix("balanced_accuracy_")
    wide = auc.join(bal).reset_index()
    return wide.rename(columns={"auc_clean": "clean_auc", "balanced_accuracy_clean": "clean_balanced_accuracy"})


def paired_sensitivity(wide: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    rows = []
    cond_cols = [c for c in wide.columns if c.startswith("auc_") and c != "clean_auc"]
    for col in sorted(cond_cols):
        d = wide[["subject", "clean_auc", col]].dropna()
        if len(d) < 2:
            continue
        diff = d[col] - d["clean_auc"]
        lo, hi = bootstrap_ci(diff.to_numpy(), seed=seed)
        try:
            wil = stats.wilcoxon(diff, zero_method="wilcox")
            wil_stat, wil_p = float(wil.statistic), float(wil.pvalue)
        except ValueError:
            wil_stat, wil_p = np.nan, np.nan
        shapiro_p = float(stats.shapiro(diff).pvalue) if 3 <= len(diff) <= 5000 else np.nan
        t = stats.ttest_rel(d[col], d["clean_auc"])
        rows.append({
            "condition": col.replace("auc_", ""),
            "n_subjects": int(len(d)),
            "mean_condition_auc": float(d[col].mean()),
            "mean_clean_auc": float(d["clean_auc"].mean()),
            "mean_delta_auc": float(diff.mean()),
            "delta_ci_low": lo,
            "delta_ci_high": hi,
            "shapiro_p": shapiro_p,
            "paired_t_stat": float(t.statistic),
            "paired_t_p": float(t.pvalue),
            "wilcoxon_stat": wil_stat,
            "wilcoxon_p": wil_p,
            "cohens_dz": float(diff.mean() / diff.std(ddof=1)) if diff.std(ddof=1) > 0 else np.nan,
        })
    out = pd.DataFrame(rows)
    if not out.empty:
        for col in ["paired_t_p", "wilcoxon_p"]:
            vals = out[col].to_numpy(dtype=float)
            mask = np.isfinite(vals)
            adj = np.full(len(out), np.nan)
            if mask.any():
                adj[mask] = multipletests(vals[mask], method="fdr_bh")[1]
            out[f"{col}_bh_fdr"] = adj
    return out


def intervention_classes(wide: pd.DataFrame, clean_thr: float = 0.60, fail_thr: float = 0.60) -> pd.DataFrame:
    rows = []
    dropout_cols = sorted([c for c in wide.columns if c.startswith("auc_dropout_")], key=lambda c: float(c.split("_")[-1]))
    montage_cols = [c for c in ["auc_motor_core", "auc_motor_extended"] if c in wide.columns]
    for _, r in wide.iterrows():
        clean_auc = float(r["clean_auc"])
        clean_working = clean_auc >= clean_thr
        d50_col = next((c for c in dropout_cols if abs(float(c.split("_")[-1]) - 0.5) < 1e-9), None)
        d50 = float(r[d50_col]) if d50_col and pd.notna(r[d50_col]) else np.nan
        dropout_failure = bool(clean_working and pd.notna(d50) and d50 < fail_thr)
        best_montage = None
        best_auc = np.nan
        if montage_cols:
            vals = [(c, r[c]) for c in montage_cols if pd.notna(r[c])]
            if vals:
                best_montage, best_auc = max(vals, key=lambda x: x[1])
                best_montage = best_montage.replace("auc_", "")
                best_auc = float(best_auc)
        montage_rescue = bool(pd.notna(best_auc) and best_auc >= fail_thr)
        worst_dropout_auc = min([float(r[c]) for c in dropout_cols if pd.notna(r[c])], default=np.nan)
        worst_delta = worst_dropout_auc - clean_auc if pd.notna(worst_dropout_auc) else np.nan
        if dropout_failure and montage_rescue:
            cls = "A_high"
        elif (not clean_working) and montage_rescue:
            cls = "B_rescue_candidate"
        elif clean_working and pd.notna(worst_delta) and worst_delta <= -0.20:
            cls = "B_fragile"
        elif clean_working:
            cls = "C_ok_dev"
        else:
            cls = "D_low_clean"
        rows.append({
            "subject": int(r["subject"]),
            "clean_auc": clean_auc,
            "dropout50_auc": d50,
            "worst_dropout_auc": worst_dropout_auc,
            "worst_dropout_delta": worst_delta,
            "best_montage": best_montage,
            "best_montage_auc": best_auc,
            "clean_working_threshold": clean_thr,
            "failure_threshold": fail_thr,
            "clean_working": clean_working,
            "dropout_failure_at_50pct": dropout_failure,
            "montage_rescue": montage_rescue,
            "intervention_class": cls,
        })
    return pd.DataFrame(rows).sort_values(["intervention_class", "subject"]).reset_index(drop=True)


def intervention_class_rates(classes: pd.DataFrame) -> pd.DataFrame:
    n = len(classes)
    rows = []
    for cls in ["A_high", "B_rescue_candidate", "B_fragile", "C_ok_dev", "D_low_clean"]:
        k = int((classes["intervention_class"] == cls).sum())
        lo, hi = exact_binom_ci(k, n)
        rows.append({"metric": f"class_{cls}", "numerator": k, "denominator": n, "rate": k / n if n else np.nan, "ci_low": lo, "ci_high": hi})
    clean = classes["clean_working"]
    k = int(clean.sum())
    lo, hi = exact_binom_ci(k, n)
    rows.append({"metric": "clean_working", "numerator": k, "denominator": n, "rate": k / n if n else np.nan, "ci_low": lo, "ci_high": hi})
    denom = int(clean.sum())
    k = int((clean & classes["dropout_failure_at_50pct"]).sum())
    lo, hi = exact_binom_ci(k, denom)
    rows.append({"metric": "failure_at_50pct_among_clean_working", "numerator": k, "denominator": denom, "rate": k / denom if denom else np.nan, "ci_low": lo, "ci_high": hi})
    fail = classes["dropout_failure_at_50pct"]
    denom = int(fail.sum())
    k = int((fail & classes["montage_rescue"]).sum())
    lo, hi = exact_binom_ci(k, denom)
    rows.append({"metric": "montage_rescue_among_50pct_failures", "numerator": k, "denominator": denom, "rate": k / denom if denom else np.nan, "ci_low": lo, "ci_high": hi})
    return pd.DataFrame(rows)


def _fit_mixed_model(df: pd.DataFrame, model_id: str, formula: str) -> list[dict[str, object]]:
    """Fit one subject-random-intercept model and return tidy coefficients."""
    rows: list[dict[str, object]] = []
    try:
        fit = mixedlm(formula, data=df, groups=df["subject"]).fit(
            reml=False, method="lbfgs", maxiter=1000, disp=False
        )
        conf = fit.conf_int()
        for name, coef in fit.params.items():
            rows.append({
                "model_id": model_id, "model": formula, "term": name,
                "estimate": float(coef),
                "ci_low": float(conf.loc[name, 0]) if name in conf.index else np.nan,
                "ci_high": float(conf.loc[name, 1]) if name in conf.index else np.nan,
                "p_value": float(fit.pvalues.get(name, np.nan)),
                "n_subjects": int(df["subject"].nunique()),
                "n_subject_condition_rows": int(len(df)), "status": "fit",
            })
    except Exception as exc:
        rows.append({
            "model_id": model_id, "model": formula, "term": np.nan, "estimate": np.nan,
            "ci_low": np.nan, "ci_high": np.nan, "p_value": np.nan,
            "n_subjects": int(df["subject"].nunique()),
            "n_subject_condition_rows": int(len(df)),
            "status": f"not_fit: {type(exc).__name__}: {exc}",
        })
    return rows


def mixed_effects(subj: pd.DataFrame) -> pd.DataFrame:
    """Fit prespecified condition and channel-dropout dose-response models.

    Treating all non-dropout stressors as severity zero in one model confounds
    stressor identity with dropout dose. The categorical model estimates each
    condition against clean; the dose model is restricted to clean and random
    channel dropout, where ``dropout_fraction`` has a consistent meaning.
    """
    df = subj[np.isfinite(subj["roc_auc"])].copy()
    df["condition"] = df.apply(condition_label, axis=1)
    rows = _fit_mixed_model(df, "all_conditions", "roc_auc ~ C(condition, Treatment(reference='clean'))")

    dose = df[df["stressor"].isin(["clean", "channel_dropout"])].copy()
    dose["dropout_fraction"] = dose["dropout_fraction"].astype(float)
    if dose["dropout_fraction"].nunique() >= 2:
        rows += _fit_mixed_model(dose, "channel_dropout_dose", "roc_auc ~ dropout_fraction")

    out = pd.DataFrame(rows)
    out["p_value_bh_fdr"] = np.nan
    for _, idx in out.groupby("model_id").groups.items():
        idx = list(idx)
        mask = out.loc[idx, "p_value"].notna() & ~out.loc[idx, "term"].isin(["Intercept", "Group Var"])
        selected = out.loc[idx].index[mask]
        if len(selected):
            out.loc[selected, "p_value_bh_fdr"] = multipletests(out.loc[selected, "p_value"], method="fdr_bh")[1]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=Path, default=Path("results"))
    ap.add_argument("--prefix", default="PhysionetMI_PhysionetMI_all_csp_lda")
    ap.add_argument("--clean-threshold", type=float, default=0.60)
    ap.add_argument("--failure-threshold", type=float, default=0.60)
    args = ap.parse_args()

    subj = load_subject_level(args.results_dir, args.prefix)
    pop = population_metrics(subj)
    wide = wide_auc(subj)
    paired = paired_sensitivity(wide)
    classes = intervention_classes(wide, args.clean_threshold, args.failure_threshold)
    class_rates = intervention_class_rates(classes)
    model = mixed_effects(subj)

    outputs = {
        "subject_level_metrics": args.results_dir / f"{args.prefix}_final_subject_level_metrics.csv",
        "population_metrics": args.results_dir / f"{args.prefix}_final_population_metrics.csv",
        "subject_wide_metrics": args.results_dir / f"{args.prefix}_final_subject_wide_metrics.csv",
        "paired_sensitivity": args.results_dir / f"{args.prefix}_final_paired_sensitivity.csv",
        "intervention_classes": args.results_dir / f"{args.prefix}_final_intervention_classes.csv",
        "intervention_class_rates": args.results_dir / f"{args.prefix}_final_intervention_class_rates.csv",
        "mixed_effects": args.results_dir / f"{args.prefix}_final_mixed_effects.csv",
    }
    subj.to_csv(outputs["subject_level_metrics"], index=False)
    pop.to_csv(outputs["population_metrics"], index=False)
    wide.to_csv(outputs["subject_wide_metrics"], index=False)
    paired.to_csv(outputs["paired_sensitivity"], index=False)
    classes.to_csv(outputs["intervention_classes"], index=False)
    class_rates.to_csv(outputs["intervention_class_rates"], index=False)
    model.to_csv(outputs["mixed_effects"], index=False)
    manifest = {"prefix": args.prefix, "n_subjects": int(subj["subject"].nunique()), "source_csv": str(args.results_dir / f"{args.prefix}_subject_summary.csv"), "outputs": {k: str(v) for k, v in outputs.items()}}
    (args.results_dir / f"{args.prefix}_final_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
