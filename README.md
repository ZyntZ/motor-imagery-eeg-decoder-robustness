# BCI Prosthesis Robustness Benchmark

A reproducible benchmark for motor-imagery EEG decoders under deployment stressors relevant to BCI-controlled prostheses: test-time channel dropout, reduced electrode montages, spatially clustered motor-channel dropout, and cross-session shift.

The project uses open EEG datasets available through MOABB and MNE. The benchmark reports subject-level outcomes, uncertainty estimates, paired stressor-vs-baseline comparisons, calibration metrics when probabilities are available, and subject-level intervention recommendations.


## Quality checks

The repository is installable as a `src/`-layout Python package and includes lightweight tests for core array utilities, summary-schema stability, and intervention-class rules.

```bash
python -m pip install -e .
python -m compileall -q scripts src
python -m pytest
```

## Included components

- Benchmark runner for MOABB datasets: `scripts/run_benchmark.py`.
- CSP+LDA and optional Riemannian tangent-space logistic regression baselines.
- Stress tests for random channel dropout, named motor-region dropout, reduced motor montages, and cross-session evaluation when session metadata permit it.
- Post-processing scripts for robustness summaries, failure rates, paired statistics, mixed-effects models, and recommendation cards.
- Example result tables and figures for PhysioNetMI development runs and BNCI2014-001 full-subject runs.

## Repository layout

```text
configs/                 Benchmark configuration
scripts/                 Command-line entry points
src/bci_robustness/      Core evaluation and summary utilities
results/                 Example benchmark outputs and derived statistics
reports/                 Figures and HTML reports generated from results
DATA_PROVENANCE.md       Dataset/result provenance notes
REPRODUCIBILITY.md       Commands for reproducing analyses
```

## Installation

Conda:

```bash
conda env create -f environment.yml
conda activate bci-robustness-benchmark
```

Pip:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The benchmark downloads EEG data through MOABB/MNE when `--download-and-run` is used. Set `moabb_data_dir` in `configs/benchmark.yaml` if the data cache should live outside the repository.

## Quick checks

```bash
python scripts/run_benchmark.py --config configs/benchmark.yaml --dry-run
python scripts/run_benchmark.py --config configs/benchmark.yaml --dataset PhysionetMI --list-subjects
```


## Long-run resume and transient download failures

Full MOABB/PhysioNet runs are subject-level resumable. Completed subjects are stored in `results/checkpoints/` and are reused on the next run unless `--overwrite` is supplied.

For transient network failures, the runner retries each subject before failing:

```bash
python scripts/run_benchmark.py --config configs/benchmark.yaml --download-and-run --dataset PhysionetMI --subjects 29 --include-reduced-montage --include-region-dropout --pipeline csp_lda --max-retries 5 --retry-wait-seconds 60
```

To continue past subjects that still fail after all retries, add `--skip-failed`. The runner writes `results/{dataset}_{suffix}_failed_subjects.csv` and `.json`. Treat skipped-subject outputs as incomplete until the failed subjects are rerun successfully.

If a checkpoint was created before optional stressors were requested, the runner now detects the missing stressor rows and recomputes that subject instead of silently reusing an incompatible checkpoint.

## Running benchmarks

Development run on selected PhysioNetMI subjects:

```bash
python scripts/run_benchmark.py   --config configs/benchmark.yaml   --download-and-run   --dataset PhysionetMI   --subjects 1 2 3 4 5 6 7 8 9 10   --include-reduced-montage   --pipeline csp_lda   --suffix dev10
```

Full BNCI2014-001 runs:

```bash
make bnci-full
```

Full PhysioNetMI runs:

```bash
make physionet-full
```

These commands may take substantial time because MOABB downloads and processes raw EEG data.


## Statistical reporting

For completed runs, generate methods-audit tables, paired subject-level effects, channel-dropout slopes, and compact CSV/LaTeX result tables:

```bash
python scripts/generate_statistical_report.py --results-dir results --reports-dir reports --prefix PhysionetMI_PhysionetMI_all_riemann_lr
```

See `STATISTICAL_REPORTING.md` for output definitions and statistical conventions.


## Post-processing

```bash
python scripts/analyze_robustness.py --results-dir results --prefix PhysionetMI_dev10 --reports-dir reports
python scripts/recommend_interventions.py --results-dir results --reports-dir reports --prefix PhysionetMI_dev10
python scripts/final_statistics.py --results-dir results --prefix PhysionetMI_dev10
```

Convenience target:

```bash
make all-dev10
```

## Main outputs

For a run prefix such as `PhysionetMI_dev10`, the pipeline writes:

- `{prefix}_results.csv`: fold/repeat-level benchmark rows.
- `{prefix}_subject_summary.csv`: one row per subject/condition for inference.
- `{prefix}_population_summary.csv`: condition-level means and bootstrap confidence intervals.
- `{prefix}_paired_comparisons.csv` and `{prefix}_final_paired_sensitivity.csv`: paired comparisons against the clean all-channel baseline.
- `{prefix}_subject_risk_cards.csv`: subject-level robustness flags.
- `{prefix}_intervention_recommendations.csv`: subject-level deployment recommendations.
- HTML reports in `reports/` when Plotly is available.

## Statistical approach

Inference is performed after collapsing fold/repeat outputs to subject-level summaries. Paired stressor-vs-baseline analyses use within-subject differences. The scripts report confidence intervals, Shapiro-Wilk diagnostics for paired differences, paired t-tests, Wilcoxon signed-rank tests, standardized paired effect sizes, and Benjamini-Hochberg false-discovery-rate adjusted p-values where multiple comparisons are evaluated. Mixed-effects models use subject random intercepts for condition-level comparisons.

## Data and interpretation notes

- Example outputs in `results/` are benchmark artifacts produced from MOABB/MNE-accessible datasets and should be regenerated for final analyses.
- PhysioNetMI `dev10` outputs are a development subset and should not be interpreted as final population estimates.
- BNCI2014-001 outputs cover subjects 1-9 for the included CSP+LDA and Riemannian baseline runs.
- Metrics based on predicted probabilities, such as Brier score and expected calibration error, are available only when the fitted pipeline exposes usable probability estimates.
- Raw EEG downloads are intentionally not included in this repository.

## Technical status

This repository snapshot is for technical development of the benchmark code, result-processing scripts, and example outputs. Non-technical metadata and writing-stage materials are intentionally not included in this archive.
