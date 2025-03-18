import os
import subprocess
import time
import uuid
from subtitle_generator import create_word_by_word_subtitle_file
from face_tracker import track_face_and_crop_mediapipe


def extract_segment(video_path, start_time, end_time, output_path):
    """Extract a segment from a video while preserving audio."""
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-ss', str(start_time),
        '-t', str(end_time - start_time),
        '-c:v', 'h264',  # Specify video codec
        '-c:a', 'aac',   # Specify audio codec
        '-b:a', '192k',  # Good audio quality
        '-ac', '2',      # Stereo audio
        output_path
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting segment: {e}")
        if e.stderr:
            print(f"FFMPEG error: {e.stderr}")
        return False


def add_subtitles(video_path, subtitle_path, output_path, font_size=22):
    """Add subtitles to video with specific styling."""
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-vf', f"subtitles={subtitle_path}:force_style='FontName=Arial,FontSize={font_size},PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=2,Shadow=1,Alignment=2'",
        '-c:a', 'copy',  # Copy audio stream without re-encoding
        '-vsync', 'cfr',  # Constant frame rate for better A/V sync
        output_path
    ]

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error adding subtitles: {e}")
        if e.stderr:
            print(f"FFMPEG error: {e.stderr}")
        return False


def process_segment(video_path, segment, transcript_data, aspect_ratio="9:16", output_path="output.mp4",
                    font_size=42, words_per_subtitle=2, segment_id=1, total_segments=1):
    """Process a single segment into a complete short video."""
    try:
        # Create a unique temp directory for this process
        unique_id = str(uuid.uuid4())[:8]
        temp_dir = f"temp_{segment_id}_{unique_id}"
        os.makedirs(temp_dir, exist_ok=True)

        print(
            f"[Segment {segment_id}/{total_segments}] Starting processing...")
        process_start_time = time.time()

        # Get segment timestamps
        start_time = float(segment.get('start_time', 0))
        end_time = float(segment.get('end_time', start_time + 30))

        # Validate segment duration
        if end_time <= start_time:
            print(
                f"[Segment {segment_id}] Warning: Invalid segment times. Using default 30 second duration.")
            end_time = start_time + 30

        duration = end_time - start_time
        print(
            f"[Segment {segment_id}] Processing clip of duration: {duration:.2f}s")

        # 1. Extract segment from full video
        raw_segment = f"{temp_dir}/raw_segment.mp4"
        print(f"[Segment {segment_id}] Extracting segment from full video...")
        if not extract_segment(video_path, start_time, end_time, raw_segment):
            raise Exception("Failed to extract segment")

        # 2. Create subtitle file for this segment
        subtitle_file = f"{temp_dir}/subtitles.srt"
        print(f"[Segment {segment_id}] Creating word-by-word subtitles...")
        create_word_by_word_subtitle_file(
            transcript_data,
            start_time,
            end_time,
            subtitle_file,
            words_per_subtitle
        )

        # 3. Process with face tracking
        tracked_segment = f"{temp_dir}/tracked_segment.mp4"
        print(f"[Segment {segment_id}] Applying face tracking...")
        if not track_face_and_crop_mediapipe(raw_segment, tracked_segment, aspect_ratio, segment_id, total_segments):
            raise Exception("Failed face tracking")

        # 4. Add subtitles
        print(f"[Segment {segment_id}] Adding subtitles...")
        if not add_subtitles(tracked_segment, subtitle_file, output_path, font_size):
            raise Exception("Failed to add subtitles")

        # 5. Clean up temp directory
        print(f"[Segment {segment_id}] Cleaning up temporary files...")
        try:
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
        except Exception as e:
            print(
                f"[Segment {segment_id}] Warning: Failed to clean up temporary files: {e}")

        process_end_time = time.time()
        print(
            f"[Segment {segment_id}] Processing completed in {process_end_time - process_start_time:.2f} seconds")
        return True

    except Exception as e:
        print(f"[Segment {segment_id}] Error processing segment: {e}")
        return False
