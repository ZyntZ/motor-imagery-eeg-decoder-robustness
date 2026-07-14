import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("generate_statistical_report", ROOT / "scripts" / "generate_statistical_report.py")
generate_statistical_report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_statistical_report)


def test_generate_statistical_report_on_existing_dev10_subject_summary():
    subj = generate_statistical_report.load_subject_summary(ROOT / "results", "PhysionetMI_dev10")
    audit = generate_statistical_report.methods_audit(subj)
    paired = generate_statistical_report.paired_condition_effects(subj)
    slopes = generate_statistical_report.channel_dropout_slopes(subj)
    slopes_pop = generate_statistical_report.slope_population_summary(slopes)
    table = generate_statistical_report.report_table(paired)

    assert not audit.empty
    assert "duplicate_subject_condition_rows" in set(audit["check"])
    assert not paired.empty
    assert {"roc_auc", "balanced_accuracy"}.issubset(set(paired["metric"]))
    assert not slopes.empty
    assert not slopes_pop.empty
    assert not table.empty
    assert table["condition"].str.contains("channel_dropout").any()


def test_condition_labels_are_stable_for_existing_rows():
    subj = generate_statistical_report.load_subject_summary(ROOT / "results", "PhysionetMI_dev10")
    labelled = generate_statistical_report.add_condition(subj)
    assert "clean_all_channels" in set(labelled["condition"])
    assert labelled.loc[labelled["stressor"].eq("reduced_montage"), "condition"].str.startswith("reduced_montage_").all()
