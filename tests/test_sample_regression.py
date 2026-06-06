from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis_schema import assert_valid_analysis_payload
from barbell_tracker import track_video


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = Path(__file__).parent / "fixtures" / "lifts.json"


def _load_manifest() -> list[dict]:
    """Return the list of fixture cases declared in ``lifts.json``."""

    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    cases = data.get("fixtures", [])
    if not isinstance(cases, list):
        raise ValueError(
            f"manifest {MANIFEST_PATH} must contain a list under 'fixtures'"
        )
    return cases


def _resolve(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = ROOT / path
    return path


def _pytest_id(case: dict) -> str:
    return case.get("name") or case.get("video") or "fixture"


def _build_test(case: dict):
    """Build a pytest test function that exercises ``case`` from the manifest."""

    video_path = _resolve(case["video"])
    expected_path = _resolve(case["expected_metrics"])
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    expected_rep_count = case.get(
        "expected_rep_count", expected["summary"]["rep_count"]
    )
    marks = [
        getattr(pytest.mark, name)
        for name in case.get("marks", [])
        if hasattr(pytest.mark, name)
    ]
    if not any(getattr(m, "name", None) == "regression" for m in marks):
        marks.append(pytest.mark.regression)

    def test_fixture_matches_golden_metrics(tmp_path) -> None:
        pytest.importorskip("cv2")
        if case.get("skip"):
            pytest.skip(
                f"fixture {case.get('name')!r} marked skip=true in manifest"
            )
        if not video_path.exists():
            pytest.skip(f"video {video_path} is not available")

        output_video = tmp_path / f"{video_path.stem}-output.avi"
        output_json = tmp_path / f"{video_path.stem}-analysis.json"

        track_video(
            video_path,
            output_video,
            tracker_name=case.get("tracker", "mosse"),
            roi=tuple(case["roi"]),
            display=False,
            json_output=output_json,
            scale_px_per_meter=case.get("scale_px_per_meter"),
            rep_direction=case.get("rep_direction", "up"),
            min_rep_rom_px=case.get("min_rep_rom_px", 20),
            min_rep_frames=case.get("min_rep_frames", 3),
            rep_smoothing_window=case.get("rep_smoothing_window", 1),
            rep_deadband_px=case.get("rep_deadband_px", 0),
            rep_detector=case.get("rep_detector", "direction"),
            rep_phase_jitter_px=case.get("rep_phase_jitter_px"),
        )

        actual = json.loads(output_json.read_text(encoding="utf-8"))
        assert_valid_analysis_payload(actual)
        assert_summary_matches(actual["summary"], expected["summary"])
        assert_reps_match(actual["reps"], expected["reps"])
        assert actual["summary"]["rep_count"] == expected_rep_count

    for mark in marks:
        test_fixture_matches_golden_metrics = mark(test_fixture_matches_golden_metrics)
    return test_fixture_matches_golden_metrics


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


# Generate one test function per manifest entry so each fixture has its own
# test id in the pytest report. Manual registration keeps the loader
# dependency-free and easy to inspect.
for _case in _load_manifest():
    globals()[f"test_{_pytest_id(_case)}_matches_golden_metrics"] = _build_test(_case)
