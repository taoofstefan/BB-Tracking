import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from barbell_tracker import parse_roi, track_video


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


def create_app():
    try:
        from fastapi import FastAPI, File, Form, HTTPException, UploadFile
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
            selected_roi = parse_roi(roi)
            scale = parse_optional_positive_float(scale_px_per_meter, "scale_px_per_meter")
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
                track_video(
                    input_path,
                    output_path,
                    tracker_name=tracker,
                    roi=selected_roi,
                    display=False,
                    json_output=json_path,
                    scale_px_per_meter=scale,
                    rep_direction=rep_direction,
                    min_rep_rom_px=min_rep_rom_px,
                    min_rep_frames=min_rep_frames,
                    rep_smoothing_window=rep_smoothing_window,
                    rep_deadband_px=rep_deadband_px,
                    show_hud=False,
                )
            except Exception as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc

            return JSONResponse(json.loads(json_path.read_text(encoding="utf-8")))

    return app
