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
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
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
        
        # Process each segment individually
        for i, segment in enumerate(segments):
            start_time = float(segment.get('start_time', 0))
            end_time = float(segment.get('end_time', start_time + 30))
            
            # Update status for this segment
            processing_jobs[job_id]["message"] = f"Downloading segment {i+1}/{len(segments)}"
            processing_jobs[job_id]["progress"] = 30 + (i * 15 // len(segments))
            
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
                
                if not segment_video:
                    logger.error(f"Failed to download segment {i+1}")
                    continue
                
                # Update status for processing
                processing_jobs[job_id]["message"] = f"Processing segment {i+1}/{len(segments)}"
                processing_jobs[job_id]["progress"] = 45 + (i * 55 // len(segments))
                
                # Create subtitle file for this segment
                temp_dir = f"temp_{os.path.basename(output_filename).split('.')[0]}"
                os.makedirs(temp_dir, exist_ok=True)
                
                subtitle_file = f"{temp_dir}/subtitles.srt"
                create_word_by_word_subtitle_file(
                    transcript_data=transcript,
                    start_time=start_time,
                    end_time=end_time,
                    output_file=subtitle_file,
                    words_per_subtitle=words_per_subtitle
                )
                
                # Process with face tracking
                tracked_segment = f"{temp_dir}/tracked_segment.mp4"
                logger.info(f"Applying face tracking to segment {i+1}...")
                
                if track_face_and_crop_mediapipe(segment_video, tracked_segment, aspect_ratio, segment_id=i+1, total_segments=len(segments)):
                    # Add subtitles
                    logger.info(f"Adding subtitles to segment {i+1}...")
                    
                    success = add_subtitles(tracked_segment, subtitle_file, output_filename, font_size)
                    
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
                        
                        # Force persist video to disk by syncing
                        try:
                            os.sync()  # Only works on Unix-like systems
                        except:
                            pass  # Ignore if not available
                else:
                    logger.error(f"Failed face tracking for segment {i+1}")
            except Exception as e:
                logger.exception(f"Error processing segment {i+1}: {str(e)}")
            finally:
                # Clean up temporary files
                try:
                    if os.path.exists(segment_video):
                        os.remove(segment_video)
                    
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up temporary files: {cleanup_error}")
        
        # Update final status
        if len(processing_jobs[job_id]["videos"]) > 0:
            processing_jobs[job_id]["status"] = "completed"
            processing_jobs[job_id]["message"] = "All shorts have been created successfully"
        else:
            processing_jobs[job_id]["status"] = "error"
            processing_jobs[job_id]["message"] = "Failed to create any shorts"
            
        processing_jobs[job_id]["progress"] = 100
        
    except Exception as e:
        logger.exception(f"Error processing video job {job_id}: {str(e)}")
        processing_jobs[job_id]["status"] = "error"
        processing_jobs[job_id]["message"] = f"Error processing video: {str(e)}"

# Function to get job status
def get_job_status(job_id):
    if job_id in processing_jobs:
        return processing_jobs[job_id]
    return {"status": "not_found", "message": "Job not found"} 