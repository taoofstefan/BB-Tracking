from __future__ import annotations

from compare_trackers import TrackerComparison, format_markdown_report, format_optional, format_percent


def test_format_optional_handles_missing_and_numeric_values():
    assert format_optional(None) == "--"
    assert format_optional(12) == "12.0"
    assert format_optional(12.34) == "12.3"


def test_format_percent_handles_missing_and_numeric_values():
    assert format_percent(None) == "--"
    assert format_percent(0.123) == "12.3%"


def test_format_markdown_report_renders_tracker_rows():
    report = format_markdown_report([
        TrackerComparison(
            tracker="mosse",
            elapsed_s=1.23,
            frames_processed=100,
            points_tracked=95,
            rep_count=5,
            avg_speed_px_s=10.0,
            max_speed_px_s=20.0,
            max_horizontal_drift_px=12,
            avg_horizontal_drift_px=8.5,
            rom_consistency_cv=0.1,
        )
    ])

    assert "mosse" in report
    assert "95/100" in report
    assert "10.0%" in report
