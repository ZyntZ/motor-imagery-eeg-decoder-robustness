#!/usr/bin/env python3
"""Generate submission-readiness checks from existing benchmark artifacts.

The checks are repository-level quality controls for manuscript preparation. They
read committed result, report, and metadata files only; they do not create or
modify benchmark observations.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_PREFIXES = [
    "BNCI2014-001_BNCI2014_001_all_csp_lda",
    "BNCI2014-001_BNCI2014_001_all_riemann_lr",
    "PhysionetMI_PhysionetMI_all_riemann_lr",
    "PhysionetMI_PhysionetMI_all_csp_lda",
]
FULL_RUN_PREFIXES = [
    "BNCI2014-001_BNCI2014_001_all_csp_lda",
    "BNCI2014-001_BNCI2014_001_all_riemann_lr",
    "PhysionetMI_PhysionetMI_all_riemann_lr",
    "PhysionetMI_PhysionetMI_all_csp_lda",
]
EXPECTED_SUBJECT_COUNTS = {
    "BNCI2014-001_BNCI2014_001_all_csp_lda": 9,
    "BNCI2014-001_BNCI2014_001_all_riemann_lr": 9,
    "PhysionetMI_PhysionetMI_all_riemann_lr": 109,
    "PhysionetMI_PhysionetMI_all_csp_lda": 109,
}
SUBJECT_SUMMARY_ONLY_PREFIXES: set[str] = set()
REQUIRED_PROJECT_FILES = [
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "DATA_PROVENANCE.md",
    "REPRODUCIBILITY.md",
    "STATISTICAL_REPORTING.md",
    "configs/benchmark.yaml",
    "environment.yml",
    "requirements.txt",
    "requirements-lock.txt",
    "pyproject.toml",
    "manuscript/manuscript.tex",
    "manuscript/manuscript.pdf",
    "manuscript/highlights.txt",
]
REQUIRED_REPORT_SUFFIXES = [
    "validation_checks.csv",
    "validation_summary.json",
]
REQUIRED_RESULT_SUFFIXES = [
    "results.csv",
    "subject_summary.csv",
    "population_summary.csv",
]
REQUIRED_METHOD_FIGURE_PREFIX = "PhysionetMI_PhysionetMI_all_riemann_lr"
REQUIRED_METHOD_FIGURES = [
    "methods_pipeline_schematic.svg",
    "methods_robustness_degradation_roc_auc.svg",
    "methods_figures_manifest.json",
]
DISALLOWED_FILENAME_TOKENS = ["assistant", "for_me", "for-me", "для_меня", "для-меня", "ииш", "ai_generated", "ai-generated"]
RAW_DATA_DIR_NAMES = {"data", "moabb_data", "mne_data"}
EXCLUDED_LOCAL_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".venv",
    "venv",
    "env",
    ".env",
    "node_modules",
    "checkpoints",
    "moabb_data",
    "mne_data",
    "data",
}


def is_excluded_local_path(path: Path, root: Path) -> bool:
    rel_path = path.relative_to(root)
    return any(part in EXCLUDED_LOCAL_DIR_NAMES for part in rel_path.parts)


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def check_row(category: str, check: str, severity: str, passed: bool, detail: str, **extra: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "category": category,
        "check": check,
        "severity": severity,
        "passed": bool(passed),
        "detail": detail,
    }
    row.update(extra)
    return row


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def count_unique_subjects(path: Path) -> int | None:
    if not path.exists():
        return None
    df = pd.read_csv(path, usecols=lambda col: col == "subject")
    if "subject" not in df.columns:
        return None
    return int(df["subject"].nunique())


def build_checks(root: Path, results_dir: Path, reports_dir: Path, prefixes: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for item in REQUIRED_PROJECT_FILES:
        path = root / item
        rows.append(check_row(
            "repository_metadata",
            f"required_file:{item}",
            "error",
            path.exists(),
            "Required publication-support file is present" if path.exists() else "Required publication-support file is missing",
            path=item,
        ))

    raw_dirs = [
        rel(p, root)
        for p in root.rglob("*")
        if p.is_dir() and p.name in RAW_DATA_DIR_NAMES and not is_excluded_local_path(p, root)
    ]
    rows.append(check_row(
        "repository_hygiene",
        "raw_data_directories_absent_from_release_tree",
        "error",
        len(raw_dirs) == 0,
        "No unexcluded raw EEG/data-cache directories are inside the release tree"
        if not raw_dirs
        else "Unexcluded raw/data-cache directories found: " + "; ".join(raw_dirs),
        n_findings=len(raw_dirs),
    ))

    bad_names: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if is_excluded_local_path(path, root):
            continue
        lowered = rel(path, root).lower()
        if any(token in lowered for token in DISALLOWED_FILENAME_TOKENS):
            bad_names.append(rel(path, root))
    rows.append(check_row(
        "repository_hygiene",
        "disallowed_filename_tokens_absent",
        "error",
        len(bad_names) == 0,
        "No disallowed filename tokens found" if not bad_names else "Disallowed filename tokens found: " + "; ".join(bad_names),
        n_findings=len(bad_names),
    ))

    for prefix in prefixes:
        validation_dir = root / "artifacts" / "validation"
        for suffix in REQUIRED_REPORT_SUFFIXES:
            path = validation_dir / f"{prefix}_{suffix}"
            rows.append(check_row(
                "validation_artifacts",
                f"{prefix}:{suffix}",
                "error",
                path.exists(),
                "Validation artifact is present" if path.exists() else "Validation artifact is missing",
                prefix=prefix,
                path=rel(path, root),
            ))
        summary = read_json(validation_dir / f"{prefix}_validation_summary.json")
        if summary is None:
            rows.append(check_row("validation_artifacts", f"{prefix}:validation_summary_readable", "error", False, "Validation summary JSON is missing", prefix=prefix))
        else:
            failed_errors = int(summary.get("n_failed_errors", 1))
            failed_warnings = int(summary.get("n_failed_warnings", 0))
            rows.append(check_row(
                "validation_artifacts",
                f"{prefix}:no_failed_validation_errors",
                "error",
                failed_errors == 0,
                f"Validation errors: {failed_errors}; warnings: {failed_warnings}",
                prefix=prefix,
                n_failed_errors=failed_errors,
                n_failed_warnings=failed_warnings,
            ))

        for suffix in REQUIRED_RESULT_SUFFIXES:
            path = results_dir / f"{prefix}_{suffix}"
            summary_only_fold_file = prefix in SUBJECT_SUMMARY_ONLY_PREFIXES and suffix == "results.csv"
            severity = "warning" if summary_only_fold_file else "error"
            detail = (
                "Fold-level results are unavailable; subject-level artifacts remain releaseable with an explicit provenance limitation"
                if summary_only_fold_file and not path.exists()
                else "Analysis artifact is present" if path.exists() else "Analysis artifact is missing"
            )
            rows.append(check_row(
                "analysis_artifacts", f"{prefix}:{suffix}", severity, path.exists(), detail,
                prefix=prefix, path=rel(path, root),
            ))

        n_subjects = count_unique_subjects(results_dir / f"{prefix}_subject_summary.csv")
        is_full_run = prefix in FULL_RUN_PREFIXES
        expected_subjects = EXPECTED_SUBJECT_COUNTS.get(prefix)
        count_ok = n_subjects is not None and (
            n_subjects == expected_subjects if expected_subjects is not None else (n_subjects > 1 if is_full_run else n_subjects >= 1)
        )
        rows.append(check_row(
            "analysis_scope", f"{prefix}:expected_subject_count",
            "error" if expected_subjects is not None or is_full_run else "warning", count_ok,
            f"Expected {expected_subjects} unique subjects; found {n_subjects}" if expected_subjects is not None else (
                "Subject count is documented in subject_summary.csv" if n_subjects is not None else "Could not determine subject count from subject_summary.csv"
            ), prefix=prefix, n_subjects=n_subjects, expected_subjects=expected_subjects,
        ))

    for suffix in REQUIRED_METHOD_FIGURES:
        path = reports_dir / f"{REQUIRED_METHOD_FIGURE_PREFIX}_{suffix}"
        rows.append(check_row(
            "methods_figures",
            f"{REQUIRED_METHOD_FIGURE_PREFIX}:{suffix}",
            "error",
            path.exists(),
            "Methods figure artifact is present" if path.exists() else "Methods figure artifact is missing",
            prefix=REQUIRED_METHOD_FIGURE_PREFIX,
            path=rel(path, root),
        ))

    manuscript_path = root / "manuscript" / "manuscript.tex"
    manuscript_text = manuscript_path.read_text(encoding="utf-8") if manuscript_path.exists() else ""
    manuscript_checks = [
        ("ethics_statement_present", "error", "\\section*{Ethics statement}"),
        ("funding_statement_present", "error", "\\section*{Funding}"),
        ("credit_statement_present", "error", "\\section*{CRediT authorship contribution statement}"),
        ("generative_ai_disclosure_present", "error", "\\section*{Declaration of generative AI"),
        ("physionet_license_named", "error", "Open Data Commons Attribution License v1.0"),
        ("bnci_license_named", "error", "Creative Commons Attribution-NoDerivatives 4.0"),
        ("competing_interests_declaration_present", "warning", "\\section*{Declaration of competing interests}"),
    ]
    for name, severity, marker in manuscript_checks:
        present = marker in manuscript_text
        rows.append(check_row(
            "manuscript_declarations", name, severity, present,
            "Required manuscript declaration is present" if present else "Author confirmation is required before submission",
            path="manuscript/manuscript.tex",
        ))
    doi_present = "doi:" in (root / "CITATION.cff").read_text(encoding="utf-8") if (root / "CITATION.cff").exists() else False
    rows.append(check_row(
        "manuscript_declarations", "permanent_software_doi_present", "warning", doi_present,
        "Permanent software DOI is recorded" if doi_present else "Archive the release and add its DOI before submission",
        path="CITATION.cff",
    ))

    release_manifest = read_json(root / "artifacts" / "manifests" / "release_manifest.json")
    rows.append(check_row(
        "release_manifest",
        "release_manifest_ready",
        "error",
        bool(release_manifest and release_manifest.get("release_ready")),
        "Release manifest reports release_ready=true" if release_manifest and release_manifest.get("release_ready") else "Release manifest missing or not release-ready",
        path="artifacts/manifests/release_manifest.json",
    ))

    return pd.DataFrame(rows)


def write_markdown(summary: dict[str, Any], checks: pd.DataFrame, output: Path) -> None:
    failed = checks.loc[~checks["passed"], ["severity", "category", "check", "detail"]]
    lines = [
        "# Submission readiness",
        "",
        "This file summarizes deterministic repository checks for preparing the benchmark for a methods-journal submission. The checks are derived only from files already present in the repository.",
        "",
        "## Status",
        "",
        f"- Ready for release packaging: `{str(summary['ready']).lower()}`",
        f"- Checks run: {summary['n_checks']}",
        f"- Failed errors: {summary['n_failed_errors']}",
        f"- Failed warnings: {summary['n_failed_warnings']}",
        "",
        "## Scope",
        "",
        "- Confirms required metadata, provenance, reproducibility, statistical-reporting, validation, result, method-figure, and release-manifest artifacts.",
        "- Does not judge novelty, editorial fit, or clinical claims.",
        "- Does not generate benchmark observations or alter result values.",
        "",
        "## Failed checks",
        "",
    ]
    if failed.empty:
        lines.append("No failed checks.")
    else:
        for row in failed.to_dict("records"):
            lines.append(f"- `{row['severity']}` `{row['category']}` `{row['check']}`: {row['detail']}")
    lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--results-dir", type=Path, default=Path("results"))
    ap.add_argument("--reports-dir", type=Path, default=Path("reports"))
    ap.add_argument("--prefix", action="append", dest="prefixes", help="Prefix to include; may be supplied multiple times")
    ap.add_argument("--allow-not-ready", action="store_true")
    args = ap.parse_args()

    root = args.root.resolve()
    results_dir = (root / args.results_dir).resolve() if not args.results_dir.is_absolute() else args.results_dir
    reports_dir = (root / args.reports_dir).resolve() if not args.reports_dir.is_absolute() else args.reports_dir
    prefixes = args.prefixes or DEFAULT_PREFIXES
    reports_dir.mkdir(parents=True, exist_ok=True)

    checks = build_checks(root, results_dir, reports_dir, prefixes)
    n_failed_errors = int(((checks["severity"] == "error") & (~checks["passed"])).sum())
    n_failed_warnings = int(((checks["severity"] == "warning") & (~checks["passed"])).sum())
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "prefixes": prefixes,
        "ready": n_failed_errors == 0,
        "n_checks": int(len(checks)),
        "n_failed_errors": n_failed_errors,
        "n_failed_warnings": n_failed_warnings,
        "note": "Checks are derived from repository files only; no benchmark observations were generated.",
    }

    checks_path = reports_dir / "submission_readiness_checks.csv"
    summary_path = reports_dir / "submission_readiness_summary.json"
    markdown_path = root / "SUBMISSION_READINESS.md"
    checks.to_csv(checks_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_markdown(summary, checks, markdown_path)

    print(json.dumps({
        "checks": str(checks_path),
        "summary": str(summary_path),
        "ready": summary["ready"],
        "n_checks": summary["n_checks"],
        "n_failed_errors": n_failed_errors,
        "n_failed_warnings": n_failed_warnings,
    }, indent=2))
    if not summary["ready"] and not args.allow_not_ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
