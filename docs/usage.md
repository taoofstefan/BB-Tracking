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

Velocity is still pixel-based. Calibration to meters per second is planned in a later phase.
