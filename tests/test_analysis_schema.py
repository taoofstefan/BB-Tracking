from __future__ import annotations

import pytest

from analysis_schema import assert_valid_analysis_payload, validate_analysis_payload


def valid_summary() -> dict:
    return {
        "frames_processed": 100,
        "points_tracked": 95,
        "rep_count": 3,
        "max_speed_px_s": 250.0,
        "min_speed_px_s": 0.0,
        "avg_speed_px_s": 125.5,
        "max_speed_m_s": 2.5,
        "min_speed_m_s": 0.0,
        "avg_speed_m_s": 1.255,
        "scale_px_per_meter": 100.0,
    }


def valid_frame(frame: int = 0) -> dict:
    return {
        "frame": frame,
        "time_s": 0.0,
        "center_x": 100,
        "center_y": 200,
    }


def valid_rep(index: int = 1) -> dict:
    return {
        "index": index,
        "start_frame": 0,
        "end_frame": 30,
        "duration_s": 1.0,
        "rom_px": 50.0,
    }


def valid_payload() -> dict:
    return {
        "summary": valid_summary(),
        "frames": [valid_frame()],
        "reps": [valid_rep()],
        "quality": {"reps": []},
    }


def test_valid_payload_returns_no_errors() -> None:
    assert validate_analysis_payload(valid_payload()) == []


def test_missing_top_level_keys_reports_each_missing_key() -> None:
    errors = validate_analysis_payload({})
    assert "summary is required" in errors
    assert "frames is required" in errors
    assert "reps is required" in errors


def test_non_dict_payload_reports_single_error() -> None:
    assert validate_analysis_payload(None) == ["payload must be a dict, got NoneType"]


def test_summary_integer_fields_must_be_non_negative_integers() -> None:
    payload = valid_payload()
    payload["summary"]["frames_processed"] = -1
    payload["summary"]["points_tracked"] = "95"
    payload["summary"]["rep_count"] = True

    errors = validate_analysis_payload(payload)

    assert "summary.frames_processed must be a non-negative integer" in errors
    assert "summary.points_tracked must be a non-negative integer" in errors
    assert "summary.rep_count must be a non-negative integer" in errors


def test_summary_speed_fields_must_be_number_or_null() -> None:
    payload = valid_payload()
    payload["summary"]["max_speed_px_s"] = "fast"
    payload["summary"]["avg_speed_px_s"] = None
    payload["summary"]["scale_px_per_meter"] = False

    errors = validate_analysis_payload(payload)

    assert "summary.max_speed_px_s must be a number or null" in errors
    assert "summary.scale_px_per_meter must be a number or null" in errors
    assert "summary.avg_speed_px_s must be a number or null" not in errors


def test_frames_must_be_a_list_of_dicts_with_required_fields() -> None:
    payload = valid_payload()
    payload["frames"] = [{"frame": 1}, "not a frame"]

    errors = validate_analysis_payload(payload)

    assert "frames[0].time_s is required" in errors
    assert "frames[0].center_x is required" in errors
    assert "frames[0].center_y is required" in errors
    assert "frames[1] must be a dict, got str" in errors


def test_reps_must_be_a_list_of_dicts_with_required_fields() -> None:
    payload = valid_payload()
    payload["reps"] = [{"index": 1}, "not a rep"]

    errors = validate_analysis_payload(payload)

    assert "reps[0].start_frame is required" in errors
    assert "reps[0].end_frame is required" in errors
    assert "reps[0].duration_s is required" in errors
    assert "reps[0].rom_px is required" in errors
    assert "reps[1] must be a dict, got str" in errors


def test_quality_is_optional_but_checked_when_present() -> None:
    payload = valid_payload()
    payload.pop("quality")
    assert validate_analysis_payload(payload) == []

    payload["quality"] = "bad"
    assert "quality must be a dict, got str" in validate_analysis_payload(payload)

    payload["quality"] = {"reps": "bad"}
    assert "quality.reps must be a list, got str" in validate_analysis_payload(payload)


def test_quality_warnings_and_coverage_are_validated_when_present() -> None:
    payload = valid_payload()
    payload["quality"] = {
        "reps": [],
        "warnings": ["Tracker lost the bar", "No reps were detected."],
        "tracking_coverage_ratio": 0.82,
        "tracking_lost_frames": 18,
    }
    assert validate_analysis_payload(payload) == []

    payload["quality"]["warnings"] = "bad"
    assert "quality.warnings must be a list of strings" in validate_analysis_payload(payload)

    payload["quality"]["warnings"] = ["ok", 3]
    assert "quality.warnings must be a list of strings" in validate_analysis_payload(payload)

    payload["quality"]["warnings"] = []
    payload["quality"]["tracking_coverage_ratio"] = "0.5"
    assert (
        "quality.tracking_coverage_ratio must be a number or null"
        in validate_analysis_payload(payload)
    )

    payload["quality"]["tracking_coverage_ratio"] = 1.5
    assert (
        "quality.tracking_coverage_ratio must be between 0 and 1"
        in validate_analysis_payload(payload)
    )

    payload["quality"]["tracking_coverage_ratio"] = None
    payload["quality"]["tracking_lost_frames"] = -2
    assert (
        "quality.tracking_lost_frames must be a non-negative integer"
        in validate_analysis_payload(payload)
    )

    payload["quality"]["tracking_lost_frames"] = 2.5
    assert (
        "quality.tracking_lost_frames must be a non-negative integer"
        in validate_analysis_payload(payload)
    )

    payload["quality"]["tracking_lost_frames"] = None
    assert validate_analysis_payload(payload) == []


def test_quality_warning_fields_optional_for_backward_compat() -> None:
    payload = valid_payload()
    payload["quality"] = {"reps": []}
    assert validate_analysis_payload(payload) == []


def test_unknown_fields_are_allowed() -> None:
    payload = valid_payload()
    payload["future_top_level"] = {"anything": "goes"}
    payload["summary"]["future_summary_metric"] = 12
    payload["frames"][0]["future_frame_metric"] = 13
    payload["reps"][0]["future_rep_metric"] = 14

    assert validate_analysis_payload(payload) == []


def test_generated_style_payload_is_valid() -> None:
    payload = {
        "summary": {
            "frames_processed": 766,
            "points_tracked": 627,
            "rep_count": 7,
            "max_speed_px_s": 758.0,
            "min_speed_px_s": 0.0,
            "avg_speed_px_s": 250.0,
            "max_speed_m_s": 7.58,
            "min_speed_m_s": 0.0,
            "avg_speed_m_s": 2.5,
            "scale_px_per_meter": 100.0,
        },
        "frames": [
            {
                "frame": 12,
                "time_s": 0.4,
                "center_x": 344,
                "center_y": 122,
                "speed_px_s": None,
                "speed_m_s": None,
            }
        ],
        "reps": [
            {
                "index": 1,
                "start_frame": 10,
                "end_frame": 40,
                "start_time_s": 0.4,
                "end_time_s": 1.8,
                "duration_s": 1.4,
                "rom_px": 126,
                "mean_speed_m_s": 1.065,
                "velocity_loss_pct": 0.0,
            }
        ],
        "quality": {
            "max_horizontal_drift_px": 73,
            "avg_horizontal_drift_px": 31.7,
            "rom_consistency_cv": 0.399,
            "sticking_rep_index": 1,
            "sticking_time_s": 0.43,
            "reps": [
                {
                    "index": 1,
                    "horizontal_drift_px": 30.0,
                    "min_center_x": 300,
                    "max_center_x": 370,
                }
            ],
        },
    }

    assert validate_analysis_payload(payload) == []


def test_assert_valid_analysis_payload_raises_joined_errors() -> None:
    with pytest.raises(ValueError) as exc_info:
        assert_valid_analysis_payload({})

    message = str(exc_info.value)
    assert "summary is required" in message
    assert "frames is required" in message
    assert "reps is required" in message
    assert "; " in message


def test_assert_valid_analysis_payload_accepts_valid_payload() -> None:
    assert_valid_analysis_payload(valid_payload())
