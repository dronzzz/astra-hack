import cv2
import mediapipe as mp
import collections
import os
import subprocess


def track_face_and_crop_mediapipe(input_file, output_file, aspect_ratio="9:16", segment_id=1, total_segments=1):
    """Track faces using MediaPipe with improved smoothing for stable tracking"""
    print(
        f"[Segment {segment_id}/{total_segments}] Processing with face tracking: {input_file}")

    # Initialize MediaPipe Face Detection
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(
        min_detection_confidence=0.5)

    # Open the video
    cap = cv2.VideoCapture(input_file)
    if not cap.isOpened():
        print(
            f"[Segment {segment_id}] Error: Could not open video {input_file}")
        return False

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate target dimensions based on aspect ratio
    if aspect_ratio == "9:16":
        target_width = height * 9 // 16
        target_height = height
    elif aspect_ratio == "1:1":
        target_width = min(width, height)
        target_height = min(width, height)
    elif aspect_ratio == "4:5":
        target_width = height * 4 // 5
        target_height = height
    else:  # Default to 16:9
        target_width = width
        target_height = width * 9 // 16

    if target_width > width:
        target_width = width
        if aspect_ratio == "9:16":
            target_height = width * 16 // 9
        elif aspect_ratio == "4:5":
            target_height = width * 5 // 4

    # Create a unique temp file for this segment
    temp_video = f"temp_tracked_video_{segment_id}.mp4"

    # Create a video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video, fourcc, fps,
                          (target_width, target_height))

    # Skip frames: only process every nth frame to speed up (adjust based on fps)
    # For higher fps videos we can skip more frames
    # Process ~10 frames per second for tracking
    skip_frames = max(1, int(fps // 10))

    # Initialize a deque for tracking centerpoints
    # Store last 10 center points for smoothing
    center_points = collections.deque(maxlen=10)
    last_detected_frame = -999  # Track when we last detected a face
    has_detection = False  # Track if we ever found a face
    default_center_x, default_center_y = width // 2, height // 2  # Default center
    scale_factor = 0.5  # Process at half resolution for tracking only

    try:
        frame_index = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_for_tracking = None
            tracking_result = None
            current_center_x, current_center_y = default_center_x, default_center_y

            # Only run face detection on certain frames to speed up processing
            if frame_index % skip_frames == 0:
                # Resize frame for faster processing (only for detection)
                frame_for_tracking = cv2.resize(
                    frame, (int(width * scale_factor), int(height * scale_factor)))

                # Convert to RGB for MediaPipe
                frame_for_tracking = cv2.cvtColor(
                    frame_for_tracking, cv2.COLOR_BGR2RGB)
                tracking_result = face_detection.process(frame_for_tracking)

                # Process tracking results
                if tracking_result.detections:
                    has_detection = True
                    last_detected_frame = frame_index

                    # Get the first face detected (highest confidence)
                    detection = tracking_result.detections[0]
                    face_bbox = detection.location_data.relative_bounding_box

                    # Convert relative coordinates to actual pixel values (accounting for scale_factor)
                    relative_x = face_bbox.xmin + face_bbox.width / 2
                    relative_y = face_bbox.ymin + face_bbox.height / 2

                    # Convert back to original image coordinates
                    current_center_x = int(relative_x * width)
                    current_center_y = int(relative_y * height)

                    # Add to our smoothing deque
                    center_points.append((current_center_x, current_center_y))

            # If we haven't found a face in too many frames, use the default center
            if frame_index - last_detected_frame > 30 * fps:  # If no face for 30 seconds
                center_points.clear()  # Clear history
                center_points.append((default_center_x, default_center_y))

            # Use the average of recent points for smooth tracking
            if center_points:
                avg_x = sum(p[0] for p in center_points) // len(center_points)
                avg_y = sum(p[1] for p in center_points) // len(center_points)
            else:
                avg_x, avg_y = default_center_x, default_center_y

            # Calculate crop region
            x1 = max(0, avg_x - target_width // 2)
            # Ensure we don't go beyond the right edge
            if x1 + target_width > width:
                x1 = max(0, width - target_width)

            y1 = max(0, avg_y - target_height // 2)
            # Ensure we don't go beyond the bottom edge
            if y1 + target_height > height:
                y1 = max(0, height - target_height)

            # Crop and write
            cropped = frame[y1:y1+target_height, x1:x1+target_width]

            # Handle edge cases where the crop might not have the expected dimensions
            if cropped.shape[1] != target_width or cropped.shape[0] != target_height:
                # Resize to expected dimensions
                cropped = cv2.resize(cropped, (target_width, target_height))

            out.write(cropped)
            frame_index += 1

            # Print progress
            if frame_index % 100 == 0:
                progress = min(100, int(100 * frame_index / frame_count))
                print(
                    f"[Segment {segment_id}] Processing: {progress}% complete", end="\r")

        print(
            f"[Segment {segment_id}] Processed {frame_index} frames, writing video...")

        # Release resources
        cap.release()
        out.release()

        # If we didn't find any faces, just use center crop
        if not has_detection:
            print(
                f"[Segment {segment_id}] No faces detected, using center crop")

        # Use ffmpeg to convert the temp video to the final output with proper encoding
        cmd = [
            'ffmpeg', '-y',
            '-i', temp_video,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',  # Required for compatibility
            output_file
        ]

        subprocess.run(cmd)

        # Clean up temp file
        try:
            os.remove(temp_video)
        except:
            pass

        print(f"[Segment {segment_id}] Face tracking completed")
        return True

    except Exception as e:
        print(f"[Segment {segment_id}] Error in face tracking: {e}")
        return False
