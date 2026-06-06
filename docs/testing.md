# Testing

## Quick Start

```bash
# Sample-video regression test (runs the real pipeline against lift.mp4).
/tmp/bbtracking-venv/bin/python -m pytest -q tests/test_sample_regression.py

# Full unit + regression suite.
/tmp/bbtracking-venv/bin/python -m pytest -q
```

The regression test is marked with the `regression` marker so it can be
targeted directly: `pytest -m regression -q`.

## Sample Regression Test

`tests/test_sample_regression.py` runs the real tracker against
`lift.mp4` and compares the resulting analysis JSON against a compact
golden fixture. The test is **data-driven**: it loads its cases from
`tests/fixtures/lifts.json` (the fixture manifest) and dynamically
registers one pytest test function per entry.

Each generated test:

1. Resolves the manifest entry's `video` and `expected_metrics` paths
   relative to the repo root.
2. Skips cleanly if the video file is missing or the entry has
   `skip: true`.
3. Runs `barbell_tracker.track_video` with the manifest's `roi`,
   `tracker`, `scale_px_per_meter`, and rep-segmentation settings.
4. Validates the resulting analysis payload via
   `analysis_schema.assert_valid_analysis_payload`.
5. Compares the summary block (frame counts, rep count, average/max
   speeds) and per-rep block (index, frames, ROM, mean speed, velocity
   loss) against the compact golden fixture.
6. Asserts the actual rep count matches the manifest's
   `expected_rep_count` (defaulting to the value in the golden fixture).

The current manifest has a single `lift` entry that exercises the
MOSSE tracker with the same ROI and calibration that have produced
the canonical 7-rep golden metrics.

## Fixture Manifest

`tests/fixtures/lifts.json` is the source of truth for which samples
exist and how they should be run. The schema is documented in
`tests/fixtures/README.md`. To add a new sample:

1. Drop the video into the repo root.
2. Generate compact expected metrics once and save them under
   `tests/fixtures/`.
3. Append a new entry to `lifts.json`.
4. Re-run the regression test to confirm.

## Compact Metrics In Git, Generated Artifacts Out

`tests/fixtures/sample_metrics.json` is a small, reviewable subset of
the full analysis payload — summary plus per-rep summary. Per-frame
telemetry and annotated output videos are not committed.

The repo's `.gitignore` excludes the common generated patterns under
`tests/fixtures/` (`*-output.avi`, `*-analysis.json`, and a
`generated/` directory for one-off run output). Add new patterns there
when introducing a new output flavor.
