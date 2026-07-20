# Data provenance

This repository contains code and derived benchmark outputs derived from EEG datasets accessed through MOABB/MNE wrappers.

Included BNCI2014-001 outputs:

- `BNCI2014-001_BNCI2014_001_all_csp_lda*`: BNCI2014-001 subjects 1-9 with CSP+LDA.
- `BNCI2014-001_BNCI2014_001_all_riemann_lr*`: BNCI2014-001 subjects 1-9 with a Riemannian tangent-space logistic regression baseline.

Raw EEG data are not bundled. Reproduction requires downloading datasets through MOABB/MNE and following the dataset providers' license requirements.

## Access, licensing, and original-participant records

- PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0: open access under the Open Data Commons Attribution License v1.0; dataset DOI: https://doi.org/10.13026/C28G6P.
- BNCI2014-001: open access through the BNCI Horizon 2020 database under the Creative Commons Attribution-NoDerivatives 4.0 International License; licensor: Institute for Knowledge Discovery, Graz University of Technology.
- This repository redistributes neither raw EEG nor participant identifiers. The analyses use data obtained through MOABB/MNE and publish derived numerical benchmark outputs.
- The public PhysioNet page, BNCI Horizon 2020 dataset card, and BNCI2014-001 description reviewed for this release do not state original ethics-committee names, approval identifiers, or consent wording. These details are therefore not inferred. Questions requiring acquisition-level documentation should be directed to the original data custodians.


## Full PhysioNet release outputs

- `PhysionetMI_PhysionetMI_all_csp_lda*`: 109 participants; fold-level and participant-level outputs are included.
- `PhysionetMI_PhysionetMI_all_riemann_lr*`: 109 participants; 25,070 fold/repeat rows and 1,090 participant-condition rows are included. Fold-to-participant aggregation passed all validation checks.
- Both full PhysioNet summaries retain the named left, midline, and right motor-strip dropout conditions. Direct decoder comparison matches these anatomical conditions without averaging or imputation.
- PhysioNet cross-session rows were not available. Cross-session results in the manuscript are restricted to BNCI2014-001 (`n=9`).
