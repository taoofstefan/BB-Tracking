# Package 2: Async Analysis Service

## Goal

Turn the synchronous service spike into a simple local async job service.

The mobile prototype should be able to submit a video analysis job, poll status, and render the completed JSON result.

## Current Context

- `service.py` currently exposes:
  - `GET /health`
  - `POST /analyze` synchronous multipart analysis.
- Static prototype can call `/health` and `/analyze`.
- Service is optional and started with `uvicorn service:create_app --factory --reload`.
- CORS is already enabled for local prototype use.

## Target Files

Likely files:

- `service.py`
- `tests/test_service.py`
- `docs/service.md`
- `prototypes/mobile/index.html`
- `TODO.md`

## Required Behavior

Add endpoints:

- `POST /jobs`
  - Accepts the same multipart fields as `/analyze`.
  - Creates a local in-memory job.
  - Returns `{ "job_id": "...", "status": "queued" }`.
- `GET /jobs/{job_id}`
  - Returns status: `queued`, `running`, `complete`, or `failed`.
  - Include `error` when failed.
- `GET /jobs/{job_id}/result`
  - Returns the analysis JSON when complete.
  - Returns 404 for unknown job.
  - Returns 409 or 425-style error when job is not complete.

Implementation style:

- In-memory only is fine.
- Use `uuid.uuid4()` for job IDs.
- Use `BackgroundTasks` or a small threadpool helper.
- Store job input in temp files while running.
- Keep `/analyze` synchronous endpoint working for backward compatibility.

Prototype changes:

- Prefer `/jobs` flow for Analyze.
- After submit, poll `GET /jobs/{job_id}` every 1-2 seconds.
- On complete, fetch `/jobs/{job_id}/result` and call `renderAnalysis`.
- Keep `?demo=1` working.

## Constraints

- No database.
- No production queue.
- Do not persist large files in repo.
- Do not remove synchronous `/analyze`.
- Keep local/dev scope explicit in docs.

## Verification

Run:

```bash
/tmp/bbtracking-venv/bin/python -m pytest -q
/tmp/bbtracking-venv/bin/python - <<'PY'
from fastapi.testclient import TestClient
from service import create_app
client = TestClient(create_app())
print(client.get('/health').status_code)
PY
git diff --check
npx playwright screenshot --full-page --viewport-size=390,844 file:///home/stefan/projects/BB-Tracking/prototypes/mobile/index.html /tmp/bbtracking-jobs.png
```

## M3 Prompt

Use this package as the implementation brief. Produce exact patches. Keep the async service simple and local. Add tests for job creation, unknown job, status flow with a monkeypatched analysis runner if possible, and backward compatibility for `/health`.
