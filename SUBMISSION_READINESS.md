# Submission readiness

This file summarizes deterministic repository checks for preparing the benchmark for a methods-journal submission. The checks are derived only from files already present in the repository.

## Status

- Ready for release packaging: `true`
- Checks run: 55
- Failed errors: 0
- Failed warnings: 2

## Scope

- Confirms required metadata, provenance, reproducibility, statistical-reporting, validation, result, method-figure, and release-manifest artifacts.
- Does not judge novelty, editorial fit, or clinical claims.
- Does not generate benchmark observations or alter result values.

## Failed checks

- `warning` `manuscript_declarations` `competing_interests_declaration_present`: Author confirmation is required before submission
- `warning` `manuscript_declarations` `permanent_software_doi_present`: Archive the release and add its DOI before submission
