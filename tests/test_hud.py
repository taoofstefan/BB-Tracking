from __future__ import annotations

from barbell_tracker import build_hud_lines


def test_build_hud_lines_with_calibration():
    lines = build_hud_lines(
        frame_number=10,
        time_s=0.5,
        points_tracked=8,
        speed_px_s=120.0,
        speed_m_s_value=1.2,
        peak_speed_px_s=150.0,
        scale_px_per_meter=100.0,
    )

    assert lines == [
        "Frame: 10  Time: 0.50s",
        "Speed: 1.200 m/s (120.0 px/s)",
        "Peak: 1.500 m/s (150.0 px/s)",
        "Tracked points: 8",
    ]
