from __future__ import annotations

from pathlib import Path


def open_capture(input_file: str | Path):
    import cv2

    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input video not found: {input_path}")

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open input video: {input_path}")
    return cap


def get_fps(cap) -> float:
    import cv2

    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    if fps <= 0:
        raise RuntimeError("Input video FPS is missing or invalid")
    return fps


def get_frame_size(cap) -> tuple[int, int]:
    import cv2

    return (
        int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    )


def open_writer(output_file: str | Path, fps: float, frame_size: tuple[int, int]):
    import cv2

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, frame_size)
    if not writer.isOpened():
        raise RuntimeError(f"Could not open output video for writing: {output_path}")
    return writer
