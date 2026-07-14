# Statistical reporting workflow

This repository includes a reporting script that converts completed benchmark summaries into tables suitable for methods and results sections. The script reads existing `{prefix}_subject_summary.csv` files and writes derived quality-control and inferential summaries. It does not download data or add benchmark observations.

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

## Statistical conventions

- Stressor comparisons are paired within subject against the clean all-channel baseline.
- Mean paired deltas and channel-dropout slopes use Student t confidence intervals.
- Shapiro-Wilk tests screen normality of paired deltas and slopes when sample size permits.
- Wilcoxon signed-rank tests are reported as non-parametric sensitivity checks.
- Benjamini-Hochberg false discovery rate correction is applied across paired p-values.

## Commit hygiene

Generated report files are reproducible from the CSV summaries and can be regenerated with the command above. Keep source scripts, tests, configuration, and selected reference CSV outputs under version control; keep local caches, checkpoints, bytecode, and one-off dashboards out of commits.
