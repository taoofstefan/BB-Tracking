from __future__ import annotations

from dataclasses import asdict, is_dataclass
from html import escape
from pathlib import Path
from typing import Sequence


def write_report_html(
    output_file: str | Path,
    summary: object,
    frames: Sequence[object],
    reps: Sequence[object],
) -> None:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_report_html(summary, frames, reps), encoding="utf-8")


def render_report_html(summary: object, frames: Sequence[object], reps: Sequence[object]) -> str:
    summary_data = object_to_dict(summary)
    frame_rows = [object_to_dict(frame) for frame in frames]
    rep_rows = [object_to_dict(rep) for rep in reps]
    title = "Barbell Tracking Report"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: light; font-family: Arial, sans-serif; }}
    body {{ margin: 0; background: #f5f7fa; color: #1c232b; }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 24px; }}
    h1, h2 {{ margin: 0 0 12px; }}
    section {{ margin: 0 0 24px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }}
    .metric {{ background: white; border: 1px solid #d9e0e8; border-radius: 6px; padding: 12px; }}
    .label {{ color: #637083; font-size: 12px; text-transform: uppercase; }}
    .value {{ font-size: 22px; font-weight: 700; margin-top: 4px; }}
    .panel {{ background: white; border: 1px solid #d9e0e8; border-radius: 6px; padding: 16px; overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #e6ebf0; padding: 8px; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
    th {{ color: #526173; font-weight: 700; }}
    svg {{ width: 100%; height: auto; display: block; }}
    .empty {{ color: #637083; }}
  </style>
</head>
<body>
<main>
  <h1>{title}</h1>
  <section class="metrics">
    {render_metric("Frames", summary_data.get("frames_processed"))}
    {render_metric("Tracked Points", summary_data.get("points_tracked"))}
    {render_metric("Reps", summary_data.get("rep_count"))}
    {render_metric("Avg Speed", format_speed(summary_data.get("avg_speed_px_s"), summary_data.get("avg_speed_m_s")))}
    {render_metric("Peak Speed", format_speed(summary_data.get("max_speed_px_s"), summary_data.get("max_speed_m_s")))}
  </section>
  <section class="panel">
    <h2>Velocity Over Time</h2>
    {render_speed_chart(frame_rows)}
  </section>
  <section class="panel">
    <h2>Bar Path</h2>
    {render_path_chart(frame_rows)}
  </section>
  <section class="panel">
    <h2>Reps</h2>
    {render_rep_table(rep_rows)}
  </section>
</main>
</body>
</html>
"""


def object_to_dict(value: object) -> dict:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return value
    raise TypeError(f"Unsupported report object: {type(value).__name__}")


def render_metric(label: str, value: object) -> str:
    return f"""<div class="metric"><div class="label">{escape(label)}</div><div class="value">{escape(format_value(value))}</div></div>"""


def render_speed_chart(frames: Sequence[dict]) -> str:
    points = [
        (frame.get("time_s"), frame.get("speed_m_s") or frame.get("speed_px_s"))
        for frame in frames
        if frame.get("speed_m_s") is not None or frame.get("speed_px_s") is not None
    ]
    return render_line_chart(points, stroke="#0b6bcb", empty_label="No speed data available")


def render_path_chart(frames: Sequence[dict]) -> str:
    points = [
        (frame.get("center_x"), frame.get("center_y"))
        for frame in frames
        if frame.get("center_x") is not None and frame.get("center_y") is not None
    ]
    return render_line_chart(points, stroke="#c23b22", empty_label="No path data available", invert_y=False)


def render_line_chart(
    points: Sequence[tuple[float | int | None, float | int | None]],
    *,
    stroke: str,
    empty_label: str,
    invert_y: bool = True,
) -> str:
    valid_points = [(float(x), float(y)) for x, y in points if x is not None and y is not None]
    if len(valid_points) < 2:
        return f'<p class="empty">{escape(empty_label)}</p>'

    width = 900
    height = 260
    padding = 24
    xs = [point[0] for point in valid_points]
    ys = [point[1] for point in valid_points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    x_range = max(max_x - min_x, 1)
    y_range = max(max_y - min_y, 1)

    def scale(point: tuple[float, float]) -> tuple[float, float]:
        x, y = point
        scaled_x = padding + ((x - min_x) / x_range) * (width - padding * 2)
        y_position = (y - min_y) / y_range
        if invert_y:
            y_position = 1 - y_position
        scaled_y = padding + y_position * (height - padding * 2)
        return scaled_x, scaled_y

    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in (scale(point) for point in valid_points))
    return f"""<svg viewBox="0 0 {width} {height}" role="img">
  <rect x="0" y="0" width="{width}" height="{height}" fill="#f8fafc"/>
  <polyline points="{polyline}" fill="none" stroke="{escape(stroke)}" stroke-width="3"/>
</svg>"""


def render_rep_table(reps: Sequence[dict]) -> str:
    if not reps:
        return '<p class="empty">No reps detected.</p>'
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(format_value(rep.get('index')))}</td>"
        f"<td>{escape(format_seconds(rep.get('start_time_s')))}</td>"
        f"<td>{escape(format_seconds(rep.get('end_time_s')))}</td>"
        f"<td>{escape(format_seconds(rep.get('duration_s')))}</td>"
        f"<td>{escape(format_value(rep.get('rom_px')))}</td>"
        f"<td>{escape(format_speed(rep.get('mean_speed_px_s'), rep.get('mean_speed_m_s')))}</td>"
        f"<td>{escape(format_percent(rep.get('velocity_loss_pct')))}</td>"
        "</tr>"
        for rep in reps
    )
    return f"""<table>
  <thead><tr><th>Rep</th><th>Start</th><th>End</th><th>Duration</th><th>ROM</th><th>Mean Speed</th><th>Velocity Loss</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""


def format_value(value: object) -> str:
    if value is None:
        return "--"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def format_seconds(value: object) -> str:
    if value is None:
        return "--"
    return f"{float(value):.2f}s"


def format_percent(value: object) -> str:
    if value is None:
        return "--"
    return f"{float(value):.1f}%"


def format_speed(px_s: object, m_s: object) -> str:
    if px_s is None and m_s is None:
        return "--"
    if m_s is not None:
        return f"{float(m_s):.3f} m/s"
    return f"{float(px_s):.1f} px/s"
