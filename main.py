import cv2
import numpy as np

# Load video
cap = cv2.VideoCapture('lift.mp4')

# Define output video properties
output_file = 'output.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = cap.get(cv2.CAP_PROP_FPS)
frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

# Create VideoWriter object
out = cv2.VideoWriter(output_file, fourcc, fps, frame_size)

# Select ROI
ret, frame = cap.read()
r = cv2.selectROI(frame)

# Initialize tracker
tracker = cv2.legacy.TrackerMOSSE_create()
tracker.init(frame, r)

# Initialize variables
positions = []
speeds = []

# Create blank image for line overlay
overlay = np.zeros_like(frame)

# Process video frame by frame
while True:
    # Read frame
    ret, frame = cap.read()
    if not ret:
        break

    # Track object
    ok, bbox = tracker.update(frame)

    # Draw bounding box and center point
    if ok:
        # Convert bounding box to integers
        bbox = np.int0(bbox)

        # Draw bounding box
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 2)

        # Calculate center point
        cx = bbox[0] + bbox[2] // 2
        cy = bbox[1] + bbox[3] // 2

        # Draw center point
        cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        # Save position
        positions.append((cx, cy))

        # Draw line to previous center point
        if len(positions) > 1:
            cv2.line(overlay, positions[-1], positions[-2], (0, 0, 255), 2)

        # Calculate speed
        if len(positions) > 1:
            distance = np.sqrt((positions[-1][0] - positions[-2][0]) ** 2 + (positions[-1][1] - positions[-2][1]) ** 2)
            speed = distance / (1 / cap.get(cv2.CAP_PROP_FPS))
            speeds.append(speed)

    # Add line overlay to frame
    frame = cv2.addWeighted(frame, 1, overlay, 0.5, 0)

    # Display frame
    cv2.imshow('Frame', frame)
    
    # Write frame to output video
    out.write(frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Calculate maximum, minimum, and average speed
if len(speeds) > 0:
    max_speed = max(speeds)
    min_speed = min(speeds)
    avg_speed = sum(speeds) / len(speeds)
    print(f"Max speed: {max_speed:.2f} pixels per second")
    print(f"Min speed: {min_speed:.2f} pixels per second")
    print(f"Avg speed: {avg_speed:.2f} pixels per second")
else:
    print("No speed data available")

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()