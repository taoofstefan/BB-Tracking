# Backend / Test Gap Audit

Generated from an Ollama M3 audit pass and corrected against the current test suite.

## Highest-Value Gaps

### 1. Service option forwarding contract

Target files: `service.py`, `tests/test_service.py`

`build_analysis_params()` and `run_analysis()` are mostly covered through HTTP endpoint tests, but there is no focused test that locks down exactly which analysis options the service forwards to `track_video`.

Useful lightweight tests:

- Monkeypatch `service.track_video` and assert `run_analysis()` forwards `roi`, `tracker_name`, `scale_px_per_meter`, `rep_direction`, `min_rep_rom_px`, `min_rep_frames`, `rep_smoothing_window`, and `rep_deadband_px`.
- Assert currently unsupported CLI-only options such as `rep_detector`, `rep_phase_jitter_px`, `show_hud`, and `report_output` are intentionally not part of the service contract.
- Add direct `build_analysis_params()` cases for no scale/reference, direct scale, reference scale, and rep option pass-through.

Why it matters: the mobile prototype now sends rep options through the service form. A small kwargs contract test would catch silent drift between the prototype, service, and tracker.

### 2. Service runtime status and cleanup edges

Target files: `service.py`, `tests/test_service.py`

The async job path is well covered for complete/failed/video states, but some lifecycle edges are still light.

Useful lightweight tests:

- `run_job()` no-ops cleanly when the job id is missing from `JOB_STORE`.
- `run_job()` exposes a `running` state while `run_analysis()` is still executing, using a controlled slow stub.
- `clear_jobs()` removes/cleans temporary job directories.
- `GET` and `HEAD` parity for `/jobs/{job_id}/video` on queued, failed, and missing-file (`410`) cases.

Why it matters: the prototype now depends on async polling and annotated-video retrieval. These tests protect the job lifecycle rather than only the final response.

### 3. Service input parsing edge cases

Target files: `service.py`, `tests/test_service.py`, `barbell_tracker.py`

Existing tests cover common parsing paths, but a few cheap edge cases remain.

Useful lightweight tests:

- `safe_video_suffix("")`, `"lift."`, and unknown uppercase extensions.
- `parse_optional_positive_float(" 3.5 ")`, `"abc"`, and `"Infinity"`.
- `parse_roi()` with non-integers, too few values, zero width/height, and negative width/height.
- Unknown `tracker` passed to `/analyze` or `/jobs`, either as a documented pass-through to OpenCV failure or as a new 400 validation path.

Why it matters: malformed form data is likely from a prototype UI or user-edited API call. These are cheap tests with good failure messages.

### 4. Generated fixture bootstrap failures

Target files: `tests/test_sample_regression.py`, `tests/fixtures/generate_synthetic_lift.py`

The generated synthetic fixture works in the happy path, but the generator failure paths are not locked down.

Useful lightweight tests:

- `_ensure_fixture_video()` raises when the manifest references a missing generator script.
- `_ensure_fixture_video()` surfaces a non-zero generator exit.
- `_load_manifest()` rejects a non-list `fixtures` value.
- A manifest case with `skip: true` actually skips without attempting generation.

Why it matters: generated fixtures are now part of regression coverage. If fixture bootstrap breaks, the failure should be explicit and easy to diagnose.

### 5. Tracker warning boundary cases

Target files: `quality.py`, `tests/test_quality.py`

Warning behavior has solid coverage for the main branches. Remaining gaps are threshold and preservation edges.

Useful lightweight tests:

- `analyze_tracking_warnings()` at exact `0.5` and `0.8` coverage thresholds.
- `points_tracked > frames_processed` clamps `tracking_lost_frames` to zero.
- `rep_count=None` behaves like missing reps.
- `attach_tracking_warnings()` preserves all existing `PathQuality` fields, including `reps`, not just drift and warning fields.
- `analyze_rep_quality([])` returns the all-null `RepQuality` shape.
- `find_sticking_frame()` returns `None` when all speed points are zero or missing.

Why it matters: `quality.warnings` now drives user-facing uncertainty. Boundary behavior should stay stable.

### 6. Regression helper contract tests

Target files: `tests/test_sample_regression.py`

The sample regression path validates real output, but its helper assertions are not directly tested.

Useful lightweight tests:

- `assert_summary_matches()` fails on changed frame count, rep count, and speed tolerance violations.
- `assert_reps_match()` fails on length mismatch, changed `rom_px`, and velocity-loss tolerance violations.
- `_resolve()` returns absolute paths unchanged and resolves relative paths against the repo root.

Why it matters: these helpers define the golden fixture contract. A couple of unit tests make future manifest changes safer.

## Lower Priority

- Parser-only tests for `barbell_tracker.build_parser()` would protect CLI option availability, but this is lower value while the prototype mostly uses the service.
- `create_app()` behavior when FastAPI is missing could be tested, but it may require module import gymnastics and is less valuable than service behavior tests.

