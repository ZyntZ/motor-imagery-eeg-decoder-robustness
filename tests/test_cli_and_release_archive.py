import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_NAMES = [
    "analyze_robustness.py",
    "build_release_archive.py",
    "build_release_manifest.py",
    "final_statistics.py",
    "generate_methods_figures.py",
    "generate_statistical_report.py",
    "generate_submission_readiness.py",
    "recommend_interventions.py",
    "run_benchmark.py",
    "refresh_benchmark_summaries.py",
    "validate_results.py",
]
FIGURE_PREFIX = "PhysionetMI_PhysionetMI_all_riemann_lr"

SPEC_ARCHIVE = importlib.util.spec_from_file_location("build_release_archive", ROOT / "scripts" / "build_release_archive.py")
build_release_archive = importlib.util.module_from_spec(SPEC_ARCHIVE)
SPEC_ARCHIVE.loader.exec_module(build_release_archive)

SPEC_FIGURES = importlib.util.spec_from_file_location("generate_methods_figures", ROOT / "scripts" / "generate_methods_figures.py")
generate_methods_figures = importlib.util.module_from_spec(SPEC_FIGURES)
SPEC_FIGURES.loader.exec_module(generate_methods_figures)


def ensure_required_method_figures_exist():
    """Create required figure artifacts from committed CSVs for clean CI checkouts."""
    generate_methods_figures.generate_figures(ROOT / "results", ROOT / "reports", FIGURE_PREFIX, "roc_auc")


def ensure_submission_readiness_exists():
    """Create readiness artifacts from committed reports for archive-audit tests."""
    spec = importlib.util.spec_from_file_location("generate_submission_readiness", ROOT / "scripts" / "generate_submission_readiness.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    checks = mod.build_checks(ROOT, ROOT / "results", ROOT / "reports", mod.DEFAULT_PREFIXES)
    n_failed_errors = int(((checks["severity"] == "error") & (~checks["passed"])).sum())
    summary = {
        "generated_at_utc": "test",
        "prefixes": mod.DEFAULT_PREFIXES,
        "ready": n_failed_errors == 0,
        "n_checks": int(len(checks)),
        "n_failed_errors": n_failed_errors,
        "n_failed_warnings": int(((checks["severity"] == "warning") & (~checks["passed"])).sum()),
        "note": "test-generated readiness summary",
    }
    checks.to_csv(ROOT / "reports" / "submission_readiness_checks.csv", index=False)
    (ROOT / "reports" / "submission_readiness_summary.json").write_text(__import__("json").dumps(summary, indent=2) + "\n", encoding="utf-8")
    mod.write_markdown(summary, checks, ROOT / "SUBMISSION_READINESS.md")


def test_cli_help_smoke_for_all_scripts():
    for name in SCRIPT_NAMES:
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / name), "--help"], cwd=ROOT, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, name + " failed: " + result.stderr
        assert "usage" in result.stdout.lower()


def test_run_benchmark_dry_run_smoke():
    result = subprocess.run([sys.executable, "scripts/run_benchmark.py", "--config", "configs/benchmark.yaml", "--dry-run"], cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    assert "dataset" in result.stdout.lower() or "config" in result.stdout.lower()


def test_release_archive_audit_passes_after_generating_required_outputs():
    ensure_required_method_figures_exist()
    ensure_submission_readiness_exists()
    audit = build_release_archive.audit_release(ROOT)
    assert audit["passed"]
    assert audit["missing_required_files"] == []
    assert audit["disallowed_filenames"] == []
    assert audit["raw_data_like_directories"] == []


def test_release_archive_builder_excludes_cache_files(tmp_path):
    ensure_required_method_figures_exist()
    ensure_submission_readiness_exists()
    output = tmp_path / "release.zip"
    result = build_release_archive.build_archive(ROOT, output, top_level_name="release-test")
    assert result["passed"]
    assert result["archive_file_count"] == result["n_included_files"]
    assert result["archive_junk_entries"] == []
    assert output.exists() and output.stat().st_size > 0


def test_generated_manuscript_pdf_is_not_required_by_release_audit():
    assert "manuscript/manuscript.pdf" not in build_release_archive.REQUIRED_FILES
