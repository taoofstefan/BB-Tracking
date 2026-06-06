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
- Calibration helper: tap two points on the displayed video to fill reference pixels, then enter the known real-world distance manually.
- Bar selection: tap-to-place target marker on the first frame.
- Analysis status: queued, processing, complete, failed.
- Set review: annotated playback, summary metrics, per-rep table, velocity loss, and bar path.
- Per-rep jump / play-segment controls: when an analysis JSON includes `start_time_s` and `end_time_s`, each rep row exposes two compact icon buttons (jump-to-start, play-segment). The play button attaches a one-shot `timeupdate` listener that pauses the existing `<video id="video">` at `end_time_s` and removes the listener, with no `setInterval` or leaked handlers. Both controls are disabled when no video is loaded or when rep timing is missing.
- Local session history: the prototype stores up to five compact analysis entries in `localStorage` under `bbtracking.history.v1`. Entries keep the JSON payload and small metadata only; video files and blob URLs are not stored.

## Upgrade Path

Keep the analysis data contract close to the current JSON shape:

- `summary`
- `frames`
- `reps`

The static prototype can import the current JSON output directly. A React Native app can later send videos to a local/server Python analysis service and render the same contract.
