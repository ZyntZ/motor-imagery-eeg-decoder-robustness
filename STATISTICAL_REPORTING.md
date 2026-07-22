# Statistical reporting specification

This document defines the inferential unit, estimands, uncertainty measures, and multiplicity handling used by the committed benchmark analyses. It is a reporting specification for existing observations, not a preregistration.

## Analysis unit and outcomes

The participant is the independent population-level analysis unit. Fold and channel-mask repeat rows are averaged within each participant and condition before inference; folds and repeats are not counted as independent observations.

The primary outcome is receiver operating characteristic area under the curve (ROC-AUC). Balanced accuracy is secondary. Brier score and 10-bin equal-width expected calibration error are calibration outcomes when predicted probabilities are available. Higher ROC-AUC and balanced accuracy are better; lower Brier score and expected calibration error are better.

## Estimands

Within each dataset and decoder, a stressor effect is the paired participant-level difference

`condition metric - clean all-channel metric`.

For direct PhysioNet decoder comparisons, the difference is

`CSP-LDA ROC-AUC - Riemann-LR ROC-AUC`;

negative values favor Riemann-LR. The exploratory difference-in-degradation contrast subtracts the clean decoder difference from the corresponding stressed-condition decoder difference.

Reduced-montage analyses compare models retrained and tested on the stated montage with the clean all-channel model. They do not estimate the effect of unexpected electrode failure. No equivalence or non-inferiority margin was prespecified, so a confidence interval containing zero is not evidence of equivalence.

## Estimates and uncertainty

Population condition means use participant-level bias-corrected and accelerated bootstrap 95% confidence intervals with a fixed seed. Paired changes use two-sided 95% Student t confidence intervals for the mean difference. Reports also include Cohen's paired-sample effect size, `d_z = mean(difference) / SD(difference)`.

For each paired comparison, the analysis reports a paired t test, Wilcoxon signed-rank sensitivity test, exact sign test, and Shapiro-Wilk descriptive normality test when sample size permits. A distribution-free order-statistic interval is reported for the median paired difference. Exact Clopper-Pearson intervals are used for binomial proportions. All tests are two-sided unless a generated table explicitly states otherwise.

## Multiplicity and decision rule

Benjamini-Hochberg false-discovery-rate adjustment is applied separately within each generated test family across the available conditions. Adjusted p-values are reported alongside effect estimates and confidence intervals. The conventional threshold `alpha = 0.05` is used as a descriptive decision threshold; interpretation does not rely on the threshold alone. Primary, secondary, calibration, and exploratory results remain labelled as such.

## Assumptions and sensitivity analyses

The paired analyses assume independent participants and correct within-participant matching. The paired t procedure assumes that participant-level differences are approximately normally distributed; Shapiro-Wilk results and Wilcoxon/sign-test analyses are supplied as sensitivity checks. The Wilcoxon test concerns a symmetric distribution of paired differences, while the sign test avoids that symmetry assumption but has lower power. Homoscedasticity is not required for a one-sample analysis of paired differences.

Mixed-effects models use a participant random intercept and maximum-likelihood estimation. The categorical model compares conditions with clean data. The continuous dose model is restricted to clean and random channel dropout, where dropout fraction has a consistent interpretation. Convergence, boundary variance, residual normality, heteroscedasticity, nonlinear dose response, functional form, and leave-one-participant-out influence are checked. When diagnostics fail, mixed-model estimates are treated as descriptive secondary evidence rather than the sole inferential basis.

## Missingness and exclusions

Comparisons use complete participant pairs for the relevant condition and outcome. No missing values are imputed. Each output reports its paired sample size. Failed-subject logs and discrepancies between expected and observed participant counts are release-readiness failures or warnings, as implemented in `scripts/generate_submission_readiness.py` and `scripts/validate_results.py`.

## Reproducibility boundary

The committed manuscript results use `configs/benchmark.yaml`, the legacy fixed cross-validation split and deterministic channel-mask schedule. Because participant identity was not included in that schedule, matching fold/repeat indices can reuse channel indices across participants. Confidence intervals quantify participant variation conditional on this one schedule; they do not include variation across alternative splits or mask schedules. `configs/benchmark_independent_masks.yaml` is recommended for future inference, but its results must not be combined with the committed legacy outputs.

The statistical implementations are in `scripts/final_statistics.py`, `scripts/generate_statistical_report.py`, `scripts/compare_physionet_pipelines.py`, and `scripts/mixed_model_diagnostics.py`. Generated tables record test statistics, sample sizes, confidence limits, effect sizes, raw p-values, and adjusted p-values where applicable.
