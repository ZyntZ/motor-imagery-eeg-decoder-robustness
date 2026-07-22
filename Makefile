PYTHON ?= python
CONFIG ?= configs/benchmark.yaml
RESULTS_DIR ?= results
REPORTS_DIR ?= reports
VALIDATION_DIR ?= artifacts/validation
MANIFEST_DIR ?= artifacts/manifests
PREFIX ?= PhysionetMI_PhysionetMI_all_riemann_lr
EXPECTED_SUBJECTS ?= 109
PHYSIONET_FULL_PREFIXES ?= PhysionetMI_PhysionetMI_all_riemann_lr PhysionetMI_PhysionetMI_all_csp_lda
MAX_RETRIES ?= 5
RETRY_WAIT_SECONDS ?= 60
SKIP_FAILED ?= 1
MAX_CONSECUTIVE_FAILURES ?= 5
SKIP_FAILED_FLAG = $(if $(filter 1 true yes,$(SKIP_FAILED)),--skip-failed,)


.PHONY: manuscript compare-physionet-pipelines install-lock  physionet-csp-preflight physionet-csp-full postprocess-physionet-full-available refresh-full-summaries postprocess-full statistical-report-full install-eeg ensure-eeg install-reports ensure-reports validate-physionet-full analyze-full final-stats-full all-full publication-check release-archive archive-audit release-manifest methods-figures statistical-reports validate-bnci validate-results statistical-report physionet-full-skip-failed physionet-full-strict install-dev test compile-check dry-run list-subjects physionet-full bnci-full

install-lock:
	$(PYTHON) -m pip install -r requirements-lock.txt

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

install-eeg:
	$(PYTHON) -m pip install -e ".[eeg]"

ensure-eeg:
	@$(PYTHON) -c "import mne, moabb, pyriemann" >/dev/null 2>&1 || { \
		echo "EEG dependencies are missing; installing the eeg extra with $(PYTHON)..."; \
		$(PYTHON) -m pip install -e ".[eeg]"; \
	}
	@$(PYTHON) -c "import mne, moabb, pyriemann" >/dev/null 2>&1 || { \
		echo 'EEG dependency installation failed. Run: $(PYTHON) -m pip install -e ".[eeg]"'; \
		exit 1; \
	}

install-reports:
	$(PYTHON) -m pip install -e ".[reports]"

ensure-reports:
	@$(PYTHON) -c "import matplotlib, plotly, seaborn" >/dev/null 2>&1 || { \
		echo "Reporting dependencies are missing; installing the reports extra with $(PYTHON)..."; \
		$(PYTHON) -m pip install -e ".[reports]"; \
	}
	@$(PYTHON) -c "import matplotlib, plotly, seaborn" >/dev/null 2>&1 || { \
		echo 'Reporting dependency installation failed. Run: $(PYTHON) -m pip install -e ".[reports]"'; \
		exit 1; \
	}

test:
	$(PYTHON) -m pytest

compile-check:
	$(PYTHON) -m compileall -q scripts src

manuscript:
	@if command -v latexmk >/dev/null 2>&1; then \
		cd manuscript && latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript.tex; \
	elif command -v pdflatex >/dev/null 2>&1; then \
		cd manuscript && pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex >/dev/null && pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex >/dev/null; \
	else \
		echo "latexmk or pdflatex is required to build manuscript/manuscript.pdf"; exit 1; \
	fi
	@rm -f manuscript/manuscript.aux manuscript/manuscript.log manuscript/manuscript.out manuscript/manuscript.fls manuscript/manuscript.fdb_latexmk

dry-run:
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --dry-run

list-subjects: ensure-eeg
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --dataset PhysionetMI --list-subjects
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --dataset BNCI2014-001 --list-subjects

physionet-csp-preflight: ensure-eeg
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --subjects 1 --include-reduced-montage --include-region-dropout --include-cross-session --pipeline csp_lda --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) --max-consecutive-failures 1 --suffix Physionet_csp_preflight

physionet-csp-full: ensure-eeg
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-region-dropout --include-cross-session --pipeline csp_lda --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) $(SKIP_FAILED_FLAG) --max-consecutive-failures $(MAX_CONSECUTIVE_FAILURES) --suffix PhysionetMI_all_csp_lda

physionet-full: ensure-eeg physionet-csp-full
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-region-dropout --include-cross-session --pipeline riemann_lr --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) $(SKIP_FAILED_FLAG) --max-consecutive-failures $(MAX_CONSECUTIVE_FAILURES) --suffix PhysionetMI_all_riemann_lr

physionet-full-strict: ensure-eeg
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-region-dropout --include-cross-session --pipeline csp_lda --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) --suffix PhysionetMI_all_csp_lda
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-region-dropout --include-cross-session --pipeline riemann_lr --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) --suffix PhysionetMI_all_riemann_lr

bnci-full: ensure-eeg
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset BNCI2014-001 --include-reduced-montage --include-region-dropout --include-cross-session --pipeline csp_lda --suffix BNCI2014_001_all_csp_lda
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset BNCI2014-001 --include-reduced-montage --include-region-dropout --include-cross-session --pipeline riemann_lr --suffix BNCI2014_001_all_riemann_lr


physionet-full-skip-failed: ensure-eeg
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-region-dropout --include-cross-session --pipeline csp_lda --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) --skip-failed --max-consecutive-failures $(MAX_CONSECUTIVE_FAILURES) --suffix PhysionetMI_all_csp_lda
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG) --download-and-run --dataset PhysionetMI --include-reduced-montage --include-region-dropout --include-cross-session --pipeline riemann_lr --max-retries $(MAX_RETRIES) --retry-wait-seconds $(RETRY_WAIT_SECONDS) --skip-failed --max-consecutive-failures $(MAX_CONSECUTIVE_FAILURES) --suffix PhysionetMI_all_riemann_lr


refresh-full-summaries:
	$(PYTHON) scripts/refresh_benchmark_summaries.py --results-dir $(RESULTS_DIR) --prefix $(PREFIX) --recover-from-checkpoints --allow-existing-subject-summary --expected-subjects $(EXPECTED_SUBJECTS)

statistical-report-full:
	$(PYTHON) scripts/generate_statistical_report.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix $(PREFIX)

postprocess-full: ensure-reports
	$(PYTHON) scripts/refresh_benchmark_summaries.py --results-dir $(RESULTS_DIR) --prefix $(PREFIX) --recover-from-checkpoints --allow-existing-subject-summary --expected-subjects $(EXPECTED_SUBJECTS)
	@if [ -f "$(RESULTS_DIR)/$(PREFIX)_results.csv" ]; then \
		$(PYTHON) scripts/validate_results.py --results-dir $(RESULTS_DIR) --reports-dir $(VALIDATION_DIR) --prefix $(PREFIX) --expected-subjects $(EXPECTED_SUBJECTS) --allow-warnings; \
	else \
		$(PYTHON) scripts/validate_results.py --results-dir $(RESULTS_DIR) --reports-dir $(VALIDATION_DIR) --prefix $(PREFIX) --expected-subjects $(EXPECTED_SUBJECTS) --allow-missing-fold-results --allow-warnings; \
	fi
	$(PYTHON) scripts/generate_statistical_report.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix $(PREFIX)
	$(PYTHON) scripts/analyze_robustness.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix $(PREFIX)
	$(PYTHON) scripts/final_statistics.py --results-dir $(RESULTS_DIR) --prefix $(PREFIX)
	$(PYTHON) scripts/mixed_model_diagnostics.py --results-dir $(RESULTS_DIR) --prefix $(PREFIX)

postprocess-physionet-full-available: ensure-reports
	@set -e; processed=0; \
	for pfx in $(PHYSIONET_FULL_PREFIXES); do \
		echo "==> Probing prefix: $$pfx"; \
		set +e; \
		$(PYTHON) scripts/refresh_benchmark_summaries.py --results-dir $(RESULTS_DIR) --prefix "$$pfx" --probe; \
		status=$$?; \
		set -e; \
		if [ "$$status" -eq 0 ]; then \
			$(MAKE) --no-print-directory postprocess-full PREFIX="$$pfx" EXPECTED_SUBJECTS=$(EXPECTED_SUBJECTS); \
			processed=$$((processed + 1)); \
		elif [ "$$status" -eq 2 ]; then \
			echo "SKIP: no completed outputs found for $$pfx"; \
		else \
			echo "ERROR: source probe failed for $$pfx with exit code $$status"; \
			exit "$$status"; \
		fi; \
	done; \
	if [ "$$processed" -eq 0 ]; then \
		echo "ERROR: no completed full PhysioNet pipeline outputs were found."; \
		exit 1; \
	fi

analyze-full: ensure-reports
	$(PYTHON) scripts/analyze_robustness.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix $(PREFIX)

recommendations-full: ensure-reports

final-stats-full:
	$(PYTHON) scripts/final_statistics.py --results-dir $(RESULTS_DIR) --prefix $(PREFIX)

all-full: analyze-full final-stats-full

validate-physionet-full:
	@set -e; found=0; \
	for prefix in PhysionetMI_PhysionetMI_all_csp_lda PhysionetMI_PhysionetMI_all_riemann_lr; do \
		if [ -f "$(RESULTS_DIR)/$${prefix}_subject_summary.csv" ]; then \
			found=1; \
			if [ -f "$(RESULTS_DIR)/$${prefix}_results.csv" ]; then \
				$(PYTHON) scripts/validate_results.py --results-dir $(RESULTS_DIR) --reports-dir $(VALIDATION_DIR) --prefix "$${prefix}" --expected-subjects 109 --allow-warnings; \
			else \
				$(PYTHON) scripts/validate_results.py --results-dir $(RESULTS_DIR) --reports-dir $(VALIDATION_DIR) --prefix "$${prefix}" --expected-subjects 109 --allow-missing-fold-results --allow-warnings; \
			fi; \
		fi; \
	done; \
	if [ "$$found" -eq 0 ]; then echo "No full PhysioNet subject summaries found; skipping optional full-run validation."; fi

validate-bnci:
	$(PYTHON) scripts/validate_results.py --results-dir $(RESULTS_DIR) --reports-dir $(VALIDATION_DIR) --prefix BNCI2014-001_BNCI2014_001_all_csp_lda --expected-subjects 9 --allow-warnings
	$(PYTHON) scripts/validate_results.py --results-dir $(RESULTS_DIR) --reports-dir $(VALIDATION_DIR) --prefix BNCI2014-001_BNCI2014_001_all_riemann_lr --expected-subjects 9 --allow-warnings

validate-results: validate-bnci validate-physionet-full

statistical-report:
	$(PYTHON) scripts/generate_statistical_report.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix BNCI2014-001_BNCI2014_001_all_riemann_lr

statistical-reports:
	$(PYTHON) scripts/generate_statistical_report.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix BNCI2014-001_BNCI2014_001_all_csp_lda
	$(PYTHON) scripts/generate_statistical_report.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix BNCI2014-001_BNCI2014_001_all_riemann_lr
	$(PYTHON) scripts/generate_statistical_report.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix PhysionetMI_PhysionetMI_all_riemann_lr
	$(PYTHON) scripts/generate_statistical_report.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix PhysionetMI_PhysionetMI_all_csp_lda

mixed-model-diagnostics:
	$(PYTHON) scripts/mixed_model_diagnostics.py --results-dir $(RESULTS_DIR) --prefix PhysionetMI_PhysionetMI_all_csp_lda
	$(PYTHON) scripts/mixed_model_diagnostics.py --results-dir $(RESULTS_DIR) --prefix PhysionetMI_PhysionetMI_all_riemann_lr

compare-physionet-pipelines:
	$(PYTHON) scripts/compare_physionet_pipelines.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR)

methods-figures:
	$(PYTHON) scripts/generate_methods_figures.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --prefix PhysionetMI_PhysionetMI_all_riemann_lr --metric roc_auc

release-manifest: validate-results statistical-reports mixed-model-diagnostics compare-physionet-pipelines methods-figures
	$(PYTHON) scripts/build_release_manifest.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR) --output $(MANIFEST_DIR)/release_manifest.json

submission-readiness: release-manifest
	$(PYTHON) scripts/generate_submission_readiness.py --results-dir $(RESULTS_DIR) --reports-dir $(REPORTS_DIR)

archive-audit: submission-readiness
	$(PYTHON) scripts/build_release_archive.py --audit-only

release-archive: archive-audit
	$(PYTHON) scripts/build_release_archive.py --output dist/MI_EEG_repository_simplification_v0.3.1.zip

publication-check: compile-check test submission-readiness archive-audit
