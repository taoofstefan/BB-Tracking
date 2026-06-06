from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from metrics import scale_from_reference, speed_m_s, speed_px_s, summarize_speeds
from reps import detect_rep_ranges, summarize_rep_speeds


@dataclass(frozen=True)
class TrackingSummary:
    output_file: str
    frames_processed: int
    points_tracked: int
    max_speed_px_s: float | None
    min_speed_px_s: float | None
    avg_speed_px_s: float | None
    scale_px_per_meter: float | None
    max_speed_m_s: float | None
    min_speed_m_s: float | None
    avg_speed_m_s: float | None
    rep_count: int


@dataclass(frozen=True)
class TrackingFrame:
    frame: int
    time_s: float
    x: int
    y: int
    w: int
    h: int
    center_x: int
    center_y: int
    speed_px_s: float | None
    speed_m_s: float | None


def parse_roi(value: str) -> tuple[int, int, int, int]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("ROI must be x,y,w,h")
    try:
        x, y, w, h = (int(part) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("ROI values must be integers") from exc
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError("ROI width and height must be positive")
    return x, y, w, h


def create_tracker(name: str):
    import cv2

    normalized = name.lower()
    factories = {
        "mosse": ("TrackerMOSSE_create", "TrackerMOSSE_create"),
        "kcf": ("TrackerKCF_create", "TrackerKCF_create"),
        "csrt": ("TrackerCSRT_create", "TrackerCSRT_create"),
    }
    if normalized not in factories:
        raise ValueError(f"Unsupported tracker: {name}")

    legacy_name, direct_name = factories[normalized]
    legacy = getattr(cv2, "legacy", None)
    if legacy is not None and hasattr(legacy, legacy_name):
        return getattr(legacy, legacy_name)()
    if hasattr(cv2, direct_name):
        return getattr(cv2, direct_name)()
    raise RuntimeError(
        f"OpenCV tracker '{normalized}' is unavailable. Install opencv-contrib-python."
    )


def track_video(
    input_file: str | Path,
    output_file: str | Path = "output.avi",
    *,
    tracker_name: str = "mosse",
    roi: tuple[int, int, int, int] | None = None,
    display: bool = True,
    json_output: str | Path | None = None,
    scale_px_per_meter: float | None = None,
    rep_direction: str = "up",
    min_rep_rom_px: int = 20,
    min_rep_frames: int = 3,
) -> TrackingSummary:
    import cv2
    import numpy as np

    input_path = Path(input_file)
    output_path = Path(output_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input video not found: {input_path}")
    if roi is None and not display:
        raise ValueError("--roi is required when --no-display is used")

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open input video: {input_path}")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 0
        if fps <= 0:
            raise RuntimeError("Input video FPS is missing or invalid")

        ret, frame = cap.read()
        if not ret or frame is None:
            raise RuntimeError("Input video has no readable frames")

        frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(str(output_path), fourcc, fps, frame_size)
        if not out.isOpened():
            raise RuntimeError(f"Could not open output video for writing: {output_path}")

        selected_roi = roi if roi is not None else tuple(int(value) for value in cv2.selectROI("Select barbell", frame, False))
        if selected_roi[2] <= 0 or selected_roi[3] <= 0:
            raise RuntimeError("No valid ROI selected")

        tracker = create_tracker(tracker_name)
        tracker.init(frame, selected_roi)

        positions: list[tuple[int, int]] = []
        speeds: list[float] = []
        telemetry: list[TrackingFrame] = []
        overlay = np.zeros_like(frame)
        frames_processed = 0

        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            frames_processed += 1
            ok, bbox = tracker.update(frame)
            if ok:
                x, y, w, h = (int(value) for value in bbox)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cx = x + w // 2
                cy = y + h // 2
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
                positions.append((cx, cy))

                if len(positions) > 1:
                    cv2.line(overlay, positions[-1], positions[-2], (0, 0, 255), 2)
                    current_speed = speed_px_s(positions[-2], positions[-1], fps)
                    speeds.append(current_speed)
                else:
                    current_speed = None
                current_speed_m_s = (
                    speed_m_s(current_speed, scale_px_per_meter)
                    if current_speed is not None and scale_px_per_meter is not None
                    else None
                )
                telemetry.append(
                    TrackingFrame(
                        frame=frames_processed,
                        time_s=frames_processed / fps,
                        x=x,
                        y=y,
                        w=w,
                        h=h,
                        center_x=cx,
                        center_y=cy,
                        speed_px_s=current_speed,
                        speed_m_s=current_speed_m_s,
                    )
                )

            frame = cv2.addWeighted(frame, 1, overlay, 0.5, 0)
            out.write(frame)
            if display:
                cv2.imshow("BB-Tracking", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        max_speed, min_speed, avg_speed = summarize_speeds(speeds)
        calibrated_speeds = (
            [speed_m_s(speed, scale_px_per_meter) for speed in speeds]
            if scale_px_per_meter is not None
            else []
        )
        max_speed_m_s, min_speed_m_s, avg_speed_m_s = summarize_speeds(calibrated_speeds)
        rep_ranges = detect_rep_ranges(
            [frame.center_y for frame in telemetry],
            direction=rep_direction,
            min_rom_px=min_rep_rom_px,
            min_frames=min_rep_frames,
        )
        rep_summaries = [
            summarize_rep_speeds(
                index,
                rep_range,
                frames=[frame.frame for frame in telemetry],
                times=[frame.time_s for frame in telemetry],
                speeds_px_s=[frame.speed_px_s for frame in telemetry],
                speeds_m_s=[frame.speed_m_s for frame in telemetry],
            )
            for index, rep_range in enumerate(rep_ranges, start=1)
        ]
        summary = TrackingSummary(
            output_file=str(output_path),
            frames_processed=frames_processed,
            points_tracked=len(positions),
            max_speed_px_s=max_speed,
            min_speed_px_s=min_speed,
            avg_speed_px_s=avg_speed,
            scale_px_per_meter=scale_px_per_meter,
            max_speed_m_s=max_speed_m_s,
            min_speed_m_s=min_speed_m_s,
            avg_speed_m_s=avg_speed_m_s,
            rep_count=len(rep_summaries),
        )
        if json_output:
            write_analysis_json(json_output, summary, telemetry, rep_summaries)
        return summary
    finally:
        cap.release()
        if "out" in locals():
            out.release()
        cv2.destroyAllWindows()


def print_summary(summary: TrackingSummary) -> None:
    print(f"Output video: {summary.output_file}")
    print(f"Frames processed: {summary.frames_processed}")
    print(f"Points tracked: {summary.points_tracked}")
    print(f"Reps detected: {summary.rep_count}")
    if summary.avg_speed_px_s is None:
        print("No speed data available")
        return
    print(f"Max speed: {summary.max_speed_px_s:.2f} pixels per second")
    print(f"Min speed: {summary.min_speed_px_s:.2f} pixels per second")
    print(f"Avg speed: {summary.avg_speed_px_s:.2f} pixels per second")
    if summary.avg_speed_m_s is not None:
        print(f"Max speed: {summary.max_speed_m_s:.3f} meters per second")
        print(f"Min speed: {summary.min_speed_m_s:.3f} meters per second")
        print(f"Avg speed: {summary.avg_speed_m_s:.3f} meters per second")


def write_analysis_json(
    output_file: str | Path,
    summary: TrackingSummary,
    telemetry: list[TrackingFrame],
    reps: list,
) -> None:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": asdict(summary),
        "frames": [asdict(frame) for frame in telemetry],
        "reps": [asdict(rep) for rep in reps],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track a barbell/object in a lift video.")
    parser.add_argument("-i", "--input", default="lift.mp4", help="Input video path")
    parser.add_argument("-o", "--output", default="output.avi", help="Output annotated video path")
    parser.add_argument(
        "--tracker",
        choices=("mosse", "kcf", "csrt"),
        default="mosse",
        help="OpenCV tracker to use",
    )
    parser.add_argument("--roi", type=parse_roi, help="Headless ROI as x,y,w,h")
    parser.add_argument("--no-display", action="store_true", help="Disable preview windows")
    parser.add_argument("--json-output", help="Write summary and per-frame telemetry to JSON")
    parser.add_argument("--scale-px-per-meter", type=float, help="Calibration scale in pixels per meter")
    parser.add_argument("--reference-px", type=float, help="Reference length in pixels for calibration")
    parser.add_argument("--reference-m", type=float, help="Reference length in meters for calibration")
    parser.add_argument("--rep-direction", choices=("up", "down"), default="up", help="Concentric bar direction to segment")
    parser.add_argument("--min-rep-rom-px", type=int, default=20, help="Minimum vertical ROM in pixels for a rep")
    parser.add_argument("--min-rep-frames", type=int, default=3, help="Minimum tracked frames for a rep")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    scale_px_per_meter = args.scale_px_per_meter
    if scale_px_per_meter is not None and scale_px_per_meter <= 0:
        raise SystemExit("--scale-px-per-meter must be positive")
    if args.reference_px is not None or args.reference_m is not None:
        if args.reference_px is None or args.reference_m is None:
            raise SystemExit("--reference-px and --reference-m must be provided together")
        scale_px_per_meter = scale_from_reference(args.reference_px, args.reference_m)
    summary = track_video(
        args.input,
        args.output,
        tracker_name=args.tracker,
        roi=args.roi,
        display=not args.no_display,
        json_output=args.json_output,
        scale_px_per_meter=scale_px_per_meter,
        rep_direction=args.rep_direction,
        min_rep_rom_px=args.min_rep_rom_px,
        min_rep_frames=args.min_rep_frames,
    )
    print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
