from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_full_data_targets_require_eeg_dependencies():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for target in [
        "list-subjects",
        "physionet-full",
        "physionet-full-strict",
        "physionet-full-skip-failed",
        "bnci-full",
    ]:
        assert f"{target}: ensure-eeg" in makefile


def test_eeg_install_uses_same_configured_python():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert '$(PYTHON) -m pip install -e ".[eeg]"' in makefile
    assert '$(PYTHON) -c "import mne, moabb, pyriemann"' in makefile


def test_postprocessing_targets_require_reporting_dependencies():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for target in ["analyze-dev10", "recommendations-dev10", "analyze-full", "recommendations-full"]:
        assert f"{target}: ensure-reports" in makefile
    assert '$(PYTHON) -m pip install -e ".[reports]"' in makefile
    assert '$(PYTHON) -c "import matplotlib, plotly, seaborn"' in makefile


def test_validation_includes_completed_full_physionet_outputs():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "validate-results: validate-dev10 validate-bnci validate-physionet-full" in makefile
    assert "PhysionetMI_PhysionetMI_all_csp_lda" in makefile
    assert "PhysionetMI_PhysionetMI_all_riemann_lr" in makefile


def test_available_full_postprocess_target_skips_absent_pipeline():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "postprocess-physionet-full-available: ensure-reports" in makefile
    assert "PHYSIONET_FULL_PREFIXES" in makefile
    assert 'echo "SKIP: no completed outputs found for $$pfx"' in makefile
    assert "--probe" in makefile
    assert 'status=$$?' in makefile
    phony = next(line for line in makefile.splitlines() if line.startswith(".PHONY:"))
    assert "postprocess-physionet-full-available" in phony


def test_readme_does_not_instruct_unconditional_csp_postprocessing():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "# or for CSP + LDA:" not in readme
    assert "Run the CSP + LDA command only if" in readme
    assert "make postprocess-physionet-full-available" in readme


def test_publication_targets_include_full_physionet_outputs():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    full = "PhysionetMI_PhysionetMI_all_riemann_lr"
    statistical_block = makefile.split("statistical-reports:", 1)[1].split("methods-figures:", 1)[0]
    figures_block = makefile.split("methods-figures:", 1)[1].split("release-manifest:", 1)[0]
    assert full in statistical_block
    assert full in figures_block



def test_physionet_csp_has_dedicated_preflight_and_full_targets():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "physionet-csp-preflight: ensure-eeg" in makefile
    assert "physionet-csp-full: ensure-eeg" in makefile
    csp_block = makefile.split("physionet-csp-full:", 1)[1].split("physionet-full:", 1)[0]
    assert "--pipeline csp_lda" in csp_block
    assert "--suffix PhysionetMI_all_csp_lda" in csp_block
    assert "riemann_lr" not in csp_block
