from __future__ import annotations

import numpy as np

from overlay import draw_hud, format_speed_line


def test_format_speed_line_uses_placeholder_without_speed():
    assert format_speed_line(None, None) == "Speed: --"


def test_format_speed_line_uses_pixels_without_calibration():
    assert format_speed_line(123.456, None) == "Speed: 123.5 px/s"


def test_format_speed_line_includes_calibrated_speed():
    assert format_speed_line(123.456, 1.23456) == "Speed: 1.235 m/s (123.5 px/s)"


def test_draw_hud_changes_frame_pixels():
    frame = np.zeros((120, 240, 3), dtype=np.uint8)

    draw_hud(frame, ["Speed: 1.0 m/s", "Tracked points: 42"])

    assert frame.sum() > 0
