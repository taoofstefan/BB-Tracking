# BB-Tracking

Early proof of concept for tracking a barbell in training videos with OpenCV.

The current scripts let a user select a region of interest in the first video frame, track that object with a classical OpenCV tracker, draw the bar path, estimate pixel-per-second velocity, and export an annotated video.

This repo is now being shaped toward a mobile app idea: record or import a lift, track the bar path, calculate per-rep velocity, detect slowdown/sticking points, and give lifters useful visual feedback without dedicated barbell sensors.

## Current State

- `main.py` runs the local demo against `lift.mp4` and writes `output.avi`.
- `BBtracking.py` contains the same workflow wrapped in a function, but still includes hardcoded local paths.
- `lift.mp4` is the sample input clip.
- `output.avi` is the sample annotated output.

## Product Direction

See [docs/product-brief.md](docs/product-brief.md) for the app concept and [docs/roadmap.md](docs/roadmap.md) for the first implementation steps.

## Current Limitations

- Velocity is measured in pixels per second, not meters per second.
- Tracking depends on manual ROI selection.
- The tracker can drift or fail when the bar is occluded.
- There is no rep segmentation yet.
- There is no calibration, JSON output, test suite, or mobile app shell yet.
- The scripts assume desktop OpenCV UI support.

## Near-Term Goal

Turn the proof of concept into a small, testable analysis pipeline:

1. Clean up the Python CLI and remove hardcoded paths.
2. Add calibrated velocity output.
3. Export per-frame and per-rep metrics as JSON.
4. Generate annotated videos with velocity and rep overlays.
5. Use that pipeline as the analysis core for a future mobile app.
