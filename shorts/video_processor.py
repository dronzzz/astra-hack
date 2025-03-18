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
                    font_size=42, words_per_subtitle=2, segment_id=1, total_segments=1, temp_dir=None):
    """Process a single segment into a complete short video."""
    try:
        process_start_time = time.time()

        # Get segment timestamps (these are used for subtitles)
        start_time = float(segment.get('start_time', 0))
        end_time = float(segment.get('end_time', start_time + 30))

        # For creating subtitles, we need to adjust times to be relative to the segment
        # Since we're downloading just the segment, the video starts at 0, not at start_time
        local_start_time = 0
        local_end_time = end_time - start_time

        # Create subtitle file
        subtitle_file = f"{temp_dir}/subtitles.srt"
        print(f"[Segment {segment_id}] Creating word-by-word subtitles...")

        # Get transcript for this time range
        segment_transcript = [
            {
                'start': entry['start'] - start_time,  # Adjust to start at 0
                'duration': entry['duration'],
                'text': entry['text']
            }
            for entry in transcript_data
            if entry['start'] >= start_time and entry['start'] < end_time
        ]

        create_word_by_word_subtitle_file(
            segment_transcript,
            local_start_time,  # now 0
            local_end_time,    # relative duration
            subtitle_file,
            words_per_subtitle
        )

        # Track faces and apply aspect ratio
        tracked_segment = f"{temp_dir}/tracked_segment.mp4"
        print(f"[Segment {segment_id}] Applying face tracking...")
        if not track_face_and_crop_mediapipe(video_path, tracked_segment, aspect_ratio, segment_id, total_segments):
            raise Exception("Failed face tracking")

        # Add subtitles
        print(f"[Segment {segment_id}] Adding subtitles...")
        cmd = [
            'ffmpeg', '-y',
            '-i', tracked_segment,
            '-vf', f"subtitles={subtitle_file}:force_style='FontName=Arial,FontSize={font_size},PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=0,Shadow=0,Alignment=2'",
            '-c:a', 'copy',  # Copy audio stream without re-encoding
            '-vsync', 'cfr',  # Constant frame rate for better A/V sync
            output_path
        ]

        try:
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"[Segment {segment_id}] Error adding subtitles: {e}")
            if e.stderr:
                print(f"FFMPEG error: {e.stderr}")
            return False

        process_end_time = time.time()
        print(
            f"[Segment {segment_id}] Processing completed in {process_end_time - process_start_time:.2f} seconds")
        return True

    except Exception as e:
        print(f"[Segment {segment_id}] Error processing segment: {e}")
        return False
