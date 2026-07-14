# Publication-readiness update

This update adds a reviewer-facing publication pack for completed benchmark runs. The goal is to move the repository closer to a methods paper submission by making the inferential outputs explicit, reproducible, and easy to quote in a manuscript.

## New entry point

```bash
python scripts/publication_readiness_pack.py   --results-dir results   --reports-dir reports   --prefix PhysionetMI_PhysionetMI_all_riemann_lr
```

The script consumes `{prefix}_subject_summary.csv` only. It does not create, simulate, bootstrap-resample, or impute benchmark observations.

## Outputs

For prefix `PhysionetMI_PhysionetMI_all_riemann_lr`, the script writes:

- `results/{prefix}_publication_methods_audit.csv`: row counts, subject counts, missingness, duplicate subject-condition checks, and metric range checks.
- `results/{prefix}_publication_paired_effects.csv`: within-subject paired condition effects against the clean all-channel baseline for ROC AUC, balanced accuracy, Brier score, and expected calibration error.
- `results/{prefix}_publication_channel_dropout_subject_slopes.csv`: subject-level linear slopes across clean and channel-dropout fractions.
- `results/{prefix}_publication_channel_dropout_slope_summary.csv`: population mean slope per 10% channel dropout with t confidence intervals and normality screening.
- `results/{prefix}_publication_manuscript_table.csv`: compact manuscript-ready table for ROC AUC and balanced accuracy.
- `reports/{prefix}_publication_manuscript_table.tex`: LaTeX version of the manuscript table.
- `reports/{prefix}_publication_readiness_summary.md`: Markdown summary for drafting the Methods/Results text.
- `results/{prefix}_publication_manifest.json`: source and output manifest.

## Statistical conventions

- All stressor comparisons are paired within subject against the clean all-channel baseline.
- Mean paired deltas and channel-dropout slopes use Student t confidence intervals.
- Shapiro-Wilk tests screen normality of paired deltas/slopes.
- Wilcoxon signed-rank tests are reported as non-parametric sensitivity checks.
- Benjamini-Hochberg false discovery rate correction is applied across paired p-values.

## Why this helps a Journal of Neuroscience Methods submission

A methods journal reviewer will usually ask whether the benchmark is reproducible, whether intervention effects are paired at the subject level, whether uncertainty is reported, and whether data-completeness checks are explicit. This update adds those artifacts as first-class outputs rather than leaving them only in notebooks or ad hoc analysis notes.
