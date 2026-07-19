#!/usr/bin/env python3
"""Validate benchmark result tables before manuscript-level statistical reporting.

The checks are deterministic and operate only on existing CSV files. They are
intended to catch schema drift, impossible metric values, duplicate evaluation
rows, incomplete paired baselines, and mismatches between fold-level outputs and
subject-level summaries before tables are used in a methods paper.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

KEY_COLS = ["dataset", "subject", "pipeline", "stressor", "montage", "dropout_fraction"]
FOLD_KEY_COLS = KEY_COLS + ["fold", "repeat"]
# Optional fold-level disambiguators. Region-dropout rows can share the same
# dropout_fraction/fold/repeat while dropping different named channel regions;
# these columns are intentionally absent from subject summaries, where such rows
# are averaged to subject-condition level.
OPTIONAL_FOLD_KEY_COLS = ["region", "dropped_channels", "selected_channels", "session_train", "session_test"]
OPTIONAL_SUBJECT_KEY_COLS = ["region", "session_train", "session_test"]
METRIC_BOUNDS = {
    "roc_auc": (0.0, 1.0),
    "balanced_accuracy": (0.0, 1.0),
    "brier_score": (0.0, 1.0),
    "ece": (0.0, 1.0),
}
REQUIRED_SUBJECT_COLUMNS = set(KEY_COLS) | {"roc_auc", "balanced_accuracy", "n_channels", "n_dropped_channels"}
REQUIRED_RESULTS_COLUMNS = set(FOLD_KEY_COLS) | {"roc_auc", "balanced_accuracy", "n_channels", "n_dropped_channels"}


def _jsonable(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if np.isnan(value):
            return None
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def add_issue(rows: list[dict[str, object]], severity: str, check: str, passed: bool, detail: str, **extra) -> None:
    row = {"severity": severity, "check": check, "passed": bool(passed), "detail": detail}
    row.update({k: _jsonable(v) for k, v in extra.items()})
    rows.append(row)


def _load_csv(path: Path, required: set[str], rows: list[dict[str, object]], label: str) -> pd.DataFrame:
    if not path.exists():
        add_issue(rows, "error", f"{label}_exists", False, f"Missing file: {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    missing = sorted(required - set(df.columns))
    add_issue(
        rows,
        "error",
        f"{label}_required_columns",
        not missing,
        "All required columns are present" if not missing else f"Missing columns: {missing}",
        n_rows=len(df),
        n_columns=len(df.columns),
    )
    return df


def validate_metric_ranges(df: pd.DataFrame, rows: list[dict[str, object]], label: str) -> None:
    for metric, (lo, hi) in METRIC_BOUNDS.items():
        if metric not in df.columns:
            add_issue(rows, "warning", f"{label}_{metric}_present", False, f"Optional metric {metric} is absent")
            continue
        x = pd.to_numeric(df[metric], errors="coerce")
        finite = x[np.isfinite(x)]
        bad = finite[(finite < lo) | (finite > hi)]
        add_issue(
            rows,
            "error",
            f"{label}_{metric}_range",
            bad.empty,
            f"{metric} finite values are within [{lo}, {hi}]" if bad.empty else f"{len(bad)} finite {metric} values outside [{lo}, {hi}]",
            n_finite=int(finite.size),
            n_missing_or_nonfinite=int(len(x) - finite.size),
        )


def validate_duplicate_rows(
    df: pd.DataFrame,
    rows: list[dict[str, object]],
    label: str,
    key_cols: list[str],
    optional_key_cols: list[str] | None = None,
) -> None:
    available = [c for c in key_cols if c in df.columns]
    if len(available) != len(key_cols):
        add_issue(rows, "error", f"{label}_duplicate_key_available", False, f"Cannot test duplicates without columns: {sorted(set(key_cols) - set(available))}")
        return
    optional_available = [c for c in (optional_key_cols or []) if c in df.columns and df[c].notna().any()]
    duplicate_key = available + optional_available
    dup = df.duplicated(duplicate_key, keep=False)
    add_issue(
        rows,
        "error",
        f"{label}_duplicate_rows",
        not bool(dup.any()),
        "No duplicate rows for declared evaluation key" if not bool(dup.any()) else f"{int(dup.sum())} rows share a declared evaluation key",
        n_duplicate_rows=int(dup.sum()),
        key_columns=",".join(duplicate_key),
    )


def validate_channel_counts(df: pd.DataFrame, rows: list[dict[str, object]], label: str) -> None:
    needed = {"n_channels", "n_dropped_channels", "dropout_fraction"}
    if not needed.issubset(df.columns):
        add_issue(rows, "error", f"{label}_channel_columns", False, f"Missing channel-count columns: {sorted(needed - set(df.columns))}")
        return
    n_channels = pd.to_numeric(df["n_channels"], errors="coerce")
    n_dropped = pd.to_numeric(df["n_dropped_channels"], errors="coerce")
    frac = pd.to_numeric(df["dropout_fraction"], errors="coerce")
    valid_counts = (n_channels > 0) & (n_dropped >= 0) & (n_dropped <= n_channels)
    add_issue(
        rows,
        "error",
        f"{label}_channel_count_bounds",
        bool(valid_counts.fillna(False).all()),
        "Channel counts are positive and dropped-channel counts do not exceed available channels" if bool(valid_counts.fillna(False).all()) else "Invalid channel-count rows detected",
        n_invalid=int((~valid_counts.fillna(False)).sum()),
    )
    expected = n_dropped / n_channels
    stressor = df["stressor"].astype(str) if "stressor" in df.columns else pd.Series("", index=df.index)
    testable = valid_counts.fillna(False) & frac.notna() & stressor.isin(["clean", "channel_dropout", "region_dropout"])
    mismatch = testable & ~np.isclose(frac, expected, atol=0.025)
    add_issue(
        rows,
        "warning",
        f"{label}_dropout_fraction_matches_counts",
        not bool(mismatch.any()),
        "Dropout fractions match dropped/available channel counts within tolerance" if not bool(mismatch.any()) else f"{int(mismatch.sum())} rows have dropout_fraction inconsistent with channel counts",
        n_tested=int(testable.sum()),
        n_mismatch=int(mismatch.sum()),
    )


def validate_subject_summary_against_results(results: pd.DataFrame, subject: pd.DataFrame, rows: list[dict[str, object]]) -> None:
    if results.empty or subject.empty or not set(KEY_COLS).issubset(results.columns) or not set(KEY_COLS).issubset(subject.columns):
        add_issue(rows, "error", "subject_summary_crosscheck_possible", False, "Cannot compare fold-level results with subject summary because required inputs are incomplete")
        return
    metrics = [m for m in METRIC_BOUNDS if m in results.columns and m in subject.columns]
    if not metrics:
        add_issue(rows, "error", "subject_summary_metric_overlap", False, "No overlapping metric columns for cross-check")
        return
    condition_cols = KEY_COLS + [
        c for c in OPTIONAL_SUBJECT_KEY_COLS
        if c in results.columns and c in subject.columns and (results[c].notna().any() or subject[c].notna().any())
    ]
    agg = results.groupby(condition_cols, dropna=False)[metrics].mean(numeric_only=True).reset_index()
    merged = subject[condition_cols + metrics].merge(agg, on=condition_cols, how="outer", suffixes=("_subject", "_fold_mean"), indicator=True)
    missing_pairs = merged["_merge"].ne("both")
    add_issue(
        rows,
        "error",
        "subject_summary_key_match",
        not bool(missing_pairs.any()),
        "Subject summary keys match fold-level aggregation keys" if not bool(missing_pairs.any()) else f"{int(missing_pairs.sum())} condition keys appear in only one table",
        n_compared_keys=int((merged["_merge"] == "both").sum()),
        n_unmatched_keys=int(missing_pairs.sum()),
    )
    comparable = merged[merged["_merge"] == "both"]
    for metric in metrics:
        a = pd.to_numeric(comparable[f"{metric}_subject"], errors="coerce")
        b = pd.to_numeric(comparable[f"{metric}_fold_mean"], errors="coerce")
        mask = a.notna() & b.notna()
        if not mask.any():
            add_issue(rows, "warning", f"subject_summary_{metric}_mean_match", False, f"No finite paired values to compare for {metric}")
            continue
        diff = (a[mask] - b[mask]).abs()
        passed = bool((diff <= 1e-10).all())
        add_issue(
            rows,
            "error",
            f"subject_summary_{metric}_mean_match",
            passed,
            f"Subject-level {metric} equals the mean of fold-level rows" if passed else f"Maximum absolute {metric} mismatch is {diff.max():.6g}",
            n_compared=int(mask.sum()),
            max_abs_difference=float(diff.max()),
        )


def validate_paired_baselines(subject: pd.DataFrame, rows: list[dict[str, object]]) -> None:
    required = {"subject", "stressor", "montage", "dropout_fraction"}
    if not required.issubset(subject.columns):
        add_issue(rows, "error", "paired_baseline_columns", False, f"Missing paired-baseline columns: {sorted(required - set(subject.columns))}")
        return
    clean_subjects = set(subject.loc[subject["stressor"].eq("clean"), "subject"])
    add_issue(rows, "error", "clean_baseline_present", bool(clean_subjects), "Clean baseline rows are present" if clean_subjects else "No clean baseline rows found")
    if not clean_subjects:
        return
    nonclean = subject.loc[~subject["stressor"].eq("clean")]
    nonclean_subjects = set(nonclean["subject"])
    missing = sorted(nonclean_subjects - clean_subjects)
    add_issue(
        rows,
        "error",
        "all_stressor_subjects_have_clean_baseline",
        not missing,
        "Every subject with stressor rows also has a clean baseline" if not missing else f"Subjects without clean baseline: {missing[:10]}",
        n_missing_subjects=len(missing),
    )


def validate_subject_count(subject: pd.DataFrame, rows: list[dict[str, object]], expected_subjects: int | None) -> None:
    """Verify cohort completeness when the expected dataset size is known."""
    if expected_subjects is None:
        return
    if "subject" not in subject.columns:
        add_issue(rows, "error", "expected_subject_count", False, "Cannot count subjects because the subject column is absent", n_expected=expected_subjects)
        return
    actual = int(subject["subject"].nunique())
    add_issue(
        rows,
        "error",
        "expected_subject_count",
        actual == expected_subjects,
        f"Expected {expected_subjects} unique subjects; found {actual}",
        n_expected=expected_subjects,
        n_actual=actual,
    )


def validate_prefix(
    results_dir: Path,
    prefix: str,
    expected_subjects: int | None = None,
    allow_missing_fold_results: bool = False,
) -> tuple[pd.DataFrame, dict[str, object]]:
    rows: list[dict[str, object]] = []
    results_path = results_dir / f"{prefix}_results.csv"
    if allow_missing_fold_results and not results_path.exists():
        results = pd.DataFrame()
        add_issue(
            rows,
            "warning",
            "fold_results_exists",
            False,
            f"Missing file: {results_path}; validation is limited to the subject-level summary",
        )
    else:
        results = _load_csv(results_path, REQUIRED_RESULTS_COLUMNS, rows, "fold_results")
    subject = _load_csv(results_dir / f"{prefix}_subject_summary.csv", REQUIRED_SUBJECT_COLUMNS, rows, "subject_summary")
    if not results.empty:
        validate_metric_ranges(results, rows, "fold_results")
        validate_duplicate_rows(results, rows, "fold_results", FOLD_KEY_COLS, OPTIONAL_FOLD_KEY_COLS)
        validate_channel_counts(results, rows, "fold_results")
    if not subject.empty:
        validate_metric_ranges(subject, rows, "subject_summary")
        validate_duplicate_rows(subject, rows, "subject_summary", KEY_COLS, OPTIONAL_SUBJECT_KEY_COLS)
        validate_channel_counts(subject, rows, "subject_summary")
        validate_paired_baselines(subject, rows)
        validate_subject_count(subject, rows, expected_subjects)
    if results.empty and allow_missing_fold_results:
        add_issue(rows, "warning", "subject_summary_crosscheck_possible", False, "Fold-level results are unavailable; subject-summary aggregation cannot be cross-checked")
    else:
        validate_subject_summary_against_results(results, subject, rows)
    report = pd.DataFrame(rows)
    n_errors = int((report["severity"].eq("error") & ~report["passed"]).sum()) if not report.empty else 1
    n_warnings = int((report["severity"].eq("warning") & ~report["passed"]).sum()) if not report.empty else 0
    summary = {
        "prefix": prefix,
        "passed": n_errors == 0,
        "n_checks": int(len(report)),
        "n_failed_errors": n_errors,
        "n_failed_warnings": n_warnings,
    }
    return report, summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results-dir", type=Path, default=Path("results"))
    ap.add_argument("--reports-dir", type=Path, default=Path("reports"))
    ap.add_argument("--prefix", required=True, help="Run prefix, without _results.csv suffix")
    ap.add_argument("--allow-warnings", action="store_true", help="Return success when errors are absent even if warnings are present")
    ap.add_argument("--expected-subjects", type=int, help="Require this exact number of unique subjects")
    ap.add_argument(
        "--allow-missing-fold-results",
        action="store_true",
        help="Validate an existing subject summary when fold-level results are unavailable; records explicit warnings",
    )
    args = ap.parse_args()

    args.reports_dir.mkdir(parents=True, exist_ok=True)
    report, summary = validate_prefix(
        args.results_dir,
        args.prefix,
        expected_subjects=args.expected_subjects,
        allow_missing_fold_results=args.allow_missing_fold_results,
    )
    report_path = args.reports_dir / f"{args.prefix}_validation_checks.csv"
    summary_path = args.reports_dir / f"{args.prefix}_validation_summary.json"
    report.to_csv(report_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {report_path}")
    print(f"Wrote {summary_path}")
    if summary["n_failed_errors"] > 0 or (summary["n_failed_warnings"] > 0 and not args.allow_warnings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
