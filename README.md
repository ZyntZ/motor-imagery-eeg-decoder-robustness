# BCI Prosthesis Robustness Benchmark

Selected project: a reproducible benchmark of motor-imagery BCI decoders under realistic deployment stressors: cross-session/domain shift, channel dropout, reduced montages, and per-subject reliability failure.

This repository is a starting implementation. It does not include fabricated data. All analyses are designed to run on open EEG datasets fetched through MOABB/MNE.

## Why this project

Most open BCI algorithm papers optimize average decoding accuracy on clean offline data. A deployable neuroprosthetic controller also needs to fail gracefully when electrodes detach, the cap montage differs, or a subject/session shifts. This project turns that problem into a publishable, reproducible benchmark with uncertainty estimates and transparent statistics.

## Data sources

Default plan uses MOABB datasets and can begin with PhysioNet EEG Motor Movement/Imagery (`Schalk2004`) for feasibility, then expand to BNCI/BCI Competition datasets where licenses allow automatic download.

## Implementation status

- repository skeleton created
- configuration file created
- benchmark CLI scaffold created
- statistical analysis plan written

## Quick start

```bash
python -m pip install mne moabb scikit-learn pandas numpy scipy statsmodels matplotlib seaborn pyyaml
python scripts/run_benchmark.py --config configs/benchmark.yaml --dry-run
```

Remove `--dry-run` only when you are ready to download open EEG datasets.

## Core outputs planned

1. Subject-level performance table for each dataset/model/stressor.
2. Robustness curves vs. channel loss severity.
3. Mixed-effects model estimating performance loss attributable to stressors.
4. Subject-level uncertainty and reliability flags.
5. Reproducible manuscript-ready tables and figures.

## No fabricated data policy

The project must only use public datasets downloaded from their official sources or MOABB wrappers. If a dataset cannot be accessed, it is excluded and reported.


## Development continuation: PhysioNetMI n=10 run

Continuation added a writable project copy, subject-level checkpointing, reduced-montage evaluation, and a real-data run on PhysioNetMI subjects 1–10. Outputs are in `results/`:

- `PhysionetMI_dev10_results.csv`: fold/repeat-level results
- `PhysionetMI_dev10_subject_summary.csv`: subject-level summaries used for inference
- `PhysionetMI_dev10_population_summary.csv`: population summaries with bootstrap confidence intervals
- `PhysionetMI_dev10_paired_comparisons.csv`: paired subject-level comparisons against clean all-channel baseline
- `PhysionetMI_dev10_reliability_flags_ci.csv`: failure-rate estimates with exact binomial confidence intervals

Important limitation: n=10 is a development run, not the final manuscript sample. Full analysis should scale to all accessible subjects and then repeat on at least one additional dataset.


## Next-stage update: intervention recommendation layer

This repository now includes a stronger publishable layer beyond robustness curves:

1. **Subject risk cards** from real PhysioNetMI n=10 development results.
2. **Intervention recommendations**: whether a subject should use a reduced montage first, require recalibration/dropout-aware training, or be screened out for this paradigm.
3. **Interactive dashboards**:
   - `reports/PhysionetMI_dev10_interactive_dashboard.html`
   - `reports/PhysionetMI_dev10_intervention_recommendations.html`
4. **New benchmark hooks**:
   - optional Riemannian tangent-space logistic regression baseline (`riemann_lr`, requires `pyriemann`);
   - named motor-region dropout (`left_motor_strip`, `midline_motor_strip`, `right_motor_strip`) for spatially clustered channel-failure stress tests.

Run after a benchmark completes:

```bash
python scripts/analyze_robustness.py --results-dir results --prefix PhysionetMI_dev10 --reports-dir reports
python scripts/recommend_interventions.py --results-dir results --reports-dir reports --prefix PhysionetMI_dev10
```

Next benchmark run with new hooks:

```bash
python scripts/run_benchmark.py   --config configs/benchmark.yaml   --download-and-run   --dataset PhysionetMI   --subjects 1 2 3 4 5 6 7 8 9 10   --include-reduced-montage   --include-region-dropout   --pipeline csp_lda   --suffix dev10_region
```

Current evidence is a development run only (n=10). Do not treat it as a final manuscript-level estimate.

## Publication-preparation update

This repository has been advanced from the PhysioNetMI n=10 development run toward a manuscript-ready benchmark scaffold. No synthetic EEG data are included or generated. All new numerical outputs are derived from saved CSV files or from real EEG loaded through MOABB/MNE.

### Reproducibility

Install dependencies with either:

```bash
python -m pip install -r requirements.txt
# or
conda env create -f environment.yml
```

Useful entry points:

```bash
make dry-run
make list-subjects
make all-dev10
```

Full manuscript-scale commands are in `Makefile` and `run_all.sh`. By default, `scripts/run_benchmark.py` now runs all subjects exposed by MOABB for the selected dataset when `--subjects` is omitted. It also supports `--list-subjects` and repository-relative path normalization.

### Implemented benchmark extensions

- Decoders: `csp_lda` and `riemann_lr`.
- Stressors: random channel dropout, reduced montage, and cross-session train-first-session/test-later-sessions evaluation when MOABB metadata provide sessions.
- External validation dataset: BNCI2014-001 through MOABB.
- Metrics: ROC-AUC, balanced accuracy, Brier score, and expected calibration error. Brier/ECE are present for newly generated outputs; older PhysioNetMI dev10 CSVs did not store fold probabilities, so those calibration fields are `NaN` for the archived dev10 run.
- Statistics: subject-level aggregation before inference, bootstrap confidence intervals over subjects, Wilcoxon/bootstrap sensitivity tests, Benjamini-Hochberg FDR corrections, and mixed-effects models with subject random intercepts where supported by the available subject-level table.
- Pre-specified intervention thresholds: clean-working ROC-AUC >= 0.60 and stressor-failure ROC-AUC < 0.60.

### Current real-data outputs

Development validation remains PhysioNetMI n=10 and should not be interpreted as the final manuscript estimate. External validation was run on BNCI2014-001 subjects 1-9 for both `csp_lda` and `riemann_lr`.

Key CSV outputs:

- `results/manuscript_population_metrics_combined.csv`
- `results/csv_manifest.csv`
- `results/PhysionetMI_dev10_final_*.csv`
- `results/BNCI2014-001_BNCI2014_001_all_csp_lda_*.csv`
- `results/BNCI2014-001_BNCI2014_001_all_riemann_lr_*.csv`

### Current limitations

- PhysioNetMI full 1-109 was prepared in the runner but not executed in this handoff because only the existing n=10 development CSVs were available before the requested repository update. Run `make physionet-full` to generate the full PhysioNetMI manuscript tables from MOABB.
- No subject exclusions are hard-coded. Any inaccessible subject should be reported by the runner, not silently excluded.
- Fold/repeat rows are technical resampling units only. Inferential CSVs aggregate to subject level first.
- Offline EEG benchmark results do not support causal claims about online neuroprosthetic control.
