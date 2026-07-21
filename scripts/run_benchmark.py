#!/usr/bin/env python3
"""Run BCI robustness benchmarks on open MOABB datasets.

This version is resumable at the subject level and supports two stressors:
1. test-time random channel dropout;
2. reduced electrode montages trained/tested on smaller channel sets.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

import pandas as pd
import yaml

try:
    from moabb.datasets import BNCI2014_001, PhysionetMI
    from moabb.paradigms import LeftRightImagery
except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional runtime package
    BNCI2014_001 = None
    PhysionetMI = None
    LeftRightImagery = None
    _MOABB_IMPORT_ERROR = exc
else:
    _MOABB_IMPORT_ERROR = None

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bci_robustness.core import (
    evaluate_subject_cross_session,
    evaluate_subject_reduced_montages,
    evaluate_subject_region_dropout,
    evaluate_subject_with_dropout,
    population_summary,
    subject_level_summary,
    BENCHMARK_PROTOCOL_VERSION,
)

DATASET_REGISTRY = {
    "PhysionetMI": PhysionetMI,
    "PhysionetMotorImagery": PhysionetMI,
    "BNCI2014_001": BNCI2014_001,
    "BNCI2014-001": BNCI2014_001,
}


def require_moabb() -> None:
    """Raise a clear error if MOABB is unavailable for data-loading commands."""
    if _MOABB_IMPORT_ERROR is not None:
        raise RuntimeError(
            "MOABB is required for dataset listing and benchmark execution. "
            "Install them with `make install-eeg` or `python -m pip install -e '.[eeg]'` using the same Python interpreter that runs this script."
        ) from _MOABB_IMPORT_ERROR


def set_download_dir(path: str | Path) -> None:
    """Configure the MNE/MOABB data directory without relying on MOABB internals."""
    require_moabb()
    from mne import set_config

    download_dir = Path(path).expanduser().resolve()
    download_dir.mkdir(parents=True, exist_ok=True)
    set_config("MNE_DATA", str(download_dir), set_env=False)


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_config_paths(config: dict) -> dict:
    """Resolve repository-relative paths so scripts can be run from any cwd."""
    config = dict(config)
    for key in ["moabb_data_dir", "results_dir"]:
        if key in config:
            value = Path(config[key])
            if not value.is_absolute():
                config[key] = str((ROOT / value).resolve())
    return config


def instantiate_dataset(name: str, subjects: list[int] | None = None):
    require_moabb()
    if name not in DATASET_REGISTRY:
        raise ValueError(f"Unknown dataset {name!r}. Known: {sorted(DATASET_REGISTRY)}")
    cls = DATASET_REGISTRY[name]
    if cls is PhysionetMI:
        return cls(imagined=True, executed=False, subjects=subjects)
    return cls()


def config_montages(config: dict) -> dict[str, list[str]]:
    reduced_cfg = config.get("stressors", {}).get("reduced_montage", {})
    montages = {}
    for item in reduced_cfg.get("montages", []):
        montages[item["name"]] = list(item["channels"])
    return montages


def pipeline_config(config: dict, pipeline_name: str) -> dict:
    """Return the pipeline configuration by name, or an empty dict if absent."""
    for item in config.get("pipelines", []):
        if item.get("name") == pipeline_name:
            return item
    return {}


def requested_stressors(include_reduced_montage: bool, include_region_dropout: bool, include_cross_session: bool) -> set[str]:
    """Return stressors expected in a checkpoint for the requested run options."""
    needed = {"clean", "channel_dropout"}
    if include_reduced_montage:
        needed.add("reduced_montage")
    if include_region_dropout:
        needed.add("region_dropout")
    # Cross-session may be absent for datasets without usable session metadata, so it is not mandatory.
    return needed


def checkpoint_is_compatible(
    df: pd.DataFrame,
    include_reduced_montage: bool,
    include_region_dropout: bool,
    include_cross_session: bool,
) -> tuple[bool, str]:
    """Check whether an existing checkpoint contains all mandatory requested stressors.

    Older checkpoints may lack optional stressors, for example region dropout. Reusing
    them would silently omit requested outputs. Cross-session is not mandatory because
    some datasets/subjects do not expose usable session metadata.
    """
    if "stressor" not in df.columns:
        return False, "missing stressor column"
    if "protocol_version" not in df.columns:
        return False, "missing protocol_version column"
    versions = set(df["protocol_version"].dropna().astype(str))
    if versions != {BENCHMARK_PROTOCOL_VERSION}:
        return False, f"protocol version mismatch: found {sorted(versions)}, expected {BENCHMARK_PROTOCOL_VERSION}"
    present = set(df["stressor"].dropna().astype(str))
    needed = requested_stressors(include_reduced_montage, include_region_dropout, include_cross_session)
    missing = sorted(needed - present)
    if missing:
        return False, f"missing requested stressors: {missing}"
    return True, "ok"


def atomic_write_csv(frame: pd.DataFrame, path: Path) -> None:
    """Write a CSV atomically so interrupted long runs do not leave truncated files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False)
    temporary.replace(path)


def write_failure_log(results_dir: Path, dataset_name: str, suffix: str, failures: list[dict]) -> Path | None:
    """Write skipped subject failures to CSV and JSON for resuming/debugging."""
    if not failures:
        return None
    results_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{dataset_name}_{suffix}_failed_subjects"
    csv_path = results_dir / f"{stem}.csv"
    json_path = results_dir / f"{stem}.json"
    atomic_write_csv(pd.DataFrame(failures), csv_path)
    json_path.write_text(json.dumps(failures, indent=2), encoding="utf-8")
    return csv_path


def available_subjects(dataset_name: str, config: dict) -> list[int]:
    """List subjects available through the MOABB dataset wrapper without loading EEG arrays."""
    require_moabb()
    set_download_dir(config["moabb_data_dir"])
    ds = instantiate_dataset(dataset_name, subjects=None)
    return list(ds.subject_list)


def dry_run(config: dict) -> None:
    print("Dry run only: no EEG data will be downloaded.")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print("\nConfigured dataset aliases:")
    for key in DATASET_REGISTRY:
        print(f"- {key}")
    if _MOABB_IMPORT_ERROR is not None:
        print("\nMOABB is not installed in this environment; dataset metadata checks are skipped.")
        return
    print("\nAvailable starter datasets:")
    for key, cls in DATASET_REGISTRY.items():
        try:
            ds = cls(imagined=True, executed=False, subjects=[1]) if cls is PhysionetMI else cls()
            print(f"- {key}: code={ds.code}, subjects={len(ds.subject_list)}")
        except Exception as exc:
            print(f"- {key}: metadata unavailable ({exc})")

def run_one_subject(
    dataset,
    paradigm,
    subject: int,
    config: dict,
    include_reduced_montage: bool,
    include_region_dropout: bool = False,
    include_cross_session: bool = False,
    pipeline_name: str = "csp_lda",
) -> pd.DataFrame:
    seed = int(config["random_seed"])
    dropout_cfg = config["stressors"]["channel_dropout"]
    fractions = [0.0] + [float(x) for x in dropout_cfg["dropout_fractions"]]
    repeats = int(dropout_cfg["repeats_per_fraction"])
    mask_seed_scope = str(dropout_cfg.get("mask_seed_scope", "participant"))
    csp_components = int(pipeline_config(config, pipeline_name).get("csp_components", 6))

    epochs, y, metadata = paradigm.get_data(dataset=dataset, subjects=[subject], return_epochs=True)
    X = epochs.get_data(copy=True)
    channel_names = list(epochs.ch_names)
    print(f"  X={X.shape}, classes={sorted(set(y))}, channels={len(channel_names)}")

    frames = []
    dropout = evaluate_subject_with_dropout(
        X=X,
        y=y,
        subject_id=subject,
        dropout_fractions=fractions,
        repeats_per_fraction=repeats,
        random_seed=seed,
        csp_components=csp_components,
        pipeline_name=pipeline_name,
        montage_name="all_channels",
        n_channels=X.shape[1],
        mask_seed_scope=mask_seed_scope,
    )
    frames.append(dropout)

    if include_reduced_montage and config.get("stressors", {}).get("reduced_montage", {}).get("enabled", False):
        montages = config_montages(config)
        reduced = evaluate_subject_reduced_montages(
            X=X,
            y=y,
            channel_names=channel_names,
            subject_id=subject,
            montages=montages,
            random_seed=seed,
            csp_components=csp_components,
            pipeline_name=pipeline_name,
        )
        frames.append(reduced)

    if include_region_dropout:
        region_cfg = config.get("stressors", {}).get("region_dropout", {})
        region_names = region_cfg.get("regions", ["left_motor_strip", "midline_motor_strip", "right_motor_strip"])
        region = evaluate_subject_region_dropout(
            X=X,
            y=y,
            channel_names=channel_names,
            subject_id=subject,
            region_names=region_names,
            random_seed=seed,
            csp_components=csp_components,
            pipeline_name=pipeline_name,
        )
        frames.append(region)

    if include_cross_session and config.get("stressors", {}).get("cross_session", {}).get("enabled", False):
        cross = evaluate_subject_cross_session(
            X=X,
            y=y,
            metadata=metadata,
            subject_id=subject,
            random_seed=seed,
            csp_components=csp_components,
            pipeline_name=pipeline_name,
        )
        if not cross.empty:
            frames.append(cross)

    out = pd.concat(frames, ignore_index=True)
    out["protocol_version"] = BENCHMARK_PROTOCOL_VERSION
    out["mask_seed_scope"] = mask_seed_scope
    out.insert(0, "dataset", dataset.code)
    return out


def run_real_data(
    config: dict,
    dataset_name: str,
    subjects: list[int] | None,
    max_subjects: int | None,
    include_reduced_montage: bool,
    include_region_dropout: bool,
    include_cross_session: bool,
    pipeline_name: str,
    overwrite: bool,
    max_retries: int = 2,
    retry_wait_seconds: float = 15.0,
    skip_failed: bool = False,
    max_consecutive_failures: int = 5,
    suffix: str = "robustness",
) -> pd.DataFrame:
    set_download_dir(config["moabb_data_dir"])
    dataset = instantiate_dataset(dataset_name, subjects=subjects if subjects else None)
    subject_list = subjects if subjects else list(dataset.subject_list)
    if max_subjects is not None:
        subject_list = subject_list[:max_subjects]

    paradigm = LeftRightImagery(fmin=8, fmax=32, resample=128)
    results_dir = Path(config["results_dir"])
    checkpoint_dir = results_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    all_rows = []
    failures: list[dict] = []
    max_retries = max(0, int(max_retries))
    attempts_total = max_retries + 1
    max_consecutive_failures = max(0, int(max_consecutive_failures))
    consecutive_failures = 0

    for subject in subject_list:
        ckpt = checkpoint_dir / f"{dataset_name}_{pipeline_name}_{suffix}_subject-{subject:03d}.csv"
        df = None
        if ckpt.exists() and not overwrite:
            candidate = pd.read_csv(ckpt)
            ok, reason = checkpoint_is_compatible(candidate, include_reduced_montage, include_region_dropout, include_cross_session)
            if ok:
                print(f"Reusing checkpoint: {ckpt}")
                df = candidate
                consecutive_failures = 0
            else:
                print(f"Checkpoint {ckpt} is incompatible with requested run ({reason}); recomputing subject {subject}.")

        if df is None:
            last_exc: Exception | None = None
            for attempt in range(1, attempts_total + 1):
                try:
                    print(f"Loading subject {subject} from {dataset.code} (attempt {attempt}/{attempts_total})...")
                    df = run_one_subject(dataset, paradigm, subject, config, include_reduced_montage, include_region_dropout, include_cross_session, pipeline_name)
                    atomic_write_csv(df, ckpt)
                    print(f"  wrote checkpoint {ckpt}")
                    consecutive_failures = 0
                    break
                except Exception as exc:
                    last_exc = exc
                    print(f"  subject {subject} failed on attempt {attempt}/{attempts_total}: {type(exc).__name__}: {exc}")
                    if attempt < attempts_total:
                        print(f"  waiting {retry_wait_seconds:g}s before retry...")
                        time.sleep(float(retry_wait_seconds))
            if df is None:
                failure = {
                    "dataset": dataset_name,
                    "pipeline": pipeline_name,
                    "subject": int(subject),
                    "error_type": type(last_exc).__name__ if last_exc else "UnknownError",
                    "error_message": str(last_exc) if last_exc else "unknown failure",
                    "traceback_tail": "".join(traceback.format_exception(type(last_exc), last_exc, last_exc.__traceback__))[-4000:] if last_exc else "",
                }
                failures.append(failure)
                if skip_failed:
                    consecutive_failures += 1
                    print(f"  skipping failed subject {subject}; see failed-subject log after run.")
                    if max_consecutive_failures and consecutive_failures >= max_consecutive_failures:
                        write_failure_log(results_dir, dataset_name, suffix, failures)
                        raise RuntimeError(
                            f"Stopped after {consecutive_failures} consecutive failed subject(s). "
                            "This usually indicates that the data host or network is unavailable, not that all subjects are invalid. "
                            "Rerun later to resume from completed checkpoints, or increase --max-consecutive-failures to keep skipping."
                        ) from last_exc
                    continue
                write_failure_log(results_dir, dataset_name, suffix, failures)
                raise RuntimeError(
                    f"Subject {subject} failed after {attempts_total} attempt(s). "
                    f"Completed checkpoints remain reusable; rerun the command to resume, or add --skip-failed to continue past this subject."
                ) from last_exc
        all_rows.append(df)

    failure_path = write_failure_log(results_dir, dataset_name, suffix, failures)
    if failure_path is not None:
        print(f"Wrote failed-subject log: {failure_path}")
    if not all_rows:
        raise RuntimeError("No subject results were produced. Check failed-subject logs and input subject list.")
    return pd.concat(all_rows, ignore_index=True)


def write_outputs(results: pd.DataFrame, config: dict, dataset_name: str, suffix: str) -> tuple[Path, Path, Path]:
    results_dir = Path(config["results_dir"])
    results_dir.mkdir(parents=True, exist_ok=True)
    raw_path = results_dir / f"{dataset_name}_{suffix}_results.csv"
    subject_path = results_dir / f"{dataset_name}_{suffix}_subject_summary.csv"
    summary_path = results_dir / f"{dataset_name}_{suffix}_population_summary.csv"
    atomic_write_csv(results, raw_path)
    subj = subject_level_summary(results)
    atomic_write_csv(subj, subject_path)
    summary = population_summary(results, random_seed=int(config["random_seed"]))
    atomic_write_csv(summary, summary_path)
    return raw_path, subject_path, summary_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "benchmark.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Inspect plan without downloading data.")
    parser.add_argument("--download-and-run", action="store_true", help="Download public EEG data and run benchmark.")
    parser.add_argument("--dataset", default="PhysionetMI")
    parser.add_argument("--subjects", type=int, nargs="*", default=None, help="Subject IDs to run. If omitted, run all subjects exposed by MOABB for the dataset.")
    parser.add_argument("--max-subjects", type=int, default=None)
    parser.add_argument("--include-reduced-montage", action="store_true", help="Run reduced montage stressors from config.")
    parser.add_argument("--include-region-dropout", action="store_true", help="Run named region dropout stressors from config/core defaults.")
    parser.add_argument("--include-cross-session", action="store_true", help="Run train-first-session/test-later-session evaluation when MOABB metadata contain sessions.")
    parser.add_argument("--list-subjects", action="store_true", help="Print available MOABB subject IDs for the dataset and exit.")
    parser.add_argument("--pipeline", default="csp_lda", choices=["csp_lda", "riemann_lr", "tangent_space_lr"], help="Decoder pipeline to benchmark.")
    parser.add_argument("--overwrite", action="store_true", help="Recompute existing subject checkpoints.")
    parser.add_argument("--max-retries", type=int, default=2, help="Per-subject retry count after the first failed attempt, useful for transient MOABB/PhysioNet download errors.")
    parser.add_argument("--retry-wait-seconds", type=float, default=15.0, help="Seconds to wait between per-subject retry attempts.")
    parser.add_argument("--skip-failed", action="store_true", help="Continue after subjects that fail after all retry attempts and write a failed-subjects log.")
    parser.add_argument("--max-consecutive-failures", type=int, default=5, help="Stop after this many skipped subjects in a row. Set 0 to keep skipping indefinitely.")
    parser.add_argument("--suffix", default="robustness", help="Output filename suffix.")
    args = parser.parse_args()

    config = normalize_config_paths(load_config(args.config))
    if args.list_subjects:
        print(json.dumps({"dataset": args.dataset, "subjects": available_subjects(args.dataset, config)}, indent=2))
        return
    if args.dry_run or not args.download_and_run:
        dry_run(config)
        return

    results = run_real_data(
        config=config,
        dataset_name=args.dataset,
        subjects=args.subjects,
        max_subjects=args.max_subjects,
        include_reduced_montage=args.include_reduced_montage,
        include_region_dropout=args.include_region_dropout,
        include_cross_session=args.include_cross_session,
        pipeline_name=args.pipeline,
        overwrite=args.overwrite,
        max_retries=args.max_retries,
        retry_wait_seconds=args.retry_wait_seconds,
        skip_failed=args.skip_failed,
        max_consecutive_failures=args.max_consecutive_failures,
        suffix=args.suffix,
    )
    raw_path, subject_path, summary_path = write_outputs(results, config, args.dataset, args.suffix)
    print("\nPopulation summary:")
    print(pd.read_csv(summary_path).to_string(index=False))
    print(f"\nWrote {raw_path}")
    print(f"Wrote {subject_path}")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
