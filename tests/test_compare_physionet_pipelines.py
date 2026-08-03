import importlib.util
import math
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "compare_physionet_pipelines", ROOT / "scripts" / "compare_physionet_pipelines.py"
)
compare_physionet_pipelines = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare_physionet_pipelines)


def test_exact_binomial_interval_boundary_cases():
    lo, hi = compare_physionet_pipelines.proportion_ci(0, 10)
    assert lo == 0.0 and 0.0 < hi < 1.0
    lo, hi = compare_physionet_pipelines.proportion_ci(10, 10)
    assert 0.0 < lo < 1.0 and hi == 1.0
    lo, hi = compare_physionet_pipelines.proportion_ci(0, 0)
    assert math.isnan(lo) and math.isnan(hi)


def test_markdown_renderer_has_no_optional_tabulate_dependency():
    frame = pd.DataFrame({"condition": ["clean"], "difference": [-0.02]})
    rendered = compare_physionet_pipelines.dataframe_to_markdown(frame)
    assert rendered.startswith("| condition | difference |")
    assert "| clean | -0.02 |" in rendered


def test_latex_renderer_has_no_optional_jinja_dependency(monkeypatch):
    frame = pd.DataFrame({
        "condition": ["dropout_0.5"],
        "n_subjects": [109],
        "mean_paired_difference_csp_minus_riemann": [-0.027],
        "ci95_low": [-0.048],
        "ci95_high": [-0.007],
        "cohens_dz": [-0.251],
        "paired_t_p_value_bh_fdr": [0.014],
        "wilcoxon_p_value_bh_fdr": [0.028],
        "proportion_csp_better": [48 / 109],
    })
    monkeypatch.setattr(pd.DataFrame, "to_latex", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("to_latex called")))
    rendered = compare_physionet_pipelines.tex_table(frame)
    assert r"dropout\_0.5" in rendered
    assert r"\begin{tabular}{lrrrrrrrr}" in rendered
    assert "-0.027" in rendered


def test_committed_physionet_comparison_is_subject_paired_and_reproducible():
    csp = pd.read_csv(ROOT / "results" / "PhysionetMI_PhysionetMI_all_csp_lda_subject_summary.csv")
    riemann = pd.read_csv(ROOT / "results" / "PhysionetMI_PhysionetMI_all_riemann_lr_subject_summary.csv")
    observed, pairs, notes = compare_physionet_pipelines.compare(csp, riemann)
    committed = pd.read_csv(ROOT / "results" / "PhysionetMI_csp_lda_vs_riemann_lr_paired_comparison.csv")

    assert len(observed) == 10
    assert observed["n_subjects"].eq(109).all()
    assert not pairs.duplicated(["subject", "condition"]).any()
    assert any("matched directly" in note for note in notes)
    merged = observed.merge(committed, on="condition", suffixes=("_new", "_committed"), validate="one_to_one")
    for column in ["mean_paired_difference_csp_minus_riemann", "cohens_dz"]:
        delta = (merged[f"{column}_new"] - merged[f"{column}_committed"]).abs().max()
        assert delta < 1e-12
    assert (
        observed["proportion_csp_better_ci95_low"]
        <= observed["proportion_csp_better_ci95_high"]
    ).all()


def test_difference_in_degradation_uses_each_decoder_clean_baseline():
    csp = pd.read_csv(ROOT / "results" / "PhysionetMI_PhysionetMI_all_csp_lda_subject_summary.csv")
    riemann = pd.read_csv(ROOT / "results" / "PhysionetMI_PhysionetMI_all_riemann_lr_subject_summary.csv")
    _, pairs, _ = compare_physionet_pipelines.compare(csp, riemann)
    summary, subject_values = compare_physionet_pipelines.difference_in_degradation(pairs)
    assert len(summary) == 9
    assert summary["n_subjects"].eq(109).all()
    committed = pd.read_csv(
        ROOT / "results" / "PhysionetMI_csp_lda_vs_riemann_lr_difference_in_degradation.csv"
    )
    merged = summary.merge(
        committed,
        on="condition",
        suffixes=("_new", "_committed"),
        validate="one_to_one",
    )
    for column in ["mean_difference_in_degradation_csp_minus_riemann", "cohens_dz"]:
        delta = (merged[f"{column}_new"] - merged[f"{column}_committed"]).abs().max()
        assert delta < 1e-12
    dropout50 = summary.loc[summary["condition"].eq("dropout_0.5")].iloc[0]
    assert dropout50["ci95_low"] < 0 < dropout50["ci95_high"]
    assert not subject_values.duplicated(["subject", "condition"]).any()

def test_compare_rejects_missing_subject_condition_pairs():
    csp = pd.DataFrame({
        "subject": [1, 1],
        "stressor": ["clean", "channel_dropout"],
        "dropout_fraction": [0.0, 0.5],
        "montage": ["full", "full"],
        "roc_auc": [0.7, 0.6],
    })
    riemann = csp.iloc[[0]].copy()

    with pytest.raises(ValueError, match="different subject-condition pairs"):
        compare_physionet_pipelines.compare(csp, riemann)



def test_paired_comparison_figure_is_written(tmp_path):
    csp = pd.read_csv(ROOT / "results" / "PhysionetMI_PhysionetMI_all_csp_lda_subject_summary.csv")
    riemann = pd.read_csv(ROOT / "results" / "PhysionetMI_PhysionetMI_all_riemann_lr_subject_summary.csv")
    table, _, _ = compare_physionet_pipelines.compare(csp, riemann)
    output = tmp_path / "paired_comparison.pdf"
    compare_physionet_pipelines.paired_comparison_figure(table, output)
    assert output.exists()
    assert output.stat().st_size > 1000
