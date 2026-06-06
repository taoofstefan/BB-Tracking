from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, pstdev
from typing import Sequence

from reps import RepRange


# Thresholds for ``analyze_tracking_warnings``. Coverage is
# ``points_tracked / frames_processed`` and is in [0, 1].
COVERAGE_LOW_RATIO = 0.5  # below this, emit a high-severity warning
COVERAGE_CAUTION_RATIO = 0.8  # below this, emit a caution warning


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
    tracking_coverage_ratio: float | None = None
    tracking_lost_frames: int | None = None
    warnings: list[str] = field(default_factory=list)


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
        tracking_coverage_ratio=None,
        tracking_lost_frames=None,
        warnings=[],
    )


def analyze_tracking_warnings(
    frames_processed: int | None,
    points_tracked: int | None,
    rep_count: int | None,
) -> tuple[float | None, int | None, list[str]]:
    """Compute tracking coverage and a list of human-readable warnings.

    The helper is intentionally tolerant: it accepts counts that may be
    ``None`` (returned as ``None``) and clamps negative or oversized values
    so a misbehaving caller cannot crash the analysis pipeline.

    Returns
    -------
    tuple
        ``(coverage_ratio, lost_frames, warnings)`` where ``coverage_ratio``
        is ``points_tracked / frames_processed`` (or ``None`` when there is
        no frame data), ``lost_frames`` is ``frames_processed -
        points_tracked`` clamped to zero (or ``None``), and ``warnings`` is
        a list of short, user-facing strings describing tracking or rep
        quality issues. The list is empty when the run looks healthy.
    """

    warnings: list[str] = []

    if frames_processed is None or frames_processed <= 0:
        warnings.append("No frames were processed; analysis is unreliable.")
        return None, None, warnings

    if points_tracked is None or points_tracked < 0:
        points_tracked = 0

    lost_frames = max(frames_processed - points_tracked, 0)
    coverage = points_tracked / frames_processed

    if points_tracked == 0:
        warnings.append(
            "No bar position was tracked; the bar may be off-screen or "
            "the ROI is wrong."
        )
    elif coverage < COVERAGE_LOW_RATIO:
        warnings.append(
            f"Tracker lost the bar on {lost_frames} of {frames_processed} "
            f"frames (coverage {coverage:.0%}); results may be unreliable."
        )
    elif coverage < COVERAGE_CAUTION_RATIO:
        warnings.append(
            f"Tracker lost the bar on {lost_frames} of {frames_processed} "
            f"frames (coverage {coverage:.0%})."
        )

    if rep_count is None or rep_count <= 0:
        warnings.append("No reps were detected in this video.")

    return coverage, lost_frames, warnings


def attach_tracking_warnings(
    path_quality: PathQuality,
    frames_processed: int,
    points_tracked: int,
    rep_count: int,
) -> PathQuality:
    """Return a new ``PathQuality`` with coverage, lost-frames, and warnings
    populated by :func:`analyze_tracking_warnings`."""

    coverage, lost_frames, warnings = analyze_tracking_warnings(
        frames_processed, points_tracked, rep_count
    )
    return PathQuality(
        max_horizontal_drift_px=path_quality.max_horizontal_drift_px,
        avg_horizontal_drift_px=path_quality.avg_horizontal_drift_px,
        rom_consistency_cv=path_quality.rom_consistency_cv,
        sticking_rep_index=path_quality.sticking_rep_index,
        sticking_frame=path_quality.sticking_frame,
        sticking_time_s=path_quality.sticking_time_s,
        sticking_speed_px_s=path_quality.sticking_speed_px_s,
        sticking_speed_m_s=path_quality.sticking_speed_m_s,
        reps=path_quality.reps,
        tracking_coverage_ratio=coverage,
        tracking_lost_frames=lost_frames,
        warnings=warnings,
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
