# Statistical reporting pack for `PhysionetMI_PhysionetMI_all_riemann_lr`

Generated from existing subject-summary CSV files only; no simulated or additional benchmark observations are used.

## Methods audit
| check | value | status |
| --- | --- | --- |
| n_rows_subject_summary | 1090 | info |
| n_subjects | 109 | info |
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
| min_subjects_per_condition | 109 | pass |
| max_subjects_per_condition | 109 | info |

## Paired stressor effects vs clean all-channel baseline
| condition | metric | metric_role | n_subjects | clean_mean | condition_mean | mean_delta_condition_minus_clean | delta_ci_low | delta_ci_high | median_delta_condition_minus_clean | cohens_dz | t_p_value_bh_fdr | wilcoxon_p_value_bh_fdr | sign_test_p_value_bh_fdr | shapiro_p_value_delta | pct_worse_than_clean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| channel_dropout_0.1 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5504 | -0.09236 | -0.1114 | -0.0733 | -0.082 | -0.92 | 6.628e-16 | 8.943e-13 | 1.1e-10 | 0.3415 | 0.8073 |
| channel_dropout_0.2 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5266 | -0.1162 | -0.139 | -0.09334 | -0.0985 | -0.9663 | 6.594e-17 | 2.526e-13 | 6.197e-12 | 0.04446 | 0.8257 |
| channel_dropout_0.3 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5168 | -0.126 | -0.1514 | -0.1006 | -0.104 | -0.9416 | 2.398e-16 | 4.125e-13 | 6.197e-12 | 0.01912 | 0.8257 |
| channel_dropout_0.5 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5072 | -0.1355 | -0.1632 | -0.1078 | -0.113 | -0.9295 | 4.4e-16 | 4.795e-13 | 1.698e-10 | 0.01778 | 0.7982 |
| reduced_montage_motor_core | balanced_accuracy | secondary | 109 | 0.6428 | 0.6058 | -0.037 | -0.05929 | -0.01471 | -0.035 | -0.3152 | 0.001621 | 0.001035 | 0.0001181 | 0.2182 | 0.6789 |
| reduced_montage_motor_extended | balanced_accuracy | secondary | 109 | 0.6428 | 0.6427 | -7.645e-05 | -0.02112 | 0.02097 | 0.015 | -0.0006898 | 0.9943 | 0.794 | 0.3432 | 0.1178 | 0.4404 |
| region_dropout_left_motor_strip_0.140625 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5268 | -0.116 | -0.1431 | -0.08881 | -0.08 | -0.8104 | 2.126e-13 | 5.253e-12 | 2.62e-10 | 0.001119 | 0.789 |
| region_dropout_midline_motor_strip_0.046875 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5913 | -0.05145 | -0.06777 | -0.03513 | -0.045 | -0.5986 | 1.113e-08 | 3.346e-08 | 5.225e-05 | 0.0005716 | 0.6881 |
| region_dropout_right_motor_strip_0.140625 | balanced_accuracy | secondary | 109 | 0.6428 | 0.5181 | -0.1247 | -0.153 | -0.09638 | -0.08 | -0.8365 | 5.446e-14 | 1.231e-12 | 6.242e-10 | 9.497e-05 | 0.789 |
| channel_dropout_0.1 | roc_auc | primary | 109 | 0.6754 | 0.6396 | -0.03576 | -0.04247 | -0.02906 | -0.038 | -1.013 | 5.998e-18 | 4.107e-14 | 4.981e-13 | 0.7161 | 0.8349 |
| channel_dropout_0.2 | roc_auc | primary | 109 | 0.6754 | 0.6088 | -0.0666 | -0.07758 | -0.05561 | -0.074 | -1.151 | 5.427e-21 | 5.514e-15 | 3.023e-15 | 0.334 | 0.8624 |
| channel_dropout_0.3 | roc_auc | primary | 109 | 0.6754 | 0.5904 | -0.08503 | -0.09907 | -0.07098 | -0.093 | -1.149 | 5.427e-21 | 2.943e-15 | 3.023e-15 | 0.4389 | 0.8624 |
| channel_dropout_0.5 | roc_auc | primary | 109 | 0.6754 | 0.5569 | -0.1185 | -0.1389 | -0.09811 | -0.122 | -1.103 | 6.051e-20 | 8.111e-15 | 1.432e-12 | 0.1725 | 0.8349 |
| reduced_montage_motor_core | roc_auc | primary | 109 | 0.6754 | 0.6392 | -0.03624 | -0.06394 | -0.008534 | -0.035 | -0.2483 | 0.01219 | 0.01153 | 0.005834 | 0.3693 | 0.633 |
| reduced_montage_motor_extended | roc_auc | primary | 109 | 0.6754 | 0.6769 | 0.001468 | -0.0266 | 0.02954 | 0.01 | 0.009929 | 0.9438 | 0.5959 | 0.2508 | 0.1939 | 0.4128 |
| region_dropout_left_motor_strip_0.140625 | roc_auc | primary | 109 | 0.6754 | 0.6362 | -0.03918 | -0.05195 | -0.02642 | -0.04 | -0.5826 | 2.347e-08 | 2.357e-07 | 8.18e-06 | 0.24 | 0.6789 |
| region_dropout_midline_motor_strip_0.046875 | roc_auc | primary | 109 | 0.6754 | 0.6626 | -0.01282 | -0.01953 | -0.00611 | -0.01 | -0.3627 | 0.0003118 | 0.0004379 | 0.00182 | 0.003982 | 0.5596 |
| region_dropout_right_motor_strip_0.140625 | roc_auc | primary | 109 | 0.6754 | 0.6275 | -0.04786 | -0.06207 | -0.03364 | -0.04 | -0.6392 | 1.598e-09 | 8.558e-09 | 1.518e-07 | 0.2032 | 0.7248 |

## Sensitivity summary
| condition | metric | available | role | n_subjects | mean_delta_condition_minus_clean | pct_worse_than_clean | ttest_fdr | wilcoxon_fdr | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| channel_dropout_0.1 | roc_auc | True | primary | 109 | -0.03576 | 0.8349 | 5.998e-18 | 4.107e-14 | primary |
| channel_dropout_0.1 | balanced_accuracy | True | secondary | 109 | -0.09236 | 0.8073 | 6.628e-16 | 8.943e-13 | secondary |
| channel_dropout_0.1 | brier_score | True | calibration | 109 | 0.06641 | 0.9908 | 2.917e-37 | 1.183e-18 | calibration_optional |
| channel_dropout_0.1 | ece | True | calibration | 109 | 0.04429 | 0.8624 | 1.247e-19 | 2.074e-15 | calibration_optional |
| channel_dropout_0.2 | roc_auc | True | primary | 109 | -0.0666 | 0.8624 | 5.427e-21 | 5.514e-15 | primary |
| channel_dropout_0.2 | balanced_accuracy | True | secondary | 109 | -0.1162 | 0.8257 | 6.594e-17 | 2.526e-13 | secondary |
| channel_dropout_0.2 | brier_score | True | calibration | 109 | 0.1037 | 1 | 3.545e-39 | 1.183e-18 | calibration_optional |
| channel_dropout_0.2 | ece | True | calibration | 109 | 0.06565 | 0.8899 | 8.124e-23 | 6.157e-17 | calibration_optional |
| channel_dropout_0.3 | roc_auc | True | primary | 109 | -0.08503 | 0.8624 | 5.427e-21 | 2.943e-15 | primary |
| channel_dropout_0.3 | balanced_accuracy | True | secondary | 109 | -0.126 | 0.8257 | 2.398e-16 | 4.125e-13 | secondary |
| channel_dropout_0.3 | brier_score | True | calibration | 109 | 0.1248 | 1 | 3.828e-40 | 1.183e-18 | calibration_optional |
| channel_dropout_0.3 | ece | True | calibration | 109 | 0.07804 | 0.9174 | 7.05e-24 | 2.153e-17 | calibration_optional |
| channel_dropout_0.5 | roc_auc | True | primary | 109 | -0.1185 | 0.8349 | 6.051e-20 | 8.111e-15 | primary |
| channel_dropout_0.5 | balanced_accuracy | True | secondary | 109 | -0.1355 | 0.7982 | 4.4e-16 | 4.795e-13 | secondary |
| channel_dropout_0.5 | brier_score | True | calibration | 109 | 0.1611 | 1 | 4.742e-42 | 1.183e-18 | calibration_optional |
| channel_dropout_0.5 | ece | True | calibration | 109 | 0.1025 | 0.9541 | 4.793e-27 | 3.704e-18 | calibration_optional |
| reduced_montage_motor_core | roc_auc | True | primary | 109 | -0.03624 | 0.633 | 0.01219 | 0.01153 | primary |
| reduced_montage_motor_core | balanced_accuracy | True | secondary | 109 | -0.037 | 0.6789 | 0.001621 | 0.001035 | secondary |
| reduced_montage_motor_core | brier_score | True | calibration | 109 | 0.005789 | 0.5229 | 0.152 | 0.4004 | calibration_optional |
| reduced_montage_motor_core | ece | True | calibration | 109 | -0.06901 | 0.156 | 3.492e-17 | 1.585e-13 | calibration_optional |
| reduced_montage_motor_extended | roc_auc | True | primary | 109 | 0.001468 | 0.4128 | 0.9438 | 0.5959 | primary |
| reduced_montage_motor_extended | balanced_accuracy | True | secondary | 109 | -7.645e-05 | 0.4404 | 0.9943 | 0.794 | secondary |
| reduced_montage_motor_extended | brier_score | True | calibration | 109 | -0.007065 | 0.4128 | 0.04442 | 0.01325 | calibration_optional |
| reduced_montage_motor_extended | ece | True | calibration | 109 | -0.03082 | 0.3211 | 7.362e-09 | 4.172e-08 | calibration_optional |
| region_dropout_left_motor_strip_0.140625 | roc_auc | True | primary | 109 | -0.03918 | 0.6789 | 2.347e-08 | 2.357e-07 | primary |
| region_dropout_left_motor_strip_0.140625 | balanced_accuracy | True | secondary | 109 | -0.116 | 0.789 | 2.126e-13 | 5.253e-12 | secondary |
| region_dropout_left_motor_strip_0.140625 | brier_score | True | calibration | 109 | 0.0973 | 0.9633 | 1.881e-19 | 1.786e-18 | calibration_optional |
| region_dropout_left_motor_strip_0.140625 | ece | True | calibration | 109 | 0.06604 | 0.789 | 2.106e-14 | 3.29e-12 | calibration_optional |
| region_dropout_midline_motor_strip_0.046875 | roc_auc | True | primary | 109 | -0.01282 | 0.5596 | 0.0003118 | 0.0004379 | primary |
| region_dropout_midline_motor_strip_0.046875 | balanced_accuracy | True | secondary | 109 | -0.05145 | 0.6881 | 1.113e-08 | 3.346e-08 | secondary |
| region_dropout_midline_motor_strip_0.046875 | brier_score | True | calibration | 109 | 0.02756 | 0.9083 | 6.628e-16 | 1.761e-17 | calibration_optional |
| region_dropout_midline_motor_strip_0.046875 | ece | True | calibration | 109 | 0.01361 | 0.6055 | 0.00372 | 0.006084 | calibration_optional |
| region_dropout_right_motor_strip_0.140625 | roc_auc | True | primary | 109 | -0.04786 | 0.7248 | 1.598e-09 | 8.558e-09 | primary |
| region_dropout_right_motor_strip_0.140625 | balanced_accuracy | True | secondary | 109 | -0.1247 | 0.789 | 5.446e-14 | 1.231e-12 | secondary |
| region_dropout_right_motor_strip_0.140625 | brier_score | True | calibration | 109 | 0.1089 | 0.9541 | 2.859e-18 | 2.506e-18 | calibration_optional |
| region_dropout_right_motor_strip_0.140625 | ece | True | calibration | 109 | 0.07507 | 0.8165 | 1.104e-15 | 2.306e-13 | calibration_optional |

## Channel-dropout slopes
| dataset | pipeline | metric | n_subjects | mean_slope_per_10pct_dropout | slope_ci_low | slope_ci_high | slope_sd | t_statistic_vs_zero | t_p_value_vs_zero | shapiro_p_value_slope | n_harmful_slope | pct_harmful_slope | t_p_value_vs_zero_bh_fdr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PhysionetMotorImagery | riemann_lr | balanced_accuracy | 109 | -0.02339 | -0.02821 | -0.01857 | 0.02541 | -9.61 | 3.594e-16 | 0.00384 | 86 | 0.789 | 3.594e-16 |
| PhysionetMotorImagery | riemann_lr | brier_score | 109 | 0.03043 | 0.02774 | 0.03312 | 0.01416 | 22.43 | 1.876e-42 | 0.005358 | 109 | 1 | 7.506e-42 |
| PhysionetMotorImagery | riemann_lr | ece | 109 | 0.01913 | 0.01648 | 0.02177 | 0.01394 | 14.33 | 9.96e-27 | 0.02422 | 102 | 0.9358 | 1.992e-26 |
| PhysionetMotorImagery | riemann_lr | roc_auc | 109 | -0.02322 | -0.02732 | -0.01912 | 0.02159 | -11.23 | 7.466e-20 | 0.1448 | 90 | 0.8257 | 9.955e-20 |

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