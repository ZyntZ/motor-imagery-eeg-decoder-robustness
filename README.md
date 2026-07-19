# Motor-Imagery EEG Channel-Loss Benchmark

This repository evaluates two established motor-imagery EEG decoders under controlled channel loss: common spatial patterns with linear discriminant analysis (CSP–LDA) and Riemannian tangent-space logistic regression. The analyses use PhysioNet EEG Motor Movement/Imagery and BNCI2014-001.

The benchmark covers four settings:

- intact test data;
- random or anatomically grouped channels set to zero at test time;
- models retrained on 3- and 9-channel motor montages;
- first-session to later-session transfer when session metadata are available.

Channel zeroing is a reproducible perturbation, not a physical model of electrode failure. The results concern offline binary classification, mostly in healthy participants. They do not establish online or clinical prosthesis performance.

## Main result

On PhysioNet, 50% random channel dropout reduced mean receiver operating characteristic area under the curve (ROC-AUC) from 0.655 to 0.527 for CSP–LDA and from 0.675 to 0.554 for Riemannian logistic regression. Results for the 9-channel montage were close to the full-montage estimates, but equivalence was not tested.

## Install and check the included results

The locked environment targets CPython 3.11 on Linux.

```bash
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
python -m pytest
make validate-results
make compare-physionet-pipelines
```

A complete rerun downloads the source EEG data and requires the optional EEG dependencies:

```bash
python -m pip install -e ".[eeg]"
make bnci-full
make physionet-full
```

These runs can take several hours. Participant-level checkpoints allow interrupted runs to resume. See `REPRODUCIBILITY.md` for details.

To regenerate summaries from completed PhysioNet runs without refitting the decoders:

```bash
make postprocess-physionet-full-available
```

## Outputs

- `results/*_results.csv`: fold- and repeat-level measurements;
- `results/*_subject_summary.csv`: one row per participant and condition, used for inference;
- `results/PhysionetMI_csp_lda_vs_riemann_lr_paired_comparison.csv`: paired absolute ROC-AUC contrasts;
- `results/PhysionetMI_csp_lda_vs_riemann_lr_difference_in_degradation.csv`: paired contrasts of change from clean data;
- `manuscript/`: article source and figures.

Validation scripts check schemas, ranges, duplicate keys and fold-to-participant aggregation. Passing those checks establishes internal consistency, not scientific validity.

## Analysis choices and limits

Population inference uses participants rather than folds or dropout repeats as independent units. ROC-AUC is the primary outcome; balanced accuracy is secondary. Brier score and expected calibration error are included when probability estimates are available.

The reported analyses used shuffled five-fold cross-validation within participant, 8–32 Hz filtering, 128 Hz resampling, six CSP components, Oracle Approximating Shrinkage covariance, and dropout fractions of 0.1, 0.2, 0.3 and 0.5. Each nonzero fraction used 10 channel masks per fold.

The same deterministic mask schedule was used across participants and decoders for matched fold, repeat and dropout-fraction indices. This supports paired decoder comparisons but leaves the reported uncertainty conditional on that mask schedule. Sensitivity to alternative masks, cross-validation splits, frequency bands and CSP component counts was not evaluated.

Zeroing does not reproduce impedance noise, bridging, clipping, intermittent contact or adaptive recalibration. Cross-session estimates are limited to the nine BNCI2014-001 participants.

For the 9-channel montage, mean changes from the full montage were 0.014 ROC-AUC for CSP–LDA (95% CI −0.013 to 0.040) and 0.001 for Riemannian logistic regression (95% CI −0.027 to 0.030). These intervals include both small losses and small gains; they are not evidence of equivalence.

## Repository layout

```text
configs/                 benchmark parameters
src/bci_robustness/      evaluation and summary functions
scripts/                 command-line analyses
results/                 fold-, participant- and population-level tables
reports/                 reference tables, figures and validation output
artifacts/               regenerated checks and release files (not required in commits)
manuscript/              article source and submission files
tests/                   unit and integration tests
```

Raw EEG is not redistributed. Dataset identifiers, licenses and provenance are documented in `DATA_PROVENANCE.md`. Statistical definitions are in `STATISTICAL_REPORTING.md`. Software citation metadata are in `CITATION.cff`.

Benchmark code is distributed under the BSD 3-Clause License. The source EEG datasets retain their original licenses.
