from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from youtube_utils import get_video_id, fetch_transcript, download_video
from ai_extractor import extract_important_parts
from video_processor import process_segment
import os
import json
import uuid
import threading
import logging

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
        logger.info(f"Using output directory: {output_dir}")
        
        # Update status
        processing_jobs[job_id]["message"] = "Extracting video ID"
        processing_jobs[job_id]["progress"] = 5
        logger.info("Extracting video ID")
        
        # Get video ID
        video_id = get_video_id(youtube_url)
        if not video_id:
            logger.error(f"Invalid YouTube URL: {youtube_url}")
            processing_jobs[job_id]["status"] = "error"
            processing_jobs[job_id]["message"] = "Invalid YouTube URL"
            return
            
        logger.info(f"Extracted video ID: {video_id}")
        
        # Update status
        processing_jobs[job_id]["message"] = "Fetching transcript"
        processing_jobs[job_id]["progress"] = 10
        logger.info("Fetching transcript")
        
        # Get transcript
        transcript = fetch_transcript(video_id)
        if not transcript:
            logger.error(f"Could not retrieve transcript for video ID: {video_id}")
            processing_jobs[job_id]["status"] = "error"
            processing_jobs[job_id]["message"] = "Could not retrieve transcript"
            return
            
        logger.info(f"Transcript retrieved with {len(transcript)} entries")
        
        # Update status
        processing_jobs[job_id]["message"] = "Analyzing transcript to find engaging segments"
        processing_jobs[job_id]["progress"] = 20
        logger.info("Analyzing transcript for engaging segments")
        
        # Extract important segments
        segments = extract_important_parts(transcript)
        processing_jobs[job_id]["segments"] = segments
        logger.info(f"Found {len(segments)} engaging segments")
        
        # Update status
        processing_jobs[job_id]["message"] = "Downloading video from YouTube"
        processing_jobs[job_id]["progress"] = 30
        logger.info("Downloading video from YouTube")
        
        # Download video
        video_path = download_video(youtube_url)
        if not video_path:
            logger.error(f"Failed to download video from URL: {youtube_url}")
            processing_jobs[job_id]["status"] = "error"
            processing_jobs[job_id]["message"] = "Failed to download video"
            return
            
        logger.info(f"Video downloaded to: {video_path}")
        
        # Process each segment
        shorts_paths = []
        for i, segment in enumerate(segments):
            # Update status for this segment
            processing_jobs[job_id]["message"] = f"Processing segment {i+1}/{len(segments)}"
            processing_jobs[job_id]["progress"] = 30 + (i * 70 // len(segments))
            logger.info(f"Processing segment {i+1}/{len(segments)}")
            
            # Generate unique filename with job ID prefix
            output_filename = f"{output_dir}/{job_id}_short_{i+1}.mp4"
            logger.info(f"Output will be saved to: {output_filename}")
            
            # Process the segment
            try:
                success = process_segment(
                    video_path=video_path,
                    segment=segment,
                    transcript_data=transcript,
                    aspect_ratio=aspect_ratio,
                    output_path=output_filename,
                    font_size=font_size,
                    words_per_subtitle=words_per_subtitle
                )
                
                if success:
                    logger.info(f"Successfully processed segment {i+1}")
                    # Build path that can be accessed from frontend
                    video_url = f"/shorts/{job_id}_short_{i+1}.mp4"
                    shorts_paths.append({
                        "id": f"short-{i+1}",
                        "title": f"Short {i+1}: {segment.get('reason', 'Engaging clip')}",
                        "url": video_url,
                        "thumbnailUrl": video_url.replace(".mp4", ".jpg"),  # You'll need to generate thumbnails
                        "duration": f"{int(segment.get('end_time', 0) - segment.get('start_time', 0))}s",
                        "segment": segment
                    })
                else:
                    logger.error(f"Failed to process segment {i+1}")
            except Exception as e:
                logger.exception(f"Error processing segment {i+1}: {str(e)}")
        
        # Update final status
        processing_jobs[job_id]["status"] = "completed"
        processing_jobs[job_id]["message"] = "All shorts have been created successfully"
        processing_jobs[job_id]["progress"] = 100
        processing_jobs[job_id]["videos"] = shorts_paths
        logger.info(f"Job {job_id} completed successfully with {len(shorts_paths)} shorts")
        
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
