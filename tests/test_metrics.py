import pytest

from metrics import pixel_distance, speed_px_s, speeds_from_positions, summarize_speeds


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


def test_summarize_speeds_handles_values():
    assert summarize_speeds([10, 20, 40]) == (40, 10, 70 / 3)


def test_summarize_speeds_handles_empty_input():
    assert summarize_speeds([]) == (None, None, None)
