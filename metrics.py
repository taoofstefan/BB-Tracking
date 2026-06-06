from __future__ import annotations

from math import sqrt
from typing import Iterable, Sequence

Point = tuple[int, int]


def pixel_distance(a: Point, b: Point) -> float:
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def speed_px_s(previous: Point, current: Point, fps: float) -> float:
    if fps <= 0:
        raise ValueError("fps must be positive")
    return pixel_distance(previous, current) * fps


def speeds_from_positions(positions: Sequence[Point], fps: float) -> list[float]:
    if fps <= 0:
        raise ValueError("fps must be positive")
    return [
        speed_px_s(previous, current, fps)
        for previous, current in zip(positions, positions[1:])
    ]


def summarize_speeds(speeds: Iterable[float]) -> tuple[float | None, float | None, float | None]:
    values = list(speeds)
    if not values:
        return None, None, None
    return max(values), min(values), sum(values) / len(values)
