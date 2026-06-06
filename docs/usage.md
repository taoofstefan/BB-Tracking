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
  --min-rep-frames 3
```

Use `--rep-direction up` for lifts where the relevant concentric phase moves upward in the video frame. Use `--rep-direction down` for experiments where the tracked target moves downward. This is still a heuristic; bad tracking, camera angle, or occlusion can create bad rep boundaries.

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

Velocity is pixel-based unless calibration is provided. With calibration, summary, frame, and rep metrics also include meters per second.
