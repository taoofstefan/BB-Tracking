# Analysis Service Spike

The service is an optional FastAPI wrapper around the existing CLI pipeline. It is intended as a local backend target for the mobile prototype, not as a production API.

The service enables permissive CORS for local prototype development so the static HTML prototype can call it from a browser.

## Install

```bash
python -m pip install -r requirements.txt -r requirements-service.txt
```

## Run

```bash
uvicorn service:create_app --factory --reload
```

## Endpoints

- `GET /health` returns `{"status": "ok"}`.
- `POST /analyze` accepts a multipart video upload and analysis options, then returns the same JSON contract produced by `--json-output`.
- `POST /jobs` accepts the same multipart fields as `/analyze`, starts a local background job, and returns `{"job_id": "...", "status": "queued"}`.
- `GET /jobs/{job_id}` returns `queued`, `running`, `complete`, or `failed`. Failed jobs include an `error` field.
- `GET /jobs/{job_id}/result` returns the analysis JSON when the job is complete, returns `404` for unknown jobs, and returns `409` while the job is still queued/running or has failed.
- `GET /jobs/{job_id}/video` returns the annotated `annotated.avi` produced by the run when the job is complete. Responses use `video/x-msvideo` and a `Content-Disposition` filename of `{job_id}.avi`. Unknown jobs return `404`; jobs that are queued, running, or failed return `409`; complete jobs whose annotated file is no longer on disk return `410`.

The mobile prototype includes a service URL field and health check button. Start the service locally, keep the default `http://127.0.0.1:8000`, and use the health check before pressing Analyze.

The prototype can send the selected video to the async jobs flow. Keep the default ROI of `300,120,80,40` for the included sample clip, or edit the ROI field before pressing Analyze.

The prototype forwards compact analysis options too: tracker selection defaults to `mosse`, and scale defaults to `100` pixels per meter. Leave scale blank for pixel-only speed output.

### Calibration Fields

Both `/analyze` and `/jobs` accept the same calibration inputs:

- `scale_px_per_meter`: a direct pixel-to-meter ratio. Leave blank for pixel-only output.
- `reference_px` and `reference_m`: a known reference length measured in pixels and meters. When both are provided, the service derives `scale_px_per_meter` using `metrics.scale_from_reference(reference_px, reference_m)`.
- Reference fields must be provided as a pair. Sending only one of `reference_px` / `reference_m` returns `400`.
- When both a direct `scale_px_per_meter` and the reference pair are provided, the **reference-derived scale wins** (the reference pair is the more explicit calibration intent). Leave `scale_px_per_meter` blank when using a reference to keep the intent obvious.

The mobile prototype includes a visual reference picker that fills `reference_px`
from two tapped points on the displayed video. `reference_m` still needs to be
entered manually.

Synchronous example:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -F video=@lift.mp4 \
  -F roi=300,120,80,40 \
  -F tracker=mosse \
  -F scale_px_per_meter=100
```

Or derive the scale from a reference length:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -F video=@lift.mp4 \
  -F roi=300,120,80,40 \
  -F tracker=mosse \
  -F reference_px=220 \
  -F reference_m=2.2
```

Async job example:

```bash
curl -X POST http://127.0.0.1:8000/jobs \
  -F video=@lift.mp4 \
  -F roi=300,120,80,40 \
  -F tracker=mosse \
  -F scale_px_per_meter=100
```

Or with a reference pair:

```bash
curl -X POST http://127.0.0.1:8000/jobs \
  -F video=@lift.mp4 \
  -F roi=300,120,80,40 \
  -F tracker=mosse \
  -F reference_px=220 \
  -F reference_m=2.2
```

Then poll `GET /jobs/{job_id}` every 1-2 seconds until status is `complete`, and fetch `GET /jobs/{job_id}/result`.

Fetch the annotated video once the job is complete:

```bash
curl -OJ http://127.0.0.1:8000/jobs/{job_id}/video
```

The mobile prototype now points its video player at this URL after a successful async analysis and falls back gracefully with a status message when the annotated video is unavailable (job still running, failed, or expired temp directory).

Jobs are in-memory, single-process, and local-development only. Reloading the service clears the job store. Uploaded videos and analysis files live in temporary directories for the lifetime of the job process and are not written into the repo.
