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


def test_get_job_video_returns_annotated_avi_when_complete(monkeypatch):
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    def fake_run_analysis(input_path, output_path, json_path, params):
        assert input_path.exists()
        # Write a tiny stand-in for the annotated AVI so the endpoint can stream it.
        output_path.write_bytes(b"FAKEAVI" + b"\x00" * 8)
        json_path.write_text("{}", encoding="utf-8")
        return {"summary": {"rep_count": 1}, "frames": [], "reps": []}

    monkeypatch.setattr(service, "run_analysis", fake_run_analysis)
    client = testclient.TestClient(create_app())

    response = client.post(
        "/jobs",
        data={"roi": "300,120,80,40", "tracker": "mosse"},
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    job_id = response.json()["job_id"]
    video_response = client.get(f"/jobs/{job_id}/video")
    head_response = client.head(f"/jobs/{job_id}/video")

    assert video_response.status_code == 200
    assert video_response.headers["content-type"].startswith("video/x-msvideo")
    assert f'filename="{job_id}.avi"' in video_response.headers["content-disposition"]
    assert len(video_response.content) > 0
    assert video_response.content.startswith(b"FAKEAVI")
    assert head_response.status_code == 200
    assert head_response.headers["content-type"].startswith("video/x-msvideo")


def test_get_job_video_unknown_job_returns_404_when_fastapi_is_installed():
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    client = testclient.TestClient(create_app())

    assert client.get("/jobs/missing/video").status_code == 404


def test_get_job_video_before_completion_returns_409_when_fastapi_is_installed():
    testclient = pytest.importorskip("fastapi.testclient")
    from service import JOB_LOCK, JOB_STORE, create_app

    temp_dir = TemporaryDirectory(prefix="bbtracking-test-job-")
    job = AnalysisJob(
        job_id="queued-video-job",
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
    response = client.get(f"/jobs/{job.job_id}/video")

    assert response.status_code == 409
    assert response.json()["detail"]["status"] == "queued"


def test_get_job_video_for_failed_job_returns_409_when_fastapi_is_installed(monkeypatch):
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
    video_response = client.get(f"/jobs/{job_id}/video")

    assert video_response.status_code == 409
    assert video_response.json()["detail"]["status"] == "failed"


def test_get_job_video_returns_410_when_file_missing(monkeypatch):
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    def fake_run_analysis(input_path, output_path, json_path, params):
        # Simulate a complete job whose annotated file was cleaned up.
        return {"summary": {"rep_count": 0}, "frames": [], "reps": []}

    monkeypatch.setattr(service, "run_analysis", fake_run_analysis)
    client = testclient.TestClient(create_app())

    response = client.post(
        "/jobs",
        data={"roi": "300,120,80,40"},
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    job_id = response.json()["job_id"]
    job = service.JOB_STORE[job_id]
    # Force the output file to be missing even though the job is complete.
    job.output_path.unlink(missing_ok=True)

    video_response = client.get(f"/jobs/{job_id}/video")

    assert video_response.status_code == 410


def test_analyze_endpoint_derives_scale_from_reference_when_fastapi_is_installed(monkeypatch):
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    captured: dict[str, object] = {}

    def fake_run_analysis(input_path, output_path, json_path, params):
        captured["scale_px_per_meter"] = params["scale_px_per_meter"]
        captured["reference_px"] = params["reference_px"]
        captured["reference_m"] = params["reference_m"]
        return {"summary": {"rep_count": 1}, "frames": [], "reps": []}

    monkeypatch.setattr(service, "run_analysis", fake_run_analysis)
    client = testclient.TestClient(create_app())

    response = client.post(
        "/analyze",
        data={
            "roi": "300,120,80,40",
            "reference_px": "220",
            "reference_m": "2.2",
        },
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    assert response.status_code == 200
    assert captured["scale_px_per_meter"] == pytest.approx(100)
    assert captured["reference_px"] == pytest.approx(220)
    assert captured["reference_m"] == pytest.approx(2.2)


def test_analyze_endpoint_keeps_direct_scale_without_reference(monkeypatch):
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    captured: dict[str, object] = {}

    def fake_run_analysis(input_path, output_path, json_path, params):
        captured["scale_px_per_meter"] = params["scale_px_per_meter"]
        captured["reference_px"] = params["reference_px"]
        return {"summary": {"rep_count": 0}, "frames": [], "reps": []}

    monkeypatch.setattr(service, "run_analysis", fake_run_analysis)
    client = testclient.TestClient(create_app())

    response = client.post(
        "/analyze",
        data={"roi": "300,120,80,40", "scale_px_per_meter": "75"},
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    assert response.status_code == 200
    assert captured["scale_px_per_meter"] == pytest.approx(75)
    assert captured["reference_px"] is None


def test_analyze_endpoint_reference_overrides_direct_scale(monkeypatch):
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    captured: dict[str, object] = {}

    def fake_run_analysis(input_path, output_path, json_path, params):
        captured["scale_px_per_meter"] = params["scale_px_per_meter"]
        return {"summary": {"rep_count": 0}, "frames": [], "reps": []}

    monkeypatch.setattr(service, "run_analysis", fake_run_analysis)
    client = testclient.TestClient(create_app())

    response = client.post(
        "/analyze",
        data={
            "roi": "300,120,80,40",
            "scale_px_per_meter": "75",
            "reference_px": "220",
            "reference_m": "2.2",
        },
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    assert response.status_code == 200
    # Reference-derived scale wins over the direct scale.
    assert captured["scale_px_per_meter"] == pytest.approx(100)


def test_analyze_endpoint_rejects_incomplete_reference_when_fastapi_is_installed():
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    client = testclient.TestClient(create_app())

    response = client.post(
        "/analyze",
        data={"roi": "300,120,80,40", "reference_px": "220"},
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    assert response.status_code == 400
    assert "reference_px" in response.json()["detail"]
    assert "reference_m" in response.json()["detail"]


def test_analyze_endpoint_rejects_negative_reference_when_fastapi_is_installed():
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    client = testclient.TestClient(create_app())

    response = client.post(
        "/analyze",
        data={
            "roi": "300,120,80,40",
            "reference_px": "0",
            "reference_m": "2.2",
        },
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    assert response.status_code == 400
    assert "reference_px" in response.json()["detail"]


def test_post_jobs_uses_reference_scale_when_fastapi_is_installed(monkeypatch):
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    captured: dict[str, object] = {}

    def fake_run_analysis(input_path, output_path, json_path, params):
        captured["scale_px_per_meter"] = params["scale_px_per_meter"]
        captured["reference_px"] = params["reference_px"]
        captured["reference_m"] = params["reference_m"]
        return {"summary": {"rep_count": 3}, "frames": [], "reps": []}

    monkeypatch.setattr(service, "run_analysis", fake_run_analysis)
    client = testclient.TestClient(create_app())

    response = client.post(
        "/jobs",
        data={
            "roi": "300,120,80,40",
            "tracker": "mosse",
            "reference_px": "220",
            "reference_m": "2.2",
        },
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    assert response.status_code == 202
    job_id = response.json()["job_id"]
    status_response = client.get(f"/jobs/{job_id}")
    assert status_response.json()["status"] == "complete"
    result = client.get(f"/jobs/{job_id}/result").json()
    assert result["summary"]["rep_count"] == 3
    assert captured["scale_px_per_meter"] == pytest.approx(100)
    assert captured["reference_px"] == pytest.approx(220)
    assert captured["reference_m"] == pytest.approx(2.2)


def test_post_jobs_rejects_incomplete_reference_when_fastapi_is_installed():
    testclient = pytest.importorskip("fastapi.testclient")
    from service import create_app

    client = testclient.TestClient(create_app())

    response = client.post(
        "/jobs",
        data={"roi": "300,120,80,40", "reference_m": "2.2"},
        files={"video": ("lift.mp4", b"not really a video", "video/mp4")},
    )

    assert response.status_code == 400
    assert service.JOB_STORE == {}
