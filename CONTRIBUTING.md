# Contributing

Contributions that improve reproducibility, extend a documented benchmark
condition, or make the outputs easier to inspect are welcome.

## Before opening a pull request

For a substantial benchmark extension, please open an issue first. Describe:

- the scientific question and intended estimand;
- the dataset, participants, and evaluation unit;
- whether corruption occurs during training, testing, or both;
- how random schedules will be seeded and paired across pipelines;
- which existing result tables or claims, if any, would change.

A reference, recording-system rationale, or small empirical example is helpful
for new signal-corruption models.

## Development setup

```bash
git clone https://github.com/ZyntZ/motor-imagery-eeg-decoder-robustness.git
cd motor-imagery-eeg-decoder-robustness
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[all]"
python -m pytest
```

On Windows PowerShell, activate the environment with
`.venv\Scripts\Activate.ps1`.

## Contribution types

Useful contributions include:

- a failing test or minimal reproduction for a bug;
- validation on an additional public motor-imagery dataset;
- a documented stressor such as intermittent contact or impedance-related noise;
- comparison with a principled channel-selection method;
- runtime, checkpointing, documentation, or accessibility improvements.

Raw EEG must not be committed. Keep dataset downloads in the configured MOABB
or MNE data directory and follow the source dataset's license.

## Reproducibility requirements

- Keep train/test separation explicit. Test-time corruption must not leak into
  training unless adaptation is the stated condition.
- Use deterministic seeds. When comparing pipelines, use matched folds and
  matched corruption schedules.
- Treat participants, not folds or dropout repeats, as independent units for
  population inference.
- Record protocol version, configuration, software environment, and provenance.
- Do not overwrite committed result tables with a different protocol under the
  same filename.
- State limitations and distinguish exploratory from confirmatory analyses.

## Pull-request checklist

- [ ] The change is focused and described in plain language.
- [ ] Tests pass with `python -m pytest`.
- [ ] New behavior has a test or a documented reason why testing is impractical.
- [ ] Configuration and output-schema changes are documented.
- [ ] No raw participant data, credentials, or machine-specific paths are added.
- [ ] Statistical claims use participant-level summaries.
- [ ] README, `REPRODUCIBILITY.md`, or provenance documentation is updated where needed.

## Reporting problems

For software errors, include the command, configuration path, Python version,
operating system, complete traceback, and the smallest subject/dataset subset
that reproduces the problem. For result discrepancies, also include the
protocol version and run signature stored in the output.
