"""Lightweight validation for analysis JSON payloads."""

from __future__ import annotations

from typing import Any

SUMMARY_INT_FIELDS = ("frames_processed", "points_tracked", "rep_count")
SUMMARY_NUMBER_OR_NONE_FIELDS = (
    "max_speed_px_s",
    "min_speed_px_s",
    "avg_speed_px_s",
    "max_speed_m_s",
    "min_speed_m_s",
    "avg_speed_m_s",
    "scale_px_per_meter",
)
FRAME_REQUIRED_FIELDS = ("frame", "time_s", "center_x", "center_y")
REP_REQUIRED_FIELDS = ("index", "start_frame", "end_frame", "duration_s", "rom_px")


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_summary(summary: Any, errors: list[str]) -> None:
    if not isinstance(summary, dict):
        errors.append(f"summary must be a dict, got {type(summary).__name__}")
        return

    for field in SUMMARY_INT_FIELDS:
        if field not in summary:
            errors.append(f"summary.{field} is required")
            continue
        value = summary[field]
        if not _is_int(value) or value < 0:
            errors.append(f"summary.{field} must be a non-negative integer")

    for field in SUMMARY_NUMBER_OR_NONE_FIELDS:
        if field not in summary:
            continue
        value = summary[field]
        if value is not None and not _is_number(value):
            errors.append(f"summary.{field} must be a number or null")


def _validate_frames(frames: Any, errors: list[str]) -> None:
    if not isinstance(frames, list):
        errors.append(f"frames must be a list, got {type(frames).__name__}")
        return

    for index, frame in enumerate(frames):
        if not isinstance(frame, dict):
            errors.append(f"frames[{index}] must be a dict, got {type(frame).__name__}")
            continue
        for field in FRAME_REQUIRED_FIELDS:
            if field not in frame:
                errors.append(f"frames[{index}].{field} is required")


def _validate_reps(reps: Any, errors: list[str]) -> None:
    if not isinstance(reps, list):
        errors.append(f"reps must be a list, got {type(reps).__name__}")
        return

    for index, rep in enumerate(reps):
        if not isinstance(rep, dict):
            errors.append(f"reps[{index}] must be a dict, got {type(rep).__name__}")
            continue
        for field in REP_REQUIRED_FIELDS:
            if field not in rep:
                errors.append(f"reps[{index}].{field} is required")


def _validate_quality(quality: Any, errors: list[str]) -> None:
    if not isinstance(quality, dict):
        errors.append(f"quality must be a dict, got {type(quality).__name__}")
        return
    quality_reps = quality.get("reps")
    if quality_reps is not None and not isinstance(quality_reps, list):
        errors.append(f"quality.reps must be a list, got {type(quality_reps).__name__}")

    warnings = quality.get("warnings")
    if warnings is not None and not (
        isinstance(warnings, list)
        and all(isinstance(item, str) for item in warnings)
    ):
        errors.append("quality.warnings must be a list of strings")

    for field in ("tracking_coverage_ratio", "tracking_lost_frames"):
        if field not in quality:
            continue
        value = quality[field]
        if value is None:
            continue
        if field == "tracking_lost_frames":
            if not _is_int(value) or value < 0:
                errors.append("quality.tracking_lost_frames must be a non-negative integer")
            continue
        if not _is_number(value):
            errors.append(f"quality.{field} must be a number or null")
            continue
        if field == "tracking_coverage_ratio" and not 0.0 <= float(value) <= 1.0:
            errors.append("quality.tracking_coverage_ratio must be between 0 and 1")


def validate_analysis_payload(payload: Any) -> list[str]:
    """Return human-readable schema errors for an analysis payload.

    Unknown fields are intentionally ignored so the contract can evolve
    additively without breaking older validators.
    """

    if not isinstance(payload, dict):
        return [f"payload must be a dict, got {type(payload).__name__}"]

    errors: list[str] = []
    for field in ("summary", "frames", "reps"):
        if field not in payload:
            errors.append(f"{field} is required")

    if "summary" in payload:
        _validate_summary(payload["summary"], errors)
    if "frames" in payload:
        _validate_frames(payload["frames"], errors)
    if "reps" in payload:
        _validate_reps(payload["reps"], errors)
    if "quality" in payload:
        _validate_quality(payload["quality"], errors)

    return errors


def assert_valid_analysis_payload(payload: Any) -> None:
    """Raise ``ValueError`` when ``payload`` violates the analysis contract."""

    errors = validate_analysis_payload(payload)
    if errors:
        raise ValueError("invalid analysis payload: " + "; ".join(errors))
