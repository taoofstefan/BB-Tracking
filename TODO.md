# TODO

## Active Track

Build the old OpenCV proof of concept into a testable barbell analysis pipeline, then use that pipeline as the base for a mobile app.

## Phase 1: Runnable CLI

- [x] Add Python dependency list.
- [x] Replace hardcoded paths with CLI arguments.
- [x] Preserve the existing manual ROI workflow.
- [x] Add optional `--roi x,y,w,h` for headless smoke checks.
- [x] Add `--no-display` for non-interactive runs.
- [x] Document the local run command.

## Phase 2: Analysis Pipeline

- [x] Split tracking, video IO, metrics, and overlay drawing into focused modules.
- [x] Extract velocity calculations into a metrics module.
- [x] Add unit tests for velocity calculations.
- [x] Add golden regression coverage for sample-video metrics.
- [x] Export per-frame telemetry as JSON.
- [x] Export summary metrics as JSON.
- [x] Document the analysis JSON contract.
- [x] Generate a standalone HTML analysis report from telemetry.

## Phase 3: Calibration And Reps

- [x] Add pixel-to-meter calibration.
- [x] Support reference-length calibration helper.
- [x] Segment reps from bar path with a vertical-path heuristic.
- [x] Add smoothing and deadband controls for rep segmentation.
- [x] Report per-rep peak velocity and mean velocity.
- [x] Report per-rep velocity loss.
- [x] Report bar path quality metrics.
- [x] Overlay live frame, speed, peak speed, and tracking counts on output video.

## Phase 4: Mobile Prototype

- [x] Decide first mobile stack.
- [x] Add video import screen.
- [x] Add exercise selector.
- [x] Add tap-to-select-bar UI.
- [x] Show set summary and annotated playback.
- [x] Render velocity and bar path charts from analysis JSON.
- [x] Render quality metrics from analysis JSON.
- [x] Add optional analysis service spike.
- [x] Add prototype service health check.
- [x] Wire prototype Analyze button to the local analysis service.
- [x] Expose tracker and scale options in the mobile prototype.
- [x] Compare MOSSE/KCF/CSRT tracker behavior on the sample video.
- [x] Add local async job submission and polling for prototype analysis.
- [x] Expose the annotated video via `GET /jobs/{job_id}/video` and let the mobile prototype switch to it after async analysis completes.
- [x] Wire the calibration workflow into the service and mobile prototype: accept `reference_px` + `reference_m` on `/analyze` and `/jobs`, derive `scale_px_per_meter` via `metrics.scale_from_reference`, keep the direct scale field, and add compact Reference px / Reference m inputs to the prototype.
- [x] Add a visual reference picker in the mobile prototype so two taps on the displayed video fill `reference_px`; `reference_m` remains manual.
- [x] Add an optional phase-based rep detector mode (`--rep-detector direction|phase`) that smooths the bar path, ignores deadband deltas, and absorbs short jitter reversals so a single rep isn't split by a small reversal. Direction mode stays the default and golden sample remains stable.
- [x] Add per-rep jump and play-segment controls to the mobile prototype: when analysis reps include `start_time_s` / `end_time_s`, each rep row gets compact icon buttons that seek the existing `<video id="video">` to the rep start or play until the rep end and pause. Use a one-shot `timeupdate` listener (no runaway timers) and disable/ignore controls when no video is loaded or timing is missing.

## Open Questions

- First target lift: squat, bench, or deadlift?
- Preferred mobile stack: iOS native, React Native, Flutter, or Kotlin/Swift split?
- Accuracy target for MVP velocity readings?
- Local-only MVP or optional sync from the beginning?

## Phase 5: Fixture Library

- [x] Add a `tests/fixtures/lifts.json` manifest that names each sample,
      its video, ROI, tracker, calibration, rep-segmentation settings, and
      the path to its compact expected-metrics file.
- [x] Refactor `tests/test_sample_regression.py` to load cases from the
      manifest while preserving the 7-rep golden metrics for the existing
      `lift.mp4` sample.
- [x] Document the manifest schema in `tests/fixtures/README.md` and the
      workflow in `docs/testing.md`; cross-link from `docs/usage.md`.
- [x] Keep only compact expected metrics in git; teach `.gitignore` about
      generated `*-output.avi` and `*-analysis.json` artifacts under
      `tests/fixtures/`.
