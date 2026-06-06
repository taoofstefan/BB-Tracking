from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

Point = tuple[int, int]
BoundingBox = tuple[int, int, int, int]


def draw_hud(frame: "np.ndarray", lines: list[str]) -> None:
    import cv2

    visible_lines = [line for line in lines if line]
    if not visible_lines:
        return

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    thickness = 1
    line_height = 22
    padding = 8
    x = 12
    y = 14
    width = max(
        cv2.getTextSize(line, font, font_scale, thickness)[0][0]
        for line in visible_lines
    )
    height = line_height * len(visible_lines) + padding
    cv2.rectangle(
        frame,
        (x - padding, y - padding),
        (x + width + padding, y + height),
        (0, 0, 0),
        -1,
    )
    cv2.rectangle(
        frame,
        (x - padding, y - padding),
        (x + width + padding, y + height),
        (255, 255, 255),
        1,
    )

    for index, line in enumerate(visible_lines):
        cv2.putText(
            frame,
            line,
            (x, y + line_height * (index + 1)),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA,
        )


def format_speed_line(speed_px_s: float | None, speed_m_s: float | None) -> str:
    if speed_px_s is None:
        return "Speed: --"
    if speed_m_s is None:
        return f"Speed: {speed_px_s:.1f} px/s"
    return f"Speed: {speed_m_s:.3f} m/s ({speed_px_s:.1f} px/s)"


def draw_tracking_overlay(
    frame: "np.ndarray",
    trail: "np.ndarray",
    bbox: BoundingBox,
    center: Point,
    previous_center: Point | None,
    hud_lines: list[str] | None = None,
) -> "np.ndarray":
    import cv2

    x, y, w, h = bbox
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.circle(frame, center, 4, (0, 255, 0), -1)
    if previous_center is not None:
        cv2.line(trail, center, previous_center, (0, 0, 255), 2)
    blended = cv2.addWeighted(frame, 1, trail, 0.5, 0)
    if hud_lines is not None:
        draw_hud(blended, hud_lines)
    return blended


def apply_trail(
    frame: "np.ndarray",
    trail: "np.ndarray",
    hud_lines: list[str] | None = None,
) -> "np.ndarray":
    import cv2

    blended = cv2.addWeighted(frame, 1, trail, 0.5, 0)
    if hud_lines is not None:
        draw_hud(blended, hud_lines)
    return blended
