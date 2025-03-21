import os
import subprocess
from subtitle_generator import create_word_by_word_subtitle_file
from face_tracker import track_face_and_crop_mediapipe
import logging

logger = logging.getLogger('youtube-shorts')


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


def add_subtitles(input_video, subtitle_file, output_video, font_size=24):
    """Add subtitles to video with improved encoding for browser compatibility."""
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_video), exist_ok=True)

        # Use hardware acceleration if available and more efficient encoding settings
        cmd = [
            'ffmpeg', '-y',
            '-i', input_video,
            '-vf', f'subtitles={subtitle_file}:force_style=\'FontSize={font_size},BorderStyle=0,Outline=0,Shadow=0,Alignment=2,Bold=1\'',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',  # Fastest encoding speed
            '-tune', 'fastdecode',   # Optimize for faster decoding
            '-crf', '26',            # Slightly lower quality for faster processing
            '-c:a', 'aac',
            '-b:a', '128k',
            '-pix_fmt', 'yuv420p',  # Required for browser compatibility
            '-movflags', '+faststart',  # Web optimization
            output_video
        ]

        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Error adding subtitles: {result.stderr}")
            return False

        return os.path.exists(output_video)
    except Exception as e:
        logger.error(f"Error in add_subtitles: {e}")
        return False


def extract_thumbnail(video_path, thumbnail_path):
    """Extract a thumbnail from the video."""
    try:
        # Create a simple thumbnail using ffmpeg
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-ss', '00:00:01',  # Take frame at 1 second
            '-vframes', '1',
            '-q:v', '2',        # High quality
            thumbnail_path
        ]
        subprocess.run(cmd, check=True)

        # Verify the thumbnail was created
        if os.path.exists(thumbnail_path):
            return True
        return False
    except Exception as e:
        print(f"Error extracting thumbnail: {str(e)}")
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
