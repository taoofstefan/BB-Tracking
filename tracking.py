from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

BoundingBox = tuple[int, int, int, int]
Point = tuple[int, int]


@dataclass(frozen=True)
class TrackingUpdate:
    bbox: BoundingBox
    center: Point


def create_tracker(name: str):
    import cv2

    normalized = name.lower()
    factories = {
        "mosse": ("TrackerMOSSE_create", "TrackerMOSSE_create"),
        "kcf": ("TrackerKCF_create", "TrackerKCF_create"),
        "csrt": ("TrackerCSRT_create", "TrackerCSRT_create"),
    }
    if normalized not in factories:
        raise ValueError(f"Unsupported tracker: {name}")

    legacy_name, direct_name = factories[normalized]
    legacy = getattr(cv2, "legacy", None)
    if legacy is not None and hasattr(legacy, legacy_name):
        return getattr(legacy, legacy_name)()
    if hasattr(cv2, direct_name):
        return getattr(cv2, direct_name)()
    raise RuntimeError(
        f"OpenCV tracker '{normalized}' is unavailable. Install opencv-contrib-python."
    )


def normalize_bbox(bbox) -> BoundingBox:
    return tuple(int(value) for value in bbox)


def center_of(bbox: BoundingBox) -> Point:
    x, y, w, h = bbox
    return x + w // 2, y + h // 2


def select_roi(frame: "np.ndarray") -> BoundingBox:
    import cv2

    return normalize_bbox(cv2.selectROI("Select barbell", frame, False))


def update_tracker(tracker, frame: "np.ndarray") -> TrackingUpdate | None:
    ok, bbox = tracker.update(frame)
    if not ok:
        return None
    normalized = normalize_bbox(bbox)
    return TrackingUpdate(bbox=normalized, center=center_of(normalized))
