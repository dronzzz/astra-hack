# Import necessary modules
from youtube_utils import get_video_id, fetch_transcript, download_video, download_video_segment
from ai_extractor import extract_important_parts
from video_processor import process_segment, add_subtitles, extract_thumbnail
from subtitle_generator import create_word_by_word_subtitle_file
from face_tracker import track_face_and_crop_mediapipe
import os
import json
import threading
import logging
import subprocess
import shutil
import datetime
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('youtube-shorts-processing')

# Dictionary to track processing jobs
processing_jobs = {}


def is_valid_mp4(file_path):
    """Check if the MP4 file is valid and playable."""
    try:
        # Use ffprobe to check file validity
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,width,height',
            '-of', 'json',
            file_path
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False)

        # Parse the JSON output
        if result.returncode == 0 and "codec_name" in result.stdout:
            return True

        return False
    except Exception as e:
        logger.error(f"Error validating MP4: {str(e)}")
        return False


def process_video_job(job_id, youtube_url, aspect_ratio, words_per_subtitle, font_size):
    logger.info(f"Starting video processing job: {job_id}")
    try:
        # Create output directory if it doesn't exist
        output_dir = "shorts_output"
        os.makedirs(output_dir, exist_ok=True)

        # Create subtitle storage directory
        subtitle_storage_dir = os.path.join(output_dir, "subtitles")
        os.makedirs(subtitle_storage_dir, exist_ok=True)

        # Initialize videos array in the job status
        processing_jobs[job_id] = {
            "status": "processing",
            "videos": [],
            "message": "Extracting video ID",
            "progress": 5
        }

        # Get video ID
        video_id = get_video_id(youtube_url)
        if not video_id:
            processing_jobs[job_id]["status"] = "error"
            processing_jobs[job_id]["message"] = "Invalid YouTube URL"
            return

        # Update status
        processing_jobs[job_id]["message"] = "Fetching transcript"
        processing_jobs[job_id]["progress"] = 10

        # Get transcript
        transcript = fetch_transcript(video_id)
        if not transcript:
            processing_jobs[job_id]["status"] = "error"
            processing_jobs[job_id]["message"] = "Could not retrieve transcript"
            return

        # Update status
        processing_jobs[job_id]["message"] = "Analyzing transcript to find engaging segments"
        processing_jobs[job_id]["progress"] = 20

        # Extract important segments
        segments = extract_important_parts(transcript)
        processing_jobs[job_id]["segments"] = segments

        # Create a list to track temp files for cleanup
        temp_files_to_cleanup = []
        temp_dirs_to_cleanup = []

        # Process each segment individually
        for i, segment in enumerate(segments):
            start_time = float(segment.get('start_time', 0))
            end_time = float(segment.get('end_time', start_time + 30))

            # Update status for this segment
            processing_jobs[job_id]["message"] = f"Downloading segment {i+1}/{len(segments)}"
            processing_jobs[job_id]["progress"] = 30 + \
                (i * 15 // len(segments))

            # Generate unique filename with job ID prefix
            output_filename = f"{output_dir}/{job_id}_short_{i+1}.mp4"
            thumbnail_path = output_filename.replace(".mp4", ".jpg")

            try:
                # Download just this segment
                segment_video = download_video_segment(
                    youtube_url,
                    start_time,
                    end_time,
                    segment_id=i+1,
                    total_segments=len(segments)
                )

                # Track for cleanup
                if segment_video:
                    temp_files_to_cleanup.append(segment_video)
                    temp_dir = os.path.dirname(segment_video)
                    if temp_dir not in temp_dirs_to_cleanup:
                        temp_dirs_to_cleanup.append(temp_dir)

                if not segment_video:
                    logger.error(f"Failed to download segment {i+1}")
                    continue

                # Update status for processing
                processing_jobs[job_id][
                    "message"] = f"Processing segment {i+1}/{len(segments)}"
                processing_jobs[job_id]["progress"] = 45 + \
                    (i * 55 // len(segments))

                # Create subtitle file for this segment
                temp_dir = f"temp_{os.path.basename(output_filename).split('.')[0]}"
                os.makedirs(temp_dir, exist_ok=True)
                temp_dirs_to_cleanup.append(temp_dir)

                subtitle_file = f"{temp_dir}/subtitles.srt"
                create_word_by_word_subtitle_file(
                    transcript_data=transcript,
                    start_time=start_time,
                    end_time=end_time,
                    output_file=subtitle_file,
                    words_per_subtitle=words_per_subtitle
                )

                # Save a permanent copy of the subtitle file
                permanent_srt_file = output_filename.replace(".mp4", ".srt")
                if os.path.exists(subtitle_file):
                    shutil.copy(subtitle_file, permanent_srt_file)
                    logger.info(
                        f"Saved permanent subtitle file: {permanent_srt_file}")

                # Also extract text content and save it separately
                if os.path.exists(subtitle_file):
                    try:
                        # Extract text from SRT file
                        subtitle_text = []
                        with open(subtitle_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()

                        # Process SRT format
                        i = 0
                        while i < len(lines):
                            line = lines[i].strip()
                            if line.isdigit():  # This is a subtitle number
                                i += 1  # Skip to timestamp line
                                i += 1  # Skip to text line
                                # Collect all text lines until a blank line
                                text_lines = []
                                while i < len(lines) and lines[i].strip():
                                    text_lines.append(lines[i].strip())
                                    i += 1

                                if text_lines:
                                    subtitle_text.append(" ".join(text_lines))
                            else:
                                i += 1

                        if subtitle_text:
                            text_content = " ".join(subtitle_text)
                            # Save to text file
                            video_name_without_ext = os.path.splitext(
                                os.path.basename(output_filename))[0]
                            text_file_path = os.path.join(
                                subtitle_storage_dir, f"{video_name_without_ext}.txt")
                            with open(text_file_path, 'w', encoding='utf-8') as f:
                                f.write(text_content)
                            logger.info(
                                f"Saved text content to: {text_file_path}")
                    except Exception as e:
                        logger.error(f"Error extracting subtitle text: {e}")

                # Process with face tracking
                tracked_segment = f"{temp_dir}/tracked_segment.mp4"
                logger.info(f"Applying face tracking to segment {i+1}...")

                if track_face_and_crop_mediapipe(segment_video, tracked_segment, aspect_ratio, segment_id=i+1, total_segments=len(segments)):
                    # Track for cleanup
                    temp_files_to_cleanup.append(tracked_segment)

                    # Add subtitles
                    logger.info(f"Adding subtitles to segment {i+1}...")

                    success = add_subtitles(
                        tracked_segment, subtitle_file, output_filename, font_size)

                    if success:
                        logger.info(f"Successfully processed segment {i+1}")
                        # Generate thumbnail
                        extract_thumbnail(output_filename, thumbnail_path)

                        # Use direct paths to the files
                        video_basename = os.path.basename(output_filename)
                        thumbnail_basename = os.path.basename(thumbnail_path)

                        # Use direct paths to the files
                        video_url = f"/shorts_output/{video_basename}"
                        thumbnail_url = f"/shorts_output/{thumbnail_basename}"

                        # Add to videos list
                        new_video = {
                            "id": f"short-{i+1}",
                            "title": f"Short {i+1}: {segment.get('reason', 'Engaging clip')}",
                            "url": video_url,
                            "thumbnailUrl": thumbnail_url,
                            "duration": f"{int(end_time - start_time)}s"
                        }

                        processing_jobs[job_id]["videos"].append(new_video)
                        logger.info(f"Segment {i+1} ready for viewing")

                        # Ensure file is flushed to disk
                        try:
                            os.sync()  # Only works on Unix-like systems
                        except:
                            pass  # Ignore if not available
                else:
                    logger.error(f"Failed face tracking for segment {i+1}")
            except Exception as e:
                logger.exception(f"Error processing segment {i+1}: {str(e)}")
            finally:
                # Don't clean up temp files yet - we'll do it at the end
                pass

        # Clean up all temporary files
        logger.info(f"Cleaning up temporary files")
        for temp_file in temp_files_to_cleanup:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.info(f"Removed temporary file: {temp_file}")
            except Exception as e:
                logger.error(f"Error removing temporary file {temp_file}: {e}")

        # Clean up temporary directories
        for temp_dir in temp_dirs_to_cleanup:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    logger.info(f"Removed temporary directory: {temp_dir}")
            except Exception as e:
                logger.error(
                    f"Error removing temporary directory {temp_dir}: {e}")

        # Update final status
        if len(processing_jobs[job_id]["videos"]) > 0:
            processing_jobs[job_id]["status"] = "completed"
            processing_jobs[job_id]["message"] = "All shorts have been created successfully"
        else:
            processing_jobs[job_id]["status"] = "error"
            processing_jobs[job_id]["message"] = "Failed to create any shorts"

        processing_jobs[job_id]["progress"] = 100

    except Exception as e:
        # Handle any unexpected errors
        logger.exception(f"Error in process_video_job: {str(e)}")
        processing_jobs[job_id]["status"] = "error"
        processing_jobs[job_id]["message"] = f"Unexpected error: {str(e)}"
        processing_jobs[job_id]["progress"] = 100

# Function to get job status


def get_job_status(job_id):
    if job_id in processing_jobs:
        return processing_jobs[job_id]
    return {"status": "not_found", "message": "Job not found"}
