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
    logger.info(f"[Segment {segment_id}/{total_segments}] Downloading segment from {start_time}s to {end_time}s")
    
    # Create a unique temporary directory for this download
    temp_dir = f"temp_download_{uuid.uuid4().hex[:8]}"
    os.makedirs(temp_dir, exist_ok=True)
    output_file = os.path.join(temp_dir, f"segment_{segment_id}.mp4")
    
    try:
        # First, extract video info to get formats
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            
            if not info:
                raise Exception("Failed to get video info")
                
            logger.info(f"[Segment {segment_id}] Got video info, duration: {info.get('duration')}s")
            
            # Add 1-second padding before and after to ensure we get good keyframes
            padded_start = max(0, start_time - 1) 
            padded_duration = min((end_time - start_time) + 2, info.get('duration') - padded_start)
            
            # Download with ffmpeg using direct URL extraction
            formats = info.get('formats', [])
            
            # Best video format
            video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('acodec') == 'none']
            video_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
            
            # Best audio format
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            audio_formats.sort(key=lambda x: x.get('tbr', 0), reverse=True)
            
            if video_formats and audio_formats:
                video_url = video_formats[0]['url']
                audio_url = audio_formats[0]['url']
                
                logger.info(f"[Segment {segment_id}] Using video format: {video_formats[0].get('format_id')} ({video_formats[0].get('height')}p)")
                logger.info(f"[Segment {segment_id}] Using audio format: {audio_formats[0].get('format_id')}")
                
                # Download segment directly with ffmpeg
                cmd = [
                    'ffmpeg', '-y',
                    '-ss', str(padded_start),
                    '-i', video_url,
                    '-ss', str(padded_start),
                    '-i', audio_url,
                    '-t', str(padded_duration),
                    '-map', '0:v:0',
                    '-map', '1:a:0',
                    '-c:v', 'libx264',
                    '-preset', 'fast',  # Fast encoding for segments
                    '-crf', '22',       # Reasonable quality
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    output_file
                ]
                
                logger.info(f"[Segment {segment_id}] Downloading segment with ffmpeg...")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"[Segment {segment_id}] ffmpeg error: {result.stderr}")
                    raise Exception("ffmpeg download failed")
                
                # Verify the segment was downloaded successfully
                if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
                    logger.info(f"[Segment {segment_id}] Successfully downloaded segment to {output_file}")
                    
                    # Now extract the exact segment to ensure we have the precise timing
                    precise_output = os.path.join(temp_dir, f"precise_segment_{segment_id}.mp4")
                    precise_cmd = [
                        'ffmpeg', '-y',
                        '-i', output_file,
                        '-ss', str(1),  # Skip the first second of padding
                        '-t', str(end_time - start_time),  # Exact duration
                        '-c:v', 'libx264',
                        '-preset', 'medium',  # Better quality for final output
                        '-crf', '18',         # High quality
                        '-c:a', 'aac',
                        '-b:a', '192k',
                        precise_output
                    ]
                    
                    subprocess.run(precise_cmd, check=True)
                    
                    # Replace the original output with the precise one
                    shutil.move(precise_output, output_file)
                    
                    return output_file
                else:
                    raise Exception(f"Output file is missing or too small: {output_file}")
            else:
                # Fallback: use yt-dlp's direct download with segment extraction
                logger.info(f"[Segment {segment_id}] Falling back to yt-dlp direct download...")
                ydl_opts = {
                    'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
                    'outtmpl': os.path.join(temp_dir, 'full_segment.mp4'),
                    'quiet': True,
                    'no_warnings': True,
                    'download_ranges': {
                        'videos': [
                            {
                                'start_time': padded_start,
                                'end_time': padded_start + padded_duration,
                            }
                        ],
                    },
                    'postprocessors': [{
                        'key': 'FFmpegVideoRemuxer',
                        'preferedformat': 'mp4',
                    }],
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])
                
                # Use ffmpeg to extract exact segment
                input_file = os.path.join(temp_dir, 'full_segment.mp4')
                if os.path.exists(input_file):
                    precise_cmd = [
                        'ffmpeg', '-y',
                        '-i', input_file,
                        '-ss', str(1),  # Skip the first second of padding
                        '-t', str(end_time - start_time),  # Exact duration
                        '-c:v', 'libx264',
                        '-preset', 'medium',
                        '-crf', '18',
                        '-c:a', 'aac',
                        '-b:a', '192k',
                        output_file
                    ]
                    
                    subprocess.run(precise_cmd, check=True)
                    
                    if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
                        return output_file
        
        # If all methods fail, raise exception
        raise Exception("Failed to download segment using any method")
                
    except Exception as e:
        logger.error(f"Error downloading segment: {e}")
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
