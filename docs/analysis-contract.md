# Analysis JSON Contract

The analysis JSON is produced by `track_video(..., json_output=...)` and by the optional `/analyze` service endpoint. It is consumed by the HTML report and the mobile prototype.

Schema changes should be additive when possible. New fields may appear at any level. Existing fields should keep their meaning, units, and nullability unless a future schema version explicitly documents a breaking change.

## Top-Level Shape

```json
{
  "summary": {},
  "frames": [],
  "reps": [],
  "quality": {}
}
```

## `summary`

Set-level metrics for the whole video.

| Field | Unit | Nullable | Meaning |
| --- | --- | --- | --- |
| `output_file` | path | no | Annotated video path produced by the local run. Mobile clients should not rely on this path. |
| `frames_processed` | frames | no | Number of video frames processed after tracker initialization. |
| `points_tracked` | frames | no | Number of frames where the tracker returned a usable bounding box. |
| `max_speed_px_s` | px/s | yes | Fastest tracked frame-to-frame bar speed in pixels per second. |
| `min_speed_px_s` | px/s | yes | Slowest tracked frame-to-frame bar speed in pixels per second. |
| `avg_speed_px_s` | px/s | yes | Mean tracked frame-to-frame bar speed in pixels per second. |
| `scale_px_per_meter` | px/m | yes | Calibration scale used for meter-per-second values. |
| `max_speed_m_s` | m/s | yes | Fastest calibrated speed, present only when calibration is provided. |
| `min_speed_m_s` | m/s | yes | Slowest calibrated speed, present only when calibration is provided. |
| `avg_speed_m_s` | m/s | yes | Mean calibrated speed, present only when calibration is provided. |
| `rep_count` | reps | no | Number of detected rep summaries. |

## `frames`

Frame-level telemetry for each tracked frame. Frames where tracking fails are omitted from this array.

| Field | Unit | Nullable | Meaning |
| --- | --- | --- | --- |
| `frame` | frame index | no | Processed frame number after initialization. |
| `time_s` | seconds | no | Timestamp derived from frame number and video FPS. |
| `x`, `y`, `w`, `h` | px | no | Tracker bounding box. |
| `center_x`, `center_y` | px | no | Center point of the bounding box. |
| `speed_px_s` | px/s | yes | Speed from the previous tracked point. First tracked point has `null`. |
| `speed_m_s` | m/s | yes | Calibrated speed when scale is available and `speed_px_s` is not null. |

## `reps`

Per-rep summaries from the current vertical-path heuristic.

| Field | Unit | Nullable | Meaning |
| --- | --- | --- | --- |
| `index` | rep number | no | Human-facing 1-based rep number. |
| `start_frame`, `end_frame` | frame index | no | First and last tracked frame in the detected rep range. |
| `start_time_s`, `end_time_s` | seconds | no | Start/end timestamps. |
| `duration_s` | seconds | no | Rep duration. |
| `rom_px` | px | no | Vertical range of motion used by the detector. |
| `peak_speed_px_s` | px/s | yes | Fastest speed inside the rep. |
| `mean_speed_px_s` | px/s | yes | Mean speed inside the rep. |
| `peak_speed_m_s` | m/s | yes | Calibrated peak speed when scale is available. |
| `mean_speed_m_s` | m/s | yes | Calibrated mean speed when scale is available. |
| `velocity_loss_pct` | percent | yes | Percent slowdown versus rep 1 mean pixel speed. Positive means slower. |

## `quality`

Path-quality metrics derived from tracked frame centers and detected rep ranges.

| Field | Unit | Nullable | Meaning |
| --- | --- | --- | --- |
| `max_horizontal_drift_px` | px | yes | Largest per-rep horizontal center drift. |
| `avg_horizontal_drift_px` | px | yes | Mean per-rep horizontal center drift. |
| `rom_consistency_cv` | ratio | yes | Coefficient of variation for per-rep vertical ROM. Render as percent in UI. |
| `sticking_rep_index` | rep number | yes | 1-based rep number containing the slowest positive-speed tracked point. |
| `sticking_frame` | frame index | yes | Frame containing the slowest positive-speed tracked point. |
| `sticking_time_s` | seconds | yes | Timestamp for the slowest positive-speed tracked point. |
| `sticking_speed_px_s` | px/s | yes | Slowest positive speed in pixels per second. |
| `sticking_speed_m_s` | m/s | yes | Calibrated slowest positive speed when scale is available. |
| `reps` | array | no | Per-rep quality entries. Empty when no reps are detected. |

Each `quality.reps[]` entry contains `index`, `horizontal_drift_px`, `min_center_x`, `max_center_x`, and the same sticking fields scoped to that rep.

## Compact Example

```json
{
  "summary": {
    "frames_processed": 766,
    "points_tracked": 627,
    "rep_count": 7,
    "avg_speed_m_s": 0.758
  },
  "frames": [
    {
      "frame": 12,
      "time_s": 0.4,
      "center_x": 344,
      "center_y": 122,
      "speed_px_s": null,
      "speed_m_s": null
    }
  ],
  "reps": [
    {
      "index": 1,
      "start_time_s": 0.4,
      "end_time_s": 1.8,
      "rom_px": 126,
      "mean_speed_m_s": 1.065,
      "velocity_loss_pct": 0.0
    }
  ],
  "quality": {
    "max_horizontal_drift_px": 73,
    "avg_horizontal_drift_px": 31.7,
    "rom_consistency_cv": 0.399,
    "sticking_rep_index": 1,
    "sticking_time_s": 0.43
  }
}
```

## Mobile Notes

- Prefer calibrated `*_m_s` fields when present; fall back to `*_px_s`.
- Treat missing or null values as unavailable, not as zero.
- `rom_consistency_cv` is a ratio. Display `0.399` as `39.9%`.
- `sticking_rep_index` and `reps[].index` are already 1-based.
- Mobile clients should ignore unknown fields.

## Validation

`analysis_schema.validate_analysis_payload(payload)` returns all detected contract
errors as human-readable strings and accepts unknown additive fields.
`analysis_schema.assert_valid_analysis_payload(payload)` raises `ValueError` with
the collected errors joined by `; `.
