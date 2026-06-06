from __future__ import annotations

from tempfile import TemporaryDirectory

import pytest

import service
from service import (
    AnalysisJob,
    JobStatus,
    clear_jobs,
    parse_optional_positive_float,
    safe_video_suffix,
)


@pytest.fixture(autouse=True)
def isolate_jobs():
    clear_jobs()
    yield
    clear_jobs()


def test_parse_optional_positive_float_handles_empty_values():
    assert parse_optional_positive_float(None, "scale") is None
    assert parse_optional_positive_float("", "scale") is None


def test_parse_optional_positive_float_rejects_non_positive_values():
    with pytest.raises(ValueError, match="scale"):
        parse_optional_positive_float("0", "scale")


def test_parse_optional_positive_float_parses_positive_values():
    assert parse_optional_positive_float("12.5", "scale") == pytest.approx(12.5)


def test_safe_video_suffix_allows_known_video_suffixes():
    assert safe_video_suffix("lift.mp4") == ".mp4"
    assert safe_video_suffix("lift.MOV") == ".mov"
    assert safe_video_suffix("lift.txt") == ".mp4"
    assert safe_video_suffix(None) == ".mp4"


def test_create_app_health_endpoint_when_fastapi_is_installed():
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    client = testclient.TestClient(create_app())

    assert client.get("/health").json() == {"status": "ok"}


def test_create_app_health_endpoint_allows_dev_cors_when_fastapi_is_installed():
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    client = testclient.TestClient(create_app())
    response = client.get("/health", headers={"Origin": "file://"})

    assert response.headers["access-control-allow-origin"] == "*"


def test_analyze_endpoint_uses_shared_runner_when_fastapi_is_installed(monkeypatch):
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    def fake_run_analysis(input_path, output_path, json_path, params):
        assert input_path.exists()
        assert params["roi"] == (300, 120, 80, 40)
        assert params["scale_px_per_meter"] == pytest.approx(100)
        return {"summary": {"rep_count": 1}, "frames": [], "reps": []}

    monkeypatch.setattr(service, "run_analysis", fake_run_analysis)
    client = testclient.TestClient(create_app())

    response = client.post(
        "/analyze",
        data={"roi": "300,120,80,40", "scale_px_per_meter": "100"},
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    assert response.status_code == 200
    assert response.json()["summary"]["rep_count"] == 1


def test_post_jobs_creates_job_and_completes_when_fastapi_is_installed(monkeypatch):
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    def fake_run_analysis(input_path, output_path, json_path, params):
        assert input_path.exists()
        return {"summary": {"rep_count": 2}, "frames": [], "reps": []}

    monkeypatch.setattr(service, "run_analysis", fake_run_analysis)
    client = testclient.TestClient(create_app())

    response = client.post(
        "/jobs",
        data={"roi": "300,120,80,40", "tracker": "mosse"},
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    assert response.status_code == 202
    payload = response.json()
    assert len(payload["job_id"]) == 32
    assert payload["status"] == "queued"

    status_response = client.get(f"/jobs/{payload['job_id']}")
    assert status_response.json()["status"] == "complete"

    result_response = client.get(f"/jobs/{payload['job_id']}/result")
    assert result_response.status_code == 200
    assert result_response.json()["summary"]["rep_count"] == 2


def test_job_status_unknown_job_returns_404_when_fastapi_is_installed():
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    client = testclient.TestClient(create_app())

    assert client.get("/jobs/missing").status_code == 404
    assert client.get("/jobs/missing/result").status_code == 404


def test_job_result_before_completion_returns_409_when_fastapi_is_installed():
    testclient = pytest.importorskip("fastapi.testclient")
    from service import JOB_LOCK, JOB_STORE, create_app

    temp_dir = TemporaryDirectory(prefix="bbtracking-test-job-")
    job = AnalysisJob(
        job_id="queued-job",
        status=JobStatus.QUEUED,
        temp_dir=temp_dir,
        input_path=service.Path(temp_dir.name) / "input.mp4",
        output_path=service.Path(temp_dir.name) / "annotated.avi",
        json_path=service.Path(temp_dir.name) / "analysis.json",
        params={},
    )
    with JOB_LOCK:
        JOB_STORE[job.job_id] = job

    client = testclient.TestClient(create_app())
    response = client.get(f"/jobs/{job.job_id}/result")

    assert response.status_code == 409
    assert response.json()["detail"]["status"] == "queued"


def test_failed_job_exposes_error_when_fastapi_is_installed(monkeypatch):
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    def fake_run_analysis(input_path, output_path, json_path, params):
        raise RuntimeError("boom")

    monkeypatch.setattr(service, "run_analysis", fake_run_analysis)
    client = testclient.TestClient(create_app())

    response = client.post(
        "/jobs",
        data={"roi": "300,120,80,40"},
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    job_id = response.json()["job_id"]
    status_response = client.get(f"/jobs/{job_id}")
    assert status_response.json() == {
        "job_id": job_id,
        "status": "failed",
        "error": "boom",
    }
    assert client.get(f"/jobs/{job_id}/result").status_code == 409


def test_post_jobs_validates_roi_when_fastapi_is_installed():
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    client = testclient.TestClient(create_app())
    response = client.post(
        "/jobs",
        data={"roi": "bad"},
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    assert response.status_code == 400
    assert service.JOB_STORE == {}
