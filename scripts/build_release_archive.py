#!/usr/bin/env python3
"""Build and audit a clean commit-ready release archive.

The archive contains repository files only. It excludes caches, bytecode, VCS
metadata, local notebooks, and raw EEG/data-cache directories. It does not create
or modify benchmark observations.
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "checkpoints", "moabb_data", "mne_data", "data"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".zip"}
DISALLOWED_TOKENS = ["assistant", "for_me", "for-me", "для_меня", "для-меня", "ииш", "ai_generated", "ai-generated"]
REQUIRED_FILES = [
    "LICENSE",
    "CITATION.cff",
    "README.md",
    "REPRODUCIBILITY.md",
    "STATISTICAL_REPORTING.md",
    "MANUSCRIPT_PLACEHOLDER.md",
    "SUBMISSION_READINESS.md",
    ".github/workflows/ci.yml",
    "scripts/validate_results.py",
    "scripts/generate_statistical_report.py",
    "scripts/generate_methods_figures.py",
    "scripts/build_release_manifest.py",
    "scripts/build_release_archive.py",
    "scripts/generate_submission_readiness.py",
    "reports/release_manifest.json",
    "reports/submission_readiness_checks.csv",
    "reports/submission_readiness_summary.json",
]
REQUIRED_FIGURE_SUFFIXES = [
    "methods_pipeline_schematic.png",
    "methods_pipeline_schematic.svg",
    "methods_robustness_degradation_roc_auc.png",
    "methods_robustness_degradation_roc_auc.svg",
    "methods_intervention_class_counts.png",
    "methods_intervention_class_counts.svg",
    "methods_figures_manifest.json",
]
DEFAULT_FIGURE_PREFIX = "BNCI2014-001_BNCI2014_001_all_riemann_lr"


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    if path.name.endswith("~"):
        return False
    return path.is_file()


def archive_members(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if should_include(p, root))


def audit_release(root: Path, figure_prefix: str = DEFAULT_FIGURE_PREFIX) -> dict[str, object]:
    required = [root / p for p in REQUIRED_FILES]
    required.extend(root / "reports" / f"{figure_prefix}_{suffix}" for suffix in REQUIRED_FIGURE_SUFFIXES)
    missing = [str(p.relative_to(root)) for p in required if not p.exists()]
    bad_names = []
    for p in archive_members(root):
        rel = str(p.relative_to(root)).lower()
        if any(token in rel for token in DISALLOWED_TOKENS):
            bad_names.append(str(p.relative_to(root)))
    raw_like_dirs = [str(p.relative_to(root)) for p in root.rglob("*") if p.is_dir() and p.name in {"data", "moabb_data", "mne_data"}]
    return {
        "passed": not missing and not bad_names and not raw_like_dirs,
        "missing_required_files": missing,
        "disallowed_filenames": bad_names,
        "raw_data_like_directories": raw_like_dirs,
        "n_included_files": len(archive_members(root)),
    }


def build_archive(root: Path, output: Path, top_level_name: str | None = None) -> dict[str, object]:
    audit = audit_release(root)
    if not audit["passed"]:
        raise RuntimeError(json.dumps(audit, indent=2))
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    top = top_level_name or root.name
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in archive_members(root):
            zf.write(p, Path(top) / p.relative_to(root))
    with zipfile.ZipFile(output) as zf:
        names = zf.namelist()
        junk = [n for n in names if "__pycache__" in n or ".pytest_cache" in n or n.endswith((".pyc", ".pyo"))]
    result = {**audit, "archive": str(output), "archive_bytes": output.stat().st_size, "archive_file_count": len(names), "archive_junk_entries": junk}
    if junk:
        result["passed"] = False
        raise RuntimeError(json.dumps(result, indent=2))
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--output", type=Path, default=Path("dist/JNM_submission_readiness_update.zip"))
    ap.add_argument("--audit-only", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    if args.audit_only:
        result = audit_release(root)
    else:
        output = args.output if args.output.is_absolute() else root / args.output
        result = build_archive(root, output)
    print(json.dumps(result, indent=2))
    if not result.get("passed", False):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
