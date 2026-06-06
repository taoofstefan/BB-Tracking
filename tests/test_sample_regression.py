from __future__ import annotations

import json
from pathlib import Path

import pytest

from barbell_tracker import track_video


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_VIDEO = ROOT / "lift.mp4"
EXPECTED_FILE = Path(__file__).parent / "fixtures" / "sample_metrics.json"


@pytest.mark.regression
def test_sample_video_metrics_match_golden_fixture(tmp_path):
    pytest.importorskip("cv2")
    if not SAMPLE_VIDEO.exists():
        pytest.skip("sample video is not available")

    output_video = tmp_path / "sample-output.avi"
    output_json = tmp_path / "sample-analysis.json"

    track_video(
        SAMPLE_VIDEO,
        output_video,
        roi=(300, 120, 80, 40),
        display=False,
        json_output=output_json,
        scale_px_per_meter=100,
    )

    actual = json.loads(output_json.read_text(encoding="utf-8"))
    expected = json.loads(EXPECTED_FILE.read_text(encoding="utf-8"))
    assert_summary_matches(actual["summary"], expected["summary"])
    assert_reps_match(actual["reps"], expected["reps"])


def assert_summary_matches(actual: dict, expected: dict) -> None:
    for key in ("frames_processed", "points_tracked", "rep_count"):
        assert actual[key] == expected[key]
    for key in ("avg_speed_px_s", "max_speed_px_s", "avg_speed_m_s", "max_speed_m_s"):
        assert actual[key] == pytest.approx(expected[key], rel=0.01)


def assert_reps_match(actual: list[dict], expected: list[dict]) -> None:
    assert len(actual) == len(expected)
    for actual_rep, expected_rep in zip(actual, expected):
        for key in ("index", "start_frame", "end_frame", "rom_px"):
            assert actual_rep[key] == expected_rep[key]
        assert actual_rep["mean_speed_px_s"] == pytest.approx(
            expected_rep["mean_speed_px_s"],
            rel=0.03,
        )
        assert actual_rep["velocity_loss_pct"] == pytest.approx(
            expected_rep["velocity_loss_pct"],
            abs=0.5,
        )
