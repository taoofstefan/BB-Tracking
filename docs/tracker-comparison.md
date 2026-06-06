# Tracker Comparison

Sample: `lift.mp4`  
ROI: `300,120,80,40`  
Scale: `100 px/m`  
Date: 2026-06-06

| Tracker | Runtime | Points | Reps | Avg Speed | Peak Speed | Max Drift | Avg Drift | ROM CV |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mosse | 2.93s | 627/766 | 7 | 75.8 px/s | 488.4 px/s | 73.0 px | 31.7 px | 39.9% |
| kcf | 4.33s | 38/766 | 1 | 57.8 px/s | 150.0 px/s | 3.0 px | 3.0 px | 0.0% |
| csrt | 24.92s | 766/766 | 8 | 105.2 px/s | 454.0 px/s | 66.0 px | 49.5 px | 13.7% |

## Notes

MOSSE remains the best default for this sample: it is fast, tracks most of the video, and keeps the expected 7-rep output.

KCF loses the target early on this clip. The low drift and ROM numbers are misleading because it only tracks 38 frames and detects 1 rep.

CSRT tracks every frame but is roughly an order of magnitude slower than MOSSE on this smoke run and changes the analysis output to 8 reps. It is useful as an experiment, not as the default.
