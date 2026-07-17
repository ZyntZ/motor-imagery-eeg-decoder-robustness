from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_run_benchmark_module():
    spec = importlib.util.spec_from_file_location(
        "run_benchmark_for_test", ROOT / "scripts" / "run_benchmark.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_set_download_dir_creates_directory_and_sets_mne_config(tmp_path, monkeypatch):
    module = load_run_benchmark_module()
    target = tmp_path / "moabb data"
    calls = []

    module._MOABB_IMPORT_ERROR = None
    fake_mne = types.SimpleNamespace(
        set_config=lambda key, value, set_env: calls.append((key, value, set_env))
    )
    monkeypatch.setitem(sys.modules, "mne", fake_mne)
    module.set_download_dir(target)

    assert target.is_dir()
    assert calls == [("MNE_DATA", str(target.resolve()), False)]


def test_refresh_summaries_preserves_named_regions(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "refresh_benchmark_summaries_for_test", ROOT / "scripts" / "refresh_benchmark_summaries.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    import pandas as pd

    prefix = "demo"
    rows = []
    for region, auc in [("left_motor_strip", 0.6), ("right_motor_strip", 0.8)]:
        rows.append({
            "dataset": "D", "subject": 1, "pipeline": "p", "stressor": "region_dropout",
            "montage": "all_channels", "dropout_fraction": 0.1, "region": region,
            "fold": 1, "repeat": 0, "roc_auc": auc, "balanced_accuracy": auc,
            "brier_score": 0.2, "ece": 0.1, "n_channels": 64, "n_dropped_channels": 6,
        })
    pd.DataFrame(rows).to_csv(tmp_path / f"{prefix}_results.csv", index=False)
    result = module.refresh_summaries(tmp_path, prefix, random_seed=42)
    summary = pd.read_csv(tmp_path / f"{prefix}_subject_summary.csv")
    assert result["n_subject_condition_rows"] == 2
    assert set(summary["region"]) == {"left_motor_strip", "right_motor_strip"}


def test_refresh_summaries_recovers_missing_results_from_complete_checkpoints(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "refresh_benchmark_summaries_recovery_test", ROOT / "scripts" / "refresh_benchmark_summaries.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    import pandas as pd

    prefix = "PhysionetMI_PhysionetMI_all_riemann_lr"
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()
    for subject in [1, 2]:
        frame = pd.DataFrame([{
            "dataset": "PhysionetMotorImagery", "subject": subject, "pipeline": "riemann_lr",
            "stressor": "clean", "montage": "all_channels", "dropout_fraction": 0.0,
            "fold": 1, "repeat": 0, "roc_auc": 0.7, "balanced_accuracy": 0.6,
            "brier_score": 0.2, "ece": 0.1, "n_channels": 64, "n_dropped_channels": 0,
        }])
        frame.to_csv(checkpoint_dir / f"PhysionetMI_riemann_lr_subject-{subject:03d}_robustness.csv", index=False)

    result = module.refresh_summaries(
        tmp_path, prefix, recover_from_checkpoints=True, expected_subjects=2
    )
    assert result["recovered_from_checkpoints"] is True
    assert result["n_checkpoint_files"] == 2
    assert result["n_subjects"] == 2
    assert (tmp_path / f"{prefix}_results.csv").exists()


def test_checkpoint_recovery_refuses_incomplete_subject_set(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "refresh_benchmark_summaries_incomplete_test", ROOT / "scripts" / "refresh_benchmark_summaries.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    import pandas as pd
    import pytest

    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()
    pd.DataFrame([{
        "dataset": "PhysionetMotorImagery", "subject": 1, "pipeline": "riemann_lr",
        "stressor": "clean", "montage": "all_channels", "dropout_fraction": 0.0,
        "fold": 1, "repeat": 0, "roc_auc": 0.7, "balanced_accuracy": 0.6,
        "n_channels": 64, "n_dropped_channels": 0,
    }]).to_csv(checkpoint_dir / "PhysionetMI_riemann_lr_subject-001_robustness.csv", index=False)
    with pytest.raises(RuntimeError, match="Found 1 unique subject checkpoints, expected 2"):
        module.refresh_summaries(
            tmp_path,
            "PhysionetMI_PhysionetMI_all_riemann_lr",
            recover_from_checkpoints=True,
            expected_subjects=2,
        )


def test_refresh_uses_complete_existing_subject_summary_when_raw_and_checkpoints_absent(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "refresh_existing_summary_test", ROOT / "scripts" / "refresh_benchmark_summaries.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    import pandas as pd

    prefix = "PhysionetMI_PhysionetMI_all_riemann_lr"
    rows = []
    for subject in [1, 2]:
        rows.append({
            "dataset": "PhysionetMotorImagery", "subject": subject, "pipeline": "riemann_lr",
            "stressor": "clean", "montage": "all_channels", "dropout_fraction": 0.0,
            "roc_auc": 0.7, "balanced_accuracy": 0.6, "brier_score": 0.2,
            "ece": 0.1, "n_channels": 64, "n_dropped_channels": 0,
        })
    pd.DataFrame(rows).to_csv(tmp_path / f"{prefix}_subject_summary.csv", index=False)
    result = module.refresh_summaries(
        tmp_path, prefix, recover_from_checkpoints=True,
        allow_existing_subject_summary=True, expected_subjects=2,
    )
    assert result["mode"] == "existing_subject_summary"
    assert result["n_subjects"] == 2
    assert result["n_fold_rows"] is None
    assert (tmp_path / f"{prefix}_population_summary.csv").exists()


def test_existing_subject_summary_fallback_refuses_incomplete_cohort(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "refresh_existing_summary_incomplete_test", ROOT / "scripts" / "refresh_benchmark_summaries.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    import pandas as pd
    import pytest

    prefix = "PhysionetMI_PhysionetMI_all_riemann_lr"
    pd.DataFrame([{
        "dataset": "PhysionetMotorImagery", "subject": 1, "pipeline": "riemann_lr",
        "stressor": "clean", "montage": "all_channels", "dropout_fraction": 0.0,
        "roc_auc": 0.7, "balanced_accuracy": 0.6, "n_channels": 64,
        "n_dropped_channels": 0,
    }]).to_csv(tmp_path / f"{prefix}_subject_summary.csv", index=False)
    with pytest.raises(RuntimeError, match="contains 1 unique subjects, expected 2"):
        module.refresh_summaries(
            tmp_path, prefix, recover_from_checkpoints=True,
            allow_existing_subject_summary=True, expected_subjects=2,
        )


def test_find_subject_summary_in_sibling_project(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "refresh_summary_discovery_test", ROOT / "scripts" / "refresh_benchmark_summaries.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    prefix = "PhysionetMI_PhysionetMI_all_riemann_lr"
    current_project = tmp_path / "current"
    current_results = current_project / "results"
    sibling_results = tmp_path / "old-copy" / "results"
    sibling_results.mkdir(parents=True)
    monkeypatch.setattr(module, "ROOT", current_project)
    expected = sibling_results / f"{prefix}_subject_summary.csv"
    expected.write_text("subject\n1\n", encoding="utf-8")
    found, searched = module.find_subject_summary(current_results, prefix)
    assert found == expected
    assert searched


def test_extract_subject_summary_from_single_nearby_archive(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "refresh_summary_archive_test", ROOT / "scripts" / "refresh_benchmark_summaries.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    import zipfile
    prefix = "PhysionetMI_PhysionetMI_all_riemann_lr"
    fake_root = tmp_path / "project"
    fake_root.mkdir()
    monkeypatch.setattr(module, "ROOT", fake_root)
    archive = tmp_path / "backup.zip"
    member = f"backup/results/{prefix}_subject_summary.csv"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(member, "subject\n1\n")
    target, archives = module.extract_subject_summary_from_archives(fake_root / "results", prefix)
    assert target is not None and target.exists()
    assert target.read_text(encoding="utf-8") == "subject\n1\n"
    assert archive in archives
