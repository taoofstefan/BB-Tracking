import pytest

from metrics import (
    pixel_distance,
    scale_from_reference,
    speed_m_s,
    speed_px_s,
    speeds_from_positions,
    summarize_speeds,
)


def test_pixel_distance_uses_euclidean_distance():
    assert pixel_distance((0, 0), (3, 4)) == 5


def test_speed_px_s_multiplies_frame_distance_by_fps():
    assert speed_px_s((0, 0), (3, 4), fps=30) == 150


def test_speed_px_s_rejects_invalid_fps():
    with pytest.raises(ValueError, match="fps must be positive"):
        speed_px_s((0, 0), (1, 1), fps=0)


def test_speeds_from_positions_uses_adjacent_points():
    positions = [(0, 0), (3, 4), (6, 8)]
    assert speeds_from_positions(positions, fps=30) == [150, 150]


def test_scale_from_reference_returns_pixels_per_meter():
    assert scale_from_reference(reference_px=220, reference_m=2.2) == pytest.approx(100)


def test_scale_from_reference_rejects_invalid_values():
    with pytest.raises(ValueError, match="reference_px must be positive"):
        scale_from_reference(reference_px=0, reference_m=2.2)
    with pytest.raises(ValueError, match="reference_m must be positive"):
        scale_from_reference(reference_px=220, reference_m=0)


def test_speed_m_s_converts_pixel_speed_to_real_units():
    assert speed_m_s(speed_pixels_s=150, scale_px_per_meter=100) == 1.5


def test_speed_m_s_rejects_invalid_scale():
    with pytest.raises(ValueError, match="scale_px_per_meter must be positive"):
        speed_m_s(speed_pixels_s=150, scale_px_per_meter=0)


def test_summarize_speeds_handles_values():
    assert summarize_speeds([10, 20, 40]) == (40, 10, 70 / 3)


def test_summarize_speeds_handles_empty_input():
    assert summarize_speeds([]) == (None, None, None)
