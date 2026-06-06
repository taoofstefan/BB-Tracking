from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Sequence

from reps import RepRange


@dataclass(frozen=True)
class RepQuality:
    index: int
    horizontal_drift_px: int | None
    min_center_x: int | None
    max_center_x: int | None
    sticking_frame: int | None
    sticking_time_s: float | None
    sticking_speed_px_s: float | None
    sticking_speed_m_s: float | None


@dataclass(frozen=True)
class PathQuality:
    max_horizontal_drift_px: int | None
    avg_horizontal_drift_px: float | None
    rom_consistency_cv: float | None
    sticking_rep_index: int | None
    sticking_frame: int | None
    sticking_time_s: float | None
    sticking_speed_px_s: float | None
    sticking_speed_m_s: float | None
    reps: list[RepQuality]


def analyze_path_quality(frames: Sequence[object], rep_ranges: Sequence[RepRange]) -> PathQuality:
    rep_quality = [
        analyze_rep_quality(index, frames[rep_range.start_index: rep_range.end_index + 1])
        for index, rep_range in enumerate(rep_ranges, start=1)
    ]
    drifts = [
        rep.horizontal_drift_px
        for rep in rep_quality
        if rep.horizontal_drift_px is not None
    ]
    roms = [
        vertical_rom(frames[rep_range.start_index: rep_range.end_index + 1])
        for rep_range in rep_ranges
    ]
    roms = [rom for rom in roms if rom is not None]
    global_sticking = find_global_sticking_rep(rep_quality)

    return PathQuality(
        max_horizontal_drift_px=max(drifts) if drifts else None,
        avg_horizontal_drift_px=mean(drifts) if drifts else None,
        rom_consistency_cv=coefficient_of_variation(roms),
        sticking_rep_index=global_sticking.index if global_sticking else None,
        sticking_frame=global_sticking.sticking_frame if global_sticking else None,
        sticking_time_s=global_sticking.sticking_time_s if global_sticking else None,
        sticking_speed_px_s=global_sticking.sticking_speed_px_s if global_sticking else None,
        sticking_speed_m_s=global_sticking.sticking_speed_m_s if global_sticking else None,
        reps=rep_quality,
    )


def analyze_rep_quality(index: int, frames: Sequence[object]) -> RepQuality:
    if not frames:
        return RepQuality(index, None, None, None, None, None, None, None)

    center_xs = [getattr(frame, "center_x") for frame in frames]
    sticking = find_sticking_frame(frames)
    return RepQuality(
        index=index,
        horizontal_drift_px=max(center_xs) - min(center_xs),
        min_center_x=min(center_xs),
        max_center_x=max(center_xs),
        sticking_frame=getattr(sticking, "frame") if sticking is not None else None,
        sticking_time_s=getattr(sticking, "time_s") if sticking is not None else None,
        sticking_speed_px_s=getattr(sticking, "speed_px_s") if sticking is not None else None,
        sticking_speed_m_s=getattr(sticking, "speed_m_s") if sticking is not None else None,
    )


def find_sticking_frame(frames: Sequence[object]) -> object | None:
    candidates = [
        frame
        for frame in frames
        if getattr(frame, "speed_px_s") is not None and getattr(frame, "speed_px_s") > 0
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda frame: getattr(frame, "speed_px_s"))


def find_global_sticking_rep(reps: Sequence[RepQuality]) -> RepQuality | None:
    candidates = [rep for rep in reps if rep.sticking_speed_px_s is not None]
    if not candidates:
        return None
    return min(candidates, key=lambda rep: rep.sticking_speed_px_s or 0)


def vertical_rom(frames: Sequence[object]) -> int | None:
    if not frames:
        return None
    center_ys = [getattr(frame, "center_y") for frame in frames]
    return max(center_ys) - min(center_ys)


def coefficient_of_variation(values: Sequence[int | float]) -> float | None:
    if not values:
        return None
    average = mean(values)
    if average <= 0:
        return None
    return pstdev(values) / average
