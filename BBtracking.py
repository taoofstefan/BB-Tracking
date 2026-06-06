from barbell_tracker import track_video


def BBtracking(video_file):
    """Backward-compatible wrapper for the original function name."""
    summary = track_video(video_file)
    return summary.output_file
