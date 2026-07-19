#!/usr/bin/env python3
"""Generate restrained methods figures from existing benchmark CSV outputs only."""
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

DEFAULT_PREFIX = "BNCI2014-001_BNCI2014_001_all_riemann_lr"
INK = "#222222"
MUTED = "#666666"
BLUE = "#1f5a7a"


def set_style() -> None:
    """Apply a compact, conventional journal style."""
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8.5,
        "axes.titlesize": 9.5, "axes.titleweight": "normal", "axes.labelsize": 9,
        "axes.edgecolor": INK, "axes.linewidth": 0.8,
        "xtick.color": INK, "ytick.color": INK, "text.color": INK,
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "svg.fonttype": "none",
    })


def require_columns(df: pd.DataFrame, cols: set[str], source: Path | str) -> None:
    missing = cols - set(df.columns)
    if missing:
        raise ValueError(f"{source} is missing required columns: {sorted(missing)}")


def load_subject_summary(results_dir: Path, prefix: str) -> pd.DataFrame:
    path = results_dir / f"{prefix}_subject_summary.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    require_columns(df, {"dataset", "subject", "pipeline", "stressor", "dropout_fraction", "roc_auc", "balanced_accuracy"}, path)
    return df


def save(fig: plt.Figure, base: Path) -> dict[str, str]:
    base.parent.mkdir(parents=True, exist_ok=True)
    png, svg = base.with_suffix(".png"), base.with_suffix(".svg")
    fig.savefig(png, dpi=300, bbox_inches="tight", pad_inches=0.12)
    fig.savefig(svg, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    return {"png": str(png), "svg": str(svg)}


def metric_label(metric: str) -> str:
    return "ROC AUC" if metric == "roc_auc" else metric.replace("_", " ").title()



def dropout_table(subj: pd.DataFrame, metric: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    keep = subj[subj["stressor"].isin(["clean", "channel_dropout"])].copy()
    keep["dropout_fraction"] = keep["dropout_fraction"].astype(float)
    pivot = keep.pivot_table(index="subject", columns="dropout_fraction", values=metric, aggfunc="mean").sort_index(axis=1)
    if pivot.shape[1] < 2:
        raise ValueError("Need at least two dropout fractions")
    rows = []
    for frac, values in pivot.items():
        x = values.dropna().astype(float).to_numpy()
        mean = float(x.mean())
        if len(x) > 1:
            se = float(x.std(ddof=1) / np.sqrt(len(x)))
            lo, hi = stats.t.interval(0.95, len(x) - 1, loc=mean, scale=se)
        else:
            lo = hi = np.nan
        rows.append({"dropout_fraction": float(frac), "mean": mean, "ci_low": float(lo), "ci_high": float(hi), "n": int(len(x))})
    return pivot, pd.DataFrame(rows)


def pipeline_schematic(subj: pd.DataFrame, prefix: str, reports_dir: Path) -> dict[str, str]:
    """Draw a fixed-grid workflow with short labels contained inside each stage."""
    set_style()
    dataset = ", ".join(sorted(map(str, subj["dataset"].dropna().unique())))
    pipeline_key = ", ".join(sorted(map(str, subj["pipeline"].dropna().unique())))
    pipeline = {"riemann_lr": "Riemannian features\n+ logistic regression", "csp_lda": "CSP + LDA"}.get(pipeline_key, pipeline_key.replace("_", " "))
    n_subjects = int(subj["subject"].nunique())
    stressor_names = set(map(str, subj["stressor"].dropna().unique()))
    stressor_lines = []
    if "channel_dropout" in stressor_names or "region_dropout" in stressor_names:
        stressor_lines.append("channel and region dropout")
    if "reduced_montage" in stressor_names: stressor_lines.append("reduced montages")
    if "cross_session" in stressor_names: stressor_lines.append("cross-session transfer")
    stressors = "\n".join(stressor_lines) or "configured perturbations"
    metric_names = [label for key, label in [("roc_auc", "ROC AUC"), ("balanced_accuracy", "balanced accuracy"), ("brier_score", "Brier score"), ("ece", "calibration error")] if key in subj.columns and not subj[key].isna().all()]
    metrics = "\n".join([", ".join(metric_names[:2]), ", ".join(metric_names[2:])]).strip()
    stages = [
        ("1", "Dataset", f"{dataset}\n{n_subjects} subjects"),
        ("2", "Epochs", "MOABB/MNE loading\n8–32 Hz; 128 Hz"),
        ("3", "Decoder", pipeline),
        ("4", "Robustness tests", stressors),
        ("5", "Subject summaries", "cross-validation means\nby condition"),
        ("6", "Statistical analysis", metrics),
    ]
    fig, ax = plt.subplots(figsize=(8.2, 3.4), layout="constrained")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    positions = [(0.03, 0.56), (0.35, 0.56), (0.67, 0.56), (0.67, 0.12), (0.35, 0.12), (0.03, 0.12)]
    box_w, box_h = 0.27, 0.27
    for (number, title, body), (x, y) in zip(stages, positions):
        ax.add_patch(plt.Rectangle((x, y), box_w, box_h, facecolor="white", edgecolor="#777777", linewidth=0.9))
        ax.text(x + 0.025, y + box_h - 0.055, number, ha="left", va="center", fontsize=8, weight="bold", color=BLUE)
        ax.text(x + 0.065, y + box_h - 0.055, title, ha="left", va="center", fontsize=8.5, weight="bold")
        ax.text(x + box_w / 2, y + 0.095, body, ha="center", va="center", fontsize=7.2, color=MUTED, linespacing=1.35)
    centers = [(x + box_w / 2, y + box_h / 2) for x, y in positions]
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]:
        xa, ya = centers[a]; xb, yb = centers[b]
        if abs(ya - yb) < 0.05:
            sx = xa + (box_w / 2 if xb > xa else -box_w / 2); ex = xb - (box_w / 2 if xb > xa else -box_w / 2)
            ax.annotate("", xy=(ex, yb), xytext=(sx, ya), arrowprops={"arrowstyle": "->", "lw": 0.9, "color": MUTED})
        else:
            ax.annotate("", xy=(xb, yb + box_h / 2), xytext=(xa, ya - box_h / 2), arrowprops={"arrowstyle": "->", "lw": 0.9, "color": MUTED})
    fig.text(0.025, 0.97, "A", ha="left", va="top", weight="bold", fontsize=11)
    fig.suptitle("Benchmark workflow", y=0.97, fontsize=10.5)
    return save(fig, reports_dir / f"{prefix}_methods_pipeline_schematic")


def robustness_degradation_plot(subj: pd.DataFrame, prefix: str, metric: str, reports_dir: Path) -> dict[str, str]:
    set_style(); pivot, summary = dropout_table(subj, metric)
    fig, ax = plt.subplots(figsize=(4.6, 3.6), layout="constrained"); x = pivot.columns.to_numpy(float)
    for _, row in pivot.iterrows(): ax.plot(x, row.to_numpy(float), color="#c7c7c7", lw=0.7, alpha=0.75, zorder=1)
    yerr = np.vstack([summary["mean"] - summary["ci_low"], summary["ci_high"] - summary["mean"]]); yerr = np.where(np.isfinite(yerr), yerr, 0.0)
    ax.errorbar(summary["dropout_fraction"], summary["mean"], yerr=yerr, color=BLUE, marker="o", ms=4.0, lw=1.5, capsize=2.5, zorder=2, label="Mean and 95% CI")
    ax.set_xlabel("Fraction of channels dropped"); ax.set_ylabel(metric_label(metric)); ax.set_title(f"Channel dropout: {pivot.shape[0]} paired subjects", loc="left", pad=10)
    ax.set_ylim(0, 1.02); ax.set_xticks(x); ax.grid(axis="y", color="#dddddd", lw=0.5); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="lower left", fontsize=7.5); fig.text(0.01, 0.99, "B", ha="left", va="top", weight="bold", fontsize=11)
    return save(fig, reports_dir / f"{prefix}_methods_robustness_degradation_{metric}")



def generate_figures(results_dir: Path, reports_dir: Path, prefix: str, metric: str = "roc_auc") -> dict[str, object]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    subj = load_subject_summary(results_dir, prefix)
    outputs = {
        "pipeline_schematic": pipeline_schematic(subj, prefix, reports_dir),
        "robustness_degradation": robustness_degradation_plot(subj, prefix, metric, reports_dir),
    }
    manifest = {"prefix": prefix, "metric": metric, "source_files": [str(results_dir / f"{prefix}_subject_summary.csv")], "outputs": outputs, "note": "Figures are generated from committed participant-level results."}
    (reports_dir / f"{prefix}_methods_figures_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results-dir", type=Path, default=Path("results")); ap.add_argument("--reports-dir", type=Path, default=Path("reports")); ap.add_argument("--prefix", default=DEFAULT_PREFIX); ap.add_argument("--metric", default="roc_auc", choices=["roc_auc", "balanced_accuracy"])
    args = ap.parse_args(); print(json.dumps(generate_figures(args.results_dir, args.reports_dir, args.prefix, args.metric), indent=2))


if __name__ == "__main__":
    main()
