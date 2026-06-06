"""Deterministic synthetic lift fixture generator.

Produces a tiny, high-contrast video of a white rectangle ("barbell
plate") moving up and down on a black background. The video is designed
to be small and stable so it can be regenerated on demand and used by the
sample-regression test suite.

Run from the repo root:

    /tmp/bbtracking-venv/bin/python tests/fixtures/generate_synthetic_lift.py \
        --output tests/fixtures/generated/synthetic_lift.avi

The output directory and AVI file are created if they do not exist.
The generator is intentionally dependency-light: only the Python
stdlib plus ``cv2``/``numpy`` (already used elsewhere in the project).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


# Default parameters are tuned to produce a tiny deterministic clip:
# 30 fps, 320x240 frames, three clear vertical reps.
DEFAULT_WIDTH = 320
DEFAULT_HEIGHT = 240
DEFAULT_FPS = 30.0
DEFAULT_REP_COUNT = 3
DEFAULT_BAR_WIDTH = 60
DEFAULT_BAR_HEIGHT = 20
DEFAULT_BASE_Y = 180  # Resting y of the bar centre.
DEFAULT_AMPLITUDE = 100  # Vertical ROM of each rep, in pixels.
DEFAULT_FRAMES_PER_REP = 40  # 20 frames up, 20 frames down at 30 fps.


def bar_y_for_frame(
    frame_index: int,
    *,
    rep_count: int,
    frames_per_rep: int,
    base_y: int,
    amplitude: int,
) -> int:
    """Return the y-coordinate of the bar centre for ``frame_index``.

    The motion is a triangle wave: 20 frames up, 20 frames down per rep.
    With ``rep_count`` reps plus one trailing rest frame the cycle
    repeats exactly for stable regression metrics.
    """

    cycle = frames_per_rep
    phase = frame_index % cycle
    reps_done = frame_index // cycle
    # The last "rest" frame holds the bar at the top; everything else
    # walks through the rep.
    if reps_done >= rep_count and phase == 0:
        return base_y - amplitude
    half = cycle // 2
    if phase < half:
        progress = phase / max(half - 1, 1) if half > 1 else 0.0
    else:
        progress = (
            1.0 - (phase - half) / max(cycle - half - 1, 1)
            if (cycle - half) > 1
            else 0.0
        )
    return int(round(base_y - amplitude * progress))


def render_frame(
    width: int,
    height: int,
    bar_x: int,
    bar_y: int,
    bar_w: int,
    bar_h: int,
) -> np.ndarray:
    """Return a single BGR frame with a white rectangle on black."""

    frame = np.zeros((height, width, 3), dtype=np.uint8)
    top_left = (bar_x, max(bar_y - bar_h // 2, 0))
    bottom_right = (
        min(bar_x + bar_w, width - 1),
        min(bar_y + bar_h // 2, height - 1),
    )
    cv2.rectangle(
        frame,
        top_left,
        bottom_right,
        (255, 255, 255),
        thickness=cv2.FILLED,
    )
    return frame


def build_video(
    output_path: Path,
    *,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    fps: float = DEFAULT_FPS,
    rep_count: int = DEFAULT_REP_COUNT,
    bar_width: int = DEFAULT_BAR_WIDTH,
    bar_height: int = DEFAULT_BAR_HEIGHT,
    base_y: int = DEFAULT_BASE_Y,
    amplitude: int = DEFAULT_AMPLITUDE,
    frames_per_rep: int = DEFAULT_FRAMES_PER_REP,
) -> Path:
    """Write the synthetic clip to ``output_path`` and return the path."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    bar_x = (width - bar_width) // 2
    # Use MJPG so the resulting AVI is small and readable on every
    # platform OpenCV supports.
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter(
        str(output_path), fourcc, fps, (width, height)
    )
    if not writer.isOpened():
        raise RuntimeError(f"Could not open video writer for {output_path}")

    total_frames = rep_count * frames_per_rep + 1
    try:
        for frame_index in range(total_frames):
            bar_y = bar_y_for_frame(
                frame_index,
                rep_count=rep_count,
                frames_per_rep=frames_per_rep,
                base_y=base_y,
                amplitude=amplitude,
            )
            frame = render_frame(
                width,
                height,
                bar_x,
                bar_y,
                bar_width,
                bar_height,
            )
            writer.write(frame)
    finally:
        writer.release()

    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("tests/fixtures/generated/synthetic_lift.avi"),
        help="Output AVI path (relative to repo root).",
    )
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--fps", type=float, default=DEFAULT_FPS)
    parser.add_argument("--rep-count", type=int, default=DEFAULT_REP_COUNT)
    parser.add_argument(
        "--frames-per-rep",
        type=int,
        default=DEFAULT_FRAMES_PER_REP,
    )
    parser.add_argument("--amplitude", type=int, default=DEFAULT_AMPLITUDE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = args.output
    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path
    build_video(
        output_path,
        width=args.width,
        height=args.height,
        fps=args.fps,
        rep_count=args.rep_count,
        amplitude=args.amplitude,
        frames_per_rep=args.frames_per_rep,
    )
    print(f"wrote synthetic lift fixture to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
