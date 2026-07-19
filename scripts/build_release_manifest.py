#!/usr/bin/env python3
"""Build a reproducibility manifest for a commit-ready benchmark release.

The manifest records file hashes, selected package versions, validation summaries,
and existence checks for expected reporting outputs. It does not create or modify
benchmark observations.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as importlib_metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PREFIXES = [
    "BNCI2014-001_BNCI2014_001_all_csp_lda",
    "BNCI2014-001_BNCI2014_001_all_riemann_lr",
    "PhysionetMI_PhysionetMI_all_riemann_lr",
    "PhysionetMI_PhysionetMI_all_csp_lda",
]
METHODS_FIGURE_PREFIXES = ["PhysionetMI_PhysionetMI_all_riemann_lr"]
FULL_PHYSIONET_PREFIXES = ["PhysionetMI_PhysionetMI_all_csp_lda", "PhysionetMI_PhysionetMI_all_riemann_lr"]
COMPARISON_OUTPUTS = [
    "results/PhysionetMI_csp_lda_vs_riemann_lr_paired_comparison.csv",
    "results/PhysionetMI_csp_lda_vs_riemann_lr_paired_subject_differences.csv",
]
HASH_SUFFIXES = {".py", ".md", ".toml", ".yml", ".yaml", ".txt", ".csv", ".json", ".cff", ".png", ".svg", ".tex"}
EXCLUDE_PARTS = {".git", "__pycache__", ".pytest_cache", "checkpoints", ".venv", "venv", "env", ".env", "moabb_data", "mne_data", "data", "dist"}
PACKAGE_NAMES = ["numpy", "pandas", "scipy", "scikit-learn", "statsmodels", "mne", "moabb", "pyriemann", "matplotlib", "plotly", "pytest", "PyYAML"]
EXPECTED_STAT_OUTPUT_SUFFIXES = ["statistical_paired_effects.csv", "statistical_report_table.csv"]
EXPECTED_REPORT_SUFFIXES = ["statistical_report_table.tex", "statistical_report_summary.md"]
EXPECTED_METHODS_FIGURE_SUFFIXES = [
    "methods_pipeline_schematic.png",
    "methods_pipeline_schematic.svg",
    "methods_robustness_degradation_roc_auc.png",
    "methods_robustness_degradation_roc_auc.svg",
    "methods_figures_manifest.json",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_manifest_files(root: Path, excluded_paths: set[Path] | None = None) -> list[Path]:
    files: list[Path] = []
    excluded = {p.resolve() for p in (excluded_paths or set())}
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if not path.is_file() or path.resolve() in excluded or any(part in EXCLUDE_PARTS for part in rel.parts):
            continue
        if path.suffix in HASH_SUFFIXES or path.name in {"LICENSE", "Makefile", "run_all.sh"}:
            files.append(path)
    return sorted(files)


def package_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for name in PACKAGE_NAMES:
        try:
            versions[name] = importlib_metadata.version(name)
        except importlib_metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def read_validation_summary(reports_dir: Path, prefix: str) -> dict[str, object] | None:
    path = reports_dir.parent / "validation" / f"{prefix}_validation_summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def expected_outputs(root: Path, results_dir: Path, reports_dir: Path, prefixes: list[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for prefix in prefixes:
        for suffix in EXPECTED_STAT_OUTPUT_SUFFIXES:
            path = results_dir / f"{prefix}_{suffix}"
            rows.append({"prefix": prefix, "path": display_path(path, root), "exists": path.exists()})
        for suffix in EXPECTED_REPORT_SUFFIXES:
            path = reports_dir / f"{prefix}_{suffix}"
            rows.append({"prefix": prefix, "path": display_path(path, root), "exists": path.exists()})
        for suffix in ["validation_checks.csv", "validation_summary.json"]:
            path = root / "artifacts" / "validation" / f"{prefix}_{suffix}"
            rows.append({"prefix": prefix, "path": display_path(path, root), "exists": path.exists()})
    for fig_prefix in METHODS_FIGURE_PREFIXES:
        for suffix in EXPECTED_METHODS_FIGURE_SUFFIXES:
            path = reports_dir / f"{fig_prefix}_{suffix}"
            rows.append({"prefix": fig_prefix, "path": display_path(path, root), "exists": path.exists()})
    for prefix in FULL_PHYSIONET_PREFIXES:
        for suffix in ["mixed_model_diagnostics.csv", "mixed_model_diagnostics_summary.json"]:
            path = results_dir / f"{prefix}_{suffix}"
            rows.append({"prefix": prefix, "path": display_path(path, root), "exists": path.exists()})
    for relative in COMPARISON_OUTPUTS:
        path = root / relative
        rows.append({"prefix": "PhysionetMI_csp_lda_vs_riemann_lr", "path": relative, "exists": path.exists()})
    return rows


def build_manifest(root: Path, results_dir: Path, reports_dir: Path, prefixes: list[str], output_path: Path | None = None) -> dict[str, object]:
    files = iter_manifest_files(root, {output_path} if output_path else set())
    expected = expected_outputs(root, results_dir, reports_dir, prefixes)
    validation = {prefix: read_validation_summary(reports_dir, prefix) for prefix in prefixes}
    failed_validations = [p for p, s in validation.items() if not s or int(s.get("n_failed_errors", 1)) > 0]
    missing_expected = [row for row in expected if not row["exists"]]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "package_versions": package_versions(),
        "prefixes": prefixes,
        "validation_summaries": validation,
        "expected_output_checks": expected,
        "release_ready": not failed_validations and not missing_expected,
        "failed_validation_prefixes": failed_validations,
        "missing_expected_outputs": missing_expected,
        "file_hashes_sha256": [
            {"path": display_path(path, root), "sha256": sha256_file(path), "bytes": path.stat().st_size}
            for path in files
        ],
        "note": "Manifest derived from files present in this repository snapshot; no benchmark observations were generated.",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--results-dir", type=Path, default=Path("results"))
    ap.add_argument("--reports-dir", type=Path, default=Path("reports"))
    ap.add_argument("--prefix", action="append", dest="prefixes", help="Prefix to include; may be supplied multiple times")
    ap.add_argument("--output", type=Path, default=Path("artifacts/manifests/release_manifest.json"))
    ap.add_argument("--allow-not-ready", action="store_true")
    args = ap.parse_args()

    root = args.root.resolve()
    results_dir = (root / args.results_dir).resolve() if not args.results_dir.is_absolute() else args.results_dir
    reports_dir = (root / args.reports_dir).resolve() if not args.reports_dir.is_absolute() else args.reports_dir
    prefixes = args.prefixes or DEFAULT_PREFIXES
    output = (root / args.output).resolve() if not args.output.is_absolute() else args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(root, results_dir, reports_dir, prefixes, output)
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "release_ready": manifest["release_ready"],
        "n_file_hashes": len(manifest["file_hashes_sha256"]),
        "n_missing_expected_outputs": len(manifest["missing_expected_outputs"]),
        "failed_validation_prefixes": manifest["failed_validation_prefixes"],
    }, indent=2))
    if not manifest["release_ready"] and not args.allow_not_ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
