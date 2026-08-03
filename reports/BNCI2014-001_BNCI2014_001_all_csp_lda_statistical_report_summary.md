# Statistical reporting pack for `BNCI2014-001_BNCI2014_001_all_csp_lda`

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
| channel_dropout_0.1 | balanced_accuracy | secondary | 9 | 0.7913 | 0.544 | -0.2473 | -0.3382 | -0.1564 | -0.2549 | -2.09 | 0.0004962 | 0.005208 | 0.005208 | 0.3887 | 1 |
| channel_dropout_0.2 | balanced_accuracy | secondary | 9 | 0.7913 | 0.5224 | -0.2689 | -0.3713 | -0.1665 | -0.2711 | -2.018 | 0.0005082 | 0.005208 | 0.005208 | 0.5637 | 1 |
| channel_dropout_0.3 | balanced_accuracy | secondary | 9 | 0.7913 | 0.515 | -0.2763 | -0.3805 | -0.1721 | -0.3187 | -2.038 | 0.0005082 | 0.005208 | 0.005208 | 0.4546 | 1 |
| channel_dropout_0.5 | balanced_accuracy | secondary | 9 | 0.7913 | 0.51 | -0.2813 | -0.3879 | -0.1746 | -0.3254 | -2.027 | 0.0005082 | 0.005208 | 0.005208 | 0.3209 | 1 |
| cross_session_0 | balanced_accuracy | secondary | 9 | 0.7913 | 0.7569 | -0.03437 | -0.08149 | 0.01276 | -0.02443 | -0.5606 | 0.1418 | 0.08024 | 0.0434 | 0.2125 | 0.8889 |
| reduced_montage_motor_core | balanced_accuracy | secondary | 9 | 0.7913 | 0.7005 | -0.09076 | -0.1356 | -0.04596 | -0.08325 | -1.557 | 0.002368 | 0.005208 | 0.005208 | 0.3497 | 1 |
| reduced_montage_motor_extended | balanced_accuracy | secondary | 9 | 0.7913 | 0.7453 | -0.046 | -0.08313 | -0.008875 | -0.03116 | -0.9524 | 0.02655 | 0.01379 | 0.0434 | 0.2911 | 0.8889 |
| region_dropout_left_motor_strip_0.318182 | balanced_accuracy | secondary | 9 | 0.7913 | 0.5385 | -0.2528 | -0.3793 | -0.1263 | -0.2677 | -1.536 | 0.002393 | 0.005208 | 0.005208 | 0.3138 | 1 |
| region_dropout_midline_motor_strip_0.136364 | balanced_accuracy | secondary | 9 | 0.7913 | 0.5868 | -0.2045 | -0.2816 | -0.1274 | -0.2298 | -2.039 | 0.0005082 | 0.005208 | 0.005208 | 0.2039 | 1 |
| region_dropout_right_motor_strip_0.318182 | balanced_accuracy | secondary | 9 | 0.7913 | 0.5094 | -0.2819 | -0.3905 | -0.1733 | -0.2996 | -1.995 | 0.0005263 | 0.005208 | 0.005208 | 0.4829 | 1 |
| channel_dropout_0.1 | roc_auc | primary | 9 | 0.8523 | 0.7378 | -0.1145 | -0.143 | -0.08596 | -0.1117 | -3.083 | 4.774e-05 | 0.005208 | 0.005208 | 0.8371 | 1 |
| channel_dropout_0.2 | roc_auc | primary | 9 | 0.8523 | 0.6871 | -0.1653 | -0.208 | -0.1225 | -0.1857 | -2.974 | 5.266e-05 | 0.005208 | 0.005208 | 0.07233 | 1 |
| channel_dropout_0.3 | roc_auc | primary | 9 | 0.8523 | 0.6496 | -0.2028 | -0.2541 | -0.1514 | -0.2203 | -3.035 | 4.866e-05 | 0.005208 | 0.005208 | 0.1351 | 1 |
| channel_dropout_0.5 | roc_auc | primary | 9 | 0.8523 | 0.6221 | -0.2303 | -0.2876 | -0.1729 | -0.2487 | -3.087 | 4.774e-05 | 0.005208 | 0.005208 | 0.3178 | 1 |
| cross_session_0 | roc_auc | primary | 9 | 0.8523 | 0.853 | 0.0006408 | -0.02137 | 0.02265 | 0.003312 | 0.02238 | 0.9724 | 1 | 1 | 0.5986 | 0.4444 |
| reduced_montage_motor_core | roc_auc | primary | 9 | 0.8523 | 0.7545 | -0.09781 | -0.1492 | -0.04642 | -0.08317 | -1.463 | 0.003095 | 0.005208 | 0.005208 | 0.256 | 1 |
| reduced_montage_motor_extended | roc_auc | primary | 9 | 0.8523 | 0.8014 | -0.05095 | -0.098 | -0.003909 | -0.0342 | -0.8325 | 0.04362 | 0.01379 | 0.0434 | 0.09048 | 0.8889 |
| region_dropout_left_motor_strip_0.318182 | roc_auc | primary | 9 | 0.8523 | 0.7061 | -0.1462 | -0.197 | -0.09537 | -0.155 | -2.211 | 0.0003641 | 0.005208 | 0.005208 | 0.6648 | 1 |
| region_dropout_midline_motor_strip_0.136364 | roc_auc | primary | 9 | 0.8523 | 0.7656 | -0.08678 | -0.13 | -0.0435 | -0.06006 | -1.541 | 0.002393 | 0.005208 | 0.005208 | 0.3637 | 1 |
| region_dropout_right_motor_strip_0.318182 | roc_auc | primary | 9 | 0.8523 | 0.671 | -0.1813 | -0.2667 | -0.09599 | -0.1422 | -1.633 | 0.001837 | 0.005208 | 0.005208 | 0.233 | 1 |

## Sensitivity summary
| condition | metric | available | role | n_subjects | mean_delta_condition_minus_clean | pct_worse_than_clean | ttest_fdr | wilcoxon_fdr | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| channel_dropout_0.1 | roc_auc | True | primary | 9 | -0.1145 | 1 | 4.774e-05 | 0.005208 | primary |
| channel_dropout_0.1 | balanced_accuracy | True | secondary | 9 | -0.2473 | 1 | 0.0004962 | 0.005208 | secondary |
| channel_dropout_0.1 | brier_score | True | calibration | 9 | 0.2836 | 1 | 1.299e-05 | 0.005208 | calibration_optional |
| channel_dropout_0.1 | ece | True | calibration | 9 | 0.3049 | 1 | 1.364e-06 | 0.005208 | calibration_optional |
| channel_dropout_0.2 | roc_auc | True | primary | 9 | -0.1653 | 1 | 5.266e-05 | 0.005208 | primary |
| channel_dropout_0.2 | balanced_accuracy | True | secondary | 9 | -0.2689 | 1 | 0.0005082 | 0.005208 | secondary |
| channel_dropout_0.2 | brier_score | True | calibration | 9 | 0.3039 | 1 | 2.455e-05 | 0.005208 | calibration_optional |
| channel_dropout_0.2 | ece | True | calibration | 9 | 0.3207 | 1 | 3.251e-06 | 0.005208 | calibration_optional |
| channel_dropout_0.3 | roc_auc | True | primary | 9 | -0.2028 | 1 | 4.866e-05 | 0.005208 | primary |
| channel_dropout_0.3 | balanced_accuracy | True | secondary | 9 | -0.2763 | 1 | 0.0005082 | 0.005208 | secondary |
| channel_dropout_0.3 | brier_score | True | calibration | 9 | 0.3151 | 1 | 1.299e-05 | 0.005208 | calibration_optional |
| channel_dropout_0.3 | ece | True | calibration | 9 | 0.3311 | 1 | 1.364e-06 | 0.005208 | calibration_optional |
| channel_dropout_0.5 | roc_auc | True | primary | 9 | -0.2303 | 1 | 4.774e-05 | 0.005208 | primary |
| channel_dropout_0.5 | balanced_accuracy | True | secondary | 9 | -0.2813 | 1 | 0.0005082 | 0.005208 | secondary |
| channel_dropout_0.5 | brier_score | True | calibration | 9 | 0.3253 | 1 | 1.659e-05 | 0.005208 | calibration_optional |
| channel_dropout_0.5 | ece | True | calibration | 9 | 0.3396 | 1 | 1.772e-06 | 0.005208 | calibration_optional |
| cross_session_0 | roc_auc | True | primary | 9 | 0.0006408 | 0.4444 | 0.9724 | 1 | primary |
| cross_session_0 | balanced_accuracy | True | secondary | 9 | -0.03437 | 0.8889 | 0.1418 | 0.08024 | secondary |
| cross_session_0 | brier_score | True | calibration | 9 | 0.03011 | 0.8889 | 0.0562 | 0.06076 | calibration_optional |
| cross_session_0 | ece | True | calibration | 9 | 0.04108 | 0.6667 | 0.02902 | 0.06076 | calibration_optional |
| reduced_montage_motor_core | roc_auc | True | primary | 9 | -0.09781 | 1 | 0.003095 | 0.005208 | primary |
| reduced_montage_motor_core | balanced_accuracy | True | secondary | 9 | -0.09076 | 1 | 0.002368 | 0.005208 | secondary |
| reduced_montage_motor_core | brier_score | True | calibration | 9 | 0.04436 | 0.8889 | 0.01211 | 0.01379 | calibration_optional |
| reduced_montage_motor_core | ece | True | calibration | 9 | -0.008478 | 0.5556 | 0.7509 | 1 | calibration_optional |
| reduced_montage_motor_extended | roc_auc | True | primary | 9 | -0.05095 | 0.8889 | 0.04362 | 0.01379 | primary |
| reduced_montage_motor_extended | balanced_accuracy | True | secondary | 9 | -0.046 | 0.8889 | 0.02655 | 0.01379 | secondary |
| reduced_montage_motor_extended | brier_score | True | calibration | 9 | 0.02105 | 0.8889 | 0.08109 | 0.01379 | calibration_optional |
| reduced_montage_motor_extended | ece | True | calibration | 9 | 0.0001052 | 0.6667 | 0.9855 | 1 | calibration_optional |
| region_dropout_left_motor_strip_0.318182 | roc_auc | True | primary | 9 | -0.1462 | 1 | 0.0003641 | 0.005208 | primary |
| region_dropout_left_motor_strip_0.318182 | balanced_accuracy | True | secondary | 9 | -0.2528 | 1 | 0.002393 | 0.005208 | secondary |
| region_dropout_left_motor_strip_0.318182 | brier_score | True | calibration | 9 | 0.2863 | 1 | 0.0004962 | 0.005208 | calibration_optional |
| region_dropout_left_motor_strip_0.318182 | ece | True | calibration | 9 | 0.3014 | 1 | 0.0001621 | 0.005208 | calibration_optional |
| region_dropout_midline_motor_strip_0.136364 | roc_auc | True | primary | 9 | -0.08678 | 1 | 0.002393 | 0.005208 | primary |
| region_dropout_midline_motor_strip_0.136364 | balanced_accuracy | True | secondary | 9 | -0.2045 | 1 | 0.0005082 | 0.005208 | secondary |
| region_dropout_midline_motor_strip_0.136364 | brier_score | True | calibration | 9 | 0.2236 | 1 | 6e-05 | 0.005208 | calibration_optional |
| region_dropout_midline_motor_strip_0.136364 | ece | True | calibration | 9 | 0.2518 | 1 | 4.174e-05 | 0.005208 | calibration_optional |
| region_dropout_right_motor_strip_0.318182 | roc_auc | True | primary | 9 | -0.1813 | 1 | 0.001837 | 0.005208 | primary |
| region_dropout_right_motor_strip_0.318182 | balanced_accuracy | True | secondary | 9 | -0.2819 | 1 | 0.0005263 | 0.005208 | secondary |
| region_dropout_right_motor_strip_0.318182 | brier_score | True | calibration | 9 | 0.3227 | 1 | 4.774e-05 | 0.005208 | calibration_optional |
| region_dropout_right_motor_strip_0.318182 | ece | True | calibration | 9 | 0.3366 | 1 | 1.299e-05 | 0.005208 | calibration_optional |

## Channel-dropout slopes
| dataset | pipeline | metric | n_subjects | mean_slope_per_10pct_dropout | slope_ci_low | slope_ci_high | slope_sd | t_statistic_vs_zero | t_p_value_vs_zero | shapiro_p_value_slope | n_harmful_slope | pct_harmful_slope | t_p_value_vs_zero_bh_fdr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BNCI2014-001 | csp_lda | balanced_accuracy | 9 | -0.04447 | -0.06162 | -0.02732 | 0.02231 | -5.979 | 0.0003309 | 0.4255 | 9 | 1 | 0.0003309 |
| BNCI2014-001 | csp_lda | brier_score | 9 | 0.05147 | 0.04074 | 0.0622 | 0.01396 | 11.06 | 3.987e-06 | 0.3683 | 9 | 1 | 7.974e-06 |
| BNCI2014-001 | csp_lda | ece | 9 | 0.05308 | 0.04562 | 0.06055 | 0.009711 | 16.4 | 1.926e-07 | 0.5963 | 9 | 1 | 7.706e-07 |
| BNCI2014-001 | csp_lda | roc_auc | 9 | -0.04301 | -0.05472 | -0.03129 | 0.01524 | -8.466 | 2.898e-05 | 0.2002 | 9 | 1 | 3.864e-05 |

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