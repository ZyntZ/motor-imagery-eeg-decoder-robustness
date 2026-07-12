#!/usr/bin/env bash
set -euo pipefail

CONFIG=${CONFIG:-configs/benchmark.yaml}
PYTHON=${PYTHON:-python}

# Development-result postprocessing from saved real CSVs.
$PYTHON scripts/analyze_robustness.py --results-dir results --reports-dir reports --prefix PhysionetMI_dev10
$PYTHON scripts/recommend_interventions.py --results-dir results --reports-dir reports --prefix PhysionetMI_dev10
$PYTHON scripts/final_statistics.py --results-dir results --prefix PhysionetMI_dev10

# Full manuscript runs. Uncomment when MOABB downloads are permitted and runtime is available.
# $PYTHON scripts/run_benchmark.py --config "$CONFIG" --download-and-run --dataset PhysionetMI --include-reduced-montage --include-cross-session --pipeline csp_lda --suffix PhysionetMI_all_csp_lda
# $PYTHON scripts/run_benchmark.py --config "$CONFIG" --download-and-run --dataset PhysionetMI --include-reduced-montage --include-cross-session --pipeline riemann_lr --suffix PhysionetMI_all_riemann_lr
# $PYTHON scripts/run_benchmark.py --config "$CONFIG" --download-and-run --dataset BNCI2014-001 --include-reduced-montage --include-cross-session --pipeline csp_lda --suffix BNCI2014_001_all_csp_lda
# $PYTHON scripts/run_benchmark.py --config "$CONFIG" --download-and-run --dataset BNCI2014-001 --include-reduced-montage --include-cross-session --pipeline riemann_lr --suffix BNCI2014_001_all_riemann_lr
