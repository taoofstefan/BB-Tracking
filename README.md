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

See [docs/product-brief.md](docs/product-brief.md) for the app concept, [docs/roadmap.md](docs/roadmap.md) for the first implementation steps, [docs/mobile-architecture.md](docs/mobile-architecture.md) for the mobile stack decision, [docs/service.md](docs/service.md) for the optional API spike, [docs/tracker-comparison.md](docs/tracker-comparison.md) for tracker results, and [docs/usage.md](docs/usage.md) for the current CLI.

## Quick Start

```bash
python -m pip install -r requirements.txt
python main.py --input lift.mp4 --output output.avi
```

For headless runs, pass a known ROI:

```bash
python main.py --input lift.mp4 --output output.avi --roi 300,120,80,40 --no-display
```

## Current Limitations

- Meter-per-second velocity depends on manual calibration.
- Tracking depends on manual ROI selection.
- The tracker can drift or fail when the bar is occluded.
- Rep segmentation is heuristic and based on vertical bar movement.
- The mobile prototype is a static shell, not a connected app.
- The scripts assume desktop OpenCV UI support.

## Near-Term Goal

Turn the proof of concept into a small, testable analysis pipeline:

1. Clean up the Python CLI and remove hardcoded paths.
2. Add calibrated velocity output.
3. Export per-frame and per-rep metrics as JSON.
4. Generate annotated videos with velocity and rep overlays.
5. Use that pipeline as the analysis core for a future mobile app.
