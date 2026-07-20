# Reproducibility

## Environment

The reference lock file targets CPython 3.11 on Linux.

```bash
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
```

Alternatively, create the supplied Conda environment:

```bash
conda env create -f environment.yml
conda activate bci-robustness-benchmark
```

For a complete rerun with EEG download and preprocessing:

```bash
python -m pip install -e ".[eeg]"
```

## Quick checks

```bash
python scripts/run_benchmark.py --config configs/benchmark.yaml --dry-run
python -m compileall -q scripts src
python -m pytest
make validate-results
make compare-physionet-pipelines
```

These commands test imports, syntax, unit-level behavior and consistency of the included result tables. They do not independently recreate the fold-level measurements from raw EEG and cannot verify that the committed outputs came from the committed code. A strong reproducibility check requires a clean full rerun and comparison of regenerated tables.

## Full benchmark

```bash
make bnci-full
make physionet-full
```

The commands download data through MOABB/MNE, preprocess the recordings and fit both decoder pipelines. Runtime depends on the local data cache and hardware.

Long runs write participant checkpoints to `results/checkpoints/`. Repeating the same command reuses compatible completed checkpoints. For unstable network connections, increase the retry count and waiting time, for example:

```bash
python scripts/run_benchmark.py   --config configs/benchmark.yaml   --download-and-run   --dataset PhysionetMI   --subjects 29   --include-reduced-montage   --include-region-dropout   --pipeline csp_lda   --max-retries 5   --retry-wait-seconds 60
```

Use `--skip-failed` only for exploratory runs. It records skipped participants in `*_failed_subjects.csv` and `*_failed_subjects.json`; those outputs are incomplete until the failed participants are rerun.

## Recreate derived files

```bash
make statistical-reports
make mixed-model-diagnostics
make compare-physionet-pipelines
make methods-figures
```

`make publication-check` runs syntax checks, tests, result validation, report regeneration, and the archive audit. `make release-archive` builds the configured release ZIP.

## Manuscript

With `latexmk` or `pdflatex` installed:

```bash
make manuscript
```

The generated PDF is written to `manuscript/manuscript.pdf`.
