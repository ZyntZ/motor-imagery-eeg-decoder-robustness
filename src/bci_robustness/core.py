"""Core utilities for the BCI robustness benchmark.

Functions operate on EEG arrays supplied by MOABB/MNE loaders or another
documented data source.
"""

from __future__ import annotations

from typing import Iterable, Sequence

import hashlib

import numpy as np
import pandas as pd
from scipy.stats import bootstrap
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline

try:
    from mne.decoding import CSP
except Exception as exc:  # pragma: no cover
    CSP = None
    _CSP_IMPORT_ERROR = exc



BENCHMARK_PROTOCOL_VERSION = "0.3.1"


def _stable_subject_seed(random_seed: int, subject_id: str | int) -> int:
    """Return a stable uint32 seed that includes participant identity.

    Python's built-in hash is intentionally avoided because it is randomized
    between interpreter processes. The same participant seed is shared between
    decoder families so participant-level comparisons remain paired.
    """
    payload = f"{int(random_seed)}|{subject_id}".encode("utf-8")
    return int.from_bytes(hashlib.blake2s(payload, digest_size=4).digest(), "little")


def _dropout_rng(
    random_seed: int, subject_id: str | int, fold: int, repeat: int, fraction: float
) -> np.random.Generator:
    """Create a deterministic participant-specific RNG for one channel mask."""
    fraction_code = int(round(float(fraction) * 1_000_000))
    seed = np.random.SeedSequence(
        [_stable_subject_seed(random_seed, subject_id), int(fold), int(repeat), fraction_code]
    )
    return np.random.default_rng(seed)


def make_csp_lda(n_components: int = 6, random_state: int = 42) -> Pipeline:
    """Create a classical motor-imagery BCI baseline: CSP + LDA."""
    if CSP is None:  # pragma: no cover
        raise ImportError(f"mne.decoding.CSP could not be imported: {_CSP_IMPORT_ERROR}")
    return Pipeline(
        steps=[
            ("csp", CSP(n_components=n_components, reg=None, log=True, norm_trace=False)),
            ("lda", LinearDiscriminantAnalysis()),
        ]
    )


def apply_channel_dropout(X: np.ndarray, fraction: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Zero a random subset of channels in all epochs.

    X must have shape (epochs, channels, samples). Training data should not be
    corrupted when this function is used to model deployment-time channel loss.
    """
    X = np.asarray(X)
    if X.ndim != 3:
        raise ValueError(f"Expected X with 3 dimensions; got shape {X.shape}")
    if not (0 <= fraction < 1):
        raise ValueError("fraction must be in [0, 1)")
    n_channels = X.shape[1]
    n_drop = int(round(fraction * n_channels))
    X2 = X.copy()
    if n_drop == 0:
        return X2, np.array([], dtype=int)
    dropped = np.sort(rng.choice(n_channels, size=n_drop, replace=False))
    X2[:, dropped, :] = 0.0
    return X2, dropped


def channel_indices(channel_names: Sequence[str], wanted: Sequence[str]) -> list[int]:
    """Return channel indices for a requested montage, preserving requested order."""
    name_to_idx = {name: idx for idx, name in enumerate(channel_names)}
    missing = [name for name in wanted if name not in name_to_idx]
    if missing:
        raise ValueError(f"Requested channels are absent from dataset: {missing}")
    return [name_to_idx[name] for name in wanted]


def select_channels(X: np.ndarray, channel_names: Sequence[str], wanted: Sequence[str]) -> tuple[np.ndarray, list[str], list[int]]:
    """Select a reduced montage from an EEG tensor."""
    idx = channel_indices(channel_names, wanted)
    return np.asarray(X)[:, idx, :], [channel_names[i] for i in idx], idx


def _binary_scores(estimator, X_test: np.ndarray) -> tuple[np.ndarray, bool]:
    """Return continuous positive-class scores and whether they are probabilities."""
    if hasattr(estimator, "predict_proba"):
        return estimator.predict_proba(X_test)[:, 1], True
    if hasattr(estimator, "decision_function"):
        return estimator.decision_function(X_test), False
    return estimator.predict(X_test), False


def _positive_class_binary(estimator, y_test: np.ndarray) -> np.ndarray:
    """Encode y_test as 0/1 using the estimator positive class when available."""
    classes = getattr(estimator, "classes_", None)
    if classes is None and hasattr(estimator, "steps"):
        classes = getattr(estimator.steps[-1][1], "classes_", None)
    if classes is None:
        classes = np.unique(y_test)
    if len(classes) != 2:
        raise ValueError("Expected exactly two estimator classes")
    return (np.asarray(y_test) == classes[1]).astype(int)


def expected_calibration_error(y_true_bin: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Expected calibration error for binary probabilities using equal-width bins."""
    y_true_bin = np.asarray(y_true_bin, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    ok = np.isfinite(y_true_bin) & np.isfinite(y_prob)
    y_true_bin = y_true_bin[ok]
    y_prob = y_prob[ok]
    if y_true_bin.size == 0:
        return np.nan
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        if i == n_bins - 1:
            mask = (y_prob >= edges[i]) & (y_prob <= edges[i + 1])
        else:
            mask = (y_prob >= edges[i]) & (y_prob < edges[i + 1])
        if np.any(mask):
            ece += mask.mean() * abs(y_true_bin[mask].mean() - y_prob[mask].mean())
    return float(ece)


def _score_fold(estimator, X_test: np.ndarray, y_test: np.ndarray) -> tuple[float, float, float, float]:
    y_pred = estimator.predict(X_test)
    y_score, is_probability = _binary_scores(estimator, X_test)
    y_true_bin = _positive_class_binary(estimator, y_test)
    try:
        auc = roc_auc_score(y_test, y_score)
    except ValueError:
        auc = np.nan
    if is_probability:
        brier = brier_score_loss(y_true_bin, y_score)
        ece = expected_calibration_error(y_true_bin, y_score)
    else:
        brier = np.nan
        ece = np.nan
    return float(auc), float(balanced_accuracy_score(y_test, y_pred)), float(brier), float(ece)


def evaluate_subject_with_dropout(
    X: np.ndarray,
    y: np.ndarray,
    subject_id: str | int,
    dropout_fractions: Iterable[float] = (0.0, 0.1, 0.2, 0.3, 0.5),
    repeats_per_fraction: int = 20,
    n_splits: int = 5,
    random_seed: int = 42,
    csp_components: int = 6,
    pipeline_name: str = "csp_lda",
    montage_name: str = "all_channels",
    n_channels: int | None = None,
    mask_seed_scope: str = "participant",
) -> pd.DataFrame:
    """Evaluate clean and test-time channel-dropout performance for one subject.

    Folds/repeats are technical resampling units. For inference, collapse these
    rows to subject-level summaries before computing confidence intervals or p-values.
    """
    X = np.asarray(X)
    y = np.asarray(y)
    if len(np.unique(y)) != 2:
        raise ValueError("This evaluator expects exactly two classes")
    if X.shape[0] != y.shape[0]:
        raise ValueError("X and y have inconsistent numbers of epochs")
    if n_channels is None:
        n_channels = X.shape[1]

    _, counts = np.unique(y, return_counts=True)
    n_splits_eff = min(int(n_splits), int(counts.min()))
    if n_splits_eff < 2:
        raise ValueError("Need at least two samples per class for cross-validation")

    if mask_seed_scope not in {"participant", "shared"}:
        raise ValueError("mask_seed_scope must be participant or shared")
    # Keep the cross-validation split paired across decoders. Its sensitivity must
    # be assessed with independent reruns rather than treated as sampling variation.
    cv = StratifiedKFold(n_splits=n_splits_eff, shuffle=True, random_state=random_seed)
    rows = []
    for fold, (train_idx, test_idx) in enumerate(cv.split(X, y), start=1):
        clf = make_pipeline_by_name(pipeline_name, csp_components=min(csp_components, X.shape[1]), random_state=random_seed)
        clf.fit(X[train_idx], y[train_idx])
        y_test = y[test_idx]
        for fraction in dropout_fractions:
            fraction = float(fraction)
            n_repeats = 1 if fraction == 0.0 else repeats_per_fraction
            for repeat in range(n_repeats):
                if mask_seed_scope == "participant":
                    rng = _dropout_rng(random_seed, subject_id, fold, repeat, fraction)
                else:
                    # Legacy v0.3 schedule retained only to reproduce committed tables.
                    fraction_code = int(round(fraction * 100))
                    rng = np.random.default_rng(random_seed + 1000 * fold + 100 * repeat + fraction_code)
                X_eval, dropped = apply_channel_dropout(X[test_idx], fraction, rng)
                auc, bal_acc, brier, ece = _score_fold(clf, X_eval, y_test)
                rows.append(
                    {
                        "subject": subject_id,
                        "pipeline": pipeline_name,
                        "stressor": "channel_dropout" if fraction > 0 else "clean",
                        "montage": montage_name,
                        "fold": fold,
                        "dropout_fraction": fraction,
                        "repeat": repeat,
                        "n_channels": int(n_channels),
                        "n_dropped_channels": int(len(dropped)),
                        "balanced_accuracy": bal_acc,
                        "roc_auc": auc,
                        "brier_score": brier,
                        "ece": ece,
                        "protocol_version": BENCHMARK_PROTOCOL_VERSION,
                        "mask_seed_scope": mask_seed_scope,
                    }
                )
    return pd.DataFrame(rows)


def evaluate_subject_reduced_montages(
    X: np.ndarray,
    y: np.ndarray,
    channel_names: Sequence[str],
    subject_id: str | int,
    montages: dict[str, Sequence[str]],
    n_splits: int = 5,
    random_seed: int = 42,
    csp_components: int = 6,
    pipeline_name: str = "csp_lda",
) -> pd.DataFrame:
    """Evaluate clean performance on named reduced montages.

    Unlike random channel dropout, training and testing both use the same smaller
    channel set. This approximates a cheaper or more wearable electrode montage.
    """
    frames = []
    for montage_name, wanted in montages.items():
        X_sel, selected_names, _ = select_channels(X, channel_names, wanted)
        df = evaluate_subject_with_dropout(
            X_sel,
            y,
            subject_id=subject_id,
            dropout_fractions=(0.0,),
            repeats_per_fraction=1,
            n_splits=n_splits,
            random_seed=random_seed,
            csp_components=min(csp_components, X_sel.shape[1]),
            pipeline_name=pipeline_name,
            montage_name=montage_name,
            n_channels=X_sel.shape[1],
        )
        df["stressor"] = "reduced_montage"
        df["selected_channels"] = ",".join(selected_names)
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def subject_level_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Average folds/repeats within subject before population summaries.

    Legacy benchmark outputs may lack probability-calibration columns. Missing
    optional metrics are carried forward as NaN so downstream summary code keeps
    a stable schema without fabricating values.
    """
    results = results.copy()
    for optional in ["brier_score", "ece"]:
        if optional not in results.columns:
            results[optional] = np.nan
    if "n_dropped_channels" not in results.columns:
        results["n_dropped_channels"] = np.nan
    group_cols = ["dataset", "subject", "pipeline", "stressor", "montage", "dropout_fraction"]
    optional_condition_cols = ["region", "session_train", "session_test"]
    present = [c for c in group_cols if c in results.columns]
    present += [c for c in optional_condition_cols if c in results.columns and results[c].notna().any()]
    return (
        results.groupby(present, as_index=False, dropna=False)
        .agg(
            roc_auc=("roc_auc", "mean"),
            balanced_accuracy=("balanced_accuracy", "mean"),
            brier_score=("brier_score", "mean"),
            ece=("ece", "mean"),
            n_channels=("n_channels", "first"),
            n_dropped_channels=("n_dropped_channels", "mean"),
        )
    )


def subject_bootstrap_ci(
    values: np.ndarray,
    confidence_level: float = 0.95,
    random_seed: int = 42,
    n_resamples: int = 2000,
) -> tuple[float, float]:
    """Bootstrap confidence interval for a mean over subjects."""
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 2:
        return (np.nan, np.nan)
    res = bootstrap(
        (values,),
        np.mean,
        confidence_level=confidence_level,
        n_resamples=n_resamples,
        random_state=random_seed,
        method="BCa",
    )
    return float(res.confidence_interval.low), float(res.confidence_interval.high)


def population_summary(results: pd.DataFrame, random_seed: int = 42) -> pd.DataFrame:
    """Population summary after collapsing to one row per subject/condition."""
    subj = subject_level_summary(results)
    group_cols = ["dataset", "pipeline", "stressor", "montage", "dropout_fraction"]
    group_cols += [c for c in ["region", "session_train", "session_test"] if c in subj.columns and subj[c].notna().any()]
    rows = []
    for keys, g in subj.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        lo, hi = subject_bootstrap_ci(g["roc_auc"].to_numpy(), random_seed=random_seed)
        bal_lo, bal_hi = subject_bootstrap_ci(g["balanced_accuracy"].to_numpy(), random_seed=random_seed)
        brier_lo, brier_hi = subject_bootstrap_ci(g["brier_score"].to_numpy(), random_seed=random_seed) if "brier_score" in g else (np.nan, np.nan)
        ece_lo, ece_hi = subject_bootstrap_ci(g["ece"].to_numpy(), random_seed=random_seed) if "ece" in g else (np.nan, np.nan)
        row = dict(zip(group_cols, keys))
        row.update(
            {
                "n_subjects": int(g["subject"].nunique()),
                "mean_roc_auc": float(g["roc_auc"].mean()),
                "roc_auc_ci_low": lo,
                "roc_auc_ci_high": hi,
                "mean_balanced_accuracy": float(g["balanced_accuracy"].mean()),
                "balanced_accuracy_ci_low": bal_lo,
                "balanced_accuracy_ci_high": bal_hi,
                "mean_brier_score": float(g["brier_score"].mean()) if "brier_score" in g else np.nan,
                "brier_score_ci_low": brier_lo,
                "brier_score_ci_high": brier_hi,
                "mean_ece": float(g["ece"].mean()) if "ece" in g else np.nan,
                "ece_ci_low": ece_lo,
                "ece_ci_high": ece_hi,
                "mean_n_channels": float(g["n_channels"].mean()),
            }
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values(group_cols).reset_index(drop=True)


# ---- Optional Riemannian baseline and spatial dropout utilities ----

def make_riemannian_logreg(random_state: int = 42):
    """Create an optional Riemannian covariance baseline.

    Requires pyriemann. This is intentionally optional so the CSP+LDA pipeline
    remains usable in minimal environments. It returns a sklearn Pipeline:
    Covariances -> TangentSpace -> LogisticRegression.
    """
    try:
        from pyriemann.estimation import Covariances
        from pyriemann.tangentspace import TangentSpace
        from sklearn.linear_model import LogisticRegression
    except Exception as exc:  # pragma: no cover
        raise ImportError(
            "Riemannian baseline requires pyriemann. Install with `python -m pip install pyriemann`."
        ) from exc
    return Pipeline(
        steps=[
            ("cov", Covariances(estimator="oas")),
            ("ts", TangentSpace(metric="riemann")),
            ("lr", LogisticRegression(max_iter=2000, random_state=random_state)),
        ]
    )


def make_pipeline_by_name(name: str, csp_components: int = 6, random_state: int = 42):
    """Factory for benchmark pipelines."""
    name = str(name).lower()
    if name in {"csp_lda", "csp+lda"}:
        return make_csp_lda(n_components=csp_components, random_state=random_state)
    if name in {"riemann_lr", "tangent_space_lr", "riemannian_logreg"}:
        return make_riemannian_logreg(random_state=random_state)
    raise ValueError(f"Unknown pipeline name: {name}")


MOTOR_REGION_CHANNELS = {
    "left_motor_strip": ["FC5", "FC3", "FC1", "C5", "C3", "C1", "CP5", "CP3", "CP1"],
    "midline_motor_strip": ["FCz", "Cz", "CPz"],
    "right_motor_strip": ["FC2", "FC4", "FC6", "C2", "C4", "C6", "CP2", "CP4", "CP6"],
    "central_motor_9": ["FC3", "FCz", "FC4", "C3", "Cz", "C4", "CP3", "CPz", "CP4"],
}


def apply_named_region_dropout(
    X: np.ndarray,
    channel_names: Sequence[str],
    region_name: str,
    region_channels: dict[str, Sequence[str]] | None = None,
) -> tuple[np.ndarray, list[str], list[int]]:
    """Zero a physiologically grouped channel region, e.g. left motor strip.

    This is a stronger deployment stressor than independent random channel loss:
    it approximates cap displacement, local cable failure, or a bad-electrode cluster.
    """
    region_channels = region_channels or MOTOR_REGION_CHANNELS
    if region_name not in region_channels:
        raise ValueError(f"Unknown region {region_name!r}. Known regions: {sorted(region_channels)}")
    present = [ch for ch in region_channels[region_name] if ch in channel_names]
    if not present:
        raise ValueError(f"No channels for region {region_name!r} are present in this dataset")
    idx = channel_indices(channel_names, present)
    X2 = np.asarray(X).copy()
    X2[:, idx, :] = 0.0
    return X2, present, idx


def evaluate_subject_region_dropout(
    X: np.ndarray,
    y: np.ndarray,
    channel_names: Sequence[str],
    subject_id: str | int,
    region_names: Sequence[str] = ("left_motor_strip", "midline_motor_strip", "right_motor_strip"),
    n_splits: int = 5,
    random_seed: int = 42,
    csp_components: int = 6,
    pipeline_name: str = "csp_lda",
) -> pd.DataFrame:
    """Evaluate test-time region dropout for one subject.

    Training remains clean. Test folds are corrupted by zeroing a named channel
    region. This function operates on supplied EEG arrays and leaves training folds unmodified.
    """
    X = np.asarray(X)
    y = np.asarray(y)
    if len(np.unique(y)) != 2:
        raise ValueError("This evaluator expects exactly two classes")
    _, counts = np.unique(y, return_counts=True)
    n_splits_eff = min(int(n_splits), int(counts.min()))
    if n_splits_eff < 2:
        raise ValueError("Need at least two samples per class for cross-validation")
    cv = StratifiedKFold(n_splits=n_splits_eff, shuffle=True, random_state=random_seed)
    rows = []
    for fold, (train_idx, test_idx) in enumerate(cv.split(X, y), start=1):
        clf = make_pipeline_by_name(pipeline_name, csp_components=min(csp_components, X.shape[1]), random_state=random_seed)
        clf.fit(X[train_idx], y[train_idx])
        y_test = y[test_idx]
        for region_name in region_names:
            X_eval, dropped_names, dropped_idx = apply_named_region_dropout(X[test_idx], channel_names, region_name)
            auc, bal_acc, brier, ece = _score_fold(clf, X_eval, y_test)
            rows.append({
                "subject": subject_id,
                "pipeline": pipeline_name,
                "stressor": "region_dropout",
                "montage": "all_channels",
                "fold": fold,
                "dropout_fraction": len(dropped_idx) / X.shape[1],
                "repeat": 0,
                "region": region_name,
                "dropped_channels": ",".join(dropped_names),
                "n_channels": int(X.shape[1]),
                "n_dropped_channels": int(len(dropped_idx)),
                "balanced_accuracy": bal_acc,
                "roc_auc": auc,
                "brier_score": brier,
                "ece": ece,
            })
    return pd.DataFrame(rows)


def evaluate_subject_cross_session(
    X: np.ndarray,
    y: np.ndarray,
    metadata: pd.DataFrame,
    subject_id: str | int,
    random_seed: int = 42,
    csp_components: int = 6,
    pipeline_name: str = "csp_lda",
) -> pd.DataFrame:
    """Train on first available session and test on later sessions when metadata permit it."""
    if metadata is None or len(metadata) != len(y):
        return pd.DataFrame()
    meta = pd.DataFrame(metadata).reset_index(drop=True)
    session_col = next((c for c in ["session", "session_id", "sessions"] if c in meta.columns), None)
    if session_col is None:
        return pd.DataFrame()
    sessions = [s for s in pd.unique(meta[session_col]) if pd.notna(s)]
    sessions = sorted(sessions, key=lambda value: (str(type(value)), str(value)))
    if len(sessions) < 2:
        return pd.DataFrame()
    first_session = sessions[0]
    train_idx = np.flatnonzero(meta[session_col].to_numpy() == first_session)
    rows = []
    for test_session in sessions[1:]:
        test_idx = np.flatnonzero(meta[session_col].to_numpy() == test_session)
        if len(train_idx) == 0 or len(test_idx) == 0:
            continue
        if len(np.unique(y[train_idx])) != 2 or len(np.unique(y[test_idx])) != 2:
            continue
        clf = make_pipeline_by_name(pipeline_name, csp_components=min(csp_components, X.shape[1]), random_state=random_seed)
        clf.fit(X[train_idx], y[train_idx])
        auc, bal_acc, brier, ece = _score_fold(clf, X[test_idx], y[test_idx])
        rows.append({
            "subject": subject_id,
            "pipeline": pipeline_name,
            "stressor": "cross_session",
            "montage": "all_channels",
            "fold": 0,
            "dropout_fraction": 0.0,
            "repeat": 0,
            "session_train": str(first_session),
            "session_test": str(test_session),
            "n_channels": int(X.shape[1]),
            "n_dropped_channels": 0,
            "balanced_accuracy": bal_acc,
            "roc_auc": auc,
            "brier_score": brier,
            "ece": ece,
        })
    return pd.DataFrame(rows)
