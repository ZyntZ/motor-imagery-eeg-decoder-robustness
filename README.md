# Motor-Imagery EEG Channel-Loss Benchmark

This repository evaluates common spatial patterns with linear discriminant analysis (CSP–LDA) and Riemannian tangent-space logistic regression on two public motor-imagery EEG datasets: PhysioNet EEG Motor Movement/Imagery and BNCI2014-001.

The experiments compare:

- intact test data;
- test-time zeroing of randomly selected channels;
- zeroing of predefined motor-region channels;
- retraining and evaluation on 3- and 9-channel montages;
- first-session to later-session transfer where session metadata permit it.

Channel zeroing is a controlled perturbation, not a complete model of physical electrode failure. Results describe offline binary classification in public datasets, mostly from healthy participants. They are not evidence about online or clinical prosthesis control.

## Reproduce

```bash
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
make validate-results
make compare-physionet-pipelines
```

A complete rerun that downloads raw EEG requires the optional EEG dependencies and substantially more time:

```bash
python -m pip install -e ".[eeg]"
make bnci-full
make physionet-full
```

## Main outputs

- `results/*_subject_summary.csv`: one row per participant and condition, used for inference.
- `results/PhysionetMI_csp_lda_vs_riemann_lr_paired_comparison.csv`: paired absolute-AUC contrasts.
- `results/PhysionetMI_csp_lda_vs_riemann_lr_difference_in_degradation.csv`: paired contrasts of change from clean.
- `results/*_results.csv`: fold/repeat measurements.

Generated consistency checks are stored under `artifacts/validation/`. They test schemas, ranges, keys, and fold-to-participant aggregation; they do not establish scientific validity.

## Scope and limitations

The primary outcome is receiver operating characteristic area under the curve (ROC-AUC). Balanced accuracy is secondary. Brier score and expected calibration error are reported when probability estimates are available. Population inference uses participants, not folds or dropout repeats, as independent units.

The study evaluates two classical pipelines and two public datasets. It does not test deep networks, asynchronous control, adaptive recalibration, participants with motor impairment, or physical electrode faults. Cross-session estimates are available only for the nine BNCI2014-001 participants.

For the 9-channel montage, the estimated mean changes from the full montage were 0.014 ROC-AUC for CSP–LDA (95% CI −0.013 to 0.040) and 0.001 for Riemann–LR (95% CI −0.027 to 0.030). No equivalence or non-inferiority margin was specified, so these estimates must not be described as proof of preserved performance.

## Design choices

| Decision | Rationale | Sensitivity analysis | Limitation |
|---|---|---|---|
| Zero selected test channels | Reproducible corruption with known severity | Regional and random channel sets | Does not represent noise, bridging, clipping, or interpolation |
| Five-fold within-participant cross-validation | Estimates participant-specific decoding | Paired nonparametric tests at participant level | Split-seed sensitivity is not quantified |
| 8–32 Hz band | Covers the conventional mu and beta motor-imagery range | None in this release | Other bands and filter banks may change rankings |
| Six CSP components | Fixed conventional baseline; not selected on reported test folds | Components are capped by montage size | May not be optimal for every participant or montage |
| OAS covariance | Stabilizes covariance estimates with limited trials | None in this release | Introduces a method-specific regularization choice |
| Dropout fractions 0.1, 0.2, 0.3, 0.5 | Spans mild to severe channel loss without treating fractions as continuous | Nonlinear diagnostics included | Does not locate a failure threshold |
| Ten dropout repeats | Averages random channel-set variability at manageable runtime | Subject-level inference collapses repeats | Monte Carlo sensitivity was not separately quantified |
| ROC-AUC primary | Threshold-independent discrimination for the binary task | Balanced accuracy and calibration metrics | Does not measure online control utility |

Choices labelled “none in this release” are limitations, not evidence that the result is insensitive to that decision.

## Installation

The locked environment targets CPython 3.11 on Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
```

For development and tests:

```bash
python -m pip install -e ".[dev]"
python -m compileall -q scripts src
python -m pytest
```

## Quick smoke test

```bash
python scripts/run_benchmark.py --config configs/benchmark.yaml --dry-run
python scripts/run_benchmark.py --config configs/benchmark.yaml --dataset PhysionetMI --list-subjects
```

## Full benchmark

```bash
make bnci-full
make physionet-full
```

Long runs save compatible participant checkpoints and reuse them when the same command is restarted. Retry, checkpoint, and recovery details are documented in `REPRODUCIBILITY.md`.

To process completed full PhysioNet outputs without refitting models:

```bash
make postprocess-physionet-full-available
```

## Reproduce tables and checks

```bash
make validate-results
make statistical-reports
make compare-physionet-pipelines
make methods-figures
```

Statistical definitions and multiplicity corrections are documented in `STATISTICAL_REPORTING.md`. Dataset access, licenses, and the limits of the available acquisition-level ethics records are documented in `DATA_PROVENANCE.md`.

## Repository layout

```text
configs/                 benchmark parameters
src/bci_robustness/      evaluation and summary functions
scripts/                 command-line analyses
results/                 canonical fold, participant, and comparison tables
artifacts/validation/    generated consistency checks
artifacts/manifests/     file inventories and hashes
manuscript/              article source, figures, and cover letter
tests/                   unit and integration tests
```

## Data provenance

Raw EEG is not redistributed. PhysioNet EEGMMIDB is available under ODC-By 1.0; BNCI2014-001 is available under CC BY-ND 4.0. Reproduction downloads the data through MOABB/MNE and remains subject to the provider terms. See `DATA_PROVENANCE.md` for dataset identifiers and attribution.

## Citation

Software citation metadata are in `CITATION.cff`. Cite the original dataset and method publications listed in the manuscript when reusing results.

## License

Benchmark code is distributed under the BSD 3-Clause License. Dataset licenses apply separately to the source EEG data.
