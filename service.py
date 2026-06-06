import json
import shutil
import threading
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from barbell_tracker import parse_roi, track_video


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class AnalysisJob:
    job_id: str
    status: JobStatus
    temp_dir: TemporaryDirectory
    input_path: Path
    output_path: Path
    json_path: Path
    params: dict[str, Any]
    result: dict[str, Any] | None = None
    error: str | None = None


JOB_STORE: dict[str, AnalysisJob] = {}
JOB_LOCK = threading.Lock()


def parse_optional_positive_float(value: str | None, field_name: str) -> float | None:
    if value in (None, ""):
        return None
    parsed = float(value)
    if parsed <= 0:
        raise ValueError(f"{field_name} must be positive")
    return parsed


def safe_video_suffix(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    return suffix if suffix in {".avi", ".mov", ".mp4", ".m4v", ".webm"} else ".mp4"


def build_analysis_params(
    *,
    roi: str,
    tracker: str,
    scale_px_per_meter: str | None,
    rep_direction: str,
    min_rep_rom_px: int,
    min_rep_frames: int,
    rep_smoothing_window: int,
    rep_deadband_px: float,
) -> dict[str, Any]:
    return {
        "roi": parse_roi(roi),
        "tracker": tracker,
        "scale_px_per_meter": parse_optional_positive_float(
            scale_px_per_meter,
            "scale_px_per_meter",
        ),
        "rep_direction": rep_direction,
        "min_rep_rom_px": min_rep_rom_px,
        "min_rep_frames": min_rep_frames,
        "rep_smoothing_window": rep_smoothing_window,
        "rep_deadband_px": rep_deadband_px,
    }


def run_analysis(
    input_path: Path,
    output_path: Path,
    json_path: Path,
    params: dict[str, Any],
) -> dict[str, Any]:
    track_video(
        input_path,
        output_path,
        tracker_name=params["tracker"],
        roi=params["roi"],
        display=False,
        json_output=json_path,
        scale_px_per_meter=params["scale_px_per_meter"],
        rep_direction=params["rep_direction"],
        min_rep_rom_px=params["min_rep_rom_px"],
        min_rep_frames=params["min_rep_frames"],
        rep_smoothing_window=params["rep_smoothing_window"],
        rep_deadband_px=params["rep_deadband_px"],
        show_hud=False,
    )
    return json.loads(json_path.read_text(encoding="utf-8"))


def job_status_payload(job: AnalysisJob) -> dict[str, str]:
    payload = {"job_id": job.job_id, "status": job.status.value}
    if job.status == JobStatus.FAILED and job.error:
        payload["error"] = job.error
    return payload


def clear_jobs() -> None:
    with JOB_LOCK:
        jobs = list(JOB_STORE.values())
        JOB_STORE.clear()
    for job in jobs:
        job.temp_dir.cleanup()


def run_job(job_id: str) -> None:
    with JOB_LOCK:
        job = JOB_STORE.get(job_id)
        if job is None:
            return
        job.status = JobStatus.RUNNING

    try:
        result = run_analysis(job.input_path, job.output_path, job.json_path, job.params)
    except Exception as exc:
        with JOB_LOCK:
            job.status = JobStatus.FAILED
            job.error = str(exc)
        return

    with JOB_LOCK:
        job.status = JobStatus.COMPLETE
        job.result = result


def create_app():
    try:
        from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import JSONResponse
    except ImportError as exc:
        raise RuntimeError(
            "FastAPI service dependencies are missing. Install requirements-service.txt."
        ) from exc

    app = FastAPI(title="BB-Tracking Analysis Service")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/analyze")
    async def analyze(
        video: UploadFile = File(...),
        roi: str = Form(...),
        tracker: str = Form("mosse"),
        scale_px_per_meter: str | None = Form(None),
        rep_direction: str = Form("up"),
        min_rep_rom_px: int = Form(20),
        min_rep_frames: int = Form(3),
        rep_smoothing_window: int = Form(1),
        rep_deadband_px: float = Form(0),
    ) -> JSONResponse:
        try:
            params = build_analysis_params(
                roi=roi,
                tracker=tracker,
                scale_px_per_meter=scale_px_per_meter,
                rep_direction=rep_direction,
                min_rep_rom_px=min_rep_rom_px,
                min_rep_frames=min_rep_frames,
                rep_smoothing_window=rep_smoothing_window,
                rep_deadband_px=rep_deadband_px,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        with TemporaryDirectory(prefix="bbtracking-") as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / f"input{safe_video_suffix(video.filename)}"
            output_path = temp_path / "annotated.avi"
            json_path = temp_path / "analysis.json"
            with input_path.open("wb") as target:
                shutil.copyfileobj(video.file, target)

            try:
                return JSONResponse(run_analysis(input_path, output_path, json_path, params))
            except Exception as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/jobs")
    async def create_job(
        background_tasks: BackgroundTasks,
        video: UploadFile = File(...),
        roi: str = Form(...),
        tracker: str = Form("mosse"),
        scale_px_per_meter: str | None = Form(None),
        rep_direction: str = Form("up"),
        min_rep_rom_px: int = Form(20),
        min_rep_frames: int = Form(3),
        rep_smoothing_window: int = Form(1),
        rep_deadband_px: float = Form(0),
    ) -> JSONResponse:
        try:
            params = build_analysis_params(
                roi=roi,
                tracker=tracker,
                scale_px_per_meter=scale_px_per_meter,
                rep_direction=rep_direction,
                min_rep_rom_px=min_rep_rom_px,
                min_rep_frames=min_rep_frames,
                rep_smoothing_window=rep_smoothing_window,
                rep_deadband_px=rep_deadband_px,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        temp_dir = TemporaryDirectory(prefix="bbtracking-job-")
        temp_path = Path(temp_dir.name)
        input_path = temp_path / f"input{safe_video_suffix(video.filename)}"
        output_path = temp_path / "annotated.avi"
        json_path = temp_path / "analysis.json"
        with input_path.open("wb") as target:
            shutil.copyfileobj(video.file, target)

        job_id = uuid.uuid4().hex
        job = AnalysisJob(
            job_id=job_id,
            status=JobStatus.QUEUED,
            temp_dir=temp_dir,
            input_path=input_path,
            output_path=output_path,
            json_path=json_path,
            params=params,
        )
        with JOB_LOCK:
            JOB_STORE[job_id] = job
        background_tasks.add_task(run_job, job_id)
        return JSONResponse(job_status_payload(job), status_code=202)

    @app.get("/jobs/{job_id}")
    def get_job(job_id: str) -> dict[str, str]:
        with JOB_LOCK:
            job = JOB_STORE.get(job_id)
            if job is None:
                raise HTTPException(status_code=404, detail="unknown job")
            return job_status_payload(job)

    @app.get("/jobs/{job_id}/result")
    def get_job_result(job_id: str) -> JSONResponse:
        with JOB_LOCK:
            job = JOB_STORE.get(job_id)
            if job is None:
                raise HTTPException(status_code=404, detail="unknown job")
            if job.status != JobStatus.COMPLETE:
                raise HTTPException(
                    status_code=409,
                    detail={"message": "job not complete", "status": job.status.value},
                )
            result = job.result
        return JSONResponse(result)

    return app
