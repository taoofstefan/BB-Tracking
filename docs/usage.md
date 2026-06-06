# Usage

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

`opencv-contrib-python` is required because the current tracker uses OpenCV's legacy tracking APIs.

## Run With Interactive ROI Selection

```bash
python main.py --input lift.mp4 --output output.avi
```

The first frame opens in an OpenCV window. Select the barbell/object, confirm the ROI, and the script writes an annotated output video.

Press `q` in the preview window to stop processing early.

## Run Headless With A Known ROI

```bash
python main.py --input lift.mp4 --output output.avi --roi 300,120,80,40 --no-display
```

`--roi` uses `x,y,w,h` pixel coordinates. It is required when `--no-display` is used because manual ROI selection needs a GUI window.

## Write Analysis JSON

```bash
python main.py \
  --input lift.mp4 \
  --output output.avi \
  --roi 300,120,80,40 \
  --no-display \
  --json-output analysis.json
```

The JSON file contains a summary block and one telemetry record per tracked frame.

## Write An HTML Report

```bash
python main.py \
  --input lift.mp4 \
  --output output.avi \
  --roi 300,120,80,40 \
  --no-display \
  --scale-px-per-meter 100 \
  --json-output analysis.json \
  --report-output report.html
```

The report is a standalone HTML file with summary cards, a velocity chart, a bar path chart, and a per-rep table.

## Add Calibration

Velocity is pixel-based by default. To also report meters per second, pass either a direct scale:

```bash
python main.py \
  --input lift.mp4 \
  --output output.avi \
  --roi 300,120,80,40 \
  --no-display \
  --scale-px-per-meter 100
```

Or derive the scale from a known reference length:

```bash
python main.py \
  --input lift.mp4 \
  --output output.avi \
  --roi 300,120,80,40 \
  --no-display \
  --reference-px 220 \
  --reference-m 2.2
```

For a standard Olympic barbell, `--reference-m 2.2` is a useful first approximation if the full bar length is visible and marked in pixels.

The local analysis service (`service.py`) accepts the same calibration inputs as multipart form fields on `/analyze` and `/jobs`: `scale_px_per_meter`, or a `reference_px` + `reference_m` pair. The reference pair is converted to `scale_px_per_meter` server-side; the reference pair takes precedence when both are sent. See `docs/service.md` for details.

## Rep Segmentation

The CLI includes a conservative vertical-path heuristic for rep segmentation. It looks for movement phases in one direction and filters out phases that are too short or too small.

```bash
python main.py \
  --input lift.mp4 \
  --output output.avi \
  --roi 300,120,80,40 \
  --no-display \
  --json-output analysis.json \
  --rep-direction up \
  --min-rep-rom-px 20 \
  --min-rep-frames 3 \
  --rep-smoothing-window 1 \
  --rep-deadband-px 0 \
  --rep-detector direction
```

Use `--rep-direction up` for lifts where the relevant concentric phase moves upward in the video frame. Use `--rep-direction down` for experiments where the tracked target moves downward. This is still a heuristic; bad tracking, camera angle, or occlusion can create bad rep boundaries.

Increase `--rep-deadband-px` to ignore small vertical jitter before direction changes are counted. Increase `--rep-smoothing-window` to apply a centered moving average to the bar path before rep detection. The defaults preserve the raw detector behavior.

`--rep-detector {direction,phase}` selects the segmentation strategy. `direction` (default) is the original direction-flip heuristic. `phase` smooths the bar path, ignores `--rep-deadband-px`, and absorbs short jitter reversals (regressions at or below the jitter threshold are kept inside the in-progress rep instead of starting a new one). Phase mode still honors `--min-rep-rom-px` and `--min-rep-frames`.

```bash
python main.py \
  --input lift.mp4 \
  --output output.avi \
  --roi 300,120,80,40 \
  --no-display \
  --json-output analysis.json \
  --rep-detector phase \
  --rep-phase-jitter-px 10
```

`--rep-phase-jitter-px` sets the jitter threshold for phase mode. It defaults to half of `--min-rep-rom-px` when omitted. Increase it for noisy video, lower it for clean bar paths.

`velocity_loss_pct` is calculated against the first detected rep's mean pixel velocity. A positive value means the rep was slower than rep 1; a negative value means it was faster.

## Tracker Options

```bash
python main.py --tracker mosse
python main.py --tracker kcf
python main.py --tracker csrt
```

`mosse` keeps the original proof-of-concept behavior. `kcf` and `csrt` are available for quick experiments.

## Output

The CLI prints:

- output file path
- frames processed
- points tracked
- max speed in pixels per second
- min speed in pixels per second
- average speed in pixels per second
- calibrated speed in meters per second when calibration is provided
- detected rep count

With `--json-output`, it also writes:

- frame number
- timestamp in seconds
- bounding box
- center point
- speed in pixels per second for that frame
- speed in meters per second for that frame when calibration is provided
- per-rep start/end frames, duration, ROM, peak speed, and mean speed
- per-rep velocity loss percentage against rep 1
- bar path quality metrics: horizontal drift, ROM consistency, and the slowest tracked point per rep
- optional `quality.warnings`, `quality.tracking_coverage_ratio`, and `quality.tracking_lost_frames` to flag low tracking coverage, no tracked points, no processed frames, or missing reps. The HTML report and the mobile prototype render the warning list compactly when present, and stay quiet when it is empty or missing entirely.

Velocity is pixel-based unless calibration is provided. With calibration, summary, frame, and rep metrics also include meters per second.

The annotated video includes a small live HUD with frame time, current speed, peak speed, and tracked point count. Use `--no-hud` to keep only the bounding box and bar path trail.

## Testing

Regression and unit tests are documented in `docs/testing.md`. The
sample-video regression test is data-driven from
`tests/fixtures/lifts.json`; see `tests/fixtures/README.md` for the
manifest schema and how to add new fixtures.
