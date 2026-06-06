# Package 4: Calibration Workflow

## Goal

Add a user-visible calibration workflow around `scale_px_per_meter` so the prototype and service can derive scale from a reference length.

## Current Context

- CLI supports:
  - `--scale-px-per-meter`
  - `--reference-px`
  - `--reference-m`
- `metrics.scale_from_reference(reference_px, reference_m)` exists.
- Service `/analyze` currently accepts `scale_px_per_meter` only.
- Prototype currently has a Scale field.

## Target Files

Likely files:

- `service.py`
- `tests/test_service.py`
- `prototypes/mobile/index.html`
- `docs/service.md`
- `docs/usage.md`
- `TODO.md`

## Required Behavior

Service:

- Accept optional `reference_px` and `reference_m` fields.
- If both reference fields are provided, derive `scale_px_per_meter`.
- If only one reference field is provided, return a 400 error.
- Keep direct `scale_px_per_meter` support.
- Decide precedence if both direct scale and reference fields are provided; document it.

Prototype:

- Add compact Reference px and Reference m fields.
- If both are filled, send them.
- Keep direct Scale field.
- Make blank fields omit the values.
- Client-side validate positive numbers when fields are non-empty.

## Constraints

- No visual calibration picker yet.
- Do not remove direct scale.
- Keep UI compact.
- Keep `?demo=1` working.

## Verification

Run:

```bash
/tmp/bbtracking-venv/bin/python -m pytest -q
git diff --check
npx playwright screenshot --full-page --viewport-size=390,844 file:///home/stefan/projects/BB-Tracking/prototypes/mobile/index.html /tmp/bbtracking-calibration.png
```

## M3 Prompt

Use this package as the implementation brief. Produce exact patches. Add service tests for direct scale, reference-derived scale, and incomplete reference failure. Keep prototype validation simple and dependency-free.
