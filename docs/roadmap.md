# Roadmap

This roadmap keeps each change small and reviewable.

## Phase 1: Make The Current Proof Of Concept Usable

1. Add `requirements.txt`.
2. Replace hardcoded paths with CLI arguments.
3. Add `--input`, `--output`, and `--tracker` options.
4. Keep `lift.mp4` as a smoke-test sample.
5. Document how to run the demo locally.

## Phase 2: Modularize The Analysis Pipeline

Split the current scripts into focused modules:

- `tracker.py`: tracker initialization and frame updates.
- `video_io.py`: input/output video handling.
- `metrics.py`: position, speed, and summary calculations.
- `overlay.py`: drawing bar path, velocity, and rep labels.
- `cli.py`: command-line entry point.

## Phase 3: Add Testable Metrics

1. Add unit tests for velocity calculation.
2. Add synthetic trajectory fixtures.
3. Add JSON output for per-frame telemetry.
4. Add summary output for peak, mean, and minimum velocity.

## Phase 4: Calibration

1. Add `--scale-px-per-meter`.
2. Add helpers for bar length and plate diameter calibration.
3. Output velocity in meters per second.
4. Preserve pixel velocity for debugging.

## Phase 5: Rep Segmentation

1. Segment reps from vertical position and velocity.
2. Identify concentric phase.
3. Compute per-rep peak velocity.
4. Compute per-rep mean concentric velocity.
5. Compute velocity loss percentage across the set.

## Phase 6: Better Annotated Video

1. Draw current velocity on the video.
2. Draw rep number.
3. Draw bar path trail.
4. Add a compact velocity chart overlay.
5. Mark detected sticking points.

## Phase 7: Mobile Prototype

1. Create a `mobile/` scaffold.
2. Add video import screen.
3. Add exercise selector.
4. Add tap-to-select-bar UI.
5. Run analysis through the local pipeline or a development worker.
6. Show a set summary and annotated playback.

## Phase 8: Reliability Improvements

1. Add tracker confidence.
2. Add re-acquire prompts.
3. Try CSRT/KCF against the current MOSSE baseline.
4. Explore detector-assisted re-detection.
5. Collect and label failed tracking examples.

## Definition Of Done For Early Commits

- The repo can be cloned and run from documented commands.
- No hardcoded machine-specific paths.
- Analysis output is written to a predictable location.
- Metrics code has unit tests.
- The sample video can be used as a smoke test.
