# Statistical reporting pack for `BNCI2014-001_BNCI2014_001_all_riemann_lr`

Generated from existing subject-summary CSV files only; no simulated or additional benchmark observations are used.

## Methods audit
| check | value | status |
| --- | --- | --- |
| n_rows_subject_summary | 99 | info |
| n_subjects | 9 | info |
| n_conditions | 11 | info |
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
| channel_dropout_0.1 | balanced_accuracy | secondary | 9 | 0.8218 | 0.6235 | -0.1983 | -0.2464 | -0.1502 | -0.226 | -3.169 | 4.5e-05 | 0.004883 | 0.004883 | 0.1048 | 1 |
| channel_dropout_0.2 | balanced_accuracy | secondary | 9 | 0.8218 | 0.5608 | -0.2609 | -0.3316 | -0.1903 | -0.3054 | -2.839 | 8.542e-05 | 0.004883 | 0.004883 | 0.1048 | 1 |
| channel_dropout_0.3 | balanced_accuracy | secondary | 9 | 0.8218 | 0.5359 | -0.2859 | -0.365 | -0.2068 | -0.3133 | -2.779 | 9.258e-05 | 0.004883 | 0.004883 | 0.4007 | 1 |
| channel_dropout_0.5 | balanced_accuracy | secondary | 9 | 0.8218 | 0.5204 | -0.3014 | -0.3885 | -0.2144 | -0.3119 | -2.662 | 0.0001107 | 0.004883 | 0.004883 | 0.4877 | 1 |
| cross_session_0 | balanced_accuracy | secondary | 9 | 0.8218 | 0.7716 | -0.05018 | -0.1246 | 0.02424 | -0.01046 | -0.5183 | 0.1762 | 0.0434 | 0.1997 | 0.0002503 | 0.7778 |
| reduced_montage_motor_core | balanced_accuracy | secondary | 9 | 0.8218 | 0.7077 | -0.1141 | -0.1578 | -0.07042 | -0.1005 | -2.007 | 0.0005488 | 0.004883 | 0.004883 | 0.001824 | 1 |
| reduced_montage_motor_extended | balanced_accuracy | secondary | 9 | 0.8218 | 0.7642 | -0.05758 | -0.09105 | -0.02411 | -0.05234 | -1.322 | 0.005333 | 0.004883 | 0.004883 | 0.4114 | 1 |
| region_dropout_left_motor_strip_0.318182 | balanced_accuracy | secondary | 9 | 0.8218 | 0.5015 | -0.3203 | -0.4205 | -0.2201 | -0.3611 | -2.456 | 0.0001848 | 0.004883 | 0.004883 | 0.4961 | 1 |
| region_dropout_midline_motor_strip_0.136364 | balanced_accuracy | secondary | 9 | 0.8218 | 0.6231 | -0.1987 | -0.2692 | -0.1282 | -0.167 | -2.167 | 0.0003756 | 0.004883 | 0.004883 | 0.1567 | 1 |
| region_dropout_right_motor_strip_0.318182 | balanced_accuracy | secondary | 9 | 0.8218 | 0.5049 | -0.3169 | -0.4169 | -0.2169 | -0.3576 | -2.436 | 0.0001852 | 0.004883 | 0.004883 | 0.348 | 1 |
| channel_dropout_0.1 | roc_auc | primary | 9 | 0.8776 | 0.8498 | -0.02775 | -0.04081 | -0.01469 | -0.031 | -1.633 | 0.001643 | 0.004883 | 0.004883 | 0.7313 | 1 |
| channel_dropout_0.2 | roc_auc | primary | 9 | 0.8776 | 0.8204 | -0.05721 | -0.08261 | -0.03182 | -0.0464 | -1.732 | 0.001181 | 0.004883 | 0.004883 | 0.7749 | 1 |
| channel_dropout_0.3 | roc_auc | primary | 9 | 0.8776 | 0.7724 | -0.1052 | -0.1442 | -0.06624 | -0.09437 | -2.076 | 0.0004582 | 0.004883 | 0.004883 | 0.1657 | 1 |
| channel_dropout_0.5 | roc_auc | primary | 9 | 0.8776 | 0.7241 | -0.1535 | -0.1976 | -0.1093 | -0.1384 | -2.674 | 0.0001107 | 0.004883 | 0.004883 | 0.8181 | 1 |
| cross_session_0 | roc_auc | primary | 9 | 0.8776 | 0.8703 | -0.007336 | -0.02189 | 0.007213 | -0.003202 | -0.3876 | 0.301 | 0.3885 | 1 | 0.4849 | 0.5556 |
| reduced_montage_motor_core | roc_auc | primary | 9 | 0.8776 | 0.7669 | -0.1107 | -0.163 | -0.05832 | -0.1212 | -1.625 | 0.001643 | 0.004883 | 0.004883 | 0.5625 | 1 |
| reduced_montage_motor_extended | roc_auc | primary | 9 | 0.8776 | 0.8282 | -0.04941 | -0.08669 | -0.01213 | -0.03006 | -1.019 | 0.019 | 0.004883 | 0.004883 | 0.1249 | 1 |
| region_dropout_left_motor_strip_0.318182 | roc_auc | primary | 9 | 0.8776 | 0.7806 | -0.09703 | -0.135 | -0.05909 | -0.1081 | -1.966 | 0.0006039 | 0.00947 | 0.04464 | 0.2516 | 0.8889 |
| region_dropout_midline_motor_strip_0.136364 | roc_auc | primary | 9 | 0.8776 | 0.8561 | -0.02148 | -0.04415 | 0.001188 | -0.01216 | -0.7284 | 0.07103 | 0.03125 | 0.04464 | 0.02528 | 0.8889 |
| region_dropout_right_motor_strip_0.318182 | roc_auc | primary | 9 | 0.8776 | 0.7118 | -0.1658 | -0.2362 | -0.09531 | -0.1474 | -1.808 | 0.0009288 | 0.004883 | 0.004883 | 0.1312 | 1 |

## Sensitivity summary
| condition | metric | available | role | n_subjects | mean_delta_condition_minus_clean | pct_worse_than_clean | ttest_fdr | wilcoxon_fdr | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| channel_dropout_0.1 | roc_auc | True | primary | 9 | -0.02775 | 1 | 0.001643 | 0.004883 | primary |
| channel_dropout_0.1 | balanced_accuracy | True | secondary | 9 | -0.1983 | 1 | 4.5e-05 | 0.004883 | secondary |
| channel_dropout_0.1 | brier_score | True | calibration | 9 | 0.1712 | 1 | 2.729e-06 | 0.004883 | calibration_optional |
| channel_dropout_0.1 | ece | True | calibration | 9 | 0.1988 | 1 | 2.509e-06 | 0.004883 | calibration_optional |
| channel_dropout_0.2 | roc_auc | True | primary | 9 | -0.05721 | 1 | 0.001181 | 0.004883 | primary |
| channel_dropout_0.2 | balanced_accuracy | True | secondary | 9 | -0.2609 | 1 | 8.542e-05 | 0.004883 | secondary |
| channel_dropout_0.2 | brier_score | True | calibration | 9 | 0.2425 | 1 | 3.503e-06 | 0.004883 | calibration_optional |
| channel_dropout_0.2 | ece | True | calibration | 9 | 0.2638 | 1 | 2.147e-08 | 0.004883 | calibration_optional |
| channel_dropout_0.3 | roc_auc | True | primary | 9 | -0.1052 | 1 | 0.0004582 | 0.004883 | primary |
| channel_dropout_0.3 | balanced_accuracy | True | secondary | 9 | -0.2859 | 1 | 9.258e-05 | 0.004883 | secondary |
| channel_dropout_0.3 | brier_score | True | calibration | 9 | 0.2743 | 1 | 1.801e-06 | 0.004883 | calibration_optional |
| channel_dropout_0.3 | ece | True | calibration | 9 | 0.2885 | 1 | 5.039e-09 | 0.004883 | calibration_optional |
| channel_dropout_0.5 | roc_auc | True | primary | 9 | -0.1535 | 1 | 0.0001107 | 0.004883 | primary |
| channel_dropout_0.5 | balanced_accuracy | True | secondary | 9 | -0.3014 | 1 | 0.0001107 | 0.004883 | secondary |
| channel_dropout_0.5 | brier_score | True | calibration | 9 | 0.2866 | 1 | 3.503e-06 | 0.004883 | calibration_optional |
| channel_dropout_0.5 | ece | True | calibration | 9 | 0.2943 | 1 | 1.132e-08 | 0.004883 | calibration_optional |
| cross_session_0 | roc_auc | True | primary | 9 | -0.007336 | 0.5556 | 0.301 | 0.3885 | primary |
| cross_session_0 | balanced_accuracy | True | secondary | 9 | -0.05018 | 0.7778 | 0.1762 | 0.0434 | secondary |
| cross_session_0 | brier_score | True | calibration | 9 | 0.02311 | 0.8889 | 0.09213 | 0.01379 | calibration_optional |
| cross_session_0 | ece | True | calibration | 9 | 0.01274 | 0.5556 | 0.4286 | 0.5849 | calibration_optional |
| reduced_montage_motor_core | roc_auc | True | primary | 9 | -0.1107 | 1 | 0.001643 | 0.004883 | primary |
| reduced_montage_motor_core | balanced_accuracy | True | secondary | 9 | -0.1141 | 1 | 0.0005488 | 0.004883 | secondary |
| reduced_montage_motor_core | brier_score | True | calibration | 9 | 0.05812 | 1 | 0.0006809 | 0.004883 | calibration_optional |
| reduced_montage_motor_core | ece | True | calibration | 9 | 0.004714 | 0.6667 | 0.773 | 0.7344 | calibration_optional |
| reduced_montage_motor_extended | roc_auc | True | primary | 9 | -0.04941 | 1 | 0.019 | 0.004883 | primary |
| reduced_montage_motor_extended | balanced_accuracy | True | secondary | 9 | -0.05758 | 1 | 0.005333 | 0.004883 | secondary |
| reduced_montage_motor_extended | brier_score | True | calibration | 9 | 0.02358 | 1 | 0.01302 | 0.004883 | calibration_optional |
| reduced_montage_motor_extended | ece | True | calibration | 9 | 0.004639 | 0.6667 | 0.5726 | 0.4482 | calibration_optional |
| region_dropout_left_motor_strip_0.318182 | roc_auc | True | primary | 9 | -0.09703 | 0.8889 | 0.0006039 | 0.00947 | primary |
| region_dropout_left_motor_strip_0.318182 | balanced_accuracy | True | secondary | 9 | -0.3203 | 1 | 0.0001848 | 0.004883 | secondary |
| region_dropout_left_motor_strip_0.318182 | brier_score | True | calibration | 9 | 0.3482 | 1 | 2.721e-05 | 0.004883 | calibration_optional |
| region_dropout_left_motor_strip_0.318182 | ece | True | calibration | 9 | 0.3571 | 1 | 3.536e-07 | 0.004883 | calibration_optional |
| region_dropout_midline_motor_strip_0.136364 | roc_auc | True | primary | 9 | -0.02148 | 0.8889 | 0.07103 | 0.03125 | primary |
| region_dropout_midline_motor_strip_0.136364 | balanced_accuracy | True | secondary | 9 | -0.1987 | 1 | 0.0003756 | 0.004883 | secondary |
| region_dropout_midline_motor_strip_0.136364 | brier_score | True | calibration | 9 | 0.1803 | 1 | 0.0006809 | 0.004883 | calibration_optional |
| region_dropout_midline_motor_strip_0.136364 | ece | True | calibration | 9 | 0.2177 | 1 | 0.0004178 | 0.004883 | calibration_optional |
| region_dropout_right_motor_strip_0.318182 | roc_auc | True | primary | 9 | -0.1658 | 1 | 0.0009288 | 0.004883 | primary |
| region_dropout_right_motor_strip_0.318182 | balanced_accuracy | True | secondary | 9 | -0.3169 | 1 | 0.0001852 | 0.004883 | secondary |
| region_dropout_right_motor_strip_0.318182 | brier_score | True | calibration | 9 | 0.3178 | 1 | 0.0002939 | 0.004883 | calibration_optional |
| region_dropout_right_motor_strip_0.318182 | ece | True | calibration | 9 | 0.3132 | 1 | 7.245e-05 | 0.004883 | calibration_optional |

## Channel-dropout slopes
| dataset | pipeline | metric | n_subjects | mean_slope_per_10pct_dropout | slope_ci_low | slope_ci_high | slope_sd | t_statistic_vs_zero | t_p_value_vs_zero | shapiro_p_value_slope | n_harmful_slope | pct_harmful_slope | t_p_value_vs_zero_bh_fdr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BNCI2014-001 | riemann_lr | balanced_accuracy | 9 | -0.05288 | -0.06953 | -0.03624 | 0.02165 | -7.326 | 8.179e-05 | 0.7744 | 9 | 1 | 8.179e-05 |
| BNCI2014-001 | riemann_lr | brier_score | 9 | 0.0519 | 0.0419 | 0.06191 | 0.01301 | 11.96 | 2.194e-06 | 0.5991 | 9 | 1 | 4.388e-06 |
| BNCI2014-001 | riemann_lr | ece | 9 | 0.05159 | 0.04659 | 0.05658 | 0.006496 | 23.82 | 1.027e-08 | 0.8418 | 9 | 1 | 4.107e-08 |
| BNCI2014-001 | riemann_lr | roc_auc | 9 | -0.0317 | -0.04089 | -0.02251 | 0.01196 | -7.952 | 4.559e-05 | 0.8569 | 9 | 1 | 6.079e-05 |

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