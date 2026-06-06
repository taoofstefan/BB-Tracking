# Analysis Service Spike

The service is an optional FastAPI wrapper around the existing CLI pipeline. It is intended as a local backend target for the mobile prototype, not as a production API.

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

Example:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -F video=@lift.mp4 \
  -F roi=300,120,80,40 \
  -F scale_px_per_meter=100
```

The first spike is synchronous. A later version should add job IDs, status polling, and persisted annotated video downloads.
