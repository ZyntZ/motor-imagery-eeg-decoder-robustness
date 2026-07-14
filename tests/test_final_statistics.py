import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("final_statistics", ROOT / "scripts" / "final_statistics.py")
final_statistics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(final_statistics)


def test_intervention_classes_include_ok_dev_not_false_high_priority():
    wide = pd.DataFrame(
        {
            "subject": [1, 2, 3, 4, 5],
            "clean_auc": [0.70, 0.70, 0.55, 0.55, 0.80],
            "auc_dropout_0.5": [0.65, 0.45, 0.50, 0.50, 0.55],
            "auc_motor_core": [0.66, 0.62, 0.65, 0.50, 0.57],
            "auc_motor_extended": [0.64, 0.58, 0.61, 0.52, 0.58],
        }
    )
    out = final_statistics.intervention_classes(wide, clean_thr=0.60, fail_thr=0.60)
    by_subject = dict(zip(out["subject"], out["intervention_class"]))

    assert by_subject[1] == "C_ok_dev"
    assert by_subject[2] == "A_high"
    assert by_subject[3] == "B_rescue_candidate"
    assert by_subject[4] == "D_low_clean"
    assert by_subject[5] == "B_fragile"


def test_intervention_class_rates_report_c_ok_dev():
    classes = pd.DataFrame(
        {
            "intervention_class": ["A_high", "C_ok_dev", "D_low_clean"],
            "clean_working": [True, True, False],
            "dropout_failure_at_50pct": [True, False, False],
            "montage_rescue": [True, False, False],
        }
    )
    rates = final_statistics.intervention_class_rates(classes)
    assert "class_C_ok_dev" in set(rates["metric"])
    row = rates.loc[rates["metric"] == "class_C_ok_dev"].iloc[0]
    assert row["numerator"] == 1
    assert row["denominator"] == 3
