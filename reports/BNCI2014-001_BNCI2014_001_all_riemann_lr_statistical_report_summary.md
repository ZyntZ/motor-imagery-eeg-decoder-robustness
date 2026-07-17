# Statistical reporting pack for `BNCI2014-001_BNCI2014_001_all_riemann_lr`

Generated from existing subject-summary CSV files only; no simulated or additional benchmark observations are used.

## Methods audit
| check | value | status |
| --- | --- | --- |
| n_rows_subject_summary | 90 | info |
| n_subjects | 9 | info |
| n_conditions | 10 | info |
| duplicate_subject_condition_rows | 0 | pass |
| missing_roc_auc | 0 | pass |
| out_of_range_0_1_roc_auc | 0 | pass |
| missing_balanced_accuracy | 0 | pass |
| out_of_range_0_1_balanced_accuracy | 0 | pass |
| missing_brier_score | 0 | pass |
| out_of_range_0_1_brier_score | 0 | pass |
| missing_ece | 0 | pass |
| out_of_range_0_1_ece | 0 | pass |
| min_subjects_per_condition | 9 | pass |
| max_subjects_per_condition | 9 | info |

## Paired stressor effects vs clean all-channel baseline
| condition | metric | metric_role | n_subjects | clean_mean | condition_mean | mean_delta_condition_minus_clean | delta_ci_low | delta_ci_high | median_delta_condition_minus_clean | cohens_dz | t_p_value_bh_fdr | wilcoxon_p_value_bh_fdr | sign_test_p_value_bh_fdr | shapiro_p_value_delta | pct_worse_than_clean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| channel_dropout_0.1 | balanced_accuracy | secondary | 9 | 0.8218 | 0.6236 | -0.1982 | -0.2421 | -0.1543 | -0.2063 | -3.47 | 2.058e-05 | 0.004849 | 0.004849 | 0.472 | 1 |
| channel_dropout_0.2 | balanced_accuracy | secondary | 9 | 0.8218 | 0.5632 | -0.2586 | -0.326 | -0.1912 | -0.2897 | -2.949 | 6.311e-05 | 0.004849 | 0.004849 | 0.1114 | 1 |
| channel_dropout_0.3 | balanced_accuracy | secondary | 9 | 0.8218 | 0.5388 | -0.2829 | -0.3603 | -0.2056 | -0.2937 | -2.811 | 7.475e-05 | 0.004849 | 0.004849 | 0.2837 | 1 |
| channel_dropout_0.5 | balanced_accuracy | secondary | 9 | 0.8218 | 0.5183 | -0.3035 | -0.3915 | -0.2155 | -0.32 | -2.651 | 0.0001025 | 0.004849 | 0.004849 | 0.5087 | 1 |
| cross_session_0 | balanced_accuracy | secondary | 9 | 0.8218 | 0.7716 | -0.05018 | -0.1246 | 0.02424 | -0.01046 | -0.5183 | 0.1784 | 0.04395 | 0.2021 | 0.0002503 | 0.7778 |
| reduced_montage_motor_core | balanced_accuracy | secondary | 9 | 0.8218 | 0.7077 | -0.1141 | -0.1578 | -0.07042 | -0.1005 | -2.007 | 0.000541 | 0.004849 | 0.004849 | 0.001824 | 1 |
| reduced_montage_motor_extended | balanced_accuracy | secondary | 9 | 0.8218 | 0.7642 | -0.05758 | -0.09105 | -0.02411 | -0.05234 | -1.322 | 0.005511 | 0.004849 | 0.004849 | 0.4114 | 1 |
| region_dropout_0.136364 | balanced_accuracy | secondary | 9 | 0.8218 | 0.6231 | -0.1987 | -0.2692 | -0.1282 | -0.167 | -2.167 | 0.0003756 | 0.004849 | 0.004849 | 0.1567 | 1 |
| region_dropout_0.318182 | balanced_accuracy | secondary | 9 | 0.8218 | 0.5032 | -0.3186 | -0.4184 | -0.2188 | -0.3594 | -2.453 | 0.0001677 | 0.004849 | 0.004849 | 0.4123 | 1 |
| channel_dropout_0.1 | roc_auc | primary | 9 | 0.8776 | 0.8515 | -0.02613 | -0.04079 | -0.01148 | -0.01952 | -1.371 | 0.004677 | 0.004849 | 0.004849 | 0.4034 | 1 |
| channel_dropout_0.2 | roc_auc | primary | 9 | 0.8776 | 0.82 | -0.05761 | -0.08422 | -0.03101 | -0.04439 | -1.665 | 0.001592 | 0.004849 | 0.004849 | 0.2082 | 1 |
| channel_dropout_0.3 | roc_auc | primary | 9 | 0.8776 | 0.7739 | -0.1037 | -0.1426 | -0.06486 | -0.1 | -2.051 | 0.0004908 | 0.004849 | 0.004849 | 0.4651 | 1 |
| channel_dropout_0.5 | roc_auc | primary | 9 | 0.8776 | 0.7211 | -0.1565 | -0.1996 | -0.1135 | -0.1412 | -2.794 | 7.475e-05 | 0.004849 | 0.004849 | 0.7139 | 1 |
| cross_session_0 | roc_auc | primary | 9 | 0.8776 | 0.8703 | -0.007336 | -0.02189 | 0.007213 | -0.003202 | -0.3876 | 0.3037 | 0.392 | 1 | 0.4849 | 0.5556 |
| reduced_montage_motor_core | roc_auc | primary | 9 | 0.8776 | 0.7669 | -0.1107 | -0.163 | -0.05832 | -0.1212 | -1.625 | 0.001775 | 0.004849 | 0.004849 | 0.5625 | 1 |
| reduced_montage_motor_extended | roc_auc | primary | 9 | 0.8776 | 0.8282 | -0.04941 | -0.08669 | -0.01213 | -0.03006 | -1.019 | 0.01946 | 0.004849 | 0.004849 | 0.1249 | 1 |
| region_dropout_0.136364 | roc_auc | primary | 9 | 0.8776 | 0.8561 | -0.02148 | -0.04415 | 0.001188 | -0.01216 | -0.7284 | 0.07245 | 0.03175 | 0.04536 | 0.02528 | 0.8889 |
| region_dropout_0.318182 | roc_auc | primary | 9 | 0.8776 | 0.7462 | -0.1314 | -0.1538 | -0.109 | -0.1398 | -4.503 | 3.463e-06 | 0.004849 | 0.004849 | 0.4488 | 1 |

## Sensitivity summary
| condition | metric | available | role | n_subjects | mean_delta_condition_minus_clean | pct_worse_than_clean | ttest_fdr | wilcoxon_fdr | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| channel_dropout_0.1 | roc_auc | True | primary | 9 | -0.02613 | 1 | 0.004677 | 0.004849 | primary |
| channel_dropout_0.1 | balanced_accuracy | True | secondary | 9 | -0.1982 | 1 | 2.058e-05 | 0.004849 | secondary |
| channel_dropout_0.1 | brier_score | True | calibration | 9 | 0.1689 | 1 | 1.203e-06 | 0.004849 | calibration_optional |
| channel_dropout_0.1 | ece | True | calibration | 9 | 0.1989 | 1 | 1.203e-06 | 0.004849 | calibration_optional |
| channel_dropout_0.2 | roc_auc | True | primary | 9 | -0.05761 | 1 | 0.001592 | 0.004849 | primary |
| channel_dropout_0.2 | balanced_accuracy | True | secondary | 9 | -0.2586 | 1 | 6.311e-05 | 0.004849 | secondary |
| channel_dropout_0.2 | brier_score | True | calibration | 9 | 0.2365 | 1 | 5.561e-06 | 0.004849 | calibration_optional |
| channel_dropout_0.2 | ece | True | calibration | 9 | 0.2566 | 1 | 1.203e-06 | 0.004849 | calibration_optional |
| channel_dropout_0.3 | roc_auc | True | primary | 9 | -0.1037 | 1 | 0.0004908 | 0.004849 | primary |
| channel_dropout_0.3 | balanced_accuracy | True | secondary | 9 | -0.2829 | 1 | 7.475e-05 | 0.004849 | secondary |
| channel_dropout_0.3 | brier_score | True | calibration | 9 | 0.2633 | 1 | 2.445e-06 | 0.004849 | calibration_optional |
| channel_dropout_0.3 | ece | True | calibration | 9 | 0.2789 | 1 | 2.12e-08 | 0.004849 | calibration_optional |
| channel_dropout_0.5 | roc_auc | True | primary | 9 | -0.1565 | 1 | 7.475e-05 | 0.004849 | primary |
| channel_dropout_0.5 | balanced_accuracy | True | secondary | 9 | -0.3035 | 1 | 0.0001025 | 0.004849 | secondary |
| channel_dropout_0.5 | brier_score | True | calibration | 9 | 0.2892 | 1 | 3.463e-06 | 0.004849 | calibration_optional |
| channel_dropout_0.5 | ece | True | calibration | 9 | 0.2923 | 1 | 2.12e-08 | 0.004849 | calibration_optional |
| cross_session_0 | roc_auc | True | primary | 9 | -0.007336 | 0.5556 | 0.3037 | 0.392 | primary |
| cross_session_0 | balanced_accuracy | True | secondary | 9 | -0.05018 | 0.7778 | 0.1784 | 0.04395 | secondary |
| cross_session_0 | brier_score | True | calibration | 9 | 0.02311 | 0.8889 | 0.09362 | 0.01406 | calibration_optional |
| cross_session_0 | ece | True | calibration | 9 | 0.01274 | 0.5556 | 0.4311 | 0.5866 | calibration_optional |
| reduced_montage_motor_core | roc_auc | True | primary | 9 | -0.1107 | 1 | 0.001775 | 0.004849 | primary |
| reduced_montage_motor_core | balanced_accuracy | True | secondary | 9 | -0.1141 | 1 | 0.000541 | 0.004849 | secondary |
| reduced_montage_motor_core | brier_score | True | calibration | 9 | 0.05812 | 1 | 0.0006927 | 0.004849 | calibration_optional |
| reduced_montage_motor_core | ece | True | calibration | 9 | 0.004714 | 0.6667 | 0.773 | 0.7344 | calibration_optional |
| reduced_montage_motor_extended | roc_auc | True | primary | 9 | -0.04941 | 1 | 0.01946 | 0.004849 | primary |
| reduced_montage_motor_extended | balanced_accuracy | True | secondary | 9 | -0.05758 | 1 | 0.005511 | 0.004849 | secondary |
| reduced_montage_motor_extended | brier_score | True | calibration | 9 | 0.02358 | 1 | 0.01339 | 0.004849 | calibration_optional |
| reduced_montage_motor_extended | ece | True | calibration | 9 | 0.004639 | 0.6667 | 0.5742 | 0.4508 | calibration_optional |
| region_dropout_0.136364 | roc_auc | True | primary | 9 | -0.02148 | 0.8889 | 0.07245 | 0.03175 | primary |
| region_dropout_0.136364 | balanced_accuracy | True | secondary | 9 | -0.1987 | 1 | 0.0003756 | 0.004849 | secondary |
| region_dropout_0.136364 | brier_score | True | calibration | 9 | 0.1803 | 1 | 0.0006927 | 0.004849 | calibration_optional |
| region_dropout_0.136364 | ece | True | calibration | 9 | 0.2177 | 1 | 0.0004156 | 0.004849 | calibration_optional |
| region_dropout_0.318182 | roc_auc | True | primary | 9 | -0.1314 | 1 | 3.463e-06 | 0.004849 | primary |
| region_dropout_0.318182 | balanced_accuracy | True | secondary | 9 | -0.3186 | 1 | 0.0001677 | 0.004849 | secondary |
| region_dropout_0.318182 | brier_score | True | calibration | 9 | 0.333 | 1 | 7.475e-05 | 0.004849 | calibration_optional |
| region_dropout_0.318182 | ece | True | calibration | 9 | 0.3351 | 1 | 3.463e-06 | 0.004849 | calibration_optional |

## Channel-dropout slopes
| dataset | pipeline | metric | n_subjects | mean_slope_per_10pct_dropout | slope_ci_low | slope_ci_high | slope_sd | t_statistic_vs_zero | t_p_value_vs_zero | shapiro_p_value_slope | n_harmful_slope | pct_harmful_slope | t_p_value_vs_zero_bh_fdr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BNCI2014-001 | riemann_lr | balanced_accuracy | 9 | -0.05314 | -0.07036 | -0.03592 | 0.0224 | -7.118 | 0.0001002 | 0.7918 | 9 | 1 | 0.0001002 |
| BNCI2014-001 | riemann_lr | brier_score | 9 | 0.05206 | 0.04158 | 0.06253 | 0.01363 | 11.46 | 3.042e-06 | 0.58 | 9 | 1 | 6.085e-06 |
| BNCI2014-001 | riemann_lr | ece | 9 | 0.05077 | 0.04568 | 0.05586 | 0.006621 | 23.01 | 1.352e-08 | 0.1814 | 9 | 1 | 5.406e-08 |
| BNCI2014-001 | riemann_lr | roc_auc | 9 | -0.03232 | -0.04127 | -0.02337 | 0.01164 | -8.328 | 3.267e-05 | 0.6985 | 9 | 1 | 4.356e-05 |

## Overclaim-risk flags
| flag | triggered | detail |
| --- | --- | --- |
| low_subject_count | True | n_subjects=9; population-level claims should be cautious below 20 subjects. |
| development_subset_prefix | False | Prefix contains 'dev'; treat as development output, not final population estimate. |
| missing_calibration_metrics | False | Missing optional calibration metrics: none |
| cross_session_absent | False | Cross-session stressor present. |
| skipped_subject_log_present | False | Found 0 failed-subject log files matching prefix. |
| uneven_or_low_paired_n | False | minimum paired n=9; total subject n=9. |

## Statistical notes
- Paired effects are computed within subject against the clean all-channel baseline.
- Confidence intervals for mean paired deltas and slopes use Student t intervals.
- Median-delta intervals use a distribution-free sign-test/order-statistic interval.
- Normality of paired deltas/slopes is screened with Shapiro-Wilk where sample size permits.
- Wilcoxon signed-rank and sign tests are reported as sensitivity checks for paired deltas.
- Benjamini-Hochberg false discovery rate correction is applied to paired t-test, Wilcoxon, and sign-test p-values.