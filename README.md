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
- PDF project plan generated in `reports/`

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


## update: intervention recommendation layer

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

Current evidence is a development run only (n=10). 