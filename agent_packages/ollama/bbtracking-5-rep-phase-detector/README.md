# Package 5: Rep Phase Detector

## Goal

Improve rep segmentation by using smoothed vertical position and speed/phase transitions rather than raw direction flips alone.

## Current Context

- `reps.detect_rep_ranges` currently supports:
  - `direction`
  - `min_rom_px`
  - `min_frames`
  - `smoothing_window`
  - `deadband_px`
- Golden sample expects 7 reps with default settings.
- Tests cover basic direction, smoothing, deadband, velocity loss.

## Target Files

Likely files:

- `reps.py`
- `tests/test_reps.py`
- `tests/test_sample_regression.py` if golden must change.
- `docs/usage.md`
- `TODO.md`

## Required Behavior

Add an optional phase-based detector mode:

- New parameter: `mode="direction"` or `mode="phase"`.
- Default should remain `"direction"` unless there is a strong reason to change.
- Phase mode should:
  - Smooth y-values.
  - Ignore deadband deltas.
  - Track target movement phases.
  - Require target phase to meet min ROM and min frames.
  - Avoid splitting one rep because of short jitter reversals.
- CLI should expose `--rep-detector {direction,phase}`.

Tests:

- A jittery sequence that raw direction would split, but phase mode keeps as one rep.
- A sequence with two real reps.
- Invalid mode error.
- Existing default behavior remains stable.

## Constraints

- Do not add scipy/numpy dependency for this pure logic.
- Keep the function readable.
- Do not silently change existing default output unless golden is intentionally updated.

## Verification

Run:

```bash
/tmp/bbtracking-venv/bin/python -m pytest -q
/tmp/bbtracking-venv/bin/python main.py --input lift.mp4 --output /tmp/bbtracking-phase.avi --roi 300,120,80,40 --no-display --json-output /tmp/bbtracking-phase.json --rep-detector phase
git diff --check
```

## M3 Prompt

Use this package as the implementation brief. Produce exact patches. Preserve default detector behavior first; make phase mode opt-in. Add focused tests before changing CLI docs.
