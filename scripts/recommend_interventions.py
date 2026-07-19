#!/usr/bin/env python3
"""Generate intervention recommendations from subject-level robustness outputs.

Inputs are produced by scripts/analyze_robustness.py. Clean, dropout, and
reduced-montage ROC-AUC values are converted into subject-level decision cards
and cohort-level rescue statistics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta


def exact_binom_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if n <= 0:
        return np.nan, np.nan
    lo = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return float(lo), float(hi)


def _normalize_wide_columns(wide: pd.DataFrame) -> pd.DataFrame:
    """Accept subject-wide outputs from either analysis script.

    `analyze_robustness.py` writes `clean_bal`/`bal_*` columns, while
    `final_statistics.py` writes `clean_balanced_accuracy`/
    `balanced_accuracy_*`. Recommendation rules use AUC columns only, but this
    normalization keeps downstream exports consistent.
    """
    rename = {
        "clean_balanced_accuracy": "clean_bal",
        "balanced_accuracy_motor_core": "bal_motor_core",
        "balanced_accuracy_motor_extended": "bal_motor_extended",
    }
    for col in list(wide.columns):
        if col.startswith("balanced_accuracy_dropout_"):
            frac = col.replace("balanced_accuracy_dropout_", "")
            rename[col] = f"bal_dropout_{frac}"
    return wide.rename(columns={k: v for k, v in rename.items() if k in wide.columns})


def load_inputs(results_dir: Path, prefix: str) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    candidate_paths = [
        results_dir / f"{prefix}_subject_wide.csv",
        results_dir / f"{prefix}_final_subject_wide_metrics.csv",
    ]
    wide_path = next((p for p in candidate_paths if p.exists()), None)
    cards_path = results_dir / f"{prefix}_subject_risk_cards.csv"
    if wide_path is None:
        raise FileNotFoundError(
            "Missing subject-wide file. Expected one of: "
            + ", ".join(str(p) for p in candidate_paths)
        )
    wide = _normalize_wide_columns(pd.read_csv(wide_path))
    cards = pd.read_csv(cards_path) if cards_path.exists() else None
    return wide, cards


def best_montage(row: pd.Series) -> tuple[str | None, float, float]:
    candidates = []
    for col in ["auc_motor_core", "auc_motor_extended"]:
        if col in row.index and pd.notna(row[col]):
            candidates.append((col.replace("auc_", ""), float(row[col])))
    if not candidates:
        return None, np.nan, np.nan
    name, auc = max(candidates, key=lambda x: x[1])
    return name, auc, auc - float(row["clean_auc"])


def recommendation_for_subject(row: pd.Series, clean_thr: float, fail_thr: float, rescue_margin: float) -> dict:
    subject = int(row["subject"])
    clean_auc = float(row["clean_auc"])
    dropout_cols = sorted([c for c in row.index if c.startswith("auc_dropout_")], key=lambda c: float(c.split("_")[-1]))
    dropout50_col = next((c for c in dropout_cols if abs(float(c.split("_")[-1]) - 0.5) < 1e-9), None)
    dropout50 = float(row[dropout50_col]) if dropout50_col else np.nan
    worst_dropout_auc = min(float(row[c]) for c in dropout_cols if pd.notna(row[c])) if dropout_cols else np.nan
    worst_delta = worst_dropout_auc - clean_auc if pd.notna(worst_dropout_auc) else np.nan
    best_name, best_auc, best_gain = best_montage(row)

    clean_working = clean_auc >= clean_thr
    dropout_failure = bool(clean_working and pd.notna(dropout50) and dropout50 < fail_thr)
    montage_rescue = bool(best_name is not None and best_auc >= fail_thr and best_gain >= rescue_margin)

    if dropout_failure and montage_rescue:
        action = f"deploy reduced montage first: {best_name}; add dropout fail-safe"
        priority = "A_high"
        rationale = "clean decoder works, but 50% dropout fails; reduced montage recovers above threshold"
    elif dropout_failure:
        action = "do not deploy without recalibration/dropout-aware training"
        priority = "A_high"
        rationale = "clean decoder works, but 50% dropout fails and reduced montage does not rescue enough"
    elif (not clean_working) and montage_rescue:
        action = f"try montage-specific calibration: {best_name}"
        priority = "B_rescue_candidate"
        rationale = "all-channel clean decoder is weak, but reduced montage exceeds threshold"
    elif clean_working and pd.notna(worst_delta) and worst_delta <= -0.20:
        action = "deploy only with monitoring; subject is fragile under dropout"
        priority = "B_fragile"
        rationale = "clean decoder works, but worst dropout loss is at least 0.20 ROC-AUC"
    elif clean_working:
        action = "acceptable in dev-run; still validate on more sessions"
        priority = "C_ok_dev"
        rationale = "clean and dropout performance did not trigger failure rules"
    else:
        action = "screen out or use different paradigm/features"
        priority = "D_low_clean"
        rationale = "clean all-channel performance is below threshold"

    deployability_score = np.nanmean([
        clean_auc,
        dropout50 if pd.notna(dropout50) else np.nan,
        best_auc if pd.notna(best_auc) else np.nan,
        max(0.0, 1.0 + worst_delta) if pd.notna(worst_delta) else np.nan,
    ])

    return {
        "subject": subject,
        "clean_auc": clean_auc,
        "dropout50_auc": dropout50,
        "worst_dropout_auc": worst_dropout_auc,
        "worst_dropout_delta": worst_delta,
        "best_montage": best_name,
        "best_montage_auc": best_auc,
        "best_montage_gain": best_gain,
        "clean_working": clean_working,
        "dropout_failure": dropout_failure,
        "montage_rescue": montage_rescue,
        "deployability_score": deployability_score,
        "priority": priority,
        "recommended_action": action,
        "rationale": rationale,
    }


def build_recommendations(wide: pd.DataFrame, clean_thr: float, fail_thr: float, rescue_margin: float) -> pd.DataFrame:
    rows = [recommendation_for_subject(row, clean_thr, fail_thr, rescue_margin) for _, row in wide.iterrows()]
    order = {"A_high": 0, "B_rescue_candidate": 1, "B_fragile": 2, "C_ok_dev": 3, "D_low_clean": 4}
    out = pd.DataFrame(rows)
    out["priority_order"] = out["priority"].map(order).fillna(99)
    return out.sort_values(["priority_order", "subject"]).drop(columns="priority_order").reset_index(drop=True)


def cohort_summary(rec: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n = len(rec)
    for label, mask in {
        "clean_working": rec["clean_working"],
        "dropout_failure_among_all": rec["dropout_failure"],
        "montage_rescue_among_all": rec["montage_rescue"],
        "montage_rescue_among_dropout_failures": rec["dropout_failure"] & rec["montage_rescue"],
    }.items():
        denom = int(rec["dropout_failure"].sum()) if label == "montage_rescue_among_dropout_failures" else n
        numer = int(mask.sum())
        lo, hi = exact_binom_ci(numer, denom)
        rows.append({"metric": label, "numerator": numer, "denominator": denom, "rate": numer / denom if denom else np.nan, "ci_low": lo, "ci_high": hi})
    # Add mean scores as descriptive, not binomial rates.
    rows.append({"metric": "mean_deployability_score", "numerator": np.nan, "denominator": n, "rate": rec["deployability_score"].mean(), "ci_low": np.nan, "ci_high": np.nan})
    return pd.DataFrame(rows)


def write_html(rec: pd.DataFrame, summary: pd.DataFrame, out_path: Path) -> None:
    import plotly.express as px
    fig = px.scatter(
        rec,
        x="clean_auc",
        y="dropout50_auc",
        color="priority",
        size="deployability_score",
        hover_data=["subject", "best_montage", "best_montage_auc", "recommended_action"],
        title="Subject intervention map: clean performance vs 50% dropout robustness",
    )
    fig.add_shape(type="line", x0=0.35, x1=1.0, y0=0.60, y1=0.60, line=dict(color="firebrick", dash="dot"))
    fig.add_shape(type="line", x0=0.60, x1=0.60, y0=0.35, y1=1.0, line=dict(color="firebrick", dash="dot"))
    fig.update_layout(xaxis_title="Clean all-channel ROC-AUC", yaxis_title="ROC-AUC at 50% channel dropout")
    html = f"""
<!doctype html><html><head><meta charset='utf-8'><title>Intervention recommendations</title>
<style>body{{font-family:Arial,sans-serif; max-width:1180px; margin:30px auto; line-height:1.35}} table{{border-collapse:collapse; font-size:13px; width:100%}} th,td{{border:1px solid #ccc; padding:4px 6px}} th{{background:#e8f1f8}} .warn{{background:#fff8e1; padding:10px; border-left:4px solid #f0b400}}</style>
</head><body>
<h1>BCI intervention recommendation layer</h1>
<div class='warn'>Generated from real PhysioNetMI n=10 development outputs. This is an offline decision-support prototype, not a clinical or online deployment rule.</div>
<h2>Cohort summary</h2>{summary.round(4).to_html(index=False)}
<h2>Subject recommendations</h2>{rec.round(4).to_html(index=False)}
<h2>Intervention map</h2>{fig.to_html(include_plotlyjs='cdn', full_html=False)}
</body></html>"""
    out_path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument("--prefix", default="PhysionetMI_PhysionetMI_all_csp_lda")
    parser.add_argument("--clean-threshold", type=float, default=0.60)
    parser.add_argument("--failure-threshold", type=float, default=0.60)
    parser.add_argument("--rescue-margin", type=float, default=0.00, help="Minimum reduced-montage gain vs clean to count as rescue")
    args = parser.parse_args()
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    wide, _cards = load_inputs(args.results_dir, args.prefix)
    rec = build_recommendations(wide, args.clean_threshold, args.failure_threshold, args.rescue_margin)
    summary = cohort_summary(rec)
    rec_path = args.results_dir / f"{args.prefix}_intervention_recommendations.csv"
    summary_path = args.results_dir / f"{args.prefix}_intervention_summary.csv"
    html_path = args.reports_dir / f"{args.prefix}_intervention_recommendations.html"
    rec.to_csv(rec_path, index=False)
    summary.to_csv(summary_path, index=False)
    write_html(rec, summary, html_path)
    print(json.dumps({"recommendations": str(rec_path), "summary": str(summary_path), "html": str(html_path), "n_subjects": int(len(rec))}, indent=2))


if __name__ == "__main__":
    main()
