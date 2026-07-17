# Statistical reporting pack for `PhysionetMI_dev10`

Generated from existing subject-summary CSV files only; no simulated or additional benchmark observations are used.

## Methods audit
| check | value | status |
| --- | --- | --- |
| n_rows_subject_summary | 70 | info |
| n_subjects | 10 | info |
| n_conditions | 7 | info |
| duplicate_subject_condition_rows | 0 | pass |
| missing_roc_auc | 0 | pass |
| out_of_range_0_1_roc_auc | 0 | pass |
| missing_balanced_accuracy | 0 | pass |
| out_of_range_0_1_balanced_accuracy | 0 | pass |
| missing_brier_score | 0 | pass |
| out_of_range_0_1_brier_score | 0 | pass |
| missing_ece | 0 | pass |
| out_of_range_0_1_ece | 0 | pass |
| min_subjects_per_condition | 10 | pass |
| max_subjects_per_condition | 10 | info |

## Paired stressor effects vs clean all-channel baseline
| condition | metric | metric_role | n_subjects | clean_mean | condition_mean | mean_delta_condition_minus_clean | delta_ci_low | delta_ci_high | median_delta_condition_minus_clean | cohens_dz | t_p_value_bh_fdr | wilcoxon_p_value_bh_fdr | sign_test_p_value_bh_fdr | shapiro_p_value_delta | pct_worse_than_clean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| channel_dropout_0.1 | balanced_accuracy | secondary | 10 | 0.625 | 0.5234 | -0.1017 | -0.2289 | 0.02556 | -0.1327 | -0.5716 | 0.1249 | 0.1653 | 0.4125 | 0.8049 | 0.7 |
| channel_dropout_0.2 | balanced_accuracy | secondary | 10 | 0.625 | 0.5149 | -0.1101 | -0.2578 | 0.03762 | -0.1188 | -0.5332 | 0.1385 | 0.221 | 0.7867 | 0.7625 | 0.6 |
| channel_dropout_0.3 | balanced_accuracy | secondary | 10 | 0.625 | 0.5064 | -0.1186 | -0.266 | 0.02882 | -0.1438 | -0.5755 | 0.1249 | 0.1406 | 0.4125 | 0.6523 | 0.7 |
| channel_dropout_0.5 | balanced_accuracy | secondary | 10 | 0.625 | 0.5047 | -0.1203 | -0.2706 | 0.02988 | -0.1458 | -0.5731 | 0.1249 | 0.1922 | 0.7867 | 0.6953 | 0.6 |
| reduced_montage_motor_core | balanced_accuracy | secondary | 10 | 0.625 | 0.6505 | 0.0255 | -0.09787 | 0.1489 | 0.0125 | 0.1479 | 0.6512 | 0.5808 | 1 | 0.8798 | 0.5 |
| reduced_montage_motor_extended | balanced_accuracy | secondary | 10 | 0.625 | 0.7065 | 0.0815 | 0.003737 | 0.1593 | 0.0975 | 0.7497 | 0.07674 | 0.07812 | 0.4125 | 0.1196 | 0.3 |
| channel_dropout_0.1 | roc_auc | primary | 10 | 0.655 | 0.5846 | -0.0704 | -0.1387 | -0.002099 | -0.076 | -0.7373 | 0.07674 | 0.07812 | 0.2386 | 0.08174 | 0.9 |
| channel_dropout_0.2 | roc_auc | primary | 10 | 0.655 | 0.5407 | -0.1143 | -0.2232 | -0.0055 | -0.1353 | -0.7515 | 0.07674 | 0.07812 | 0.2386 | 0.6453 | 0.9 |
| channel_dropout_0.3 | roc_auc | primary | 10 | 0.655 | 0.5316 | -0.1234 | -0.2383 | -0.008372 | -0.147 | -0.7674 | 0.07674 | 0.07812 | 0.2386 | 0.2624 | 0.8 |
| channel_dropout_0.5 | roc_auc | primary | 10 | 0.655 | 0.5203 | -0.1347 | -0.2658 | -0.003567 | -0.147 | -0.7348 | 0.07674 | 0.07812 | 0.2386 | 0.8544 | 0.8 |
| reduced_montage_motor_core | roc_auc | primary | 10 | 0.655 | 0.691 | 0.036 | -0.1039 | 0.1759 | 0.03 | 0.184 | 0.5999 | 0.6426 | 0.7867 | 0.7721 | 0.4 |
| reduced_montage_motor_extended | roc_auc | primary | 10 | 0.655 | 0.766 | 0.111 | 0.004444 | 0.2176 | 0.085 | 0.7452 | 0.07674 | 0.06696 | 0.3594 | 0.1148 | 0.2 |

## Sensitivity summary
| condition | metric | available | role | n_subjects | mean_delta_condition_minus_clean | pct_worse_than_clean | ttest_fdr | wilcoxon_fdr | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| channel_dropout_0.1 | roc_auc | True | primary | 10 | -0.0704 | 0.9 | 0.07674 | 0.07812 | primary |
| channel_dropout_0.1 | balanced_accuracy | True | secondary | 10 | -0.1017 | 0.7 | 0.1249 | 0.1653 | secondary |
| channel_dropout_0.1 | brier_score | True | calibration | 10 | 0.135 | 0.8 | 0.05448 | 0.06696 | calibration_optional |
| channel_dropout_0.1 | ece | True | calibration | 10 | 0.1023 | 0.7 | 0.07674 | 0.07812 | calibration_optional |
| channel_dropout_0.2 | roc_auc | True | primary | 10 | -0.1143 | 0.9 | 0.07674 | 0.07812 | primary |
| channel_dropout_0.2 | balanced_accuracy | True | secondary | 10 | -0.1101 | 0.6 | 0.1385 | 0.221 | secondary |
| channel_dropout_0.2 | brier_score | True | calibration | 10 | 0.1509 | 0.8 | 0.05448 | 0.06696 | calibration_optional |
| channel_dropout_0.2 | ece | True | calibration | 10 | 0.1124 | 0.7 | 0.08957 | 0.1186 | calibration_optional |
| channel_dropout_0.3 | roc_auc | True | primary | 10 | -0.1234 | 0.8 | 0.07674 | 0.07812 | primary |
| channel_dropout_0.3 | balanced_accuracy | True | secondary | 10 | -0.1186 | 0.7 | 0.1249 | 0.1406 | secondary |
| channel_dropout_0.3 | brier_score | True | calibration | 10 | 0.1591 | 0.8 | 0.05448 | 0.06696 | calibration_optional |
| channel_dropout_0.3 | ece | True | calibration | 10 | 0.1204 | 0.7 | 0.07674 | 0.07812 | calibration_optional |
| channel_dropout_0.5 | roc_auc | True | primary | 10 | -0.1347 | 0.8 | 0.07674 | 0.07812 | primary |
| channel_dropout_0.5 | balanced_accuracy | True | secondary | 10 | -0.1203 | 0.6 | 0.1249 | 0.1922 | secondary |
| channel_dropout_0.5 | brier_score | True | calibration | 10 | 0.161 | 0.8 | 0.05448 | 0.06696 | calibration_optional |
| channel_dropout_0.5 | ece | True | calibration | 10 | 0.1222 | 0.7 | 0.07674 | 0.07812 | calibration_optional |
| reduced_montage_motor_core | roc_auc | True | primary | 10 | 0.036 | 0.4 | 0.5999 | 0.6426 | primary |
| reduced_montage_motor_core | balanced_accuracy | True | secondary | 10 | 0.0255 | 0.5 | 0.6512 | 0.5808 | secondary |
| reduced_montage_motor_core | brier_score | True | calibration | 10 | -0.09198 | 0.2 | 0.09261 | 0.1186 | calibration_optional |
| reduced_montage_motor_core | ece | True | calibration | 10 | -0.08311 | 0.3 | 0.1385 | 0.2536 | calibration_optional |
| reduced_montage_motor_extended | roc_auc | True | primary | 10 | 0.111 | 0.2 | 0.07674 | 0.06696 | primary |
| reduced_montage_motor_extended | balanced_accuracy | True | secondary | 10 | 0.0815 | 0.3 | 0.07674 | 0.07812 | secondary |
| reduced_montage_motor_extended | brier_score | True | calibration | 10 | -0.1059 | 0.2 | 0.05448 | 0.06696 | calibration_optional |
| reduced_montage_motor_extended | ece | True | calibration | 10 | -0.09486 | 0.2 | 0.05448 | 0.06696 | calibration_optional |

## Channel-dropout slopes
| dataset | pipeline | metric | n_subjects | mean_slope_per_10pct_dropout | slope_ci_low | slope_ci_high | slope_sd | t_statistic_vs_zero | t_p_value_vs_zero | shapiro_p_value_slope | n_harmful_slope | pct_harmful_slope | t_p_value_vs_zero_bh_fdr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PhysionetMotorImagery | csp_lda | balanced_accuracy | 10 | -0.01945 | -0.04359 | 0.004686 | 0.03374 | -1.823 | 0.1016 | 0.572 | 6 | 0.6 | 0.1016 |
| PhysionetMotorImagery | csp_lda | brier_score | 10 | 0.02608 | 0.007763 | 0.04441 | 0.02561 | 3.221 | 0.01048 | 0.7027 | 8 | 0.8 | 0.04191 |
| PhysionetMotorImagery | csp_lda | ece | 10 | 0.01981 | 0.0003035 | 0.03932 | 0.02727 | 2.297 | 0.0472 | 0.7288 | 7 | 0.7 | 0.06294 |
| PhysionetMotorImagery | csp_lda | roc_auc | 10 | -0.0249 | -0.0492 | -0.0005917 | 0.03398 | -2.317 | 0.04569 | 0.8191 | 8 | 0.8 | 0.06294 |

## Overclaim-risk flags
| flag | triggered | detail |
| --- | --- | --- |
| low_subject_count | True | n_subjects=10; population-level claims should be cautious below 20 subjects. |
| development_subset_prefix | True | Prefix contains 'dev'; treat as development output, not final population estimate. |
| missing_calibration_metrics | False | Missing optional calibration metrics: none |
| cross_session_absent | True | Cross-session stressor absent. |
| skipped_subject_log_present | False | Found 0 failed-subject log files matching prefix. |
| uneven_or_low_paired_n | False | minimum paired n=10; total subject n=10. |

## Statistical notes
- Paired effects are computed within subject against the clean all-channel baseline.
- Confidence intervals for mean paired deltas and slopes use Student t intervals.
- Median-delta intervals use a distribution-free sign-test/order-statistic interval.
- Normality of paired deltas/slopes is screened with Shapiro-Wilk where sample size permits.
- Wilcoxon signed-rank and sign tests are reported as sensitivity checks for paired deltas.
- Benjamini-Hochberg false discovery rate correction is applied to paired t-test, Wilcoxon, and sign-test p-values.