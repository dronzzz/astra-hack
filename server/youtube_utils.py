import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import os
import subprocess
import shutil
import uuid
import logging

logger = logging.getLogger('youtube-shorts')


def get_video_id(youtube_url):
    """Extract video ID from YouTube URL."""
    if "v=" in youtube_url:
        return youtube_url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in youtube_url:
        return youtube_url.split("youtu.be/")[1].split("?")[0]
    return None


def fetch_transcript(video_id):
    """Fetch transcript of a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        logger.error(f"Error fetching transcript: {e}")
        return None


def download_video_segment(youtube_url, start_time, end_time, segment_id=1, total_segments=1):
    """Download only the needed segment of a YouTube video."""
    logger.info(
        f"[Segment {segment_id}/{total_segments}] Downloading segment from {start_time}s to {end_time}s")

    # Create a unique temporary directory for this download
    temp_dir = f"temp_download_{uuid.uuid4().hex[:8]}"
    os.makedirs(temp_dir, exist_ok=True)
    output_file = os.path.join(temp_dir, f"segment_{segment_id}.mp4")

    try:
        # Use download-sections to directly get only the needed segment
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
            'outtmpl': output_file,
            'download_ranges': lambda _, __: {'ranges': [(start_time, end_time)]},
            'postprocessor_args': {
                'ffmpeg': [
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-crf', '23',
                    '-preset', 'fast'
                ]
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        # Verify the output file exists and is valid
        if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
            logger.info(
                f"[Segment {segment_id}] Successfully downloaded segment to {output_file}")
            return output_file
        else:
            raise Exception(
                f"Output file is missing or too small: {output_file}")

    except Exception as e:
        logger.error(f"Error downloading segment: {e}")

        # Fallback to traditional method if the primary method fails
        try:
            logger.info(
                f"[Segment {segment_id}] Falling back to traditional download method")
            # Use the simpler approach with direct ffmpeg extraction
            ydl_opts = {
                'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
                'outtmpl': os.path.join(temp_dir, 'full_video.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])

            # Find the downloaded file
            for file in os.listdir(temp_dir):
                if file.startswith('full_video.'):
                    input_file = os.path.join(temp_dir, file)

                    # Extract segment using ffmpeg
                    segment_cmd = [
                        'ffmpeg', '-y',
                        '-ss', str(start_time),
                        '-i', input_file,
                        '-t', str(end_time - start_time),
                        '-c:v', 'libx264',
                        '-preset', 'fast',
                        '-crf', '23',
                        '-c:a', 'aac',
                        '-b:a', '192k',
                        output_file
                    ]

                    subprocess.run(segment_cmd, check=True)

                    if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
                        # Clean up the full video to save space
                        try:
                            os.remove(input_file)
                        except:
                            pass
                        return output_file

            raise Exception("Failed to download segment using fallback method")
        except Exception as fallback_error:
            logger.error(f"Fallback download failed: {fallback_error}")
            return None
    finally:
        # Clean up any temporary files except the output file
        if os.path.exists(temp_dir):
            files_to_keep = [output_file]
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                if file_path not in files_to_keep and os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass


def download_video(youtube_url, output_path="video.mp4"):
    """Download a YouTube video (full video for fallback purposes)."""
    ydl_opts = {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return output_path
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        return None
