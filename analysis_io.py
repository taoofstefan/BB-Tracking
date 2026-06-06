from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from reps import RepSummary


def write_analysis_json(
    output_file: str | Path,
    summary: object,
    telemetry: Sequence[object],
    reps: Sequence[RepSummary],
    quality: object | None = None,
) -> None:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": asdict(summary),
        "frames": [asdict(frame) for frame in telemetry],
        "reps": [asdict(rep) for rep in reps],
    }
    if quality is not None:
        payload["quality"] = asdict(quality)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
