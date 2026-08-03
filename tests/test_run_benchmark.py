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
            "protocol_version": "0.3.2",
        }])
        frame.to_csv(checkpoint_dir / f"PhysionetMI_riemann_lr_PhysionetMI_all_riemann_lr_subject-{subject:03d}.csv", index=False)

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
        "n_channels": 64, "n_dropped_channels": 0, "protocol_version": "0.3.2",
    }]).to_csv(checkpoint_dir / "PhysionetMI_riemann_lr_PhysionetMI_all_riemann_lr_subject-001.csv", index=False)
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


def test_probe_source_finds_summary_using_shared_discovery(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "refresh_probe_summary_test", ROOT / "scripts" / "refresh_benchmark_summaries.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    prefix = "PhysionetMI_PhysionetMI_all_riemann_lr"
    fake_root = tmp_path / "current"
    monkeypatch.setattr(module, "ROOT", fake_root)
    summary = tmp_path / "backup" / "results" / f"{prefix}_subject_summary.csv"
    summary.parent.mkdir(parents=True)
    summary.write_text("subject\n1\n", encoding="utf-8")
    result = module.probe_source(fake_root / "results", prefix)
    assert result["available"] is True
    assert result["mode"] == "subject_summary"
    assert Path(result["source"]) == summary


def test_probe_source_returns_not_found_without_raising(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "refresh_probe_absent_test", ROOT / "scripts" / "refresh_benchmark_summaries.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    fake_root = tmp_path / "current"
    fake_root.mkdir()
    monkeypatch.setattr(module, "ROOT", fake_root)
    result = module.probe_source(fake_root / "results", "PhysionetMI_PhysionetMI_all_csp_lda")
    assert result["available"] is False
    assert result["mode"] == "not_found"



def test_atomic_write_csv_replaces_file_without_leaving_temporary(tmp_path):
    module = load_run_benchmark_module()
    import pandas as pd
    target = tmp_path / "checkpoint.csv"
    module.atomic_write_csv(pd.DataFrame({"value": [1, 2]}), target)
    module.atomic_write_csv(pd.DataFrame({"value": [3]}), target)
    assert pd.read_csv(target)["value"].tolist() == [3]
    assert not target.with_suffix(".csv.tmp").exists()


def test_checkpoint_compatibility_rejects_unversioned_rows():
    module = load_run_benchmark_module()
    import pandas as pd
    frame = pd.DataFrame({"stressor": ["clean", "channel_dropout"]})
    ok, reason = module.checkpoint_is_compatible(frame, False, False, False)
    assert not ok
    assert "protocol_version" in reason


def test_checkpoint_compatibility_accepts_current_protocol():
    module = load_run_benchmark_module()
    import pandas as pd
    frame = pd.DataFrame({
        "stressor": ["clean", "channel_dropout"],
        "protocol_version": [module.BENCHMARK_PROTOCOL_VERSION] * 2,
    })
    ok, reason = module.checkpoint_is_compatible(frame, False, False, False)
    assert ok
    assert reason == "ok"


def test_checkpoint_compatibility_rejects_different_mask_scope():
    module = load_run_benchmark_module()
    import pandas as pd
    frame = pd.DataFrame({
        "stressor": ["clean", "channel_dropout"],
        "protocol_version": [module.BENCHMARK_PROTOCOL_VERSION] * 2,
        "mask_seed_scope": ["shared"] * 2,
    })
    ok, reason = module.checkpoint_is_compatible(
        frame, False, False, False, expected_mask_seed_scope="participant"
    )
    assert not ok
    assert "mask seed scope mismatch" in reason


def test_checkpoint_compatibility_ignores_not_applicable_mask_scope():
    module = load_run_benchmark_module()
    import pandas as pd
    frame = pd.DataFrame({
        "stressor": ["clean", "channel_dropout", "region_dropout", "cross_session"],
        "protocol_version": [module.BENCHMARK_PROTOCOL_VERSION] * 4,
        "mask_seed_scope": ["participant", "participant", "not_applicable", "not_applicable"],
    })
    ok, reason = module.checkpoint_is_compatible(
        frame, False, True, True, expected_mask_seed_scope="participant"
    )
    assert ok
    assert reason == "ok"


def test_checkpoint_compatibility_rejects_mask_scope_on_nonrandom_stressors():
    module = load_run_benchmark_module()
    import pandas as pd
    frame = pd.DataFrame({
        "stressor": ["clean", "channel_dropout", "region_dropout"],
        "protocol_version": [module.BENCHMARK_PROTOCOL_VERSION] * 3,
        "mask_seed_scope": ["participant", "participant", "participant"],
    })
    ok, reason = module.checkpoint_is_compatible(
        frame, False, True, False, expected_mask_seed_scope="participant"
    )
    assert not ok
    assert "not_applicable" in reason


def test_run_one_subject_preserves_stressor_specific_mask_scope(monkeypatch):
    module = load_run_benchmark_module()
    import numpy as np
    import pandas as pd

    class Epochs:
        ch_names = ["C3", "Cz", "C4"]
        def get_data(self, copy=True):
            return np.ones((4, 3, 8))

    class Paradigm:
        def get_data(self, dataset, subjects, return_epochs):
            return Epochs(), np.array([0, 1, 0, 1]), pd.DataFrame({"session": ["1", "1", "2", "2"]})

    class Dataset:
        code = "demo"

    def frame(stressor, scope):
        return pd.DataFrame({
            "subject": [1], "pipeline": ["csp_lda"], "stressor": [stressor],
            "montage": ["all_channels"], "fold": [1], "dropout_fraction": [0.0],
            "repeat": [0], "n_channels": [3], "n_dropped_channels": [0],
            "balanced_accuracy": [0.5], "roc_auc": [0.5], "brier_score": [0.25],
            "ece": [0.0], "protocol_version": [module.BENCHMARK_PROTOCOL_VERSION],
            "mask_seed_scope": [scope],
        })

    monkeypatch.setattr(module, "evaluate_subject_with_dropout", lambda **kwargs: frame("clean", "participant"))
    monkeypatch.setattr(module, "evaluate_subject_region_dropout", lambda **kwargs: frame("region_dropout", "not_applicable"))
    monkeypatch.setattr(module, "evaluate_subject_cross_session", lambda **kwargs: frame("cross_session", "not_applicable"))
    config = {
        "random_seed": 42,
        "pipelines": [{"name": "csp_lda", "csp_components": 3}],
        "stressors": {
            "channel_dropout": {"dropout_fractions": [0.5], "repeats_per_fraction": 1, "mask_seed_scope": "participant"},
            "cross_session": {"enabled": True},
        },
    }
    out = module.run_one_subject(
        Dataset(), Paradigm(), 1, config, include_reduced_montage=False,
        include_region_dropout=True, include_cross_session=True,
    )
    scopes = out.groupby("stressor")["mask_seed_scope"].first().to_dict()
    assert scopes == {
        "clean": "participant",
        "cross_session": "not_applicable",
        "region_dropout": "not_applicable",
    }


def test_checkpoint_compatibility_accepts_matching_mask_scope():
    module = load_run_benchmark_module()
    import pandas as pd
    frame = pd.DataFrame({
        "stressor": ["clean", "channel_dropout"],
        "protocol_version": [module.BENCHMARK_PROTOCOL_VERSION] * 2,
        "mask_seed_scope": ["participant"] * 2,
    })
    ok, reason = module.checkpoint_is_compatible(
        frame, False, False, False, expected_mask_seed_scope="participant"
    )
    assert ok
    assert reason == "ok"


def test_run_signature_is_stable_and_changes_with_observation_settings():
    module = load_run_benchmark_module()
    config = {
        "random_seed": 42,
        "preprocessing": {"fmin_hz": 8, "fmax_hz": 32, "resample_hz": 128},
        "pipelines": [{"name": "csp_lda", "csp_components": 6}],
        "stressors": {
            "channel_dropout": {
                "dropout_fractions": [0.1, 0.2],
                "repeats_per_fraction": 10,
                "mask_seed_scope": "participant",
            }
        },
    }
    first = module.benchmark_run_signature(config, "PhysionetMI", "csp_lda", True, True, True)
    repeated = module.benchmark_run_signature(config, "PhysionetMI", "csp_lda", True, True, True)
    changed = {**config, "random_seed": 43}
    different = module.benchmark_run_signature(changed, "PhysionetMI", "csp_lda", True, True, True)
    assert first == repeated
    assert len(first) == 64
    assert first != different


def test_checkpoint_compatibility_requires_matching_run_signature():
    module = load_run_benchmark_module()
    import pandas as pd
    frame = pd.DataFrame({
        "stressor": ["clean", "channel_dropout"],
        "protocol_version": [module.BENCHMARK_PROTOCOL_VERSION] * 2,
        "mask_seed_scope": ["participant"] * 2,
        "run_signature": ["abc"] * 2,
    })
    ok, reason = module.checkpoint_is_compatible(
        frame, False, False, False,
        expected_mask_seed_scope="participant",
        expected_run_signature="def",
    )
    assert not ok
    assert "run signature mismatch" in reason


def test_checkpoint_compatibility_rejects_unsigned_checkpoint_when_signature_expected():
    module = load_run_benchmark_module()
    import pandas as pd
    frame = pd.DataFrame({
        "stressor": ["clean", "channel_dropout"],
        "protocol_version": [module.BENCHMARK_PROTOCOL_VERSION] * 2,
        "mask_seed_scope": ["participant"] * 2,
    })
    ok, reason = module.checkpoint_is_compatible(
        frame, False, False, False,
        expected_mask_seed_scope="participant",
        expected_run_signature="abc",
    )
    assert not ok
    assert "run_signature" in reason
