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
- [x] Generate a standalone HTML analysis report from telemetry.

## Phase 3: Calibration And Reps

- [x] Add pixel-to-meter calibration.
- [x] Support reference-length calibration helper.
- [x] Segment reps from bar path with a vertical-path heuristic.
- [x] Add smoothing and deadband controls for rep segmentation.
- [x] Report per-rep peak velocity and mean velocity.
- [x] Report per-rep velocity loss.
- [x] Overlay live frame, speed, peak speed, and tracking counts on output video.

## Phase 4: Mobile Prototype

- [x] Decide first mobile stack.
- [x] Add video import screen.
- [x] Add exercise selector.
- [x] Add tap-to-select-bar UI.
- [x] Show set summary and annotated playback.

## Open Questions

- First target lift: squat, bench, or deadlift?
- Preferred mobile stack: iOS native, React Native, Flutter, or Kotlin/Swift split?
- Accuracy target for MVP velocity readings?
- Local-only MVP or optional sync from the beginning?
