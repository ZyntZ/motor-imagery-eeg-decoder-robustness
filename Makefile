PYTHON ?= python
CONFIG ?= configs/benchmark.yaml
RESULTS_DIR ?= results
REPORTS_DIR ?= reports
MAX_RETRIES ?= 5
RETRY_WAIT_SECONDS ?= 60
SKIP_FAILED ?= 1
MAX_CONSECUTIVE_FAILURES ?= 5
SKIP_FAILED_FLAG = $(if $(filter 1 true yes,$(SKIP_FAILED)),--skip-failed,)


.PHONY: statistical-report physionet-full-skip-failed physionet-full-strict install-dev test compile-check dry-run list-subjects physionet-full bnci-full analyze-dev10 recommendations-dev10 final-stats-dev10 all-dev10

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

compile-check:
	$(PYTHON) -m compileall -q scripts src

dry-run:
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --dry-run

list-subjects:
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --dataset PhysionetMI --list-subjects
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --dataset BNCI2014-001 --list-subjects

physionet-full:
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-region-dropout --include-cross-session --pipeline csp_lda --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) $(SKIP_FAILED_FLAG) --max-consecutive-failures $(MAX_CONSECUTIVE_FAILURES) --suffix PhysionetMI_all_csp_lda
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-region-dropout --include-cross-session --pipeline riemann_lr --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) $(SKIP_FAILED_FLAG) --max-consecutive-failures $(MAX_CONSECUTIVE_FAILURES) --suffix PhysionetMI_all_riemann_lr

physionet-full-strict:
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-region-dropout --include-cross-session --pipeline csp_lda --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) --suffix PhysionetMI_all_csp_lda
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-region-dropout --include-cross-session --pipeline riemann_lr --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) --suffix PhysionetMI_all_riemann_lr

bnci-full:
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset BNCI2014-001 --include-reduced-montage --include-region-dropout --include-cross-session --pipeline csp_lda --suffix BNCI2014_001_all_csp_lda
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset BNCI2014-001 --include-reduced-montage --include-region-dropout --include-cross-session --pipeline riemann_lr --suffix BNCI2014_001_all_riemann_lr

analyze-dev10:
	$(PYTHON) scripts/analyze_robustness.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix PhysionetMI_dev10

recommendations-dev10:
	$(PYTHON) scripts/recommend_interventions.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix PhysionetMI_dev10

final-stats-dev10:
	$(PYTHON) scripts/final_statistics.py --results-dir $(RESULTS_DIR) --prefix PhysionetMI_dev10

all-dev10: analyze-dev10 recommendations-dev10 final-stats-dev10


physionet-full-skip-failed:
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-region-dropout --include-cross-session --pipeline csp_lda --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) --skip-failed --max-consecutive-failures $(MAX_CONSECUTIVE_FAILURES) --suffix PhysionetMI_all_csp_lda
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-region-dropout --include-cross-session --pipeline riemann_lr --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) --skip-failed --max-consecutive-failures $(MAX_CONSECUTIVE_FAILURES) --suffix PhysionetMI_all_riemann_lr

statistical-report:
	$(PYTHON) scripts/generate_statistical_report.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix PhysionetMI_PhysionetMI_all_riemann_lr
