import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import os
import subprocess
import shutil
import json


def get_video_id(youtube_url):
    """Extract video ID from YouTube URL."""
    if "v=" in youtube_url:
        return youtube_url.split("v=")[1].split("&")[0]
    return None


def fetch_transcript(video_id):
    """Fetch transcript of a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print("Error fetching transcript:", e)
        return None


def download_video_segment(youtube_url, start_time, end_time, output_path):
    """Download highest quality segment from YouTube video with proper audio sync."""
    print(f"Downloading segment from {start_time:.2f}s to {end_time:.2f}s...")

    try:
        # Create a unique temp directory
        temp_dir = f"temp_download_{os.path.basename(output_path).replace('.mp4', '')}"
        os.makedirs(temp_dir, exist_ok=True)

        # Calculate duration
        duration = end_time - start_time

        # Method 1: Two-step approach with proper sync
        # Step 1: Download a slightly larger segment to ensure we have proper keyframes
        padding = 5  # 5 seconds padding on each side
        padded_start = max(0, start_time - padding)
        padded_duration = duration + (start_time - padded_start) + padding

        # Temp files
        padded_file = os.path.join(temp_dir, "padded_segment.mp4")
        temp_file = os.path.join(temp_dir, "temp_segment.mp4")

        # Download command
        download_cmd = [
            'yt-dlp',
            '--no-warnings',
            '--format', 'best',  # Best available quality
            '--output', padded_file,
            '--external-downloader', 'ffmpeg',
            '--external-downloader-args', f'ffmpeg_i:-ss {padded_start} -t {padded_duration} -avoid_negative_ts make_zero',
            youtube_url
        ]

        print(f"Downloading padded segment using yt-dlp...")
        result = subprocess.run(download_cmd, capture_output=True, text=True)

        if os.path.exists(padded_file) and os.path.getsize(padded_file) > 0:
            # Step 2: Extract the exact segment with proper sync
            # Calculate the relative start time within the padded segment
            relative_start = start_time - padded_start

            sync_cmd = [
                'ffmpeg', '-y',
                '-i', padded_file,
                '-ss', str(relative_start),
                '-t', str(duration),
                '-c:v', 'libx264',     # Use libx264 for better quality
                '-preset', 'medium',   # Balanced quality/speed
                '-crf', '18',          # High quality (lower is better)
                '-c:a', 'aac',         # AAC audio codec
                '-b:a', '192k',        # Good audio quality
                '-ac', '2',            # Stereo
                '-ar', '48000',        # Standard sample rate
                '-vsync', 'cfr',       # Constant frame rate for better sync
                '-async', '1',         # Force audio sync
                temp_file
            ]

            print("Extracting precise segment with audio sync...")
            subprocess.run(sync_cmd, check=True)

            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                # Success - copy to output location
                shutil.copy2(temp_file, output_path)
                shutil.rmtree(temp_dir, ignore_errors=True)

                file_size = os.path.getsize(output_path) / (1024 * 1024)
                print(
                    f"Successfully downloaded segment ({file_size:.2f}MB): {output_path}")
                return output_path

        # If the first method fails, try a direct approach with better sync parameters
        print("First method failed, trying fallback approach...")

        # Method 2: Get the direct URL and use more aggressive sync options
        info_cmd = [
            'yt-dlp',
            '--no-warnings',
            '--get-url',
            '--format', 'best',
            youtube_url
        ]

        print("Getting direct video URL...")
        result = subprocess.run(
            info_cmd, capture_output=True, text=True, check=True)
        direct_url = result.stdout.strip()

        if direct_url:
            fallback_cmd = [
                'ffmpeg', '-y',
                '-ss', str(start_time),  # Seek to start time
                '-i', direct_url,        # Direct video URL
                '-t', str(duration),     # Duration to extract
                '-c:v', 'libx264',       # Video codec
                '-preset', 'medium',     # Encoding preset
                '-crf', '18',            # Quality (lower is better)
                '-c:a', 'aac',           # Audio codec
                '-b:a', '192k',          # Audio bitrate
                '-ac', '2',              # Stereo audio
                '-ar', '48000',          # Audio sample rate
                '-vsync', 'cfr',         # Constant frame rate
                '-async', '1',           # Force audio sync
                '-max_delay', '500000',  # Increase max A/V delay
                '-max_muxing_queue_size', '9999',  # Handle large queue
                output_path
            ]

            print("Downloading with improved sync parameters...")
            subprocess.run(fallback_cmd, check=True)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                shutil.rmtree(temp_dir, ignore_errors=True)
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                print(
                    f"Successfully downloaded segment ({file_size:.2f}MB): {output_path}")
                return output_path

        # Method 3: Last resort - download full video then extract
        print("Trying final method - downloading video then extracting segment...")
        full_video = os.path.join(temp_dir, "full_video.mp4")

        download_cmd = [
            'yt-dlp',
            '--no-warnings',
            '--format', 'best',  # Best available quality
            '--output', full_video,
            youtube_url
        ]

        subprocess.run(download_cmd, check=True)

        if os.path.exists(full_video):
            # First create a clean cut at keyframes
            keyframe_cut = os.path.join(temp_dir, "keyframe_cut.mp4")

            cut_cmd = [
                'ffmpeg', '-y',
                '-i', full_video,
                '-ss', str(start_time),
                '-t', str(duration),
                '-c', 'copy',  # Fast copy without re-encoding
                keyframe_cut
            ]

            subprocess.run(cut_cmd, check=True)

            # Then re-encode with forced sync
            final_cmd = [
                'ffmpeg', '-y',
                '-i', keyframe_cut,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '18',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-vsync', 'cfr',
                '-async', '1',
                output_path
            ]

            subprocess.run(final_cmd, check=True)

            if os.path.exists(output_path):
                shutil.rmtree(temp_dir, ignore_errors=True)
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                print(
                    f"Successfully downloaded segment ({file_size:.2f}MB): {output_path}")
                return output_path

        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("All download methods failed")
        return None

    except Exception as e:
        print(f"Error downloading segment: {e}")
        # Try to clean up temp dir if it exists
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
        return None
