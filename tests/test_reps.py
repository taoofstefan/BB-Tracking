import pytest

from reps import RepRange, detect_rep_ranges, smooth_values, summarize_rep_speeds, with_velocity_loss


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


def test_detect_rep_ranges_deadband_ignores_small_jitter_reversals():
    y_values = [200, 170, 172, 140, 210]

    jittery_ranges = detect_rep_ranges(
        y_values,
        direction="up",
        min_rom_px=20,
        min_frames=2,
    )
    filtered_ranges = detect_rep_ranges(
        y_values,
        direction="up",
        min_rom_px=20,
        min_frames=2,
        deadband_px=3,
    )

    assert [(rep.start_index, rep.end_index) for rep in jittery_ranges] == [(0, 1), (2, 3)]
    assert [(rep.start_index, rep.end_index, rep.rom_px) for rep in filtered_ranges] == [(0, 3, 60)]


def test_smooth_values_uses_centered_window():
    assert smooth_values([10, 20, 40, 80], 3) == [
        pytest.approx(15),
        pytest.approx(70 / 3),
        pytest.approx(140 / 3),
        pytest.approx(60),
    ]


def test_detect_rep_ranges_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="direction"):
        detect_rep_ranges([1, 2], direction="sideways")
    with pytest.raises(ValueError, match="min_rom_px"):
        detect_rep_ranges([1, 2], min_rom_px=0)
    with pytest.raises(ValueError, match="min_frames"):
        detect_rep_ranges([1, 2], min_frames=0)
    with pytest.raises(ValueError, match="smoothing_window"):
        detect_rep_ranges([1, 2], smoothing_window=0)
    with pytest.raises(ValueError, match="deadband_px"):
        detect_rep_ranges([1, 2], deadband_px=-1)
    with pytest.raises(ValueError, match="window"):
        smooth_values([1, 2], 0)


def test_detect_rep_ranges_default_mode_is_direction():
    y_values = [200, 170, 140, 210, 180, 150]

    default_ranges = detect_rep_ranges(
        y_values,
        direction="up",
        min_rom_px=30,
        min_frames=2,
    )
    explicit_ranges = detect_rep_ranges(
        y_values,
        direction="up",
        min_rom_px=30,
        min_frames=2,
        mode="direction",
    )

    assert default_ranges == explicit_ranges


def test_detect_rep_ranges_phase_keeps_one_rep_for_jittery_sequence():
    # One full upward rep with a tiny reversal (2px) mid-flight.
    y_values = [200, 180, 160, 162, 140, 120]

    direction_ranges = detect_rep_ranges(
        y_values,
        direction="up",
        min_rom_px=30,
        min_frames=2,
        mode="direction",
    )
    phase_ranges = detect_rep_ranges(
        y_values,
        direction="up",
        min_rom_px=30,
        min_frames=2,
        mode="phase",
    )

    # Direction mode splits at the 2px reversal; phase mode absorbs it.
    assert [(rep.start_index, rep.end_index) for rep in direction_ranges] == [(0, 2), (3, 5)]
    assert [(rep.start_index, rep.end_index, rep.rom_px) for rep in phase_ranges] == [(0, 5, 80)]


def test_detect_rep_ranges_phase_detects_two_real_reps():
    # Two clean upward reps; the second has a 2px jitter that phase mode absorbs.
    y_values = [200, 170, 140, 200, 170, 172, 140]

    phase_ranges = detect_rep_ranges(
        y_values,
        direction="up",
        min_rom_px=30,
        min_frames=2,
        mode="phase",
    )

    assert [(rep.start_index, rep.end_index, rep.rom_px) for rep in phase_ranges] == [
        (0, 2, 60),
        (3, 6, 60),
    ]


def test_detect_rep_ranges_phase_enforces_min_rom_and_min_frames():
    # Sub-ROM phase should be discarded, even though frames and phase are valid.
    small = [200, 195, 190, 200, 195, 190]
    assert detect_rep_ranges(
        small,
        direction="up",
        min_rom_px=30,
        min_frames=2,
        mode="phase",
    ) == []

    # Single-frame phase should be discarded.
    short = [200, 195, 200, 200, 200]
    assert detect_rep_ranges(
        short,
        direction="up",
        min_rom_px=5,
        min_frames=3,
        mode="phase",
    ) == []


def test_detect_rep_ranges_phase_ignores_deadband_argument():
    # Phase mode must not consult deadband_px; a tiny deadband must not break detection.
    y_values = [200, 180, 160, 140]
    assert detect_rep_ranges(
        y_values,
        direction="up",
        min_rom_px=30,
        min_frames=2,
        deadband_px=0,
        mode="phase",
    ) == [RepRange(start_index=0, end_index=3, rom_px=60)]


def test_detect_rep_ranges_rejects_invalid_mode():
    with pytest.raises(ValueError, match="mode"):
        detect_rep_ranges([200, 150], mode="unknown")


def test_detect_rep_ranges_rejects_negative_phase_jitter():
    with pytest.raises(ValueError, match="phase_jitter_px"):
        detect_rep_ranges([200, 150], mode="phase", phase_jitter_px=-1)


def test_detect_rep_ranges_phase_supports_smoothing_window():
    # Smoothing across the jitter should still produce one rep in phase mode.
    y_values = [200, 180, 160, 162, 140, 120]

    phase_ranges = detect_rep_ranges(
        y_values,
        direction="up",
        min_rom_px=30,
        min_frames=2,
        smoothing_window=3,
        mode="phase",
    )

    assert len(phase_ranges) == 1
    assert phase_ranges[0].start_index == 0
    assert phase_ranges[0].end_index == 5


def test_detect_rep_ranges_phase_downward_direction():
    # Two downward-direction (y increasing) reps; second has a small 2px reversal.
    y_values = [100, 130, 160, 100, 130, 132, 160]

    phase_ranges = detect_rep_ranges(
        y_values,
        direction="down",
        min_rom_px=30,
        min_frames=2,
        mode="phase",
    )

    assert [(rep.start_index, rep.end_index, rep.rom_px) for rep in phase_ranges] == [
        (0, 2, 60),
        (3, 6, 60),
    ]


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
