# Statistical reporting

Population inference is based on participant-level summaries. Fold and dropout-repeat measurements are averaged within each participant and condition before confidence intervals or hypothesis tests are calculated.

## Recreate the reports

```bash
make validate-results
make statistical-reports
make compare-physionet-pipelines
make mixed-model-diagnostics
```

The scripts read `results/*_subject_summary.csv`. They do not download EEG data or create additional benchmark observations. Numerical outputs remain in `results/`; formatted tables and figures are written to the selected reports directory. The main generated files are paired-effects tables, compact statistical tables, mixed-model coefficients and diagnostics, and the paired PhysioNet decoder comparison.

## Statistical conventions

Each available stressor is compared with the same participant's clean all-channel result. The reported analyses include mean paired differences with two-sided 95% Student t confidence intervals, paired t tests, Cohen's $d_z$, Wilcoxon signed-rank sensitivity tests and exact sign tests. Benjamini–Hochberg false-discovery-rate correction is applied within each stated test family. Shapiro–Wilk tests describe the distribution of paired differences.

Population condition means use bias-corrected and accelerated bootstrap intervals with 2,000 resamples and seed 42.

Two maximum-likelihood mixed-effects models with participant random intercepts are secondary analyses. One treats condition as categorical, with clean data as the reference. The other estimates a linear slope over clean and random-dropout conditions. Fixed-effect coefficients use 95% Wald intervals. Residual normality, constant variance and linear dose response are checked before interpretation. These assumptions failed for parts of the reported analysis, so the mixed-model slope is descriptive rather than the primary evidence.

For the direct PhysioNet comparison, decoders are matched by participant and condition. The principal contrast is CSP–LDA ROC-AUC minus Riemannian logistic-regression ROC-AUC. A second, exploratory contrast compares each decoder's change from its own clean baseline.

## Validation scope

`validate_results.py` checks required columns, metric ranges, duplicate evaluation keys, channel counts, paired clean baselines and agreement between fold-level and participant-level means. It does not establish that the corruption model represents physical electrode failure, that model assumptions hold, or that a result generalizes to online BCI use.
