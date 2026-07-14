import importlib.util
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("generate_methods_figures", ROOT / "scripts" / "generate_methods_figures.py")
generate_methods_figures = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_methods_figures)


def test_methods_figures_are_generated_from_existing_csvs(tmp_path):
    prefix = "BNCI2014-001_BNCI2014_001_all_riemann_lr"
    manifest = generate_methods_figures.generate_figures(ROOT / "results", tmp_path, prefix, "roc_auc")

    assert manifest["prefix"] == prefix
    assert manifest["note"].startswith("Figures are generated from existing repository CSV outputs only")
    assert set(manifest["outputs"]) == {"pipeline_schematic", "robustness_degradation", "intervention_class_counts"}
    for output in manifest["outputs"].values():
        for path in output.values():
            p = Path(path)
            assert p.exists()
            assert p.stat().st_size > 0
    assert (tmp_path / f"{prefix}_methods_figures_manifest.json").exists()


def test_intervention_classes_are_loaded_without_synthetic_rows():
    prefix = "BNCI2014-001_BNCI2014_001_all_riemann_lr"
    classes, source = generate_methods_figures.load_intervention_classes(ROOT / "results", prefix)
    source_df = pd.read_csv(source)

    assert len(classes) == len(source_df)
    assert "intervention_class" in classes.columns
    assert classes["subject"].nunique() == source_df["subject"].nunique()
