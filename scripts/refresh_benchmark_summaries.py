#!/usr/bin/env python3
"""Rebuild subject and population summaries from an existing fold-level results CSV."""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bci_robustness.core import population_summary, subject_level_summary



def find_subject_summary(results_dir: Path, prefix: str) -> tuple[Path | None, list[Path]]:
    """Find an exact subject summary in the requested or nearby result directories."""
    filename = f"{prefix}_subject_summary.csv"
    requested = results_dir / filename
    searched = [requested]
    if requested.exists():
        return requested, searched
    roots = [results_dir.parent, ROOT, ROOT.parent]
    seen = {requested.resolve()}
    matches = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.glob(f"*/results/{filename}"):
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved); searched.append(path)
                if path.is_file(): matches.append(path)
        direct = root / "results" / filename
        resolved = direct.resolve()
        if resolved not in seen:
            seen.add(resolved); searched.append(direct)
            if direct.is_file(): matches.append(direct)
    unique = sorted({path.resolve(): path for path in matches}.values())
    if len(unique) > 1:
        raise RuntimeError(f"Multiple subject summaries match {filename}: {[str(p) for p in unique]}")
    return (unique[0] if unique else None), searched


def extract_subject_summary_from_archives(results_dir: Path, prefix: str) -> tuple[Path | None, list[Path]]:
    """Extract an exact subject summary from a nearby project ZIP when unambiguous."""
    filename = f"{prefix}_subject_summary.csv"
    archives = sorted({
        *ROOT.parent.glob("*.zip"),
        *ROOT.glob("*.zip"),
        *(ROOT / "dist").glob("*.zip"),
        *ROOT.parent.glob("*/dist/*.zip"),
    })
    hits: list[tuple[Path, str]] = []
    for archive in archives:
        try:
            with zipfile.ZipFile(archive) as zf:
                for member in zf.namelist():
                    if member.endswith(f"/results/{filename}") or member == f"results/{filename}":
                        hits.append((archive, member))
        except zipfile.BadZipFile:
            continue
    if not hits:
        return None, archives
    if len(hits) > 1:
        raise RuntimeError(f"Multiple archive members match {filename}: {[(str(a), m) for a, m in hits]}")
    archive, member = hits[0]
    target = results_dir / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        data = zf.read(member)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(target)
    return target, archives

def infer_checkpoint_key(prefix: str) -> tuple[str, str]:
    """Infer the checkpoint dataset alias and decoder from a full output prefix."""
    pipeline = next((name for name in ["riemann_lr", "csp_lda", "tangent_space_lr"] if prefix.endswith(name)), None)
    dataset = next((name for name in ["PhysionetMI", "BNCI2014-001", "BNCI2014_001"] if prefix.startswith(name)), None)
    if pipeline is None or dataset is None:
        raise ValueError(
            f"Cannot infer checkpoint names from prefix {prefix!r}. "
            "Use --checkpoint-dataset and --pipeline explicitly."
        )
    return dataset, pipeline


def recover_results_from_checkpoints(
    results_dir: Path,
    prefix: str,
    checkpoint_dataset: str | None = None,
    pipeline: str | None = None,
    expected_subjects: int | None = None,
) -> tuple[pd.DataFrame, list[Path]]:
    """Reconstruct a missing fold-level results CSV from completed subject checkpoints."""
    inferred_dataset, inferred_pipeline = infer_checkpoint_key(prefix)
    checkpoint_dataset = checkpoint_dataset or inferred_dataset
    pipeline = pipeline or inferred_pipeline
    checkpoint_dir = results_dir / "checkpoints"
    paths = sorted(checkpoint_dir.glob(f"{checkpoint_dataset}_{pipeline}_subject-*_robustness.csv"))
    if not paths:
        raise FileNotFoundError(
            f"No raw results file and no matching checkpoints. Looked for "
            f"{checkpoint_dir / f'{checkpoint_dataset}_{pipeline}_subject-*_robustness.csv'}"
        )
    frames = []
    subjects = set()
    for path in paths:
        frame = pd.read_csv(path)
        if frame.empty or "subject" not in frame.columns:
            raise ValueError(f"Checkpoint is empty or lacks subject column: {path}")
        checkpoint_subjects = set(frame["subject"].dropna().astype(int))
        if len(checkpoint_subjects) != 1:
            raise ValueError(f"Checkpoint must contain exactly one subject: {path}")
        subject = next(iter(checkpoint_subjects))
        if subject in subjects:
            raise ValueError(f"Duplicate subject {subject} across checkpoints")
        subjects.add(subject)
        frames.append(frame)
    if expected_subjects is not None and len(subjects) != int(expected_subjects):
        missing = sorted(set(range(1, int(expected_subjects) + 1)) - subjects)
        raise RuntimeError(
            f"Found {len(subjects)} unique subject checkpoints, expected {expected_subjects}. "
            f"Missing subject IDs: {missing[:20]}"
        )
    return pd.concat(frames, ignore_index=True), paths



def probe_source(
    results_dir: Path,
    prefix: str,
    checkpoint_dataset: str | None = None,
    pipeline: str | None = None,
) -> dict[str, object]:
    """Locate an available source using the same discovery rules as refresh_summaries."""
    raw_path = results_dir / f"{prefix}_results.csv"
    if raw_path.exists():
        return {"available": True, "mode": "fold_results", "source": str(raw_path)}
    try:
        _, paths = recover_results_from_checkpoints(
            results_dir, prefix, checkpoint_dataset, pipeline, expected_subjects=None
        )
        return {"available": True, "mode": "checkpoints", "source": str(results_dir / "checkpoints"), "n_checkpoint_files": len(paths)}
    except FileNotFoundError:
        pass
    subject_path, searched_paths = find_subject_summary(results_dir, prefix)
    searched_archives: list[Path] = []
    if subject_path is None:
        subject_path, searched_archives = extract_subject_summary_from_archives(results_dir, prefix)
    if subject_path is not None:
        return {"available": True, "mode": "subject_summary", "source": str(subject_path)}
    return {
        "available": False,
        "mode": "not_found",
        "prefix": prefix,
        "searched_summary_paths": [str(path) for path in searched_paths],
        "searched_archives": [str(path) for path in searched_archives],
    }

def refresh_summaries(
    results_dir: Path,
    prefix: str,
    random_seed: int = 42,
    recover_from_checkpoints: bool = False,
    checkpoint_dataset: str | None = None,
    pipeline: str | None = None,
    expected_subjects: int | None = None,
    allow_existing_subject_summary: bool = False,
) -> dict[str, object]:
    raw_path = results_dir / f"{prefix}_results.csv"
    subject_path = results_dir / f"{prefix}_subject_summary.csv"
    population_path = results_dir / f"{prefix}_population_summary.csv"
    # Recovery from local fold files/checkpoints must not be shadowed by an
    # unrelated sibling checkout. Search nearby summaries only in the explicit
    # subject-summary fallback mode.
    if subject_path.exists():
        discovered_subject_path, searched_subject_paths = subject_path, [subject_path]
    elif allow_existing_subject_summary:
        discovered_subject_path, searched_subject_paths = find_subject_summary(results_dir, prefix)
    else:
        discovered_subject_path, searched_subject_paths = None, [subject_path]
    if discovered_subject_path is None and allow_existing_subject_summary:
        discovered_subject_path, searched_archives = extract_subject_summary_from_archives(results_dir, prefix)
    else:
        searched_archives = []
    if discovered_subject_path is not None and discovered_subject_path != subject_path:
        subject_path.parent.mkdir(parents=True, exist_ok=True)
        shutil_source = discovered_subject_path.read_bytes()
        temporary_subject = subject_path.with_suffix(subject_path.suffix + ".tmp")
        temporary_subject.write_bytes(shutil_source)
        temporary_subject.replace(subject_path)
    recovered = False
    checkpoint_paths: list[Path] = []
    if raw_path.exists():
        results = pd.read_csv(raw_path)
    elif recover_from_checkpoints:
        try:
            results, checkpoint_paths = recover_results_from_checkpoints(
                results_dir, prefix, checkpoint_dataset, pipeline, expected_subjects
            )
        except FileNotFoundError as checkpoint_error:
            if not (allow_existing_subject_summary and subject_path.exists()):
                searched = [str(path) for path in searched_subject_paths]
                archives = [str(path) for path in searched_archives]
                raise FileNotFoundError(
                    f"Neither fold results, checkpoints, nor the exact 109-subject summary were found for {prefix!r}. "
                    f"Searched summary paths: {searched}. Searched ZIP archives: {archives}. "
                    "The previous 109-subject computation outputs are not present in this workspace. "
                    "Restore the original results directory or the full results CSV before post-processing."
                ) from checkpoint_error
            results = None
        if results is not None:
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = raw_path.with_suffix(raw_path.suffix + ".tmp")
            results.to_csv(temporary, index=False)
            temporary.replace(raw_path)
            recovered = True
        else:
            subject = pd.read_csv(subject_path)
            required_subject = {"dataset", "subject", "pipeline", "stressor", "montage", "dropout_fraction", "roc_auc", "balanced_accuracy", "n_channels"}
            missing_subject = sorted(required_subject - set(subject.columns))
            if missing_subject:
                raise ValueError(f"{subject_path} is missing required columns: {missing_subject}")
            actual_subjects = set(pd.to_numeric(subject["subject"], errors="coerce").dropna().astype(int))
            if expected_subjects is not None and len(actual_subjects) != int(expected_subjects):
                missing_subjects = sorted(set(range(1, int(expected_subjects) + 1)) - actual_subjects)
                raise RuntimeError(
                    f"Subject summary contains {len(actual_subjects)} unique subjects, expected {expected_subjects}. "
                    f"Missing subject IDs: {missing_subjects[:20]}"
                )
            population = population_summary(subject, random_seed=random_seed)
            population.to_csv(population_path, index=False)
            return {
                "prefix": prefix, "source": str(subject_path), "mode": "existing_subject_summary",
                "recovered_from_checkpoints": False, "n_checkpoint_files": 0, "n_fold_rows": None,
                "n_subjects": int(subject["subject"].nunique()), "n_subject_condition_rows": int(len(subject)),
                "subject_summary": str(subject_path), "population_summary": str(population_path),
                "limitation": "Fold-level results and checkpoints were unavailable; fold-level validation cannot be performed.",
            }
    elif allow_existing_subject_summary and subject_path.exists():
        subject = pd.read_csv(subject_path)
        required_subject = {"dataset", "subject", "pipeline", "stressor", "montage", "dropout_fraction", "roc_auc", "balanced_accuracy", "n_channels"}
        missing_subject = sorted(required_subject - set(subject.columns))
        if missing_subject:
            raise ValueError(f"{subject_path} is missing required columns: {missing_subject}")
        actual_subjects = set(pd.to_numeric(subject["subject"], errors="coerce").dropna().astype(int))
        if expected_subjects is not None and len(actual_subjects) != int(expected_subjects):
            missing_subjects = sorted(set(range(1, int(expected_subjects) + 1)) - actual_subjects)
            raise RuntimeError(
                f"Subject summary contains {len(actual_subjects)} unique subjects, expected {expected_subjects}. "
                f"Missing subject IDs: {missing_subjects[:20]}"
            )
        population = population_summary(subject, random_seed=random_seed)
        population.to_csv(population_path, index=False)
        return {
            "prefix": prefix,
            "source": str(subject_path),
            "mode": "existing_subject_summary",
            "recovered_from_checkpoints": False,
            "n_checkpoint_files": 0,
            "n_fold_rows": None,
            "n_subjects": int(subject["subject"].nunique()),
            "n_subject_condition_rows": int(len(subject)),
            "subject_summary": str(subject_path),
            "population_summary": str(population_path),
            "limitation": "Fold-level results and checkpoints were unavailable; fold-level validation cannot be performed.",
        }
    else:
        candidates = sorted(path.name for path in results_dir.glob("*_results.csv"))
        raise FileNotFoundError(
            f"Missing {raw_path}. Available result files: {candidates or 'none'}. "
            f"No matching checkpoints were found under {results_dir / 'checkpoints'}. "
            "Use --allow-existing-subject-summary only if the 109-subject subject summary is present."
        )
    required = {"dataset", "subject", "pipeline", "stressor", "montage", "dropout_fraction", "roc_auc", "balanced_accuracy", "n_channels"}
    missing = sorted(required - set(results.columns))
    if missing:
        raise ValueError(f"{raw_path} is missing required columns: {missing}")
    actual_subjects = set(pd.to_numeric(results["subject"], errors="coerce").dropna().astype(int))
    if expected_subjects is not None and len(actual_subjects) != int(expected_subjects):
        missing_subjects = sorted(set(range(1, int(expected_subjects) + 1)) - actual_subjects)
        raise RuntimeError(
            f"Results contain {len(actual_subjects)} unique subjects, expected {expected_subjects}. "
            f"Missing subject IDs: {missing_subjects[:20]}"
        )
    subject = subject_level_summary(results)
    population = population_summary(results, random_seed=random_seed)
    subject.to_csv(subject_path, index=False)
    population.to_csv(population_path, index=False)
    return {
        "prefix": prefix,
        "source": str(raw_path),
        "mode": "recovered_checkpoints" if recovered else "fold_results",
        "recovered_from_checkpoints": recovered,
        "n_checkpoint_files": int(len(checkpoint_paths)),
        "n_fold_rows": int(len(results)),
        "n_subjects": int(subject["subject"].nunique()),
        "n_subject_condition_rows": int(len(subject)),
        "subject_summary": str(subject_path),
        "population_summary": str(population_path),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results-dir", type=Path, default=Path("results"))
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--random-seed", type=int, default=42)
    ap.add_argument("--recover-from-checkpoints", action="store_true")
    ap.add_argument("--checkpoint-dataset")
    ap.add_argument("--pipeline", choices=["riemann_lr", "csp_lda", "tangent_space_lr"])
    ap.add_argument("--expected-subjects", type=int)
    ap.add_argument("--allow-existing-subject-summary", action="store_true")
    ap.add_argument("--probe", action="store_true", help="Locate an available source without generating reports")
    args = ap.parse_args()
    if args.probe:
        result = probe_source(args.results_dir, args.prefix, args.checkpoint_dataset, args.pipeline)
        print(json.dumps(result, indent=2))
        if not result["available"]:
            raise SystemExit(2)
        return
    print(json.dumps(refresh_summaries(
        args.results_dir,
        args.prefix,
        args.random_seed,
        recover_from_checkpoints=args.recover_from_checkpoints,
        checkpoint_dataset=args.checkpoint_dataset,
        pipeline=args.pipeline,
        expected_subjects=args.expected_subjects,
        allow_existing_subject_summary=args.allow_existing_subject_summary,
    ), indent=2))


if __name__ == "__main__":
    main()
