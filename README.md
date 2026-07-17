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



## Running the full EEG benchmark

The full PhysioNet and BNCI targets require the optional EEG stack. `make physionet-full` now checks the same Python interpreter selected by `PYTHON` and installs the `eeg` extra automatically when `mne`, `moabb`, or `pyriemann` is missing:

```bash
make physionet-full
```

To install it explicitly first:

```bash
make install-eeg
# equivalent: python -m pip install -e ".[eeg]"
```

Existing files under `moabb_data/` and completed subject checkpoints under `results/checkpoints/` are reused. Installing the Python packages does not delete or restart the 108 already downloaded subject files. Use `PYTHON=/path/to/python make physionet-full` if the project runs in a specific virtual environment.


### PhysioNet CSP + LDA preflight and full run

Run one real subject through every requested CSP + LDA stressor before committing to the 109-subject computation:

```bash
make physionet-csp-preflight
```

The preflight uses subject 1, including random channel dropout, the 3- and 9-channel reduced montages, named motor-region dropout, and cross-session evaluation when the dataset metadata permit it. Its subject checkpoint is stored under `results/checkpoints/` and is reused by the full run.

After the preflight succeeds, run only the missing full CSP + LDA experiment without repeating the completed Riemannian pipeline:

```bash
make physionet-csp-full
```

The run is resumable at subject level. Re-running the same command reuses compatible checkpoints. Do not use `--overwrite` unless the existing checkpoints are known to be invalid. A complete run must contain 109 unique subjects before post-processing:

```bash
make postprocess-full PREFIX=PhysionetMI_PhysionetMI_all_csp_lda EXPECTED_SUBJECTS=109
```

Interrupted checkpoint and final CSV writes use temporary files followed by an atomic rename, reducing the risk of truncated outputs. Raw EEG caches and checkpoints are excluded from release archives.

## Submission-readiness check

For a methods-journal submission package, run the repository-level readiness gate after validation, statistical tables, and methods figures have been regenerated:

```bash
make publication-check
make release-archive
```

The readiness gate writes `SUBMISSION_READINESS.md`, `reports/submission_readiness_checks.csv`, and `reports/submission_readiness_summary.json`. These files check metadata, provenance, reproducibility, validation artifacts, statistical-report artifacts, methods figures, release manifest status, filename hygiene, and absence of raw EEG/data-cache directories. They are derived from repository files only and do not create or modify benchmark observations.

## Statistical reporting

Before using result tables for manuscript statistics, run the deterministic CSV validation checks. These checks verify required schemas, metric ranges, duplicate evaluation keys, channel-count/dropout consistency, clean-baseline pairing, and agreement between fold-level results and subject-level summaries:

```bash
python scripts/validate_results.py --results-dir results --reports-dir reports --prefix PhysionetMI_dev10 --allow-warnings
make validate-results
```

For completed runs, generate methods-audit tables, paired subject-level effects, channel-dropout slopes, and compact CSV/LaTeX result tables:

```bash
python scripts/generate_statistical_report.py --results-dir results --reports-dir reports --prefix PhysionetMI_PhysionetMI_all_riemann_lr
```

See `STATISTICAL_REPORTING.md` for output definitions and statistical conventions.


## Completed full-run post-processing

After `make physionet-full` completes, process and validate a full result prefix with one command. The target installs the reporting extra when Plotly is missing, rebuilds subject/population summaries from the existing fold-level CSV, validates them, generates statistical reports and HTML outputs, and runs final statistics:

Choose only a pipeline that actually completed. Your completed run is Riemannian logistic regression:

```bash
make postprocess-full PREFIX=PhysionetMI_PhysionetMI_all_riemann_lr
```

Run the CSP + LDA command only if that separate full benchmark also completed and its outputs exist. To process every available full PhysioNet pipeline while safely skipping absent ones, use:

```bash
make postprocess-physionet-full-available
```

This does not reload EEG or rerun model fitting. The command uses the best available source in this order: the full `*_results.csv`; all 109 subject checkpoints; or an existing `*_subject_summary.csv` containing 109 unique subjects. The last mode can generate statistical and HTML reports but cannot repeat fold-level validation, because the fold rows are unavailable. Rebuilding from fold results or checkpoints preserves named region-dropout and cross-session condition identifiers.

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



## Publication readiness gate

This release includes repository metadata and a reproducibility gate intended for methods-review workflows:

```bash
make publication-check
```

The gate compiles scripts, runs unit tests, validates included reference result tables, regenerates statistical reporting packs, and writes `reports/release_manifest.json` with file hashes, selected package versions, validation summaries, and expected-output checks.

Repository metadata included for commit readiness:

- `LICENSE`: BSD-3-Clause license text matching `pyproject.toml`.
- `CITATION.cff`: citation metadata with a placeholder contributor entry to replace before submission.
- `.github/workflows/ci.yml`: continuous-integration workflow for compile, tests, validation, and manifest generation.
- `MANUSCRIPT_PLACEHOLDER.md`: explicit placeholder because manuscript/paper sources are intentionally not included in this snapshot.



## Methods-paper figures

Generate the three included methods figures directly from existing CSV outputs:

```bash
make methods-figures
```

The target writes PNG and SVG versions of:

- `reports/PhysionetMI_PhysionetMI_all_riemann_lr_methods_pipeline_schematic.*`
- `reports/PhysionetMI_PhysionetMI_all_riemann_lr_methods_robustness_degradation_roc_auc.*`
- `reports/PhysionetMI_PhysionetMI_all_riemann_lr_methods_intervention_class_counts.*`

The figure manifest is `reports/PhysionetMI_PhysionetMI_all_riemann_lr_methods_figures_manifest.json`. Figures are generated only from repository CSV outputs; no synthetic benchmark observations are created.

## Main outputs

For a run prefix such as `PhysionetMI_dev10`, the pipeline writes:

- `{prefix}_results.csv`: fold/repeat-level benchmark rows.
- `{prefix}_subject_summary.csv`: one row per subject/condition for inference.
- `{prefix}_population_summary.csv`: condition-level means and bootstrap confidence intervals.
- `{prefix}_paired_comparisons.csv` and `{prefix}_final_paired_sensitivity.csv`: paired comparisons of every available stressor condition (random dropout, reduced montage, region dropout, and cross-session transfer) against the clean all-channel baseline.
- `{prefix}_subject_risk_cards.csv`: subject-level robustness flags.
- `{prefix}_intervention_recommendations.csv`: subject-level deployment recommendations.
- HTML reports in `reports/` when Plotly is available.

## Statistical approach

Inference is performed after collapsing fold/repeat outputs to subject-level summaries. Paired stressor-vs-baseline analyses use within-subject differences. The scripts report confidence intervals, Shapiro-Wilk diagnostics for paired differences, paired t-tests, Wilcoxon signed-rank tests, standardized paired effect sizes, and Benjamini-Hochberg false-discovery-rate adjusted p-values where multiple comparisons are evaluated. Mixed-effects inference uses subject random intercepts in two prespecified models: an all-condition categorical model against the clean reference and a dose-response model restricted to clean plus random channel-dropout rows. Restricting the continuous dropout term prevents region, montage, and cross-session conditions from being incorrectly encoded as zero-severity dropout.

## Data and interpretation notes

- Example outputs in `results/` are benchmark artifacts produced from MOABB/MNE-accessible datasets and should be regenerated for final analyses.
- PhysioNetMI `dev10` outputs are a development subset and should not be interpreted as final population estimates.
- BNCI2014-001 outputs cover subjects 1-9 for the included CSP+LDA and Riemannian baseline runs.
- Metrics based on predicted probabilities, such as Brier score and expected calibration error, are available only when the fitted pipeline exposes usable probability estimates.
- Raw EEG downloads are intentionally not included in this repository.
- One-off pilot outputs not used by the current validation/release manifest are intentionally excluded from the cleaned paper-start archive.

## Technical status

This repository snapshot is for technical development of the benchmark code, result-processing scripts, and example outputs. Non-technical metadata and writing-stage materials are intentionally not included in this archive.


## Release archive audit

Run `make release-archive` to audit required metadata, validation outputs, statistical reports, methods figures, and filename hygiene before writing `dist/JNM_clean_paper_start.zip`. The audit excludes caches, bytecode, raw-data-like directories, and local temporary files.
