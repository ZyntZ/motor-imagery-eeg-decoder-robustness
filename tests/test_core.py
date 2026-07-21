import numpy as np
import pandas as pd
import pytest

from bci_robustness.core import (
    apply_channel_dropout,
    apply_named_region_dropout,
    channel_indices,
    expected_calibration_error,
    evaluate_subject_cross_session,
    evaluate_subject_reduced_montages,
    evaluate_subject_with_dropout,
    _dropout_rng,
    select_channels,
    subject_level_summary,
)


def test_apply_channel_dropout_is_deterministic_and_does_not_mutate_input():
    x = np.arange(2 * 5 * 3, dtype=float).reshape(2, 5, 3)
    original = x.copy()
    rng1 = np.random.default_rng(123)
    rng2 = np.random.default_rng(123)

    x_drop1, dropped1 = apply_channel_dropout(x, 0.4, rng1)
    x_drop2, dropped2 = apply_channel_dropout(x, 0.4, rng2)

    assert np.array_equal(x, original)
    assert np.array_equal(dropped1, dropped2)
    assert len(dropped1) == 2
    assert np.all(x_drop1[:, dropped1, :] == 0.0)
    keep = [i for i in range(x.shape[1]) if i not in set(dropped1)]
    assert np.array_equal(x_drop1[:, keep, :], original[:, keep, :])
    assert np.array_equal(x_drop1, x_drop2)


def test_apply_channel_dropout_validates_shape_and_fraction():
    with pytest.raises(ValueError, match="3 dimensions"):
        apply_channel_dropout(np.zeros((3, 4)), 0.2, np.random.default_rng(1))
    with pytest.raises(ValueError, match="fraction"):
        apply_channel_dropout(np.zeros((3, 4, 5)), 1.0, np.random.default_rng(1))


def test_channel_selection_and_named_region_dropout():
    x = np.ones((2, 4, 3))
    names = ["C3", "Cz", "C4", "Pz"]
    assert channel_indices(names, ["C4", "C3"]) == [2, 0]

    x_sel, selected, idx = select_channels(x, names, ["C3", "C4"])
    assert selected == ["C3", "C4"]
    assert idx == [0, 2]
    assert x_sel.shape == (2, 2, 3)

    x_region, dropped_names, dropped_idx = apply_named_region_dropout(
        x, names, "custom", {"custom": ["C3", "C4", "Missing"]}
    )
    assert dropped_names == ["C3", "C4"]
    assert dropped_idx == [0, 2]
    assert np.all(x_region[:, dropped_idx, :] == 0.0)
    assert np.all(x_region[:, [1, 3], :] == 1.0)


def test_expected_calibration_error_equal_width_bins():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.1, 0.2, 0.8, 0.9])
    assert expected_calibration_error(y, p, n_bins=2) == pytest.approx(0.15)


def test_subject_level_summary_adds_missing_optional_metrics_as_nan():
    df = pd.DataFrame(
        {
            "dataset": ["D", "D"],
            "subject": [1, 1],
            "pipeline": ["p", "p"],
            "stressor": ["clean", "clean"],
            "montage": ["all_channels", "all_channels"],
            "dropout_fraction": [0.0, 0.0],
            "roc_auc": [0.6, 0.8],
            "balanced_accuracy": [0.55, 0.65],
            "n_channels": [8, 8],
        }
    )
    out = subject_level_summary(df)
    assert out.shape[0] == 1
    assert out.loc[0, "roc_auc"] == pytest.approx(0.7)
    assert "brier_score" in out.columns and np.isnan(out.loc[0, "brier_score"])
    assert "ece" in out.columns and np.isnan(out.loc[0, "ece"])


def test_subject_summary_preserves_named_region_conditions():
    rows = []
    for region, auc in [("left_motor_strip", 0.6), ("right_motor_strip", 0.8)]:
        for fold in [1, 2]:
            rows.append({
                "dataset": "demo", "subject": 1, "pipeline": "riemann_lr",
                "stressor": "region_dropout", "montage": "all_channels",
                "dropout_fraction": 0.1, "region": region, "fold": fold, "repeat": 0,
                "roc_auc": auc, "balanced_accuracy": auc, "brier_score": 0.2,
                "ece": 0.1, "n_channels": 64, "n_dropped_channels": 6,
            })
    summary = subject_level_summary(pd.DataFrame(rows))
    assert len(summary) == 2
    assert set(summary["region"]) == {"left_motor_strip", "right_motor_strip"}


@pytest.mark.filterwarnings("ignore:.*not fully.*:RuntimeWarning")
def test_csp_lda_handles_three_channel_montage_and_high_dropout():
    pytest.importorskip("mne", reason="MNE is required for CSP integration tests")
    rng = np.random.default_rng(7)
    X = rng.normal(size=(40, 3, 96))
    y = np.array([0] * 20 + [1] * 20)
    out = evaluate_subject_with_dropout(
        X, y, subject_id=1, dropout_fractions=(0.0, 0.5),
        repeats_per_fraction=2, n_splits=4, csp_components=6,
        pipeline_name="csp_lda", montage_name="motor_core",
    )
    assert len(out) == 12
    assert np.isfinite(out["roc_auc"]).all()
    assert out["roc_auc"].between(0.0, 1.0).all()
    assert set(out["stressor"]) == {"clean", "channel_dropout"}


@pytest.mark.filterwarnings("ignore:.*not fully.*:RuntimeWarning")
def test_csp_reduced_montages_clamp_components_to_channel_count():
    pytest.importorskip("mne", reason="MNE is required for CSP integration tests")
    rng = np.random.default_rng(11)
    X = rng.normal(size=(40, 5, 96))
    y = np.array([0] * 20 + [1] * 20)
    names = ["C3", "Cz", "C4", "FC3", "FC4"]
    out = evaluate_subject_reduced_montages(
        X, y, names, subject_id=1,
        montages={"motor_core": ["C3", "Cz", "C4"]},
        n_splits=4, csp_components=6, pipeline_name="csp_lda",
    )
    assert len(out) == 4
    assert set(out["n_channels"]) == {3}
    assert np.isfinite(out["roc_auc"]).all()


def test_cross_session_uses_sorted_session_labels(monkeypatch):
    class DummyClassifier:
        def fit(self, X, y):
            return self

    monkeypatch.setattr("bci_robustness.core.make_pipeline_by_name", lambda *args, **kwargs: DummyClassifier())
    monkeypatch.setattr("bci_robustness.core._score_fold", lambda clf, X, y: (0.7, 0.6, 0.2, 0.1))
    X = np.zeros((8, 3, 12))
    y = np.array([0, 1, 0, 1, 0, 1, 0, 1])
    metadata = pd.DataFrame({"session": ["session_2"] * 4 + ["session_1"] * 4})
    out = evaluate_subject_cross_session(X, y, metadata, subject_id=1)
    assert set(out["session_train"]) == {"session_1"}
    assert set(out["session_test"]) == {"session_2"}


def test_participant_specific_dropout_masks_are_reproducible_and_distinct():
    first = _dropout_rng(42, 1, 1, 0, 0.3).choice(64, size=19, replace=False)
    repeated = _dropout_rng(42, 1, 1, 0, 0.3).choice(64, size=19, replace=False)
    other_subject = _dropout_rng(42, 2, 1, 0, 0.3).choice(64, size=19, replace=False)
    assert np.array_equal(first, repeated)
    assert not np.array_equal(np.sort(first), np.sort(other_subject))


def test_dropout_evaluator_records_protocol_and_mask_scope(monkeypatch):
    class DummyClassifier:
        def fit(self, X, y):
            return self

    monkeypatch.setattr("bci_robustness.core.make_pipeline_by_name", lambda *args, **kwargs: DummyClassifier())
    monkeypatch.setattr("bci_robustness.core._score_fold", lambda clf, X, y: (0.7, 0.6, 0.2, 0.1))
    X = np.ones((8, 6, 12))
    y = np.array([0, 1, 0, 1, 0, 1, 0, 1])
    out = evaluate_subject_with_dropout(
        X, y, subject_id=7, dropout_fractions=(0.0, 0.5),
        repeats_per_fraction=1, n_splits=2, mask_seed_scope="participant",
    )
    assert set(out["protocol_version"]) == {"0.3.1"}
    assert set(out["mask_seed_scope"]) == {"participant"}


def test_dropout_evaluator_rejects_unknown_mask_scope():
    X = np.ones((8, 3, 12))
    y = np.array([0, 1, 0, 1, 0, 1, 0, 1])
    with pytest.raises(ValueError, match="mask_seed_scope"):
        evaluate_subject_with_dropout(X, y, subject_id=1, n_splits=2, mask_seed_scope="global")
