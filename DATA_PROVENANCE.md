# Data provenance

This repository contains code and example benchmark outputs derived from EEG datasets accessed through MOABB/MNE wrappers.

Included example outputs:

- `BNCI2014-001_BNCI2014_001_all_csp_lda*`: BNCI2014-001 subjects 1-9 with CSP+LDA.
- `BNCI2014-001_BNCI2014_001_all_riemann_lr*`: BNCI2014-001 subjects 1-9 with a Riemannian tangent-space logistic regression baseline.

Raw EEG data are not bundled. Reproduction requires downloading datasets through MOABB/MNE and following the dataset providers' license requirements.


## Full PhysioNet release outputs

- `PhysionetMI_PhysionetMI_all_csp_lda*`: 109 participants; fold-level and participant-level outputs are included.
- `PhysionetMI_PhysionetMI_all_riemann_lr*`: 109 participants; 25,070 fold/repeat rows and 1,090 participant-condition rows are included. Fold-to-participant aggregation passed all validation checks.
- Both full PhysioNet summaries retain the named left, midline, and right motor-strip dropout conditions. Direct decoder comparison matches these anatomical conditions without averaging or imputation.
- PhysioNet cross-session rows were not available. Cross-session results in the manuscript are restricted to BNCI2014-001 (`n=9`).
