# Statistical reporting pack for `PhysionetMI_PhysionetMI_all_riemann_lr`

Generated from existing subject-summary CSV files only; no simulated or additional benchmark observations are used.

## Methods audit
| check | value | status |
| --- | --- | --- |
| n_rows_subject_summary | 981 | info |
| n_subjects | 109 | info |
| n_conditions | 9 | info |
| duplicate_subject_condition_rows | 0 | pass |
| missing_roc_auc | 0 | pass |
| out_of_range_0_1_roc_auc | 0 | pass |
| missing_balanced_accuracy | 0 | pass |
| out_of_range_0_1_balanced_accuracy | 0 | pass |
| missing_brier_score | 0 | pass |
| out_of_range_0_1_brier_score | 0 | pass |
| missing_ece | 0 | pass |
| out_of_range_0_1_ece | 0 | pass |
| min_subjects_per_condition | 109 | pass |
| max_subjects_per_condition | 109 | info |

## Paired stressor effects vs clean all-channel baseline
| condition | metric | metric_role | n_subjects | clean_mean | condition_mean | mean_delta_condition_minus_clean | delta_ci_low | delta_ci_high | median_delta_condition_minus_clean | cohens_dz | t_p_value_bh_fdr | wilcoxon_p_value_bh_fdr | sign_test_p_value_bh_fdr | shapiro_p_value_delta | pct_worse_than_clean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| channel_dropout_0.1 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5496 | -0.0932 | -0.1116 | -0.07476 | -0.0795 | -0.9595 | 8.501e-17 | 2.045e-13 | 9.122e-12 | 0.3867 | 0.8165 |
| channel_dropout_0.2 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5252 | -0.1175 | -0.1409 | -0.09415 | -0.1085 | -0.9546 | 1.048e-16 | 2.819e-13 | 1.198e-12 | 0.07258 | 0.8349 |
| channel_dropout_0.3 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5166 | -0.1262 | -0.1522 | -0.1001 | -0.1025 | -0.9201 | 6.193e-16 | 6.013e-13 | 3.983e-10 | 0.02717 | 0.7982 |
| channel_dropout_0.5 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5068 | -0.1359 | -0.1641 | -0.1078 | -0.105 | -0.9166 | 7.122e-16 | 6.907e-13 | 3.983e-10 | 0.01882 | 0.7982 |
| reduced_montage_motor_core | balanced_accuracy | secondary | 109 | 0.6428 | 0.6058 | -0.037 | -0.05929 | -0.01471 | -0.035 | -0.3152 | 0.001663 | 0.001062 | 0.0001224 | 0.2182 | 0.6789 |
| reduced_montage_motor_extended | balanced_accuracy | secondary | 109 | 0.6428 | 0.6427 | -7.645e-05 | -0.02112 | 0.02097 | 0.015 | -0.0006898 | 0.9943 | 0.794 | 0.3445 | 0.1178 | 0.4404 |
| region_dropout_0.046875 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5913 | -0.05145 | -0.06777 | -0.03513 | -0.045 | -0.5986 | 1.113e-08 | 3.362e-08 | 5.452e-05 | 0.0005716 | 0.6881 |
| region_dropout_0.140625 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5224 | -0.1203 | -0.1471 | -0.09359 | -0.0775 | -0.8545 | 2e-14 | 1.048e-12 | 5.098e-09 | 0.0004846 | 0.7798 |
| channel_dropout_0.1 | roc_auc | primary | 109 | 0.6754 | 0.6397 | -0.03572 | -0.04273 | -0.02872 | -0.033 | -0.968 | 5.709e-17 | 6.617e-14 | 8.634e-14 | 0.3531 | 0.844 |
| channel_dropout_0.2 | roc_auc | primary | 109 | 0.6754 | 0.604 | -0.07143 | -0.08286 | -0.06 | -0.075 | -1.187 | 6.514e-22 | 9.518e-16 | 3.515e-17 | 0.6437 | 0.8899 |
| channel_dropout_0.3 | roc_auc | primary | 109 | 0.6754 | 0.5944 | -0.08102 | -0.09447 | -0.06757 | -0.095 | -1.144 | 5.902e-21 | 3.289e-15 | 2.453e-13 | 0.6408 | 0.844 |
| channel_dropout_0.5 | roc_auc | primary | 109 | 0.6754 | 0.5544 | -0.121 | -0.1412 | -0.1008 | -0.126 | -1.135 | 8.116e-21 | 4.834e-15 | 9.883e-15 | 0.3267 | 0.8624 |
| reduced_montage_motor_core | roc_auc | primary | 109 | 0.6754 | 0.6392 | -0.03624 | -0.06394 | -0.008534 | -0.035 | -0.2483 | 0.01239 | 0.01171 | 0.005954 | 0.3693 | 0.633 |
| reduced_montage_motor_extended | roc_auc | primary | 109 | 0.6754 | 0.6769 | 0.001468 | -0.0266 | 0.02954 | 0.01 | 0.009929 | 0.9472 | 0.598 | 0.2527 | 0.1939 | 0.4128 |
| region_dropout_0.046875 | roc_auc | primary | 109 | 0.6754 | 0.6626 | -0.01282 | -0.01953 | -0.00611 | -0.01 | -0.3627 | 0.0003215 | 0.0003697 | 0.001866 | 0.003982 | 0.5596 |
| region_dropout_0.140625 | roc_auc | primary | 109 | 0.6754 | 0.6319 | -0.04352 | -0.05437 | -0.03268 | -0.04 | -0.7619 | 2.775e-12 | 2.777e-10 | 6.335e-10 | 0.3476 | 0.7706 |

## Sensitivity summary
| condition | metric | available | role | n_subjects | mean_delta_condition_minus_clean | pct_worse_than_clean | ttest_fdr | wilcoxon_fdr | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| channel_dropout_0.1 | roc_auc | True | primary | 109 | -0.03572 | 0.844 | 5.709e-17 | 6.617e-14 | primary |
| channel_dropout_0.1 | balanced_accuracy | True | secondary | 109 | -0.0932 | 0.8165 | 8.501e-17 | 2.045e-13 | secondary |
| channel_dropout_0.1 | brier_score | True | calibration | 109 | 0.06574 | 1 | 5.497e-38 | 8.183e-19 | calibration_optional |
| channel_dropout_0.1 | ece | True | calibration | 109 | 0.04445 | 0.8807 | 8.116e-21 | 9.128e-16 | calibration_optional |
| channel_dropout_0.2 | roc_auc | True | primary | 109 | -0.07143 | 0.8899 | 6.514e-22 | 9.518e-16 | primary |
| channel_dropout_0.2 | balanced_accuracy | True | secondary | 109 | -0.1175 | 0.8349 | 1.048e-16 | 2.819e-13 | secondary |
| channel_dropout_0.2 | brier_score | True | calibration | 109 | 0.1047 | 1 | 5.9e-40 | 8.183e-19 | calibration_optional |
| channel_dropout_0.2 | ece | True | calibration | 109 | 0.06541 | 0.9083 | 3.373e-24 | 1.392e-17 | calibration_optional |
| channel_dropout_0.3 | roc_auc | True | primary | 109 | -0.08102 | 0.844 | 5.902e-21 | 3.289e-15 | primary |
| channel_dropout_0.3 | balanced_accuracy | True | secondary | 109 | -0.1262 | 0.7982 | 6.193e-16 | 6.013e-13 | secondary |
| channel_dropout_0.3 | brier_score | True | calibration | 109 | 0.1244 | 1 | 6.858e-41 | 8.183e-19 | calibration_optional |
| channel_dropout_0.3 | ece | True | calibration | 109 | 0.07802 | 0.945 | 3.301e-25 | 5.078e-18 | calibration_optional |
| channel_dropout_0.5 | roc_auc | True | primary | 109 | -0.121 | 0.8624 | 8.116e-21 | 4.834e-15 | primary |
| channel_dropout_0.5 | balanced_accuracy | True | secondary | 109 | -0.1359 | 0.7982 | 7.122e-16 | 6.907e-13 | secondary |
| channel_dropout_0.5 | brier_score | True | calibration | 109 | 0.1629 | 1 | 2.055e-42 | 8.183e-19 | calibration_optional |
| channel_dropout_0.5 | ece | True | calibration | 109 | 0.1033 | 0.9541 | 2.653e-28 | 2.052e-18 | calibration_optional |
| reduced_montage_motor_core | roc_auc | True | primary | 109 | -0.03624 | 0.633 | 0.01239 | 0.01171 | primary |
| reduced_montage_motor_core | balanced_accuracy | True | secondary | 109 | -0.037 | 0.6789 | 0.001663 | 0.001062 | secondary |
| reduced_montage_motor_core | brier_score | True | calibration | 109 | 0.005789 | 0.5229 | 0.1532 | 0.4034 | calibration_optional |
| reduced_montage_motor_core | ece | True | calibration | 109 | -0.06901 | 0.156 | 3.326e-17 | 1.408e-13 | calibration_optional |
| reduced_montage_motor_extended | roc_auc | True | primary | 109 | 0.001468 | 0.4128 | 0.9472 | 0.598 | primary |
| reduced_montage_motor_extended | balanced_accuracy | True | secondary | 109 | -7.645e-05 | 0.4404 | 0.9943 | 0.794 | secondary |
| reduced_montage_motor_extended | brier_score | True | calibration | 109 | -0.007065 | 0.4128 | 0.04494 | 0.01341 | calibration_optional |
| reduced_montage_motor_extended | ece | True | calibration | 109 | -0.03082 | 0.3211 | 7.397e-09 | 4.172e-08 | calibration_optional |
| region_dropout_0.046875 | roc_auc | True | primary | 109 | -0.01282 | 0.5596 | 0.0003215 | 0.0003697 | primary |
| region_dropout_0.046875 | balanced_accuracy | True | secondary | 109 | -0.05145 | 0.6881 | 1.113e-08 | 3.362e-08 | secondary |
| region_dropout_0.046875 | brier_score | True | calibration | 109 | 0.02756 | 0.9083 | 6.193e-16 | 1.392e-17 | calibration_optional |
| region_dropout_0.046875 | ece | True | calibration | 109 | 0.01361 | 0.6055 | 0.003797 | 0.006209 | calibration_optional |
| region_dropout_0.140625 | roc_auc | True | primary | 109 | -0.04352 | 0.7706 | 2.775e-12 | 2.777e-10 | primary |
| region_dropout_0.140625 | balanced_accuracy | True | secondary | 109 | -0.1203 | 0.7798 | 2e-14 | 1.048e-12 | secondary |
| region_dropout_0.140625 | brier_score | True | calibration | 109 | 0.1031 | 1 | 2.251e-22 | 8.183e-19 | calibration_optional |
| region_dropout_0.140625 | ece | True | calibration | 109 | 0.07056 | 0.8532 | 2.783e-18 | 1.432e-14 | calibration_optional |

## Channel-dropout slopes
| dataset | pipeline | metric | n_subjects | mean_slope_per_10pct_dropout | slope_ci_low | slope_ci_high | slope_sd | t_statistic_vs_zero | t_p_value_vs_zero | shapiro_p_value_slope | n_harmful_slope | pct_harmful_slope | t_p_value_vs_zero_bh_fdr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PhysionetMotorImagery | riemann_lr | balanced_accuracy | 109 | -0.02339 | -0.02837 | -0.01841 | 0.02625 | -9.303 | 1.791e-15 | 0.005242 | 85 | 0.7798 | 1.791e-15 |
| PhysionetMotorImagery | riemann_lr | brier_score | 109 | 0.03081 | 0.02812 | 0.03349 | 0.01414 | 22.74 | 5.555e-43 | 0.008365 | 109 | 1 | 2.222e-42 |
| PhysionetMotorImagery | riemann_lr | ece | 109 | 0.01927 | 0.01671 | 0.02182 | 0.01347 | 14.93 | 5.01e-28 | 0.01141 | 105 | 0.9633 | 1.002e-27 |
| PhysionetMotorImagery | riemann_lr | roc_auc | 109 | -0.02341 | -0.02742 | -0.0194 | 0.02113 | -11.57 | 1.263e-20 | 0.266 | 93 | 0.8532 | 1.684e-20 |

## Overclaim-risk flags
| flag | triggered | detail |
| --- | --- | --- |
| low_subject_count | False | n_subjects=109; population-level claims should be cautious below 20 subjects. |
| development_subset_prefix | False | Prefix contains 'dev'; treat as development output, not final population estimate. |
| missing_calibration_metrics | False | Missing optional calibration metrics: none |
| cross_session_absent | True | Cross-session stressor absent. |
| skipped_subject_log_present | False | Found 0 failed-subject log files matching prefix. |
| uneven_or_low_paired_n | False | minimum paired n=109; total subject n=109. |

## Statistical notes
- Paired effects are computed within subject against the clean all-channel baseline.
- Confidence intervals for mean paired deltas and slopes use Student t intervals.
- Median-delta intervals use a distribution-free sign-test/order-statistic interval.
- Normality of paired deltas/slopes is screened with Shapiro-Wilk where sample size permits.
- Wilcoxon signed-rank and sign tests are reported as sensitivity checks for paired deltas.
- Benjamini-Hochberg false discovery rate correction is applied to paired t-test, Wilcoxon, and sign-test p-values.