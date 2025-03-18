import os
import subprocess
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
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting segment: {e}")
        return False


def add_subtitles(video_path, subtitle_path, output_path, font_size=12):
    """Add subtitles to video with specific styling."""
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-vf', f"subtitles={subtitle_path}:force_style='FontName=Arial,FontSize={font_size},PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=2,Shadow=0,Alignment=2'",
        '-c:a', 'copy',  # Copy audio stream without re-encoding
        '-vsync', 'cfr',  # Constant frame rate for better A/V sync
        output_path
    ]

    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error adding subtitles: {e}")
        return False


def process_segment(video_path, segment, transcript_data, aspect_ratio="9:16", output_path="output.mp4", font_size=42, words_per_subtitle=2):
    """Process a single segment into a complete short video."""
    try:
        # Create temp directory for this segment's processing
        temp_dir = f"temp_{os.path.basename(output_path).split('.')[0]}"
        os.makedirs(temp_dir, exist_ok=True)

        # Get segment timestamps
        start_time = float(segment.get('start_time', 0))
        end_time = float(segment.get('end_time', start_time + 30))

        # Validate segment duration
        if end_time <= start_time:
            print(f"Warning: Invalid segment times. Using default 30 second duration.")
            end_time = start_time + 30

        duration = end_time - start_time
        print(f"Processing segment - Duration: {duration:.2f}s")

        # 1. Extract segment from full video
        raw_segment = f"{temp_dir}/raw_segment.mp4"
        print("Extracting segment from full video...")
        if not extract_segment(video_path, start_time, end_time, raw_segment):
            raise Exception("Failed to extract segment")

        # 2. Create subtitle file for this segment
        subtitle_file = f"{temp_dir}/subtitles.srt"
        create_word_by_word_subtitle_file(
            transcript_data,
            start_time,
            end_time,
            subtitle_file,
            words_per_subtitle
        )

        # 3. Process with face tracking
        tracked_segment = f"{temp_dir}/tracked_segment.mp4"
        print("Applying face tracking...")
        if not track_face_and_crop_mediapipe(raw_segment, tracked_segment, aspect_ratio):
            raise Exception("Failed face tracking")

        # 4. Add subtitles
        print("Adding subtitles...")
        if not add_subtitles(tracked_segment, subtitle_file, output_path, font_size):
            raise Exception("Failed to add subtitles")

        # 5. Clean up temp directory
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        os.rmdir(temp_dir)

        return True

    except Exception as e:
        print(f"Error processing segment: {e}")
        return False
