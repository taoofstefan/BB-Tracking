# Product Brief

## Working Name

LiftLens

## One-Liner

Film a barbell set with your phone, tap the bar once, and get bar path, rep velocity, slowdown, sticking-point, and annotated-video feedback without a dedicated velocity sensor.

## Target User

Intermediate to advanced strength athletes who already record their lifts and want objective feedback:

- powerlifters
- weightlifters
- CrossFit athletes
- home-gym lifters
- coaches reviewing remote athlete videos

## Core Journeys

### Import Existing Lift

1. Pick a training video from the camera roll.
2. Choose the exercise.
3. Scrub to a clear frame and tap the bar.
4. Calibrate scale from known bar length, plate diameter, or two manual points.
5. Analyze the clip.
6. Review bar path, rep velocity, velocity loss, and annotated playback.

### Record In App

1. Open the app and record a set.
2. Confirm the lift and bar position.
3. Run analysis locally.
4. Save the set to history.

### Compare Reps And Sessions

1. Open a set detail screen.
2. Compare reps inside the same set.
3. Compare against previous sessions or personal bests for the same lift.
4. Highlight the rep where velocity loss or stalling started.

### Share Feedback

1. Export an annotated MP4, GIF, or still card.
2. Include bar path, peak velocity, mean velocity, and rep number overlays.
3. Share with a coach or training partner.

## Feature Inventory From The Original Idea

- Import training videos.
- Record training videos directly in the app.
- Track barbell movement.
- Visualize the bar path over the video.
- Show velocity readings.
- Show peak velocity.
- Estimate where the lift starts to stall.
- Segment multiple reps.
- Identify which rep slowed down compared with earlier reps.
- Compare against historical averages or personal bests.
- Give visual feedback and eventually useful hints.

## Missing Features Needed For A Useful App

- Real-world calibration from pixels to meters.
- Reliable timestamp and frame-rate handling, including slow motion and variable frame-rate clips.
- A small-screen ROI selection flow.
- Tracker confidence and re-acquire prompts.
- Rep segmentation.
- Exercise presets for squat, bench, deadlift, and Olympic lifts.
- Local history, set detail screens, and charts.
- Privacy-first local video storage.
- Export/share workflow.
- A clear failure state when tracking quality is too low.

## MVP Scope

- Import video from camera roll.
- Manual bar selection.
- Calibration with known bar length or plate diameter.
- On-device or local Python tracking.
- Bar path overlay.
- Per-frame velocity.
- Auto rep segmentation.
- Per-rep peak velocity, mean velocity, and velocity loss percentage.
- Annotated video export.
- Local-only set history.

## Later Versions

- In-app recording.
- Sticking-point heatmaps.
- Historical comparisons.
- Canned coaching hints.
- Cloud sync and optional coach review.
- Detector-assisted bar re-acquisition.
- Pose-estimation fallback when the bar is occluded.
- Custom detector trained on labeled gym videos.

## Metrics

- Bar position per frame.
- Tracker confidence per frame.
- Peak velocity per rep.
- Mean concentric velocity per rep.
- Velocity loss percentage across a set.
- Rep duration.
- Range of motion.
- Sticking point frame and sticking point velocity.
- Bar path deviation from a straight line.
- Frames lost or re-acquired by the tracker.

## Computer Vision Direction

The existing MOSSE proof of concept is useful for learning and demos, but the product needs a more robust path:

- MVP: classical tracker such as CSRT or KCF, with manual ROI and confidence checks.
- V2: detector plus tracker, where a small model re-detects barbell or plates when tracking confidence drops.
- V3: pose-estimation fallback using wrist/hand landmarks when the bar is occluded.
- R&D: custom barbell detector trained on labeled gym footage.

Main constraints:

- Occlusion by the athlete.
- Lighting and background clutter in gyms.
- Lens distortion and camera angle.
- Variable frame rate and slow-motion metadata.
- Phone heat and battery usage.
- Real-world accuracy from a single 2D camera.

## App Architecture

The app should be local-first:

- Capture/import module for camera roll and in-app recording.
- Frame pipeline for decoding video frames.
- ROI and calibration UI.
- Tracker module that emits per-frame telemetry.
- Analyzer module that segments reps and computes metrics.
- Renderer that exports annotated videos.
- Local storage for videos, sets, reps, and metrics.

Optional backend:

- API for opt-in sync.
- Python worker for heavy re-analysis.
- Object storage for video backups.
- Postgres for set and metric history.
- Future coach review views.

For this repo, the current Python script can become the first analysis worker and CLI before a mobile shell exists.

## Open Questions

- Which lift should the first reliable flow target: squat, bench, or deadlift?
- Should MVP prioritize iOS-native capture quality, or a cross-platform shell?
- How much accuracy is acceptable for a first version?
- Should cloud sync exist at all in MVP?
- What calibration method is least annoying in the gym?
- How should the app communicate uncertainty when tracking quality is low?
