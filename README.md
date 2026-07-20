# Motor-imagery EEG decoding under channel zeroing

This repository compares two offline binary motor-imagery decoders:

- common spatial patterns followed by linear discriminant analysis (CSP–LDA);
- covariance features mapped to a Riemannian tangent space, followed by logistic regression (Riemann–LR).

The evaluation uses PhysioNet EEG Motor Movement/Imagery and BNCI2014-001. It tests intact data, test-time channel zeroing, retraining on 3- and 9-channel montages, and cross-session transfer where session metadata permit it.

**Scope.** Channel zeroing is a software perturbation. It is not a physical model of electrode impedance, bridging, clipping, intermittent contact, cap displacement, or online recalibration. The study concerns offline classification, mostly in healthy participants; it does not measure prosthesis control or clinical performance.

## Result reported in the manuscript

In the included PhysioNet participant summaries ($n=109$), 50% random channel zeroing changed mean ROC-AUC from 0.655 to 0.527 for CSP–LDA (mean paired change −0.128, 95% CI −0.153 to −0.102) and from 0.675 to 0.554 for Riemann–LR (−0.121, 95% CI −0.141 to −0.101).

These estimates are conditional on one shuffled cross-validation split and one deterministic channel-mask schedule. The mask seed does not include participant identity, so matched fold/repeat indices reuse the same channel indices across participants when channel order agrees. Alternative splits and mask schedules were not evaluated.

## Check the included outputs

The locked environment targets CPython 3.11 on Linux.

```bash
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
python -m pytest
make validate-results
make compare-physionet-pipelines
```

These commands test code behavior and the internal consistency of the committed tables. They do not recreate the EEG preprocessing or model fits.

To regenerate summaries from available completed PhysioNet runs without refitting decoders:

```bash
make postprocess-physionet-full-available
```

## Re-run from source EEG

```bash
python -m pip install -e ".[eeg]"
make bnci-full
make physionet-full
```

The commands download data through MOABB/MNE and may take several hours. Participant checkpoints allow interrupted runs to resume. See `REPRODUCIBILITY.md`.

## Analysis unit and uncertainty

Population analyses use participants, not folds or dropout repeats, as independent units. ROC-AUC is the primary outcome. Balanced accuracy is secondary; Brier score and expected calibration error are retained where probability estimates are available. Paired comparisons report confidence intervals, effect sizes, parametric tests, signed-rank sensitivity tests, and false-discovery-rate adjustment.

The 9-channel montage estimates were close to the full-montage estimates: mean paired changes were 0.014 for CSP–LDA (95% CI −0.013 to 0.040) and 0.001 for Riemann–LR (95% CI −0.027 to 0.030). No equivalence or non-inferiority margin was specified, so these results do not establish equivalence.

## Layout

```text
configs/                 benchmark parameters
src/bci_robustness/      evaluation and summary functions
scripts/                 command-line analyses
results/                 fold-, participant-, and population-level tables
reports/                 generated tables, figures, and validation output
manuscript/              article source and submission figures
tests/                   unit and integration tests
```

Raw EEG is not redistributed. Dataset identifiers and licenses are listed in `DATA_PROVENANCE.md`; statistical definitions are in `STATISTICAL_REPORTING.md`. The code is released under the BSD 3-Clause License. Source datasets retain their original licenses.
