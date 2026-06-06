from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path

from barbell_tracker import parse_roi, track_video


@dataclass(frozen=True)
class TrackerComparison:
    tracker: str
    elapsed_s: float
    frames_processed: int
    points_tracked: int
    rep_count: int
    avg_speed_px_s: float | None
    max_speed_px_s: float | None
    max_horizontal_drift_px: int | None
    avg_horizontal_drift_px: float | None
    rom_consistency_cv: float | None


def compare_tracker(
    tracker: str,
    input_file: Path,
    output_dir: Path,
    roi: tuple[int, int, int, int],
    scale_px_per_meter: float | None,
) -> TrackerComparison:
    output_video = output_dir / f"{tracker}.avi"
    output_json = output_dir / f"{tracker}.json"
    start = time.perf_counter()
    track_video(
        input_file,
        output_video,
        tracker_name=tracker,
        roi=roi,
        display=False,
        json_output=output_json,
        scale_px_per_meter=scale_px_per_meter,
        show_hud=False,
    )
    elapsed = time.perf_counter() - start
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    summary = payload["summary"]
    quality = payload.get("quality", {})
    return TrackerComparison(
        tracker=tracker,
        elapsed_s=elapsed,
        frames_processed=summary["frames_processed"],
        points_tracked=summary["points_tracked"],
        rep_count=summary["rep_count"],
        avg_speed_px_s=summary["avg_speed_px_s"],
        max_speed_px_s=summary["max_speed_px_s"],
        max_horizontal_drift_px=quality.get("max_horizontal_drift_px"),
        avg_horizontal_drift_px=quality.get("avg_horizontal_drift_px"),
        rom_consistency_cv=quality.get("rom_consistency_cv"),
    )


def format_markdown_report(results: list[TrackerComparison]) -> str:
    rows = [
        "| Tracker | Runtime | Points | Reps | Avg Speed | Peak Speed | Max Drift | Avg Drift | ROM CV |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        rows.append(
            "| "
            f"{result.tracker} | "
            f"{result.elapsed_s:.2f}s | "
            f"{result.points_tracked}/{result.frames_processed} | "
            f"{result.rep_count} | "
            f"{format_optional(result.avg_speed_px_s)} px/s | "
            f"{format_optional(result.max_speed_px_s)} px/s | "
            f"{format_optional(result.max_horizontal_drift_px)} px | "
            f"{format_optional(result.avg_horizontal_drift_px)} px | "
            f"{format_percent(result.rom_consistency_cv)} |"
        )
    return "\n".join(rows)


def format_optional(value: float | int | None) -> str:
    if value is None:
        return "--"
    return f"{float(value):.1f}"


def format_percent(value: float | None) -> str:
    if value is None:
        return "--"
    return f"{value * 100:.1f}%"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare OpenCV trackers on one lift video.")
    parser.add_argument("--input", default="lift.mp4", help="Input video path")
    parser.add_argument("--roi", type=parse_roi, default=(300, 120, 80, 40), help="ROI as x,y,w,h")
    parser.add_argument("--output-dir", default="tracker-comparison", help="Directory for generated videos and JSON")
    parser.add_argument("--report-output", default="docs/tracker-comparison.md", help="Markdown report path")
    parser.add_argument("--scale-px-per-meter", type=float, default=100, help="Calibration scale in pixels per meter")
    parser.add_argument("--trackers", nargs="+", default=["mosse", "kcf", "csrt"], help="Trackers to compare")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = [
        compare_tracker(
            tracker,
            Path(args.input),
            output_dir,
            args.roi,
            args.scale_px_per_meter,
        )
        for tracker in args.trackers
    ]
    report = "# Tracker Comparison\n\n" + format_markdown_report(results) + "\n"
    report_path = Path(args.report_output)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
