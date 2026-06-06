# Test Fixtures

This directory holds compact golden fixtures for the sample regression test
and any future video fixtures.

## Layout

- `lifts.json` — the **fixture manifest**. Describes every sample video the
  regression suite can run, with its video path, ROI, tracker, calibration,
  rep-segmentation settings, and the path to its expected metrics file.
  The test loader walks this manifest to build a pytest test case per
  fixture, so adding a new sample is a matter of dropping the video into the
  repo root and appending an entry.
- `sample_metrics.json` — compact expected metrics for the `lift` sample
  (summary block + per-rep summary). Only compact metrics are kept in git;
  full per-frame telemetry and annotated output videos are not committed.
- `generate_synthetic_lift.py` — creates the tiny deterministic
  `synthetic_lift` video on demand under `tests/fixtures/generated/`.
- `synthetic_metrics.json` — compact expected metrics for the generated
  synthetic fixture. The generated video is ignored; the generator and
  metrics stay reviewable in git.

## Manifest Schema

Each entry in `lifts.json` under the `fixtures` array is a JSON object:

| Field | Type | Notes |
| --- | --- | --- |
| `name` | string | Short fixture id; used as the pytest test id suffix. |
| `description` | string | Human-readable summary of the sample. |
| `video` | string | Path to the input video, resolved relative to the repo root. |
| `roi` | `[x, y, w, h]` | Headless ROI in pixel coordinates. |
| `tracker` | string | One of `mosse`, `kcf`, `csrt`. |
| `scale_px_per_meter` | number | Calibration scale used when running the pipeline. |
| `rep_direction` | string | `up` or `down`. |
| `rep_detector` | string | `direction` or `phase`. |
| `min_rep_rom_px` | integer | Minimum ROM in pixels for a rep to count. |
| `min_rep_frames` | integer | Minimum tracked frames for a rep to count. |
| `expected_metrics` | string | Path to the compact expected metrics JSON, relative to the repo root. |
| `expected_rep_count` | integer | Sanity-checked against the actual rep count. |
| `marks` | string list | Optional pytest marks applied to the generated test. |
| `skip` | bool | When true, the test is registered but skipped unconditionally. |
| `generate` | object | Optional generator block with `script` and `output`. The regression test runs the script with `--output` when the video is missing. |

Unknown fields are ignored, so the manifest can grow additively.

## Adding A Fixture

1. Add the video to the repo root (or a documented location), or add a small
   generator script and point a manifest `generate` block at it.
2. Generate the compact expected metrics once by running the pipeline with
   `--json-output`, then keep only the `summary` and `reps` blocks.
3. Append a new entry to `lifts.json` and add the expected-metrics file.
4. Re-run `pytest tests/test_sample_regression.py -q` to confirm.

## What Is Not Committed

Generated annotated output videos (`*.avi`, `*.mp4`), full per-frame
telemetry JSON, and any large run artifacts must be ignored. The repo's
`.gitignore` already excludes the common `*.avi` patterns. Compact metrics
files like `sample_metrics.json` are kept under `tests/fixtures/` because
they are small, reviewable, and essential for regression coverage.
