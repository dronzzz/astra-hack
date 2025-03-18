import openai
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import json
import os
import subprocess
import cv2
import numpy as np
import mediapipe as mp
from datetime import datetime, timedelta


def get_video_id(youtube_url):
    if "v=" in youtube_url:
        return youtube_url.split("v=")[1].split("&")[0]
    return None


def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print("Error fetching transcript:", e)
        return None


def download_video(youtube_url, output_path="video.mp4"):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return output_path
    except Exception as e:
        print("Error downloading video:", e)
        return None


def extract_important_parts(transcript, model="gpt-4-turbo"):
    api_key = "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"

    if not api_key:
        print("Error: OpenAI API key not set. Please set the OPENAI_API_KEY environment variable.")
        return []

    client = openai.OpenAI(api_key=api_key)

    transcript_text = "\n".join(
        [f"[{entry['start']}] {entry['text']}" for entry in transcript])

    prompt = f"""
    Analyze the following transcript and identify 2-3 engaging segments that would work well for YouTube Shorts (max 60 seconds each).
    Return the response in this exact JSON format:
    [
        {{
            "start_time": <number>,
            "end_time": <number>,
            "reason": "<why this segment is engaging>"
        }}
    ]
    
    IMPORTANT: Each segment MUST have both start_time and end_time as numeric values, with end_time greater than start_time.
    The difference between end_time and start_time should be less than 60 seconds.
    
    Transcript:
    {transcript_text}
    
    Remember to return ONLY valid JSON, no additional text.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns only valid JSON responses."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()

        try:
            segments = json.loads(content)
            valid_segments = []
            for i, segment in enumerate(segments):
                if not isinstance(segment, dict):
                    print(f"Skipping segment {i+1}: Not a valid dictionary")
                    continue

                if 'start_time' not in segment or 'end_time' not in segment:
                    print(
                        f"Skipping segment {i+1}: Missing start_time or end_time")
                    continue

                try:
                    start = float(segment['start_time'])
                    end = float(segment['end_time'])

                    if end <= start:
                        print(
                            f"Fixing segment {i+1}: end_time ({end}) must be greater than start_time ({start})")
                        end = start + 30

                    if end - start > 60:
                        print(
                            f"Fixing segment {i+1}: Duration too long ({end-start}s), limiting to 60s")
                        end = start + 60

                    segment['start_time'] = start
                    segment['end_time'] = end

                    valid_segments.append(segment)
                except (ValueError, TypeError):
                    print(
                        f"Skipping segment {i+1}: Invalid numeric values for start_time or end_time")
                    continue

            if not valid_segments:
                print("No valid segments found. Creating a default segment.")
                valid_segments = [{
                    "start_time": 0.0,
                    "end_time": 60.0,
                    "reason": "Default segment (first minute of video)"
                }]

            return valid_segments

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {content}")
            return [{
                "start_time": 0.0,
                "end_time": 60.0,
                "reason": "Default segment (first minute of video)"
            }]
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return [{
            "start_time": 0.0,
            "end_time": 60.0,
            "reason": "Default segment (first minute of video)"
        }]


def create_subtitle_file(transcript_data, start_time, end_time, output_file="subtitles.srt"):
    """Create SRT subtitle file from transcript data for a specific segment"""
    with open(output_file, 'w', encoding='utf-8') as f:
        counter = 1

        # Filter transcript entries that fall within our segment
        segment_transcript = [
            entry for entry in transcript_data
            if entry['start'] >= start_time and entry['start'] < end_time
        ]

        # Process each entry in the transcript
        for entry in segment_transcript:
            # Calculate relative time within the segment
            rel_start = entry['start'] - start_time
            rel_end = min(entry['start'] + entry['duration'],
                          end_time) - start_time

            # Format timestamps for SRT
            start_ts = str(timedelta(seconds=rel_start)).replace('.', ',')
            # Ensure it has milliseconds
            if ',' not in start_ts:
                start_ts += ',000'
            else:
                # Ensure 3 decimal places for milliseconds
                parts = start_ts.split(',')
                start_ts = f"{parts[0]},{parts[1][:3].ljust(3, '0')}"

            end_ts = str(timedelta(seconds=rel_end)).replace('.', ',')
            if ',' not in end_ts:
                end_ts += ',000'
            else:
                # Ensure 3 decimal places for milliseconds
                parts = end_ts.split(',')
                end_ts = f"{parts[0]},{parts[1][:3].ljust(3, '0')}"

            # Format to ensure proper SRT timestamp format (HH:MM:SS,mmm)
            if len(start_ts.split(':')) == 2:
                start_ts = f"00:{start_ts}"
            if len(end_ts.split(':')) == 2:
                end_ts = f"00:{end_ts}"

            # Write the subtitle entry
            f.write(f"{counter}\n")
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{entry['text']}\n\n")
            counter += 1

    return output_file


def get_aspect_ratio_choice():
    """Prompt user to choose an aspect ratio"""
    print("\nChoose an aspect ratio:")
    print("1. 9:16 (Vertical - Best for Shorts/TikTok/Reels)")
    print("2. 16:9 (Horizontal - Standard Widescreen)")
    print("3. 1:1 (Square - Instagram)")
    print("4. 4:5 (Vertical - Instagram)")
    print("5. Keep original aspect ratio")

    choice = input("Enter your choice (1-5): ").strip()

    aspect_ratios = {
        "1": "9:16",
        "2": "16:9",
        "3": "1:1",
        "4": "4:5",
        "5": "original"
    }

    return aspect_ratios.get(choice, "original")


def get_video_dimensions(input_file):
    """Get video dimensions using ffprobe"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=p=0',
        input_file
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True)
        width, height = map(int, result.stdout.strip().split(','))
        return width, height
    except subprocess.CalledProcessError as e:
        print(f"Error getting video dimensions: {e}")
        return 1920, 1080  # Default fallback dimensions


def apply_aspect_ratio(input_file, output_file, aspect_ratio):
    """Apply the chosen aspect ratio to the video"""
    if aspect_ratio == "original":
        # Just copy the file if keeping original aspect ratio
        cmd = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-c', 'copy',
            output_file
        ]
        subprocess.run(cmd, check=True)
        return output_file

    # Get video dimensions
    width, height = get_video_dimensions(input_file)

    # Calculate new dimensions based on aspect ratio
    if aspect_ratio == "9:16":
        new_width = height * 9 // 16
        new_height = height
        if new_width > width:
            new_width = width
            new_height = width * 16 // 9
    elif aspect_ratio == "16:9":
        new_width = width
        new_height = width * 9 // 16
        if new_height > height:
            new_height = height
            new_width = height * 16 // 9
    elif aspect_ratio == "1:1":
        new_size = min(width, height)
        new_width = new_size
        new_height = new_size
    elif aspect_ratio == "4:5":
        new_width = height * 4 // 5
        new_height = height
        if new_width > width:
            new_width = width
            new_height = width * 5 // 4

    # Calculate padding/cropping
    x_offset = (width - new_width) // 2
    y_offset = (height - new_height) // 2

    # Apply transformation
    cmd = [
        'ffmpeg', '-y',
        '-i', input_file,
        '-vf', f'crop={new_width}:{new_height}:{x_offset}:{y_offset}',
        '-c:a', 'copy',
        output_file
    ]

    subprocess.run(cmd, check=True)
    return output_file


def track_face_and_crop_mediapipe(input_file, output_file, aspect_ratio="9:16"):
    """Track faces using MediaPipe (much faster than OpenCV) and crop video to follow faces"""
    print(f"Processing segment with face tracking: {input_file}")

    # Initialize MediaPipe Face Detection
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(
        min_detection_confidence=0.5)

    # Open the video
    cap = cv2.VideoCapture(input_file)
    if not cap.isOpened():
        print(f"Error: Could not open video {input_file}")
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
        # If calculated width exceeds available width, adjust dimensions
        target_width = width
        if aspect_ratio == "9:16":
            target_height = width * 16 // 9
        elif aspect_ratio == "4:5":
            target_height = width * 5 // 4

    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps,
                          (target_width, target_height))

    # Variables to smooth motion
    last_x_center = width // 2
    last_y_center = height // 2
    smoothing_factor = 0.8  # Higher values = smoother but slower to follow

    # Process frames
    frame_number = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1
        if frame_number % (fps * 5) == 0:  # Status update every 5 seconds of video
            print(
                f"Processing frame {frame_number}/{frame_count} ({frame_number/frame_count*100:.1f}%)")

        # Convert frame color for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process with MediaPipe
        results = face_detection.process(rgb_frame)

        # Default crop center (center of frame)
        x_center = width // 2
        y_center = height // 2

        # If faces detected, update crop center
        if results.detections:
            # Get the most prominent face (first detection)
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

            # Apply smoothing for camera movement
            x_center = int(smoothing_factor * last_x_center +
                           (1 - smoothing_factor) * face_x_center)
            y_center = int(smoothing_factor * last_y_center +
                           (1 - smoothing_factor) * face_y_center)

            # Update for next frame
            last_x_center = x_center
            last_y_center = y_center
        else:
            # If no face detected, use previous position
            x_center = last_x_center
            y_center = last_y_center

        # Calculate crop region (center on face)
        x_start = max(0, min(x_center - target_width //
                      2, width - target_width))
        y_start = max(0, min(y_center - target_height //
                      2, height - target_height))

        # Crop the frame
        try:
            cropped_frame = frame[y_start:y_start +
                                  target_height, x_start:x_start + target_width]
            # Write the frame
            out.write(cropped_frame)
        except Exception as e:
            print(f"Error cropping frame: {e}")
            # Fallback to center crop if there's an issue
            x_start = (width - target_width) // 2
            y_start = (height - target_height) // 2
            cropped_frame = frame[y_start:y_start +
                                  target_height, x_start:x_start + target_width]
            out.write(cropped_frame)

    # Release resources
    cap.release()
    out.release()
    face_detection.close()

    print(f"Face tracking completed for segment: {output_file}")
    return True


def create_shorts_ffmpeg(video_path, segments, transcript_data, aspect_ratio="9:16", output_path="shorts.mp4"):
    """Create shorts video using ffmpeg with transcript overlay and custom aspect ratio"""
    try:
        if not segments or len(segments) == 0:
            print("No segments provided. Creating a default segment.")
            segments = [{
                "start_time": 0.0,
                "end_time": 60.0,
                "reason": "Default segment (first minute of video)"
            }]

        # Create temporary files for each segment
        temp_files = []
        final_temp_files = []

        for i, seg in enumerate(segments):
            try:
                # Extract segment's start and end time
                start = float(seg.get('start_time', 0))
                end = float(seg.get('end_time', start + 30))

                if end <= start:
                    print(
                        f"Warning: end_time {end} <= start_time {start} for segment {i+1}, using default duration")
                    end = start + 30

                duration = end - start
                print(
                    f"\nProcessing segment {i+1}/{len(segments)} - Duration: {duration:.2f}s")

                # 1. Extract segment from full video (fast operation using ffmpeg)
                raw_segment = f"temp_segment_raw_{i}.mp4"
                print(f"Extracting segment {i+1} from full video...")
                cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-ss', str(start),
                    '-t', str(duration),
                    '-c', 'copy',  # Copy without re-encoding for speed
                    raw_segment
                ]
                subprocess.run(cmd, check=True)
                temp_files.append(raw_segment)

                # 2. Create subtitle file for this specific segment
                subtitle_file = f"subtitles_{i}.srt"
                create_subtitle_file(
                    transcript_data, start, end, subtitle_file)
                temp_files.append(subtitle_file)

                # 3. Track faces and crop to desired aspect ratio
                # This only processes the extracted segment, not the full video
                face_tracked_segment = f"temp_segment_face_tracked_{i}.mp4"
                track_face_and_crop_mediapipe(
                    raw_segment, face_tracked_segment, aspect_ratio)
                temp_files.append(face_tracked_segment)

                # 4. Add subtitles to the face-tracked segment
                final_segment = f"temp_segment_final_{i}.mp4"
                print(f"Adding subtitles to segment {i+1}...")
                cmd = [
                    'ffmpeg', '-y',
                    '-i', face_tracked_segment,
                    '-vf', f"subtitles={subtitle_file}:force_style='FontName=Arial,FontSize=30,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=2,Shadow=1,Alignment=2'",
                    '-c:a', 'copy',
                    final_segment
                ]
                subprocess.run(cmd, check=True)

                final_temp_files.append(final_segment)
                temp_files.append(final_segment)

                print(f"Completed processing segment {i+1}/{len(segments)}")

            except Exception as e:
                print(f"Error processing segment {i+1}: {e}")
                continue  # Skip this segment and continue with others

        if not final_temp_files:
            raise ValueError("No segments were successfully processed")

        # 5. Concatenate all processed segments
        print("\nCombining all segments into final video...")
        with open('segments.txt', 'w') as f:
            for temp_file in final_temp_files:
                f.write(f"file '{temp_file}'\n")

        concat_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', 'segments.txt',
            '-c', 'copy',
            output_path
        ]
        subprocess.run(concat_cmd, check=True)

        # Clean up temporary files
        print("Cleaning up temporary files...")
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        os.remove('segments.txt')

        print(f"Shorts video created successfully! Saved to: {output_path}")
    except Exception as e:
        print(f"Error creating Shorts video: {e}")
        print("Attempting to clean up temporary files...")
        try:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            if os.path.exists('segments.txt'):
                os.remove('segments.txt')
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")


def main():
    youtube_url = input("Enter YouTube video URL: ")
    video_id = get_video_id(youtube_url)

    if not video_id:
        print("Invalid YouTube URL.")
        return

    transcript = fetch_transcript(video_id)
    if not transcript:
        print("Could not retrieve transcript.")
        return

    print("Analyzing transcript to find engaging segments...")
    segments = extract_important_parts(transcript)
    print("Extracted segments:", json.dumps(segments, indent=2))

    # Choose aspect ratio
    print("\nChoose an aspect ratio:")
    print("1. 9:16 (Vertical - Best for Shorts/TikTok/Reels)")
    print("2. 16:9 (Horizontal - Standard Widescreen)")
    print("3. 1:1 (Square - Instagram)")
    print("4. 4:5 (Vertical - Instagram)")
    print("5. Keep original aspect ratio")

    choice = input("Enter your choice (default: 1): ").strip()
    aspect_ratios = {
        "1": "9:16",
        "2": "16:9",
        "3": "1:1",
        "4": "4:5",
        "5": "original"
    }
    aspect_ratio = aspect_ratios.get(choice, "9:16")
    print(f"Using aspect ratio: {aspect_ratio}")

    # Custom output filename
    output_filename = input(
        "Enter output filename (default: shorts.mp4): ").strip()
    if not output_filename:
        output_filename = "shorts.mp4"
    if not output_filename.endswith(".mp4"):
        output_filename += ".mp4"

    print(f"\nDownloading video from YouTube...")
    video_path = download_video(youtube_url)
    if not video_path:
        print("Failed to download video.")
        return

    print("\nBeginning video processing...")
    create_shorts_ffmpeg(video_path, segments, transcript,
                         aspect_ratio, output_filename)


if __name__ == "__main__":
    main()
