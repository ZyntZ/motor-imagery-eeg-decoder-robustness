import numpy as np
import pandas as pd
import pytest

from bci_robustness.core import (
    apply_channel_dropout,
    apply_named_region_dropout,
    channel_indices,
    expected_calibration_error,
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
