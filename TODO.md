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

- [ ] Split tracking, video IO, metrics, and overlay drawing into focused modules.
- [x] Extract velocity calculations into a metrics module.
- [x] Add unit tests for velocity calculations.
- [x] Export per-frame telemetry as JSON.
- [x] Export summary metrics as JSON.

## Phase 3: Calibration And Reps

- [x] Add pixel-to-meter calibration.
- [x] Support reference-length calibration helper.
- [ ] Segment reps from bar path and velocity.
- [ ] Report per-rep peak velocity, mean velocity, and velocity loss.

## Phase 4: Mobile Prototype

- [ ] Decide first mobile stack.
- [ ] Add video import screen.
- [ ] Add exercise selector.
- [ ] Add tap-to-select-bar UI.
- [ ] Show set summary and annotated playback.

## Open Questions

- First target lift: squat, bench, or deadlift?
- Preferred mobile stack: iOS native, React Native, Flutter, or Kotlin/Swift split?
- Accuracy target for MVP velocity readings?
- Local-only MVP or optional sync from the beginning?
