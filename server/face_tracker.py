import cv2
import mediapipe as mp
import collections
import os
import subprocess


def track_face_and_crop_mediapipe(input_file, output_file, aspect_ratio="9:16", segment_id=1, total_segments=1):
    """Track faces using MediaPipe with improved smoothing for stable tracking"""
    print(f"[Segment {segment_id}/{total_segments}] Processing with face tracking: {input_file}")

    # Initialize MediaPipe Face Detection
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(
        min_detection_confidence=0.5)

    # Open the video
    cap = cv2.VideoCapture(input_file)
    if not cap.isOpened():
        print(f"[Segment {segment_id}] Error: Could not open video {input_file}")
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
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video, fourcc, fps,
                          (target_width, target_height))

    # Initialize smooth tracking with a longer history window for even smoother movement
    # Increased history length for smoother motion
    position_history_x = collections.deque(maxlen=45)
    position_history_y = collections.deque(maxlen=45)

    # Fill position history with initial center
    for _ in range(45):
        position_history_x.append(width // 2)
        position_history_y.append(height // 2)

    # Process frames
    frame_number = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1
        if frame_number % (fps * 5) == 0:  # Status update every 5 seconds
            print(
                f"[Segment {segment_id}] Processing frame {frame_number}/{frame_count} ({frame_number/frame_count*100:.1f}%)")

        # Convert frame color for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process with MediaPipe
        results = face_detection.process(rgb_frame)

        if results.detections:
            # Get the most prominent face
            detection = results.detections[0]

            # Get bounding box
            bbox = detection.location_data.relative_bounding_box

            # Convert relative coordinates to absolute
            x = int(bbox.xmin * width)
            y = int(bbox.ymin * height)
            w = int(bbox.width * width)
            h = int(bbox.height * height)

            # Calculate center of face
            face_x_center = x + w // 2
            face_y_center = y + h // 2

            # Add to position history
            position_history_x.append(face_x_center)
            position_history_y.append(face_y_center)

        # Calculate smooth position using weighted average
        # This gives more weight to recent positions but still maintains smoothness
        weights = list(range(1, len(position_history_x) + 1))
        total_weight = sum(weights)

        x_center = int(
            sum(x * w for x, w in zip(position_history_x, weights)) / total_weight)
        y_center = int(
            sum(y * w for y, w in zip(position_history_y, weights)) / total_weight)

        # Calculate crop region (center on smoothed face position)
        x_start = max(0, min(x_center - target_width //
                      2, width - target_width))
        y_start = max(0, min(y_center - target_height //
                      2, height - target_height))

        # Crop the frame
        try:
            cropped_frame = frame[y_start:y_start +
                                  target_height, x_start:x_start + target_width]
            out.write(cropped_frame)
        except Exception as e:
            print(f"[Segment {segment_id}] Error cropping frame: {e}")
            # Fallback to center crop
            x_start = (width - target_width) // 2
            y_start = (height - target_height) // 2
            cropped_frame = frame[y_start:y_start +
                                  target_height, x_start:x_start + target_width]
            out.write(cropped_frame)

    # Release OpenCV resources
    cap.release()
    out.release()
    face_detection.close()

    # Now combine the video with the original audio using ffmpeg
    print(f"[Segment {segment_id}] Merging tracked video with original audio...")
    cmd = [
        'ffmpeg', '-y',
        '-i', temp_video,
        '-i', input_file,
        '-c:v', 'libx264',    # Use libx264 for better quality
        '-preset', 'medium',  # Better quality preset
        '-crf', '18',         # High quality (lower is better)
        '-vsync', 'cfr',      # Constant frame rate for better sync
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        output_file
    ]
    subprocess.run(cmd, check=True)

    # Clean up temp file
    if os.path.exists(temp_video):
        os.remove(temp_video)

    print(f"[Segment {segment_id}] Face tracking with audio completed: {output_file}")
    return True
