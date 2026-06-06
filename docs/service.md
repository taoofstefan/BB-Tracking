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

The mobile prototype includes a service URL field and health check button. Start the service locally, keep the default `http://127.0.0.1:8000`, and use the health check before pressing Analyze.

The prototype can also send the selected video to `POST /analyze`. Keep the default ROI of `300,120,80,40` for the included sample clip, or edit the ROI field before pressing Analyze.

The prototype forwards compact analysis options too: tracker selection defaults to `mosse`, and scale defaults to `100` pixels per meter. Leave scale blank for pixel-only speed output.

Example:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -F video=@lift.mp4 \
  -F roi=300,120,80,40 \
  -F tracker=mosse \
  -F scale_px_per_meter=100
```

The first spike is synchronous. A later version should add job IDs, status polling, and persisted annotated video downloads.
