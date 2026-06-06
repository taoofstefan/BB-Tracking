import pytest

from reps import detect_rep_ranges, summarize_rep_speeds, with_velocity_loss


def test_detect_rep_ranges_finds_upward_phases():
    y_values = [200, 170, 140, 210, 180, 150]

    ranges = detect_rep_ranges(y_values, direction="up", min_rom_px=30, min_frames=2)

    assert [(rep.start_index, rep.end_index, rep.rom_px) for rep in ranges] == [
        (0, 2, 60),
        (3, 5, 60),
    ]


def test_detect_rep_ranges_finds_downward_phases():
    y_values = [100, 130, 160, 90, 120, 150]

    ranges = detect_rep_ranges(y_values, direction="down", min_rom_px=30, min_frames=2)

    assert [(rep.start_index, rep.end_index, rep.rom_px) for rep in ranges] == [
        (0, 2, 60),
        (3, 5, 60),
    ]


def test_detect_rep_ranges_filters_small_movements():
    y_values = [200, 190, 205, 195, 210]

    assert detect_rep_ranges(y_values, direction="up", min_rom_px=20, min_frames=2) == []


def test_detect_rep_ranges_filters_short_movements():
    y_values = [200, 140, 210]

    assert detect_rep_ranges(y_values, direction="up", min_rom_px=20, min_frames=3) == []


def test_detect_rep_ranges_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="direction"):
        detect_rep_ranges([1, 2], direction="sideways")
    with pytest.raises(ValueError, match="min_rom_px"):
        detect_rep_ranges([1, 2], min_rom_px=0)
    with pytest.raises(ValueError, match="min_frames"):
        detect_rep_ranges([1, 2], min_frames=0)


def test_summarize_rep_speeds_builds_rep_summary():
    rep_range = detect_rep_ranges([200, 170, 140], direction="up", min_rom_px=30, min_frames=2)[0]

    summary = summarize_rep_speeds(
        1,
        rep_range,
        frames=[10, 11, 12],
        times=[0.33, 0.36, 0.40],
        speeds_px_s=[None, 100.0, 140.0],
        speeds_m_s=[None, 1.0, 1.4],
    )

    assert summary.index == 1
    assert summary.start_frame == 10
    assert summary.end_frame == 12
    assert summary.duration_s == pytest.approx(0.07)
    assert summary.rom_px == 60
    assert summary.peak_speed_px_s == 140.0
    assert summary.mean_speed_px_s == 120.0
    assert summary.peak_speed_m_s == 1.4
    assert summary.mean_speed_m_s == 1.2
    assert summary.velocity_loss_pct is None


def test_with_velocity_loss_compares_mean_speed_to_first_rep():
    first = summarize_rep_speeds(
        1,
        detect_rep_ranges([200, 170, 140], direction="up", min_rom_px=30, min_frames=2)[0],
        frames=[1, 2, 3],
        times=[0.0, 0.1, 0.2],
        speeds_px_s=[None, 100.0, 100.0],
        speeds_m_s=[None, None, None],
    )
    second = summarize_rep_speeds(
        2,
        detect_rep_ranges([210, 180, 150], direction="up", min_rom_px=30, min_frames=2)[0],
        frames=[4, 5, 6],
        times=[0.3, 0.4, 0.5],
        speeds_px_s=[None, 80.0, 80.0],
        speeds_m_s=[None, None, None],
    )

    reps = with_velocity_loss([first, second])

    assert reps[0].velocity_loss_pct == pytest.approx(0)
    assert reps[1].velocity_loss_pct == pytest.approx(20)
