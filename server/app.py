from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from youtube_utils import get_video_id, fetch_transcript, download_video, download_video_segment
from ai_extractor import extract_important_parts
from video_processor import process_segment, add_subtitles, extract_thumbnail
from subtitle_generator import create_word_by_word_subtitle_file
from face_tracker import track_face_and_crop_mediapipe
import os
import json
import uuid
import threading
import logging
import subprocess
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('youtube-shorts')

app = Flask(__name__)
CORS(app)

# Track processing jobs
processing_jobs = {}

# Serve generated videos
@app.route('/shorts/<filename>')
def serve_video(filename):
    # Directory where videos are stored
    directory = os.path.abspath("shorts_output")
    file_path = os.path.join(directory, filename)
    
    # Enhanced logging
    logger.info(f"Request for file: {filename}")
    logger.info(f"Looking in directory: {directory}")
    logger.info(f"Full path: {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        # List directory contents to help debug
        try:
            dir_contents = os.listdir(directory)
            logger.info(f"Directory contents: {dir_contents}")
        except Exception as e:
            logger.error(f"Could not list directory: {str(e)}")
        return jsonify({"error": "File not found"}), 404
    
    # Log file details
    logger.info(f"File exists, size: {os.path.getsize(file_path)} bytes")
    
    # Check if file is actually readable
    try:
        with open(file_path, 'rb') as f:
            # Just read a small amount to verify file is accessible
            _ = f.read(1024)
    except Exception as e:
        logger.error(f"File exists but cannot be read: {str(e)}")
        return jsonify({"error": "File cannot be read"}), 500
    
    # Determine content type based on file extension
    file_extension = os.path.splitext(filename)[1].lower()
    
    if file_extension == '.mp4':
        content_type = 'video/mp4'
    elif file_extension == '.jpg' or file_extension == '.jpeg':
        content_type = 'image/jpeg'
    elif file_extension == '.png':
        content_type = 'image/png'
    else:
        content_type = 'application/octet-stream'
    
    # Use an improved method for serving potentially large files
    try:
        # For videos, use a streaming response with byte range support
        if file_extension == '.mp4':
            response = send_file(
                file_path,
                mimetype=content_type,
                as_attachment=False,
                conditional=True  # Enables partial content responses
            )
            response.headers['Accept-Ranges'] = 'bytes'
            return response
        else:
            # For images and other files
            return send_file(file_path, mimetype=content_type)
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        return jsonify({"error": "Error serving file"}), 500

# Get processing status
@app.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    logger.info(f"Status check for job: {job_id}")
    if job_id in processing_jobs:
        logger.info(f"Job status: {processing_jobs[job_id]['status']}, progress: {processing_jobs[job_id]['progress']}%")
        return jsonify(processing_jobs[job_id])
    logger.warning(f"Job not found: {job_id}")
    return jsonify({"error": "Job not found"}), 404

# Process YouTube URL and generate shorts
@app.route('/api/process-youtube', methods=['POST'])
def process_youtube():
    logger.info("API request received at /api/process-youtube")
    logger.debug(f"Request JSON: {request.json}")
    
    data = request.json
    if not data:
        logger.error("No JSON data in request")
        return jsonify({"error": "No data provided"}), 400
        
    youtube_url = data.get('youtubeUrl')
    logger.info(f"Processing YouTube URL: {youtube_url}")
    
    aspect_ratio = data.get('aspectRatio', '9:16')
    words_per_subtitle = int(data.get('wordsPerSubtitle', 2))
    font_size = int(data.get('fontSize', 36))
    
    if not youtube_url:
        logger.error("YouTube URL is required but not provided")
        return jsonify({"error": "YouTube URL is required"}), 400
        
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    logger.info(f"Generated job ID: {job_id}")
    
    # Initialize job status
    processing_jobs[job_id] = {
        "status": "processing",
        "message": "Starting video processing",
        "segments": [],
        "progress": 0,
        "youtubeUrl": youtube_url
    }
    
    # Start processing in background thread
    logger.info("Starting background processing thread")
    thread = threading.Thread(
        target=process_video_job,
        args=(job_id, youtube_url, aspect_ratio, words_per_subtitle, font_size)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "jobId": job_id,
        "status": "processing",
        "message": "Video processing started"
    })

# Upload endpoint - handle both form data and JSON
@app.route('/upload', methods=['POST'])
def upload_file():
    logger.info("Request received at /upload")
    logger.debug(f"Request form: {request.form}")
    logger.debug(f"Request files: {request.files}")
    logger.debug(f"Request JSON: {request.get_json(silent=True)}")
    logger.debug(f"Request data: {request.data}")
    
    # First try to process as form data
    if 'file' in request.files:
        logger.info("File upload detected")
        file = request.files['file']
        # Implement file handling if needed
        return jsonify({"error": "File upload not implemented yet"}), 501
        
    elif 'youtubeUrl' in request.form:
        logger.info("YouTube URL detected in form data")
        youtube_url = request.form.get('youtubeUrl')
        logger.info(f"Processing YouTube URL from form: {youtube_url}")
        
        aspect_ratio = request.form.get('aspectRatio', '9:16')
        words_per_subtitle = int(request.form.get('wordsPerSubtitle', 2))
        font_size = int(request.form.get('fontSize', 36))
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        logger.info(f"Generated job ID: {job_id}")
        
        # Initialize job status
        processing_jobs[job_id] = {
            "status": "processing",
            "message": "Starting video processing",
            "segments": [],
            "progress": 0,
            "youtubeUrl": youtube_url
        }
        
        # Start processing in background
        logger.info("Starting background processing thread")
        thread = threading.Thread(
            target=process_video_job,
            args=(job_id, youtube_url, aspect_ratio, words_per_subtitle, font_size)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "jobId": job_id,
            "message": "YouTube processing started"
        })
    
    # Try JSON if form data doesn't have what we need
    elif request.is_json:
        logger.info("JSON data detected")
        data = request.get_json()
        youtube_url = data.get('youtubeUrl')
        if youtube_url:
            logger.info(f"Processing YouTube URL from JSON: {youtube_url}")
            
            aspect_ratio = data.get('aspectRatio', '9:16')
            words_per_subtitle = int(data.get('wordsPerSubtitle', 2))
            font_size = int(data.get('fontSize', 36))
            
            # Generate job ID
            job_id = str(uuid.uuid4())
            logger.info(f"Generated job ID: {job_id}")
            
            # Initialize job status
            processing_jobs[job_id] = {
                "status": "processing",
                "message": "Starting video processing",
                "segments": [],
                "progress": 0,
                "youtubeUrl": youtube_url
            }
            
            # Start processing in background
            logger.info("Starting background processing thread")
            thread = threading.Thread(
                target=process_video_job,
                args=(job_id, youtube_url, aspect_ratio, words_per_subtitle, font_size)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                "success": True,
                "jobId": job_id,
                "message": "YouTube processing started"
            })
    
    # Try to parse potential raw data
    elif request.data:
        logger.info("Raw data detected, trying to parse as JSON")
        try:
            data = json.loads(request.data)
            youtube_url = data.get('youtubeUrl')
            if youtube_url:
                logger.info(f"Processing YouTube URL from raw data: {youtube_url}")
                
                aspect_ratio = data.get('aspectRatio', '9:16')
                words_per_subtitle = int(data.get('wordsPerSubtitle', 2))
                font_size = int(data.get('fontSize', 36))
                
                # Generate job ID
                job_id = str(uuid.uuid4())
                logger.info(f"Generated job ID: {job_id}")
                
                # Initialize job status
                processing_jobs[job_id] = {
                    "status": "processing",
                    "message": "Starting video processing",
                    "segments": [],
                    "progress": 0,
                    "youtubeUrl": youtube_url
                }
                
                # Start processing in background
                logger.info("Starting background processing thread")
                thread = threading.Thread(
                    target=process_video_job,
                    args=(job_id, youtube_url, aspect_ratio, words_per_subtitle, font_size)
                )
                thread.daemon = True
                thread.start()
                
                return jsonify({
                    "success": True,
                    "jobId": job_id,
                    "message": "YouTube processing started"
                })
        except json.JSONDecodeError:
            logger.error("Failed to parse raw data as JSON")
    
    logger.error("No valid data found in request")
    return jsonify({"error": "No file or YouTube URL provided", "requestInfo": {
        "hasForm": len(request.form) > 0,
        "hasFiles": len(request.files) > 0,
        "isJson": request.is_json,
        "hasData": bool(request.data)
    }}), 400

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

def extract_thumbnail(video_path, output_path):
    """Generate a thumbnail from a video file using ffmpeg."""
    try:
        # Make sure we capture a frame at 1 second to avoid black frames
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-ss', '00:00:01',  # Take frame at 1 second
            '-frames:v', '1',
            '-q:v', '2',       # High quality
            '-vf', 'scale=640:-1',  # Resize to reasonable width
            output_path
        ]
        subprocess.run(cmd, check=True)
        
        # Verify thumbnail was created
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            logger.info(f"Generated thumbnail: {output_path}")
            return True
        else:
            logger.error(f"Failed to generate valid thumbnail: {output_path}")
            return False
    except Exception as e:
        logger.error(f"Error generating thumbnail: {str(e)}")
        return False

def process_video_job(job_id, youtube_url, aspect_ratio, words_per_subtitle, font_size):
    logger.info(f"Starting video processing job: {job_id}")
    try:
        # Create output directory if it doesn't exist
        output_dir = "shorts_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize videos array in the job status
        processing_jobs[job_id]["videos"] = []
        processing_jobs[job_id]["message"] = "Extracting video ID"
        processing_jobs[job_id]["progress"] = 5
        
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
                        # Extra step to ensure video is web-compatible
                        def ensure_web_compatible_video(input_file, output_file=None):
                            """Ensure video is encoded in a web-compatible format."""
                            if output_file is None:
                                output_file = f"{os.path.splitext(input_file)[0]}_web.mp4"
                            
                            try:
                                cmd = [
                                    'ffmpeg', '-y',
                                    '-i', input_file,
                                    '-c:v', 'libx264',
                                    '-profile:v', 'main',
                                    '-preset', 'fast',
                                    '-crf', '23',
                                    '-movflags', '+faststart',
                                    '-pix_fmt', 'yuv420p',
                                    '-c:a', 'aac',
                                    '-b:a', '128k',
                                    output_file
                                ]
                                subprocess.run(cmd, check=True)
                                
                                if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
                                    return output_file
                                return None
                            except Exception as e:
                                logger.error(f"Error making video web compatible: {str(e)}")
                                return None

                        # After processing each segment and creating output_filename
                        final_video_path = output_filename
                        web_compatible_path = ensure_web_compatible_video(output_filename)
                        if web_compatible_path:
                            final_video_path = web_compatible_path
                            # If we created a new file, rename it to the original
                            if web_compatible_path != output_filename:
                                try:
                                    os.replace(web_compatible_path, output_filename)
                                    final_video_path = output_filename
                                except Exception as e:
                                    logger.error(f"Error replacing video with web compatible version: {str(e)}")

                        # Generate thumbnail with more reliable method
                        thumbnail_path = f"{os.path.splitext(output_filename)[0]}.jpg"
                        extract_thumbnail(final_video_path, thumbnail_path)

                        # Create explicit, absolute URLs that will work in the browser
                        video_basename = os.path.basename(final_video_path)
                        thumbnail_basename = os.path.basename(thumbnail_path)

                        # Use absolute URLs to avoid any path resolution issues
                        video_url = f"{request.url_root.rstrip('/')}/video/{video_basename}"
                        thumbnail_url = f"{request.url_root.rstrip('/')}/thumbnail/{thumbnail_basename}"

                        # Logging for debugging
                        logger.info(f"Created video URL: {video_url}")
                        logger.info(f"Created thumbnail URL: {thumbnail_url}")

                        # Add to videos list
                        new_video = {
                            "id": f"short-{i+1}",
                            "title": f"Short {i+1}: {segment.get('reason', 'Engaging clip')}",
                            "url": video_url,
                            "thumbnailUrl": thumbnail_url,
                            "duration": f"{int(end_time - start_time)}s"
                        }
                        
                        processing_jobs[job_id]["videos"].append(new_video)
                    else:
                        logger.error(f"Failed to add subtitles to segment {i+1}")
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

@app.route('/api/test', methods=['GET'])
def test_api():
    logger.info("Test API endpoint called")
    return jsonify({"status": "ok", "message": "API is working"})

# Simple, direct route for video files
@app.route('/video/<filename>')
def serve_video_file(filename):
    directory = os.path.abspath("shorts_output")
    file_path = os.path.join(directory, filename)
    
    # Check if file exists and is valid
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
        return jsonify({"error": "Video file is missing or invalid"}), 404
    
    # For video files, we need to use byte-range requests
    # This enables proper seeking in the video player
    response = send_file(
        file_path,
        mimetype='video/mp4',
        as_attachment=False,
        conditional=True  # Enable partial content responses
    )
    
    # Add necessary headers for video streaming
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response

# Simple route for thumbnail files  
@app.route('/thumbnail/<filename>')
def serve_thumbnail_file(filename):
    directory = os.path.abspath("shorts_output")
    return send_file(os.path.join(directory, filename), mimetype='image/jpeg')

if __name__ == '__main__':
    port = 8080
    logger.info(f"Starting server on http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)
