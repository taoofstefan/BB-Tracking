from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

Point = tuple[int, int]
BoundingBox = tuple[int, int, int, int]


def draw_tracking_overlay(
    frame: "np.ndarray",
    trail: "np.ndarray",
    bbox: BoundingBox,
    center: Point,
    previous_center: Point | None,
) -> "np.ndarray":
    import cv2

    x, y, w, h = bbox
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.circle(frame, center, 4, (0, 255, 0), -1)
    if previous_center is not None:
        cv2.line(trail, center, previous_center, (0, 0, 255), 2)
    return cv2.addWeighted(frame, 1, trail, 0.5, 0)


def apply_trail(frame: "np.ndarray", trail: "np.ndarray") -> "np.ndarray":
    import cv2

    return cv2.addWeighted(frame, 1, trail, 0.5, 0)
