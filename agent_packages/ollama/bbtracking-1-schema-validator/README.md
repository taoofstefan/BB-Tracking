# Package 1: Analysis Schema Validator

## Goal

Add a lightweight Python validation module for the analysis JSON contract documented in `docs/analysis-contract.md`.

The validator should help the CLI/service/report/mobile flow catch accidental schema regressions without adding heavy dependencies.

## Current Context

- JSON is written by `analysis_io.write_analysis_json`.
- Top-level keys are `summary`, `frames`, `reps`, and optional/current `quality`.
- Contract doc exists at `docs/analysis-contract.md`.
- Existing golden regression test reads generated JSON in `tests/test_sample_regression.py`.
- Existing tests are pytest-based and should remain dependency-light.

## Target Files

Likely files:

- Add `schema.py` or `analysis_schema.py`.
- Add `tests/test_analysis_schema.py`.
- Update `tests/test_sample_regression.py` to validate generated JSON.
- Optional: update `docs/analysis-contract.md` with a validator note.
- Optional: update `TODO.md`.

## Required Behavior

Implement:

- `validate_analysis_payload(payload: dict) -> list[str]`
  - Returns a list of human-readable validation errors.
  - Returns `[]` for valid payloads.
  - Does not throw for ordinary missing/wrong fields.
- `assert_valid_analysis_payload(payload: dict) -> None`
  - Raises `ValueError` with joined errors when invalid.

Validation should check:

- Top-level `summary`, `frames`, `reps`, `quality` presence.
- `summary.frames_processed`, `summary.points_tracked`, `summary.rep_count` are non-negative integers.
- Speed fields are either numbers or null.
- `frames` is a list.
- Each frame has `frame`, `time_s`, `center_x`, `center_y`.
- `reps` is a list.
- Each rep has `index`, `start_frame`, `end_frame`, `duration_s`, `rom_px`.
- `quality` is a dict.
- `quality.reps` is a list when present.

Do not overbuild full JSON Schema. Keep this pure Python and readable.

## Constraints

- No new dependencies.
- Do not change output JSON shape.
- Do not make validator so strict that harmless additive fields fail.
- Do not validate every single optional field exhaustively.
- Keep tests focused.

## Verification

Run:

```bash
/tmp/bbtracking-venv/bin/python -m pytest -q
python3 -m py_compile analysis_schema.py
git diff --check
```

If module name differs, adjust the compile command.

## M3 Prompt

Use this package as the implementation brief. Produce exact patches for the target files. Prefer `analysis_schema.py` unless there is a strong reason to choose another name. Add tests for valid payload, missing top-level keys, wrong scalar types, and validation of the generated sample JSON.
