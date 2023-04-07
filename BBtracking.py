def BBtracking(video_file):
    """
    Function Name: BBtracking

    Description:
    This function takes a video file as input, tracks a selected object within the video using the MOSSE tracking algorithm and calculates the speed of the object. The function displays the tracking results and saves the output video with tracking overlay as an AVI file. Finally, the function returns the file path of the output video.

    Parameters:
    video_file: string representing the file path of the video to be processed
    
    Returns:
    output_file: string representing the file path of the output video with tracking overlay
    
    Libraries:
    cv2: OpenCV library for computer vision tasks
    numpy: Library for mathematical operations on multi-dimensional arrays and matrices
    
    Algorithm:
    Load the input video using cv2.VideoCapture.
    Define the output video properties using cv2.VideoWriter and set the codec, FPS and frame size.
    Allow user to select a Region of Interest (ROI) in the first frame using cv2.selectROI.
    Initialize the MOSSE tracker using cv2.legacy.TrackerMOSSE_create and pass the first frame and ROI.
    Create empty lists to store the center positions and speeds of the tracked object.
    Create a blank image for overlaying the tracking line on each frame.
    Process each frame of the video in a loop using cap.read().
    Update the tracker with the current frame using tracker.update() and get the bounding box coordinates.
    Draw the bounding box and center point on the frame using cv2.rectangle and cv2.circle.
    Save the center point coordinates to the positions list.
    Draw a line connecting the current center point and the previous center point on the overlay image.
    Calculate the speed of the object as the distance between the current center point and the previous center point divided by the time interval between the frames.
    Add the overlay image to the current frame using cv2.addWeighted.
    Display the frame using cv2.imshow and write it to the output video using out.write.
    Calculate and display the maximum, minimum, and average speed of the object.
    Release all resources using cap.release(), out.release(), and cv2.destroyAllWindows.
    Return the file path of the output video.
    
    Example Usage:
    output_path = BBtracking('C:/BB tracking/input_video.avi')
    BBtracking(output_path)
    """
    import cv2
    import numpy as np

    # Load video
    cap = cv2.VideoCapture(video_file)
    # Define output video properties
    output_file = 'C:/Users/stefa/OneDrive/Coding/BB tracking/output.avi'
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
    
    return output_file
    
# file_path = 'lift.mp4' # Spyder
file_path = 'C:/Users/stefa/OneDrive/Coding/BB tracking/lift.mp4'
    
BBtracking(file_path)	