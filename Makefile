PYTHON ?= python
CONFIG ?= configs/benchmark.yaml
RESULTS_DIR ?= results
REPORTS_DIR ?= reports

.PHONY: dry-run list-subjects physionet-full bnci-full analyze-dev10 recommendations-dev10 final-stats-dev10 all-dev10

dry-run:
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --dry-run

list-subjects:
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --dataset PhysionetMI --list-subjects
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --dataset BNCI2014-001 --list-subjects

physionet-full:
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-cross-session --pipeline csp_lda --suffix PhysionetMI_all_csp_lda
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-cross-session --pipeline riemann_lr --suffix PhysionetMI_all_riemann_lr

bnci-full:
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset BNCI2014-001 --include-reduced-montage --include-cross-session --pipeline csp_lda --suffix BNCI2014_001_all_csp_lda
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset BNCI2014-001 --include-reduced-montage --include-cross-session --pipeline riemann_lr --suffix BNCI2014_001_all_riemann_lr

analyze-dev10:
	$(PYTHON) scripts/analyze_robustness.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix PhysionetMI_dev10

recommendations-dev10:
	$(PYTHON) scripts/recommend_interventions.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix PhysionetMI_dev10

final-stats-dev10:
	$(PYTHON) scripts/final_statistics.py --results-dir $(RESULTS_DIR) --prefix PhysionetMI_dev10

all-dev10: analyze-dev10 recommendations-dev10 final-stats-dev10 publication-artifacts

.PHONY: publication-artifacts
publication-artifacts:
	$(PYTHON) scripts/generate_publication_artifacts.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR)
	$(PYTHON) scripts/generate_submission_package.py --repo-root . --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR)

.PHONY: jnm-package
jnm-package:
	$(PYTHON) scripts/generate_jnm_submission_package.py --repo-root . --results-dir $(RESULTS_DIR)
