# Statistical reporting pack for `BNCI2014-001_BNCI2014_001_all_csp_lda`

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
| channel_dropout_0.1 | balanced_accuracy | secondary | 9 | 0.7913 | 0.5449 | -0.2465 | -0.3452 | -0.1477 | -0.2631 | -1.919 | 0.0006974 | 0.005409 | 0.005409 | 0.8136 | 1 |
| channel_dropout_0.2 | balanced_accuracy | secondary | 9 | 0.7913 | 0.5297 | -0.2616 | -0.3568 | -0.1664 | -0.2869 | -2.111 | 0.000449 | 0.005409 | 0.005409 | 0.2975 | 1 |
| channel_dropout_0.3 | balanced_accuracy | secondary | 9 | 0.7913 | 0.5187 | -0.2727 | -0.3739 | -0.1714 | -0.3128 | -2.07 | 0.0004613 | 0.005409 | 0.005409 | 0.2941 | 1 |
| channel_dropout_0.5 | balanced_accuracy | secondary | 9 | 0.7913 | 0.5124 | -0.2789 | -0.3822 | -0.1757 | -0.3232 | -2.078 | 0.0004613 | 0.005409 | 0.005409 | 0.325 | 1 |
| cross_session_0 | balanced_accuracy | secondary | 9 | 0.7913 | 0.7569 | -0.03437 | -0.08149 | 0.01276 | -0.02443 | -0.5606 | 0.1431 | 0.08097 | 0.04395 | 0.2125 | 0.8889 |
| reduced_montage_motor_core | balanced_accuracy | secondary | 9 | 0.7913 | 0.7005 | -0.09076 | -0.1356 | -0.04596 | -0.08325 | -1.557 | 0.002398 | 0.005409 | 0.005409 | 0.3497 | 1 |
| reduced_montage_motor_extended | balanced_accuracy | secondary | 9 | 0.7913 | 0.7453 | -0.046 | -0.08313 | -0.008875 | -0.03116 | -0.9524 | 0.02731 | 0.01406 | 0.04395 | 0.2911 | 0.8889 |
| region_dropout_0.136364 | balanced_accuracy | secondary | 9 | 0.7913 | 0.5868 | -0.2045 | -0.2816 | -0.1274 | -0.2298 | -2.039 | 0.0004865 | 0.005409 | 0.005409 | 0.2039 | 1 |
| region_dropout_0.318182 | balanced_accuracy | secondary | 9 | 0.7913 | 0.524 | -0.2673 | -0.3785 | -0.1562 | -0.2713 | -1.849 | 0.000849 | 0.005409 | 0.005409 | 0.6835 | 1 |
| channel_dropout_0.1 | roc_auc | primary | 9 | 0.8523 | 0.7365 | -0.1158 | -0.1456 | -0.08603 | -0.113 | -2.987 | 4.59e-05 | 0.005409 | 0.005409 | 0.2727 | 1 |
| channel_dropout_0.2 | roc_auc | primary | 9 | 0.8523 | 0.6912 | -0.1611 | -0.2016 | -0.1207 | -0.187 | -3.062 | 4.098e-05 | 0.005409 | 0.005409 | 0.1385 | 1 |
| channel_dropout_0.3 | roc_auc | primary | 9 | 0.8523 | 0.6412 | -0.2112 | -0.2615 | -0.1608 | -0.2422 | -3.222 | 3.574e-05 | 0.005409 | 0.005409 | 0.1164 | 1 |
| channel_dropout_0.5 | roc_auc | primary | 9 | 0.8523 | 0.6165 | -0.2359 | -0.2932 | -0.1785 | -0.2603 | -3.16 | 3.786e-05 | 0.005409 | 0.005409 | 0.09309 | 1 |
| cross_session_0 | roc_auc | primary | 9 | 0.8523 | 0.853 | 0.0006408 | -0.02137 | 0.02265 | 0.003312 | 0.02238 | 0.9752 | 1 | 1 | 0.5986 | 0.4444 |
| reduced_montage_motor_core | roc_auc | primary | 9 | 0.8523 | 0.7545 | -0.09781 | -0.1492 | -0.04642 | -0.08317 | -1.463 | 0.003214 | 0.005409 | 0.005409 | 0.256 | 1 |
| reduced_montage_motor_extended | roc_auc | primary | 9 | 0.8523 | 0.8014 | -0.05095 | -0.098 | -0.003909 | -0.0342 | -0.8325 | 0.04449 | 0.01406 | 0.04395 | 0.09048 | 0.8889 |
| region_dropout_0.136364 | roc_auc | primary | 9 | 0.8523 | 0.7656 | -0.08678 | -0.13 | -0.0435 | -0.06006 | -1.541 | 0.00245 | 0.005409 | 0.005409 | 0.3637 | 1 |
| region_dropout_0.318182 | roc_auc | primary | 9 | 0.8523 | 0.6886 | -0.1638 | -0.202 | -0.1255 | -0.1702 | -3.293 | 3.574e-05 | 0.005409 | 0.005409 | 0.8925 | 1 |

## Sensitivity summary
| condition | metric | available | role | n_subjects | mean_delta_condition_minus_clean | pct_worse_than_clean | ttest_fdr | wilcoxon_fdr | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| channel_dropout_0.1 | roc_auc | True | primary | 9 | -0.1158 | 1 | 4.59e-05 | 0.005409 | primary |
| channel_dropout_0.1 | balanced_accuracy | True | secondary | 9 | -0.2465 | 1 | 0.0006974 | 0.005409 | secondary |
| channel_dropout_0.1 | brier_score | True | calibration | 9 | 0.2819 | 1 | 3.926e-05 | 0.005409 | calibration_optional |
| channel_dropout_0.1 | ece | True | calibration | 9 | 0.3008 | 1 | 1.005e-05 | 0.005409 | calibration_optional |
| channel_dropout_0.2 | roc_auc | True | primary | 9 | -0.1611 | 1 | 4.098e-05 | 0.005409 | primary |
| channel_dropout_0.2 | balanced_accuracy | True | secondary | 9 | -0.2616 | 1 | 0.000449 | 0.005409 | secondary |
| channel_dropout_0.2 | brier_score | True | calibration | 9 | 0.3039 | 1 | 7.951e-06 | 0.005409 | calibration_optional |
| channel_dropout_0.2 | ece | True | calibration | 9 | 0.3212 | 1 | 6.095e-07 | 0.005409 | calibration_optional |
| channel_dropout_0.3 | roc_auc | True | primary | 9 | -0.2112 | 1 | 3.574e-05 | 0.005409 | primary |
| channel_dropout_0.3 | balanced_accuracy | True | secondary | 9 | -0.2727 | 1 | 0.0004613 | 0.005409 | secondary |
| channel_dropout_0.3 | brier_score | True | calibration | 9 | 0.3135 | 1 | 1.156e-05 | 0.005409 | calibration_optional |
| channel_dropout_0.3 | ece | True | calibration | 9 | 0.3266 | 1 | 8.743e-07 | 0.005409 | calibration_optional |
| channel_dropout_0.5 | roc_auc | True | primary | 9 | -0.2359 | 1 | 3.786e-05 | 0.005409 | primary |
| channel_dropout_0.5 | balanced_accuracy | True | secondary | 9 | -0.2789 | 1 | 0.0004613 | 0.005409 | secondary |
| channel_dropout_0.5 | brier_score | True | calibration | 9 | 0.3228 | 1 | 1.156e-05 | 0.005409 | calibration_optional |
| channel_dropout_0.5 | ece | True | calibration | 9 | 0.3386 | 1 | 8.743e-07 | 0.005409 | calibration_optional |
| cross_session_0 | roc_auc | True | primary | 9 | 0.0006408 | 0.4444 | 0.9752 | 1 | primary |
| cross_session_0 | balanced_accuracy | True | secondary | 9 | -0.03437 | 0.8889 | 0.1431 | 0.08097 | secondary |
| cross_session_0 | brier_score | True | calibration | 9 | 0.03011 | 0.8889 | 0.05711 | 0.06152 | calibration_optional |
| cross_session_0 | ece | True | calibration | 9 | 0.04108 | 0.6667 | 0.02972 | 0.06152 | calibration_optional |
| reduced_montage_motor_core | roc_auc | True | primary | 9 | -0.09781 | 1 | 0.003214 | 0.005409 | primary |
| reduced_montage_motor_core | balanced_accuracy | True | secondary | 9 | -0.09076 | 1 | 0.002398 | 0.005409 | secondary |
| reduced_montage_motor_core | brier_score | True | calibration | 9 | 0.04436 | 0.8889 | 0.01252 | 0.01406 | calibration_optional |
| reduced_montage_motor_core | ece | True | calibration | 9 | -0.008478 | 0.5556 | 0.7554 | 1 | calibration_optional |
| reduced_montage_motor_extended | roc_auc | True | primary | 9 | -0.05095 | 0.8889 | 0.04449 | 0.01406 | primary |
| reduced_montage_motor_extended | balanced_accuracy | True | secondary | 9 | -0.046 | 0.8889 | 0.02731 | 0.01406 | secondary |
| reduced_montage_motor_extended | brier_score | True | calibration | 9 | 0.02105 | 0.8889 | 0.0821 | 0.01406 | calibration_optional |
| reduced_montage_motor_extended | ece | True | calibration | 9 | 0.0001052 | 0.6667 | 0.9855 | 1 | calibration_optional |
| region_dropout_0.136364 | roc_auc | True | primary | 9 | -0.08678 | 1 | 0.00245 | 0.005409 | primary |
| region_dropout_0.136364 | balanced_accuracy | True | secondary | 9 | -0.2045 | 1 | 0.0004865 | 0.005409 | secondary |
| region_dropout_0.136364 | brier_score | True | calibration | 9 | 0.2236 | 1 | 5.4e-05 | 0.005409 | calibration_optional |
| region_dropout_0.136364 | ece | True | calibration | 9 | 0.2518 | 1 | 3.574e-05 | 0.005409 | calibration_optional |
| region_dropout_0.318182 | roc_auc | True | primary | 9 | -0.1638 | 1 | 3.574e-05 | 0.005409 | primary |
| region_dropout_0.318182 | balanced_accuracy | True | secondary | 9 | -0.2673 | 1 | 0.000849 | 0.005409 | secondary |
| region_dropout_0.318182 | brier_score | True | calibration | 9 | 0.3045 | 1 | 6.53e-05 | 0.005409 | calibration_optional |
| region_dropout_0.318182 | ece | True | calibration | 9 | 0.319 | 1 | 2.176e-05 | 0.005409 | calibration_optional |

## Channel-dropout slopes
| dataset | pipeline | metric | n_subjects | mean_slope_per_10pct_dropout | slope_ci_low | slope_ci_high | slope_sd | t_statistic_vs_zero | t_p_value_vs_zero | shapiro_p_value_slope | n_harmful_slope | pct_harmful_slope | t_p_value_vs_zero_bh_fdr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BNCI2014-001 | csp_lda | balanced_accuracy | 9 | -0.04399 | -0.06015 | -0.02784 | 0.02102 | -6.279 | 0.000238 | 0.2331 | 9 | 1 | 0.000238 |
| BNCI2014-001 | csp_lda | brier_score | 9 | 0.05105 | 0.04142 | 0.06069 | 0.01253 | 12.22 | 1.862e-06 | 0.1784 | 9 | 1 | 3.725e-06 |
| BNCI2014-001 | csp_lda | ece | 9 | 0.05298 | 0.04686 | 0.05911 | 0.007972 | 19.94 | 4.172e-08 | 0.4389 | 9 | 1 | 1.669e-07 |
| BNCI2014-001 | csp_lda | roc_auc | 9 | -0.04447 | -0.05654 | -0.0324 | 0.0157 | -8.498 | 2.821e-05 | 0.08212 | 9 | 1 | 3.761e-05 |

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