#!/usr/bin/env python3
"""Generate methods-paper figures from existing benchmark CSV outputs only."""
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
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

DEFAULT_PREFIX = "BNCI2014-001_BNCI2014_001_all_riemann_lr"


def require_columns(df: pd.DataFrame, columns: set[str], source: Path | str) -> None:
    missing = columns - set(df.columns)
    if missing:
        raise ValueError(f"{source} is missing required columns: {sorted(missing)}")


def load_subject_summary(results_dir: Path, prefix: str) -> pd.DataFrame:
    path = results_dir / f"{prefix}_subject_summary.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    require_columns(df, {"dataset", "subject", "pipeline", "stressor", "dropout_fraction", "roc_auc", "balanced_accuracy"}, path)
    return df


def save_figure(fig: plt.Figure, base_path: Path) -> dict[str, str]:
    base_path.parent.mkdir(parents=True, exist_ok=True)
    png = base_path.with_suffix(".png")
    svg = base_path.with_suffix(".svg")
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)
    return {"png": str(png), "svg": str(svg)}


def pipeline_schematic(subj: pd.DataFrame, prefix: str, reports_dir: Path) -> dict[str, str]:
    datasets = ", ".join(sorted(map(str, subj["dataset"].dropna().unique())))
    pipelines = ", ".join(sorted(map(str, subj["pipeline"].dropna().unique())))
    stressors = ", ".join(sorted(map(str, subj["stressor"].dropna().unique())))
    n_subjects = int(subj["subject"].nunique())
    metrics = [m for m in ["roc_auc", "balanced_accuracy", "brier_score", "ece"] if m in subj.columns and not subj[m].isna().all()]
    labels = [
        ("Open EEG inputs", f"{datasets}\nsubjects: {n_subjects}"),
        ("MOABB/MNE access", "dataset loaders\nmetadata"),
        ("Preprocessing", "epoch arrays\nchannel names"),
        ("Decoder", pipelines),
        ("Stressors", stressors),
        ("Subject aggregation", "fold/repeat means\nsubject-condition rows"),
        ("Paired inference", ", ".join(metrics) + "\nclean-baseline contrasts"),
    ]
    fig, ax = plt.subplots(figsize=(13.5, 4.2))
    ax.set_axis_off()
    xs = np.linspace(0.06, 0.94, len(labels))
    y = 0.52
    box_w, box_h = 0.12, 0.34
    for idx, (x, (title, body)) in enumerate(zip(xs, labels)):
        box = FancyBboxPatch((x - box_w / 2, y - box_h / 2), box_w, box_h,
                             boxstyle="round,pad=0.02,rounding_size=0.025",
                             linewidth=1.4, edgecolor="#1f4e79", facecolor="#eaf3fb")
        ax.add_patch(box)
        ax.text(x, y + 0.075, title, ha="center", va="center", fontsize=9, weight="bold")
        ax.text(x, y - 0.055, body, ha="center", va="center", fontsize=7.2)
        if idx < len(xs) - 1:
            ax.add_patch(FancyArrowPatch((x + box_w / 2 + 0.01, y), (xs[idx + 1] - box_w / 2 - 0.01, y),
                                         arrowstyle="-|>", mutation_scale=12, linewidth=1.2, color="#444444"))
    ax.text(0.5, 0.94, "Intervention-robust EEG benchmark analysis flow", ha="center", va="center", fontsize=13, weight="bold")
    ax.text(0.5, 0.08, f"Source: {prefix}_subject_summary.csv. Schematic annotations are derived from repository CSV metadata.", ha="center", fontsize=8)
    return save_figure(fig, reports_dir / f"{prefix}_methods_pipeline_schematic")


def _mean_ci(vals: pd.Series) -> tuple[float, float, float]:
    arr = vals.dropna().astype(float).to_numpy()
    if len(arr) == 0:
        return np.nan, np.nan, np.nan
    mean = float(arr.mean())
    if len(arr) < 2:
        return mean, np.nan, np.nan
    se = float(arr.std(ddof=1) / np.sqrt(len(arr)))
    lo, hi = stats.t.interval(0.95, len(arr) - 1, loc=mean, scale=se)
    return mean, float(lo), float(hi)


def robustness_degradation_plot(subj: pd.DataFrame, prefix: str, metric: str, reports_dir: Path) -> dict[str, str]:
    if metric not in subj.columns:
        raise ValueError(f"Metric {metric!r} is not present in subject summary")
    keep = subj[subj["stressor"].isin(["clean", "channel_dropout"])].copy()
    keep["dropout_fraction"] = keep["dropout_fraction"].astype(float)
    pivot = keep.pivot_table(index="subject", columns="dropout_fraction", values=metric, aggfunc="mean").sort_index(axis=1)
    if pivot.shape[1] < 2:
        raise ValueError("Need at least two dropout fractions to draw degradation plot")
    summary = pd.DataFrame([{"dropout_fraction": float(frac), "mean": _mean_ci(vals)[0], "ci_low": _mean_ci(vals)[1], "ci_high": _mean_ci(vals)[2], "n": int(vals.notna().sum())} for frac, vals in pivot.items()])
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    for _, row in pivot.iterrows():
        ax.plot(pivot.columns.to_numpy(dtype=float), row.to_numpy(dtype=float), color="#8a8a8a", linewidth=0.8, alpha=0.45)
    yerr = np.vstack([summary["mean"] - summary["ci_low"], summary["ci_high"] - summary["mean"]])
    yerr = np.where(np.isfinite(yerr), yerr, 0.0)
    ax.errorbar(summary["dropout_fraction"], summary["mean"], yerr=yerr, color="#b2182b", marker="o", linewidth=2.4, capsize=4, label="Mean ± 95% CI")
    ax.set_xlabel("Test-time channel dropout fraction")
    ax.set_ylabel("ROC AUC" if metric == "roc_auc" else metric.replace("_", " ").title())
    ax.set_title("Robustness degradation under channel dropout")
    ax.set_ylim(0, 1.03)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False, loc="best")
    ax.text(0.01, -0.18, f"Source: {prefix}_subject_summary.csv; grey lines are paired subjects (n={pivot.shape[0]}).", transform=ax.transAxes, fontsize=8)
    return save_figure(fig, reports_dir / f"{prefix}_methods_robustness_degradation_{metric}")


def load_intervention_classes(results_dir: Path, prefix: str) -> tuple[pd.DataFrame, Path]:
    for path in [results_dir / f"{prefix}_final_intervention_classes.csv", results_dir / f"{prefix}_subject_risk_cards.csv"]:
        if path.exists():
            df = pd.read_csv(path)
            if "intervention_class" in df.columns:
                return df, path
            if "risk_level" in df.columns:
                out = df.copy(); out["intervention_class"] = out["risk_level"]
                return out, path
    raise FileNotFoundError(f"No intervention class or risk-card CSV found for prefix {prefix}")


def intervention_class_plot(results_dir: Path, prefix: str, reports_dir: Path) -> dict[str, str]:
    classes, source = load_intervention_classes(results_dir, prefix)
    require_columns(classes, {"subject", "intervention_class"}, source)
    counts = classes["intervention_class"].fillna("missing").value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    colors = plt.cm.Blues(np.linspace(0.45, 0.85, len(counts)))
    bars = ax.bar(counts.index.astype(str), counts.values, color=colors, edgecolor="#333333", linewidth=0.8)
    ax.set_ylabel("Subjects")
    ax.set_title("Deployment-risk class counts")
    ax.set_xlabel("Intervention/risk class")
    ax.set_ylim(0, max(counts.values) + 1.5)
    ax.grid(True, axis="y", alpha=0.25)
    for bar, value in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, str(int(value)), ha="center", va="bottom", fontsize=9)
    ax.tick_params(axis="x", rotation=25)
    ax.text(0.01, -0.25, f"Source: {source.name}. Counts are descriptive deployment-risk strata, not causal effects.", transform=ax.transAxes, fontsize=8)
    return save_figure(fig, reports_dir / f"{prefix}_methods_intervention_class_counts")


def generate_figures(results_dir: Path, reports_dir: Path, prefix: str, metric: str = "roc_auc") -> dict[str, object]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    subj = load_subject_summary(results_dir, prefix)
    class_source = (results_dir / f"{prefix}_final_intervention_classes.csv") if (results_dir / f"{prefix}_final_intervention_classes.csv").exists() else (results_dir / f"{prefix}_subject_risk_cards.csv")
    outputs = {
        "pipeline_schematic": pipeline_schematic(subj, prefix, reports_dir),
        "robustness_degradation": robustness_degradation_plot(subj, prefix, metric, reports_dir),
        "intervention_class_counts": intervention_class_plot(results_dir, prefix, reports_dir),
    }
    manifest = {"prefix": prefix, "metric": metric, "source_files": [str(results_dir / f"{prefix}_subject_summary.csv"), str(class_source)], "outputs": outputs, "note": "Figures are generated from existing repository CSV outputs only; no synthetic benchmark observations are used."}
    manifest_path = reports_dir / f"{prefix}_methods_figures_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results-dir", type=Path, default=Path("results"))
    ap.add_argument("--reports-dir", type=Path, default=Path("reports"))
    ap.add_argument("--prefix", default=DEFAULT_PREFIX)
    ap.add_argument("--metric", default="roc_auc", choices=["roc_auc", "balanced_accuracy"])
    args = ap.parse_args()
    print(json.dumps(generate_figures(args.results_dir, args.reports_dir, args.prefix, args.metric), indent=2))


if __name__ == "__main__":
    main()
