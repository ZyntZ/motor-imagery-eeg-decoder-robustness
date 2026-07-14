import importlib.util
import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("generate_submission_readiness", ROOT / "scripts" / "generate_submission_readiness.py")
generate_submission_readiness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_submission_readiness)


def test_submission_readiness_checks_current_repository_pass_without_failed_errors():
    checks = generate_submission_readiness.build_checks(ROOT, ROOT / "results", ROOT / "reports", generate_submission_readiness.DEFAULT_PREFIXES)
    assert not checks.empty
    failed_errors = checks[(checks["severity"] == "error") & (~checks["passed"])]
    assert failed_errors.empty, failed_errors[["category", "check", "detail"]].to_dict("records")
    assert {"repository_metadata", "validation_artifacts", "analysis_artifacts", "methods_figures"}.issubset(set(checks["category"]))


def test_submission_readiness_detects_missing_required_artifact(tmp_path):
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".pytest_cache", "__pycache__", "*.pyc", "dist"))
    missing = work / "reports" / "release_manifest.json"
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
