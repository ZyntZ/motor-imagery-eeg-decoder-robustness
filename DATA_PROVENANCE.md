# Data provenance

This repository contains code and example benchmark outputs derived from EEG datasets accessed through MOABB/MNE wrappers.

Included example outputs:

- `PhysionetMI_dev10*`: development subset using PhysioNetMI subjects 1-10.
- `BNCI2014-001_BNCI2014_001_all_csp_lda*`: BNCI2014-001 subjects 1-9 with CSP+LDA.
- `BNCI2014-001_BNCI2014_001_all_riemann_lr*`: BNCI2014-001 subjects 1-9 with a Riemannian tangent-space logistic regression baseline.

Raw EEG data are not bundled. Reproduction requires downloading datasets through MOABB/MNE and following the dataset providers' license requirements.

The PhysioNetMI `dev10` files are retained as development artifacts. They should not be used as final population-level evidence without rerunning the full planned benchmark.
