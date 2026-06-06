# Package 6: Fixture Library

## Goal

Prepare the repo for multiple lift video fixtures without bloating tests or committing unnecessary generated outputs.

## Current Context

- `lift.mp4` is the only sample input.
- `tests/fixtures/sample_metrics.json` stores compact golden metrics.
- `tests/test_sample_regression.py` runs the real sample video.

## Target Files

Likely files:

- `tests/fixtures/README.md`
- `tests/fixtures/sample_metrics.json`
- `tests/test_sample_regression.py`
- Add `tests/fixtures/lifts.json` or similar manifest.
- `docs/usage.md` or new `docs/testing.md`.
- `.gitignore` if generated fixture outputs need ignoring.
- `TODO.md`.

## Required Behavior

Add a fixture manifest describing each sample:

- name
- video path
- roi
- tracker
- scale_px_per_meter
- expected metrics fixture path
- optional marks/skips

Refactor `test_sample_regression.py` to load fixture cases from the manifest.

Keep only compact expected metrics in git. Do not commit generated videos or full frame dumps.

## Constraints

- Do not add more videos in this package.
- Do not remove existing `lift.mp4`.
- Keep current single fixture test passing.
- Keep manifest readable.

## Verification

Run:

```bash
/tmp/bbtracking-venv/bin/python -m pytest -q tests/test_sample_regression.py
/tmp/bbtracking-venv/bin/python -m pytest -q
git diff --check
```

## M3 Prompt

Use this package as the implementation brief. Produce exact patches. Refactor the regression test to use a manifest while preserving the current sample metrics and expected 7-rep behavior.
