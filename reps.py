from __future__ import annotations

from dataclasses import dataclass, replace
from statistics import mean
from typing import Sequence


@dataclass(frozen=True)
class RepRange:
    start_index: int
    end_index: int
    rom_px: int


@dataclass(frozen=True)
class RepSummary:
    index: int
    start_frame: int
    end_frame: int
    start_time_s: float
    end_time_s: float
    duration_s: float
    rom_px: int
    peak_speed_px_s: float | None
    mean_speed_px_s: float | None
    peak_speed_m_s: float | None
    mean_speed_m_s: float | None
    velocity_loss_pct: float | None


def detect_rep_ranges(
    y_values: Sequence[int],
    *,
    direction: str = "up",
    min_rom_px: int = 20,
    min_frames: int = 3,
    smoothing_window: int = 1,
    deadband_px: float = 0,
) -> list[RepRange]:
    if direction not in {"up", "down"}:
        raise ValueError("direction must be 'up' or 'down'")
    if min_rom_px <= 0:
        raise ValueError("min_rom_px must be positive")
    if min_frames <= 0:
        raise ValueError("min_frames must be positive")
    if smoothing_window <= 0:
        raise ValueError("smoothing_window must be positive")
    if deadband_px < 0:
        raise ValueError("deadband_px must be zero or positive")
    if len(y_values) < 2:
        return []

    detection_values = smooth_values(y_values, smoothing_window)
    ranges: list[RepRange] = []
    start_index: int | None = None
    best_index: int | None = None

    for index in range(1, len(detection_values)):
        delta = detection_values[index] - detection_values[index - 1]
        if abs(delta) <= deadband_px:
            continue
        is_target_direction = delta < 0 if direction == "up" else delta > 0
        is_reverse_direction = delta > 0 if direction == "up" else delta < 0

        if start_index is None:
            if is_target_direction:
                start_index = index - 1
                best_index = index
            continue

        assert best_index is not None
        if direction == "up" and detection_values[index] < detection_values[best_index]:
            best_index = index
        elif direction == "down" and detection_values[index] > detection_values[best_index]:
            best_index = index

        if is_reverse_direction:
            maybe_add_rep_range(ranges, y_values, start_index, best_index, min_rom_px, min_frames)
            start_index = None
            best_index = None

    if start_index is not None and best_index is not None:
        maybe_add_rep_range(ranges, y_values, start_index, best_index, min_rom_px, min_frames)

    return ranges


def smooth_values(values: Sequence[int], window: int) -> list[float]:
    if window <= 0:
        raise ValueError("window must be positive")
    if window == 1:
        return [float(value) for value in values]

    radius = window // 2
    smoothed: list[float] = []
    for index in range(len(values)):
        start = max(index - radius, 0)
        end = min(index + radius + 1, len(values))
        smoothed.append(mean(values[start:end]))
    return smoothed


def maybe_add_rep_range(
    ranges: list[RepRange],
    y_values: Sequence[int],
    start_index: int,
    end_index: int,
    min_rom_px: int,
    min_frames: int,
) -> None:
    rom_px = abs(y_values[start_index] - y_values[end_index])
    if rom_px < min_rom_px:
        return
    if end_index - start_index + 1 < min_frames:
        return
    ranges.append(RepRange(start_index=start_index, end_index=end_index, rom_px=rom_px))


def summarize_rep_speeds(
    index: int,
    rep_range: RepRange,
    *,
    frames: Sequence[int],
    times: Sequence[float],
    speeds_px_s: Sequence[float | None],
    speeds_m_s: Sequence[float | None],
) -> RepSummary:
    speed_slice = [value for value in speeds_px_s[rep_range.start_index: rep_range.end_index + 1] if value is not None]
    calibrated_slice = [value for value in speeds_m_s[rep_range.start_index: rep_range.end_index + 1] if value is not None]
    start_time = times[rep_range.start_index]
    end_time = times[rep_range.end_index]
    return RepSummary(
        index=index,
        start_frame=frames[rep_range.start_index],
        end_frame=frames[rep_range.end_index],
        start_time_s=start_time,
        end_time_s=end_time,
        duration_s=max(end_time - start_time, 0),
        rom_px=rep_range.rom_px,
        peak_speed_px_s=max(speed_slice) if speed_slice else None,
        mean_speed_px_s=mean(speed_slice) if speed_slice else None,
        peak_speed_m_s=max(calibrated_slice) if calibrated_slice else None,
        mean_speed_m_s=mean(calibrated_slice) if calibrated_slice else None,
        velocity_loss_pct=None,
    )


def with_velocity_loss(reps: Sequence[RepSummary]) -> list[RepSummary]:
    if not reps:
        return []
    baseline = reps[0].mean_speed_px_s
    if baseline is None or baseline <= 0:
        return list(reps)
    return [
        replace(
            rep,
            velocity_loss_pct=((baseline - rep.mean_speed_px_s) / baseline * 100)
            if rep.mean_speed_px_s is not None
            else None,
        )
        for rep in reps
    ]
