# Reproducibility guide

## Environment

```bash
conda env create -f environment.yml
conda activate bci-robustness-benchmark
```

or

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Smoke checks

```bash
python scripts/run_benchmark.py --config configs/benchmark.yaml --dry-run
python -m compileall -q scripts src
```

## Recreate derived PhysioNetMI development outputs

```bash
python scripts/analyze_robustness.py --results-dir results --prefix PhysionetMI_dev10 --reports-dir reports
python scripts/recommend_interventions.py --results-dir results --reports-dir reports --prefix PhysionetMI_dev10
python scripts/final_statistics.py --results-dir results --prefix PhysionetMI_dev10
```

## Full benchmark runs

```bash
make bnci-full
make physionet-full
```

Full runs download and preprocess EEG data through MOABB/MNE and can take substantial time.

## Technical validation

```bash
python -m pip install -e .
python -m compileall -q scripts src
python -m pytest
make validate-results
```

These checks validate package importability, syntax, lightweight unit tests, and publication-facing result-table integrity for the included reference outputs.




## Commit-ready publication check

Run the full local gate before tagging or archiving a release:

```bash
make publication-check
```

This target runs syntax checks, unit tests, validation of included reference results, statistical report regeneration for the included prefixes, and release manifest generation. The manifest is written to `reports/release_manifest.json` and records SHA-256 hashes for source, configuration, documentation, reference CSV/JSON outputs, and report files.

## Transient download failures and resume

Subject-level checkpoints live in `results/checkpoints/`. If a network timeout occurs, rerun the same command; completed checkpoints are reused. Increase retry settings for unstable connections:

```bash
python scripts/run_benchmark.py --config configs/benchmark.yaml --download-and-run --dataset PhysionetMI --subjects 29 --include-reduced-montage --include-region-dropout --pipeline csp_lda --max-retries 5 --retry-wait-seconds 60
```

Use `--skip-failed` only for exploratory continuation. It writes `*_failed_subjects.csv` and `*_failed_subjects.json`; outputs from skipped-subject runs are incomplete until those subjects are rerun successfully.

Post-processing scripts rebuild `{prefix}_subject_wide.csv` from the current `{prefix}_subject_summary.csv` by default. Use `--use-cached-wide` only when intentionally reusing a previous wide table.


## CI note for release manifest generation

The `release-manifest` target intentionally depends on `validate-results`, `statistical-reports`, and `methods-figures`. This lets CI call `make release-manifest` directly after checkout while still generating all outputs required by `reports/release_manifest.json`.
