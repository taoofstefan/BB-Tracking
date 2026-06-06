# PR Draft: BB-Tracking product brief, analysis service, and mobile prototype

## Summary

This branch turns the original barbell tracking proof of concept into a more testable analysis pipeline with a documented product direction, a local analysis service, regression fixtures, and a mobile HTML prototype. It keeps the current OpenCV/classical-tracker approach, but splits the implementation into focused modules and adds a JSON analysis contract so the CLI, service, reports, and prototype can consume the same result shape.

## Major Changes

### Product and planning docs

- Added product direction and roadmap docs under `docs/`.
- Added an analysis JSON contract in `docs/analysis-contract.md`.
- Added service, testing, mobile architecture, tracker comparison, and usage docs.
- Added Ollama work packages under `agent_packages/ollama/`.
- Added QA artifacts under `agent_packages/ollama/bbtracking-qa/`.

### Tracking and analysis pipeline

- Split the old tracking script into focused modules:
  - `barbell_tracker.py`
  - `tracking.py`
  - `video_io.py`
  - `metrics.py`
  - `reps.py`
  - `quality.py`
  - `overlay.py`
  - `analysis_io.py`
  - `analysis_schema.py`
  - `report.py`
- Added pixel and calibrated velocity metrics.
- Added rep segmentation, smoothing/deadband controls, per-rep speed summaries, and velocity-loss reporting.
- Added phase-based rep detection as an optional detector mode.
- Added bar-path quality metrics and tracker confidence/warning signals.
- Added HUD overlays for frame time, current speed, peak speed, and tracked point count.

### Service and prototype

- Added a FastAPI service spike in `service.py`.
- Added async job submission/polling.
- Added annotated-video retrieval via `/jobs/{job_id}/video`.
- Added service health checks and service docs.
- Added a mobile HTML prototype with:
  - video import
  - analysis JSON loading
  - local service submission
  - summary cards
  - quality metrics
  - warning rendering
  - velocity/path charts
  - per-rep jump/play controls
  - visual reference calibration picker
  - local analysis history
  - lift-specific analysis presets

### Fixtures and tests

- Added a manifest-driven regression fixture library under `tests/fixtures/`.
- Preserved the existing `lift.mp4` golden regression behavior.
- Added a generated synthetic lift fixture and compact metrics.
- Added unit/regression tests for schema validation, service endpoints, metrics, reps, quality, overlay, report rendering, tracker comparison, and sample regression.

## Verification

Current local verification:

```bash
/tmp/bbtracking-venv/bin/python -m pytest -q
```

Result:

```text
93 passed
```

Also checked mobile prototype screenshots at `390x844` during the recent prototype slices.

## Known Limitations / Follow-Ups

- Tracking is still heuristic/classical OpenCV tracking, not a trained detector.
- The mobile prototype is a static HTML prototype, not a production mobile app.
- The service is local-development scoped: in-memory job state, no auth, no persistent job store.
- History storage now uses compact/downsampled analysis payloads, but it is still browser-local only.
- Generated synthetic fixtures are useful for stability, but not realistic enough to replace real training videos.
- Backend/test-gap audit lives in `agent_packages/ollama/bbtracking-qa/backend-test-gap-audit.md`.

