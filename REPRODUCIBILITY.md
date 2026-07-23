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
python scripts/run_benchmark.py --config configs/benchmark_independent_masks.yaml --dry-run
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

The commands download data through MOABB/MNE, preprocess the recordings and fit both decoder pipelines using participant-specific dropout masks. Runtime depends on the local data cache and hardware. Use `make legacy-bnci-full` or `make legacy-physionet-full` only when reproducing the committed v0.3 tables.

Long runs write participant checkpoints to `results/checkpoints/`. Checkpoint names include the dataset, pipeline, and run suffix. Repeating the same command reuses only checkpoints with the current protocol marker and requested stressors. For unstable network connections, increase the retry count and waiting time, for example:

```bash
python scripts/run_benchmark.py   --config configs/benchmark.yaml   --download-and-run   --dataset PhysionetMI   --subjects 29   --include-reduced-montage   --include-region-dropout   --pipeline csp_lda   --max-retries 5   --retry-wait-seconds 60
```

Checkpoint reuse is also gated on `mask_seed_scope`, so a participant-specific run cannot silently reuse legacy shared-mask checkpoints. Use separate result directories for protocol variants.

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

## Perturbation schedules

The committed tables were generated with `configs/benchmark.yaml`, in which matched fold/repeat indices reuse channel indices across participants when channel order agrees. This is retained only for exact legacy reproduction. New studies should use `configs/benchmark_independent_masks.yaml`; it derives deterministic masks from participant identity, fold, repeat, fraction, and the global seed. Decoder families still receive matched masks for the same participant. A full independent-mask rerun is required before replacing the committed numerical results.
