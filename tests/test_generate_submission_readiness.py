import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("generate_submission_readiness", ROOT / "scripts" / "generate_submission_readiness.py")
generate_submission_readiness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_submission_readiness)


def prepare_release_ready_tree(source_root: Path, tmp_path: Path) -> Path:
    """Create generated reporting artifacts in a temporary copy for readiness tests.

    A clean CI checkout may contain source result tables but not every generated
    statistical-report file. The readiness gate is still supposed to block a
    release until those files exist, so this test prepares them explicitly rather
    than requiring generated artifacts to be committed before pytest runs.
    """
    work = tmp_path / "repo"
    shutil.copytree(source_root, work, ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "*.pyc", "*.pyo", "dist", ".venv", "venv", "env", "moabb_data", "mne_data", "data"))
    for prefix in generate_submission_readiness.DEFAULT_PREFIXES:
        subprocess.run(
            [
                sys.executable,
                "scripts/generate_statistical_report.py",
                "--results-dir",
                "results",
                "--reports-dir",
                "reports",
                "--prefix",
                prefix,
            ],
            cwd=work,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    subprocess.run(
        [
            sys.executable,
            "scripts/generate_methods_figures.py",
            "--results-dir",
            "results",
            "--reports-dir",
            "artifacts/generated_reports",
            "--prefix",
            generate_submission_readiness.REQUIRED_METHOD_FIGURE_PREFIX,
            "--metric",
            "roc_auc",
        ],
        cwd=work,
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    subprocess.run(
        [
            sys.executable,
            "scripts/build_release_manifest.py",
            "--results-dir",
            "results",
            "--reports-dir",
            "artifacts/generated_reports",
            "--output",
            "artifacts/manifests/release_manifest.json",
        ],
        cwd=work,
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return work


def test_submission_readiness_checks_prepared_repository_pass_without_failed_errors(tmp_path):
    work = prepare_release_ready_tree(ROOT, tmp_path)
    checks = generate_submission_readiness.build_checks(work, work / "results", work / "reports", generate_submission_readiness.DEFAULT_PREFIXES)
    assert not checks.empty
    failed_errors = checks[(checks["severity"] == "error") & (~checks["passed"])]
    assert failed_errors.empty, failed_errors[["category", "check", "detail"]].to_dict("records")
    assert {"repository_metadata", "validation_artifacts", "analysis_artifacts", "methods_figures"}.issubset(set(checks["category"]))


def test_consistency_checks_detect_missing_canonical_subject_table(tmp_path):
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "*.pyc", "*.pyo", "dist", ".venv", "venv", "env", "moabb_data", "mne_data", "data"))
    prefix = generate_submission_readiness.DEFAULT_PREFIXES[0]
    (work / "results" / f"{prefix}_subject_summary.csv").unlink()
    checks = generate_submission_readiness.build_checks(work, work / "results", work / "reports", generate_submission_readiness.DEFAULT_PREFIXES)
    missing = checks[(checks["category"] == "analysis_artifacts") & (~checks["passed"])]
    assert f"{prefix}:subject_summary.csv" in set(missing["check"])


def test_submission_readiness_detects_missing_required_artifact(tmp_path):
    work = prepare_release_ready_tree(ROOT, tmp_path)
    missing = work / "artifacts" / "manifests" / "release_manifest.json"
    missing.unlink()
    checks = generate_submission_readiness.build_checks(work, work / "results", work / "reports", generate_submission_readiness.DEFAULT_PREFIXES)
    release_rows = checks[checks["check"] == "release_manifest_ready"]
    assert len(release_rows) == 1
    assert not bool(release_rows.iloc[0]["passed"])


def test_submission_readiness_writes_markdown_status(tmp_path):
    checks = pd.DataFrame([
        {"category": "example", "check": "ok", "severity": "error", "passed": True, "detail": "ok"},
    ])
    summary = {"ready": True, "n_checks": 1, "n_failed_errors": 0, "n_failed_warnings": 0}
    output = tmp_path / "SUBMISSION_READINESS.md"
    generate_submission_readiness.write_markdown(summary, checks, output)
    text = output.read_text(encoding="utf-8")
    assert "Ready for release packaging: `true`" in text
    assert "No failed checks." in text


def test_full_physionet_is_first_class_and_exact_cohort_size_is_enforced():
    full = "PhysionetMI_PhysionetMI_all_riemann_lr"
    assert full in generate_submission_readiness.DEFAULT_PREFIXES
    assert generate_submission_readiness.EXPECTED_SUBJECT_COUNTS[full] == 109
    assert generate_submission_readiness.REQUIRED_METHOD_FIGURE_PREFIX == full
    checks = generate_submission_readiness.build_checks(ROOT, ROOT / "results", ROOT / "reports", [full])
    count = checks.loc[checks["check"].eq(f"{full}:expected_subject_count")].iloc[0]
    folds = checks.loc[checks["check"].eq(f"{full}:results.csv")].iloc[0]
    assert count["passed"] and count["n_subjects"] == 109
    assert folds["severity"] == "error" and bool(folds["passed"])


def test_submission_readiness_checks_manuscript_declarations():
    checks = generate_submission_readiness.build_checks(
        ROOT, ROOT / "results", ROOT / "reports", generate_submission_readiness.DEFAULT_PREFIXES
    )
    declarations = checks[checks["category"].eq("manuscript_declarations")].set_index("check")
    for name in [
        "ethics_statement_present",
        "funding_statement_present",
        "credit_statement_present",
        "physionet_license_named",
        "bnci_license_named",
    ]:
        assert bool(declarations.loc[name, "passed"]), name
        assert declarations.loc[name, "severity"] == "error"
    assert declarations.loc["competing_interests_declaration_present", "severity"] == "warning"
    assert not bool(declarations.loc["competing_interests_declaration_present", "passed"])
    assert declarations.loc["permanent_software_doi_present", "severity"] == "warning"
