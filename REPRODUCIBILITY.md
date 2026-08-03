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

These checks cover imports, syntax, unit-level behavior, and internal consistency of the committed tables. They do not regenerate fold-level measurements from raw EEG. To verify the committed outputs against the committed code, run the complete benchmark from a clean checkout and compare the regenerated tables.

## Full benchmark

```bash
make bnci-full
make physionet-full
```

The commands download data through MOABB/MNE, fit both decoder pipelines using participant-specific dropout masks, and regenerate their derived summaries and reports. Use `make bnci-fit` or `make physionet-fit` only when model fitting is required without postprocessing. Runtime depends on the local data cache and hardware. Use `make legacy-bnci-full` or `make legacy-physionet-full` only when reproducing earlier shared-mask tables.

Long runs write participant checkpoints to `results/checkpoints/`. Checkpoint names include the dataset, pipeline, and run suffix. Repeating the same command reuses only checkpoints with the current protocol marker and requested stressors. For unstable network connections, increase the retry count and waiting time, for example:

```bash
python scripts/run_benchmark.py   --config configs/benchmark.yaml   --download-and-run   --dataset PhysionetMI   --subjects 29   --include-reduced-montage   --include-region-dropout   --pipeline csp_lda   --max-retries 5   --retry-wait-seconds 60
```

Checkpoint reuse also checks `mask_seed_scope`, so a participant-specific run cannot reuse a legacy shared-mask checkpoint. Keep separate result directories for each protocol variant.

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

The current PhysioNet tables use `configs/benchmark_independent_masks.yaml`; it derives deterministic masks from participant identity, fold, repeat, fraction, and the global seed. Decoder families receive matched masks for the same participant. `configs/benchmark.yaml` retains the earlier shared-mask schedule only for exact legacy reproduction. The current PhysioNet and BNCI fold-level outputs record protocol 0.3.2 provenance and participant-specific mask scope.

Participant checkpoints include a run signature over all observation-generating settings. A checkpoint with a different or missing signature is recomputed.
