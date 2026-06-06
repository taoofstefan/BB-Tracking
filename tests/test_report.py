from __future__ import annotations

from dataclasses import dataclass

from report import render_line_chart, render_rep_table, render_report_html, render_warnings


@dataclass(frozen=True)
class FakeSummary:
    frames_processed: int
    points_tracked: int
    rep_count: int
    avg_speed_px_s: float | None
    avg_speed_m_s: float | None
    max_speed_px_s: float | None
    max_speed_m_s: float | None


def test_render_report_html_contains_summary_charts_and_reps():
    summary = FakeSummary(
        frames_processed=10,
        points_tracked=8,
        rep_count=1,
        avg_speed_px_s=100.0,
        avg_speed_m_s=1.0,
        max_speed_px_s=150.0,
        max_speed_m_s=1.5,
    )
    frames = [
        {"time_s": 0.0, "speed_px_s": None, "speed_m_s": None, "center_x": 10, "center_y": 40},
        {"time_s": 0.1, "speed_px_s": 100.0, "speed_m_s": 1.0, "center_x": 12, "center_y": 30},
        {"time_s": 0.2, "speed_px_s": 120.0, "speed_m_s": 1.2, "center_x": 13, "center_y": 20},
    ]
    reps = [
        {
            "index": 1,
            "start_time_s": 0.0,
            "end_time_s": 0.2,
            "duration_s": 0.2,
            "rom_px": 20,
            "mean_speed_px_s": 110.0,
            "mean_speed_m_s": 1.1,
            "velocity_loss_pct": 0.0,
        }
    ]

    quality = {
        "max_horizontal_drift_px": 12,
        "avg_horizontal_drift_px": 8,
        "rom_consistency_cv": 0.1,
        "sticking_speed_px_s": 50,
        "sticking_speed_m_s": 0.5,
    }

    html = render_report_html(summary, frames, reps, quality)

    assert "Barbell Tracking Report" in html
    assert "Velocity Over Time" in html
    assert "Bar Path" in html
    assert "Path Quality" in html
    assert "10.0%" in html
    assert "1.100 m/s" in html


def test_render_rep_table_escapes_values():
    html = render_rep_table([
        {
            "index": "<1>",
            "start_time_s": 0,
            "end_time_s": 1,
            "duration_s": 1,
            "rom_px": 42,
            "mean_speed_px_s": 90,
            "mean_speed_m_s": None,
            "velocity_loss_pct": None,
        }
    ])

    assert "&lt;1&gt;" in html


def test_render_line_chart_handles_empty_data():
    assert "No speed data" in render_line_chart([], stroke="#000", empty_label="No speed data")


def test_render_warnings_escapes_warning_text():
    html = render_warnings(["Tracker <lost> the bar"])

    assert "Tracking warnings" in html
    assert "Tracker &lt;lost&gt; the bar" in html
