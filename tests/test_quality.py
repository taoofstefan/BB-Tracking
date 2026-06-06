from __future__ import annotations

from dataclasses import dataclass

import pytest

from quality import analyze_path_quality, coefficient_of_variation, vertical_rom
from reps import RepRange


@dataclass(frozen=True)
class Frame:
    frame: int
    time_s: float
    center_x: int
    center_y: int
    speed_px_s: float | None
    speed_m_s: float | None = None


def test_analyze_path_quality_calculates_drift_rom_and_sticking_frame():
    frames = [
        Frame(1, 0.0, 100, 200, None),
        Frame(2, 0.1, 104, 170, 80.0, 0.8),
        Frame(3, 0.2, 110, 140, 60.0, 0.6),
        Frame(4, 0.3, 120, 210, None),
        Frame(5, 0.4, 126, 180, 50.0, 0.5),
        Frame(6, 0.5, 122, 150, 70.0, 0.7),
    ]

    quality = analyze_path_quality(
        frames,
        [
            RepRange(start_index=0, end_index=2, rom_px=60),
            RepRange(start_index=3, end_index=5, rom_px=60),
        ],
    )

    assert quality.max_horizontal_drift_px == 10
    assert quality.avg_horizontal_drift_px == pytest.approx(8)
    assert quality.rom_consistency_cv == pytest.approx(0)
    assert quality.sticking_rep_index == 2
    assert quality.sticking_frame == 5
    assert quality.sticking_speed_px_s == 50.0
    assert quality.sticking_speed_m_s == 0.5
    assert [rep.horizontal_drift_px for rep in quality.reps] == [10, 6]


def test_analyze_path_quality_handles_missing_reps():
    quality = analyze_path_quality([], [])

    assert quality.max_horizontal_drift_px is None
    assert quality.avg_horizontal_drift_px is None
    assert quality.rom_consistency_cv is None
    assert quality.sticking_frame is None
    assert quality.reps == []


def test_vertical_rom_and_coefficient_of_variation():
    frames = [
        Frame(1, 0.0, 100, 200, None),
        Frame(2, 0.1, 100, 150, None),
        Frame(3, 0.2, 100, 180, None),
    ]

    assert vertical_rom(frames) == 50
    assert vertical_rom([]) is None
    assert coefficient_of_variation([100, 100, 100]) == pytest.approx(0)
    assert coefficient_of_variation([]) is None
    assert coefficient_of_variation([0, 0]) is None


def test_sticking_frame_ignores_zero_speed_points():
    frames = [
        Frame(1, 0.0, 100, 200, 0.0),
        Frame(2, 0.1, 102, 180, 25.0),
        Frame(3, 0.2, 104, 160, 40.0),
    ]

    quality = analyze_path_quality(frames, [RepRange(start_index=0, end_index=2, rom_px=40)])

    assert quality.sticking_frame == 2
    assert quality.sticking_speed_px_s == 25.0
