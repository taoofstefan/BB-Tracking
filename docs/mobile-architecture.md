# Mobile Architecture

## Decision

Start with a static/PWA-style prototype, then move to React Native when the product flow and analysis contract are stable.

This repo is still half computer-vision class relic, half strength-training idea. The fastest useful mobile step is not a native camera stack yet; it is a phone-shaped workflow that proves the screens, data, and feedback loop:

1. Import or record a lift video.
2. Pick the exercise.
3. Select the barbell target.
4. Run analysis through the existing Python pipeline.
5. Review annotated playback, bar path, velocity, reps, and slowdown.

## Why Not Native First

Native Swift/Kotlin would give the best camera and video performance, but it doubles the surface area before the tracking pipeline and feedback model are proven.

React Native is the likely app stack once this gets serious. It gives a single mobile codebase, real camera/video APIs, and room for native modules later if on-device tracking becomes important.

For the immediate prototype, plain HTML/CSS/JS keeps the project dependency-light and makes it easy to iterate on the UX beside the current Python CLI and generated HTML report.

## First Prototype Screens

- Capture/import: local video picker and future camera entry point.
- Lift setup: exercise selector, side/front angle, and optional calibration hints.
- Bar selection: tap-to-place target marker on the first frame.
- Analysis status: queued, processing, complete, failed.
- Set review: annotated playback, summary metrics, per-rep table, velocity loss, and bar path.

## Upgrade Path

Keep the analysis data contract close to the current JSON shape:

- `summary`
- `frames`
- `reps`

The static prototype can import the current JSON output directly. A React Native app can later send videos to a local/server Python analysis service and render the same contract.
