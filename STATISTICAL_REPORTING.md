# Statistical reporting workflow

This repository includes a reporting script that converts completed benchmark summaries into tables suitable for methods and results sections. The script reads existing `{prefix}_subject_summary.csv` files and writes derived quality-control and inferential summaries. It does not download data or add benchmark observations.

## Pre-report validation

Run validation before statistical reporting so schema and aggregation problems are caught before manuscript tables are produced:

```bash
python scripts/validate_results.py \
  --results-dir results \
  --reports-dir reports \
  --prefix PhysionetMI_dev10 \
  --allow-warnings
```

The validator writes `reports/{prefix}_validation_checks.csv` and `reports/{prefix}_validation_summary.json`. It fails on missing required columns, impossible metric values, duplicate evaluation keys, invalid channel counts, missing clean baselines for paired stressor rows, or mismatches between `{prefix}_results.csv` fold means and `{prefix}_subject_summary.csv`. Warnings cover optional metric absence and dropout-fraction inconsistencies that may need manual review.

## Command

```bash
python scripts/generate_statistical_report.py \
  --results-dir results \
  --reports-dir reports \
  --prefix PhysionetMI_PhysionetMI_all_riemann_lr
```

## Outputs

For a prefix such as `PhysionetMI_PhysionetMI_all_riemann_lr`, the script writes:

- `results/{prefix}_statistical_methods_audit.csv`: row counts, subject counts, duplicate subject-condition checks, missingness, and metric range checks.
- `results/{prefix}_statistical_paired_effects.csv`: within-subject paired effects against the clean all-channel baseline for ROC AUC, balanced accuracy, Brier score, and expected calibration error.
- `results/{prefix}_statistical_channel_dropout_subject_slopes.csv`: subject-level linear slopes across clean and channel-dropout fractions.
- `results/{prefix}_statistical_channel_dropout_slope_summary.csv`: population mean slope per 10% channel dropout with confidence intervals and assumption checks.
- `results/{prefix}_statistical_report_table.csv`: compact table for ROC AUC and balanced accuracy.
- `reports/{prefix}_statistical_report_table.tex`: LaTeX version of the compact table.
- `reports/{prefix}_statistical_report_summary.md`: Markdown summary of audit, paired effects, and channel-dropout slopes.
- `results/{prefix}_statistical_report_manifest.json`: source and output manifest.



## Extended interpretation outputs

The reporting script now writes additional publication-facing tables derived from the same subject-summary CSV:

- `results/{prefix}_statistical_effect_size_interpretation.csv`: mean and median paired deltas, median confidence intervals, Cohen's dz magnitude labels, sign-test results, and per-condition worsening/improvement counts.
- `results/{prefix}_statistical_sensitivity_summary.csv`: primary ROC AUC, secondary balanced accuracy, and optional calibration-metric availability by condition.
- `results/{prefix}_statistical_overclaim_flags.csv`: flags for low subject count, development-subset prefixes, missing calibration metrics, absent cross-session stressors, failed-subject logs, and uneven paired sample sizes.

These files do not add observations. They summarize existing subject-level result rows and are intended to make limitations visible before manuscript drafting.

## Statistical conventions

- Stressor comparisons are paired within subject against the clean all-channel baseline.
- Mean paired deltas and channel-dropout slopes use Student t confidence intervals.
- Shapiro-Wilk tests screen normality of paired deltas and slopes when sample size permits.
- Wilcoxon signed-rank tests are reported as non-parametric sensitivity checks.
- Benjamini-Hochberg false discovery rate correction is applied across paired p-values.

## Commit hygiene

Generated report files are reproducible from the CSV summaries and can be regenerated with the command above. Keep source scripts, tests, configuration, and selected reference CSV outputs under version control; keep local caches, checkpoints, bytecode, and one-off dashboards out of commits.


## Figure outputs

`scripts/generate_methods_figures.py` creates three methods-paper figures from existing CSV results: a pipeline schematic, a paired channel-dropout degradation plot, and intervention/risk-class counts. The bar chart is descriptive only and must not be interpreted causally.
