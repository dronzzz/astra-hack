from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from youtube_utils import get_video_id, fetch_transcript, download_video_segment
from ai_extractor import extract_important_parts
from video_processor import process_segment, create_word_by_word_subtitle_file, track_face_and_crop_mediapipe, extract_thumbnail
import os
import json
import uuid
import threading
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('youtube-shorts')

app = Flask(__name__)
CORS(app)

# Track processing jobs
processing_jobs = {}

# Serve generated videos
@app.route('/shorts/<filename>')
def serve_video(filename):
    logger.info(f"Serving video file: {filename}")
    return send_from_directory('shorts_output', filename)

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
                
            # Generate unique filename with job ID prefix
            output_filename = f"{output_dir}/{job_id}_short_{i+1}.mp4"
            
            # Update status for processing
            processing_jobs[job_id]["message"] = f"Processing segment {i+1}/{len(segments)}"
            processing_jobs[job_id]["progress"] = 45 + (i * 55 // len(segments))
            
            # Process the segment
            try:
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
                    
                    from video_processor import add_subtitles
                    success = add_subtitles(tracked_segment, subtitle_file, output_filename, font_size)
                    
                    # Generate thumbnail
                    if success:
                        thumbnail_path = output_filename.replace(".mp4", ".jpg")
                        extract_thumbnail(output_filename, thumbnail_path)
                        
                        # Build path that can be accessed from frontend
                        video_url = f"/shorts/{job_id}_short_{i+1}.mp4"
                        thumbnail_url = f"/shorts/{job_id}_short_{i+1}.jpg"
                        
                        # Add to videos list
                        new_video = {
                            "id": f"short-{i+1}",
                            "title": f"Short {i+1}: {segment.get('reason', 'Engaging clip')}",
                            "url": video_url,
                            "thumbnailUrl": thumbnail_url,
                            "filePath": output_filename,  # For debugging
                            "duration": f"{int(end_time - start_time)}s",
                            "segment": segment
                        }
                        
                        processing_jobs[job_id]["videos"].append(new_video)
                        logger.info(f"Segment {i+1} ready for viewing")
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
