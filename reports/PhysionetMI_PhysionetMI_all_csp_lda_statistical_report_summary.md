# Statistical reporting pack for `PhysionetMI_PhysionetMI_all_csp_lda`

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
| channel_dropout_0.1 | balanced_accuracy | secondary | 109 | 0.6193 | 0.5251 | -0.09417 | -0.117 | -0.07134 | -0.0805 | -0.7831 | 9.637e-13 | 4.984e-11 | 5.037e-07 | 0.08507 | 0.7431 |
| channel_dropout_0.2 | balanced_accuracy | secondary | 109 | 0.6193 | 0.5114 | -0.1079 | -0.1328 | -0.08305 | -0.083 | -0.8241 | 1.165e-13 | 7.933e-12 | 1.727e-09 | 0.0299 | 0.789 |
| channel_dropout_0.3 | balanced_accuracy | secondary | 109 | 0.6193 | 0.5092 | -0.1101 | -0.1354 | -0.08476 | -0.0915 | -0.8257 | 1.12e-13 | 1.075e-11 | 1.824e-08 | 0.1152 | 0.7706 |
| channel_dropout_0.5 | balanced_accuracy | secondary | 109 | 0.6193 | 0.506 | -0.1133 | -0.1393 | -0.08725 | -0.089 | -0.8264 | 1.12e-13 | 9.205e-12 | 1.824e-08 | 0.03296 | 0.7706 |
| reduced_montage_motor_core | balanced_accuracy | secondary | 109 | 0.6193 | 0.612 | -0.007217 | -0.03173 | 0.0173 | -0.005 | -0.0559 | 0.5767 | 0.6206 | 0.9234 | 0.9559 | 0.5046 |
| reduced_montage_motor_extended | balanced_accuracy | secondary | 109 | 0.6193 | 0.6307 | 0.01139 | -0.01036 | 0.03314 | 0.015 | 0.09942 | 0.329 | 0.2717 | 0.186 | 0.8585 | 0.422 |
| region_dropout_left_motor_strip_0.140625 | balanced_accuracy | secondary | 109 | 0.6193 | 0.5318 | -0.08751 | -0.1104 | -0.0646 | -0.075 | -0.7253 | 1.819e-11 | 2.171e-10 | 2.055e-07 | 0.004668 | 0.7339 |
| region_dropout_midline_motor_strip_0.046875 | balanced_accuracy | secondary | 109 | 0.6193 | 0.5323 | -0.08699 | -0.1086 | -0.06533 | -0.075 | -0.7627 | 2.629e-12 | 3.064e-11 | 1.743e-09 | 0.03097 | 0.7706 |
| region_dropout_right_motor_strip_0.140625 | balanced_accuracy | secondary | 109 | 0.6193 | 0.5294 | -0.08983 | -0.112 | -0.06766 | -0.085 | -0.7691 | 1.943e-12 | 6.435e-11 | 1.312e-10 | 0.07927 | 0.789 |
| channel_dropout_0.1 | roc_auc | primary | 109 | 0.655 | 0.5849 | -0.07012 | -0.08618 | -0.05406 | -0.0745 | -0.829 | 1.043e-13 | 1.075e-11 | 5.735e-09 | 0.6868 | 0.7798 |
| channel_dropout_0.2 | roc_auc | primary | 109 | 0.655 | 0.5548 | -0.1002 | -0.1219 | -0.07845 | -0.1025 | -0.8748 | 9.209e-15 | 2.459e-12 | 4.979e-10 | 0.8115 | 0.7982 |
| channel_dropout_0.3 | roc_auc | primary | 109 | 0.655 | 0.5436 | -0.1114 | -0.1351 | -0.08761 | -0.116 | -0.8898 | 4.316e-15 | 2.64e-12 | 1.727e-09 | 0.2813 | 0.789 |
| channel_dropout_0.5 | roc_auc | primary | 109 | 0.655 | 0.5277 | -0.1273 | -0.1529 | -0.1016 | -0.145 | -0.9411 | 2.987e-16 | 4.72e-13 | 1.312e-10 | 0.386 | 0.8073 |
| reduced_montage_motor_core | roc_auc | primary | 109 | 0.655 | 0.6483 | -0.006707 | -0.03465 | 0.02123 | -0.02 | -0.04558 | 0.6351 | 0.5467 | 0.6454 | 0.8705 | 0.5138 |
| reduced_montage_motor_extended | roc_auc | primary | 109 | 0.655 | 0.6687 | 0.01365 | -0.01312 | 0.04042 | 0.02 | 0.09684 | 0.3327 | 0.2078 | 0.186 | 0.2523 | 0.4128 |
| region_dropout_left_motor_strip_0.140625 | roc_auc | primary | 109 | 0.655 | 0.5974 | -0.05765 | -0.07704 | -0.03826 | -0.05 | -0.5645 | 5.604e-08 | 6.17e-07 | 0.0001779 | 0.1594 | 0.6514 |
| region_dropout_midline_motor_strip_0.046875 | roc_auc | primary | 109 | 0.655 | 0.6066 | -0.04839 | -0.06558 | -0.0312 | -0.05 | -0.5345 | 2.228e-07 | 2.447e-07 | 1.285e-05 | 0.4809 | 0.6789 |
| region_dropout_right_motor_strip_0.140625 | roc_auc | primary | 109 | 0.655 | 0.5936 | -0.06138 | -0.08334 | -0.03943 | -0.045 | -0.5308 | 2.563e-07 | 1.964e-06 | 1.285e-05 | 0.08966 | 0.6789 |

## Sensitivity summary
| condition | metric | available | role | n_subjects | mean_delta_condition_minus_clean | pct_worse_than_clean | ttest_fdr | wilcoxon_fdr | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| channel_dropout_0.1 | roc_auc | True | primary | 109 | -0.07012 | 0.7798 | 1.043e-13 | 1.075e-11 | primary |
| channel_dropout_0.1 | balanced_accuracy | True | secondary | 109 | -0.09417 | 0.7431 | 9.637e-13 | 4.984e-11 | secondary |
| channel_dropout_0.1 | brier_score | True | calibration | 109 | 0.1442 | 0.9633 | 8.901e-31 | 3.104e-18 | calibration_optional |
| channel_dropout_0.1 | ece | True | calibration | 109 | 0.1123 | 0.8899 | 1.661e-20 | 1.577e-16 | calibration_optional |
| channel_dropout_0.2 | roc_auc | True | primary | 109 | -0.1002 | 0.7982 | 9.209e-15 | 2.459e-12 | primary |
| channel_dropout_0.2 | balanced_accuracy | True | secondary | 109 | -0.1079 | 0.789 | 1.165e-13 | 7.933e-12 | secondary |
| channel_dropout_0.2 | brier_score | True | calibration | 109 | 0.1634 | 0.9633 | 5.949e-31 | 3.104e-18 | calibration_optional |
| channel_dropout_0.2 | ece | True | calibration | 109 | 0.1274 | 0.9083 | 7.895e-21 | 1.209e-16 | calibration_optional |
| channel_dropout_0.3 | roc_auc | True | primary | 109 | -0.1114 | 0.789 | 4.316e-15 | 2.64e-12 | primary |
| channel_dropout_0.3 | balanced_accuracy | True | secondary | 109 | -0.1101 | 0.7706 | 1.12e-13 | 1.075e-11 | secondary |
| channel_dropout_0.3 | brier_score | True | calibration | 109 | 0.1688 | 0.9541 | 4.402e-31 | 3.104e-18 | calibration_optional |
| channel_dropout_0.3 | ece | True | calibration | 109 | 0.1314 | 0.9083 | 3.885e-21 | 1.209e-16 | calibration_optional |
| channel_dropout_0.5 | roc_auc | True | primary | 109 | -0.1273 | 0.8073 | 2.987e-16 | 4.72e-13 | primary |
| channel_dropout_0.5 | balanced_accuracy | True | secondary | 109 | -0.1133 | 0.7706 | 1.12e-13 | 9.205e-12 | secondary |
| channel_dropout_0.5 | brier_score | True | calibration | 109 | 0.1718 | 0.9725 | 5.949e-31 | 3.104e-18 | calibration_optional |
| channel_dropout_0.5 | ece | True | calibration | 109 | 0.1338 | 0.8991 | 6.104e-21 | 1.108e-16 | calibration_optional |
| reduced_montage_motor_core | roc_auc | True | primary | 109 | -0.006707 | 0.5138 | 0.6351 | 0.5467 | primary |
| reduced_montage_motor_core | balanced_accuracy | True | secondary | 109 | -0.007217 | 0.5046 | 0.5767 | 0.6206 | secondary |
| reduced_montage_motor_core | brier_score | True | calibration | 109 | -0.06713 | 0.1835 | 4.023e-13 | 1.501e-11 | calibration_optional |
| reduced_montage_motor_core | ece | True | calibration | 109 | -0.06416 | 0.2569 | 1.607e-09 | 6.039e-09 | calibration_optional |
| reduced_montage_motor_extended | roc_auc | True | primary | 109 | 0.01365 | 0.4128 | 0.3327 | 0.2078 | primary |
| reduced_montage_motor_extended | balanced_accuracy | True | secondary | 109 | 0.01139 | 0.422 | 0.329 | 0.2717 | secondary |
| reduced_montage_motor_extended | brier_score | True | calibration | 109 | -0.04152 | 0.2844 | 4.863e-07 | 6.497e-07 | calibration_optional |
| reduced_montage_motor_extended | ece | True | calibration | 109 | -0.02214 | 0.3486 | 0.0126 | 0.007985 | calibration_optional |
| region_dropout_left_motor_strip_0.140625 | roc_auc | True | primary | 109 | -0.05765 | 0.6514 | 5.604e-08 | 6.17e-07 | primary |
| region_dropout_left_motor_strip_0.140625 | balanced_accuracy | True | secondary | 109 | -0.08751 | 0.7339 | 1.819e-11 | 2.171e-10 | secondary |
| region_dropout_left_motor_strip_0.140625 | brier_score | True | calibration | 109 | 0.1255 | 0.9266 | 1.854e-22 | 1.752e-17 | calibration_optional |
| region_dropout_left_motor_strip_0.140625 | ece | True | calibration | 109 | 0.09754 | 0.8624 | 2.211e-15 | 3.534e-14 | calibration_optional |
| region_dropout_midline_motor_strip_0.046875 | roc_auc | True | primary | 109 | -0.04839 | 0.6789 | 2.228e-07 | 2.447e-07 | primary |
| region_dropout_midline_motor_strip_0.046875 | balanced_accuracy | True | secondary | 109 | -0.08699 | 0.7706 | 2.629e-12 | 3.064e-11 | secondary |
| region_dropout_midline_motor_strip_0.046875 | brier_score | True | calibration | 109 | 0.1297 | 0.9358 | 3.207e-26 | 3.844e-18 | calibration_optional |
| region_dropout_midline_motor_strip_0.046875 | ece | True | calibration | 109 | 0.09933 | 0.8073 | 7.417e-17 | 1.099e-14 | calibration_optional |
| region_dropout_right_motor_strip_0.140625 | roc_auc | True | primary | 109 | -0.06138 | 0.6789 | 2.563e-07 | 1.964e-06 | primary |
| region_dropout_right_motor_strip_0.140625 | balanced_accuracy | True | secondary | 109 | -0.08983 | 0.789 | 1.943e-12 | 6.435e-11 | secondary |
| region_dropout_right_motor_strip_0.140625 | brier_score | True | calibration | 109 | 0.1262 | 0.9083 | 1.901e-25 | 1.762e-17 | calibration_optional |
| region_dropout_right_motor_strip_0.140625 | ece | True | calibration | 109 | 0.1001 | 0.8716 | 1.502e-17 | 1.099e-14 | calibration_optional |

## Channel-dropout slopes
| dataset | pipeline | metric | n_subjects | mean_slope_per_10pct_dropout | slope_ci_low | slope_ci_high | slope_sd | t_statistic_vs_zero | t_p_value_vs_zero | shapiro_p_value_slope | n_harmful_slope | pct_harmful_slope | t_p_value_vs_zero_bh_fdr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PhysionetMotorImagery | csp_lda | balanced_accuracy | 109 | -0.01829 | -0.02243 | -0.01414 | 0.02183 | -8.743 | 3.296e-14 | 0.02859 | 85 | 0.7798 | 3.296e-14 |
| PhysionetMotorImagery | csp_lda | brier_score | 109 | 0.02773 | 0.02445 | 0.03101 | 0.01729 | 16.74 | 8.7e-32 | 0.01668 | 106 | 0.9725 | 3.48e-31 |
| PhysionetMotorImagery | csp_lda | ece | 109 | 0.0216 | 0.01803 | 0.02518 | 0.01883 | 11.98 | 1.517e-21 | 0.01424 | 99 | 0.9083 | 3.035e-21 |
| PhysionetMotorImagery | csp_lda | roc_auc | 109 | -0.02306 | -0.02777 | -0.01834 | 0.02481 | -9.701 | 2.239e-16 | 0.2511 | 86 | 0.789 | 2.985e-16 |

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