from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import subprocess
import uuid
import threading
import logging
import sieve
from video_processor import extract_thumbnail
import datetime
import glob

# Import from our new processing module instead of app.py
from processing import process_video_job

# Set up logging
logger = logging.getLogger('youtube-shorts-upload')

upload_bp = Blueprint('upload', __name__)

# Ensure the Sieve API key is set globally
API_KEY = "DwOcdC4CPfwP-U1djJIqD0npN5ERMoGiSp6K7-cdHqk"
os.environ["SIEVE_API_KEY"] = API_KEY
sieve.api_key = API_KEY

# Make sure the dubbing_jobs dictionary exists
dubbing_jobs = {}

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    logger.info("Upload endpoint called")
    if 'file' in request.files:
        # Handle file upload case
        file = request.files['file']
        logger.info(f"File upload received: {file.filename}")
        # ... your existing file handling code ...
        return jsonify({"error": "File upload not yet implemented"}), 501
        
    elif 'youtubeUrl' in request.form:
        # Handle YouTube URL case
        youtube_url = request.form.get('youtubeUrl')
        aspect_ratio = request.form.get('aspectRatio', '9:16')
        words_per_subtitle = int(request.form.get('wordsPerSubtitle', 2))
        font_size = int(request.form.get('fontSize', 36))
        
        logger.info(f"YouTube URL received: {youtube_url}")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Start processing in background thread
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
    
    else:
        logger.warning("No file or YouTube URL provided")
        return jsonify({"error": "No file or YouTube URL provided"}), 400

@upload_bp.route('/api/process-youtube', methods=['POST'])
def process_youtube():
    logger.info("Process YouTube endpoint called")
    try:
        data = request.json
        if not data or 'youtubeUrl' not in data:
            logger.warning("No YouTube URL provided in JSON")
            return jsonify({"error": "No YouTube URL provided"}), 400
            
        youtube_url = data['youtubeUrl']
        aspect_ratio = data.get('aspectRatio', '9:16')
        words_per_subtitle = int(data.get('wordsPerSubtitle', 2))
        font_size = int(data.get('fontSize', 36))
        
        logger.info(f"YouTube URL received via API: {youtube_url}")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Start processing in background thread
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
    except Exception as e:
        logger.exception(f"Error processing YouTube URL: {str(e)}")
        return jsonify({"error": str(e)}), 500

@upload_bp.route('/api/sieve-dub', methods=['POST'])
def sieve_dub():
    """Process a video segment with Sieve's dubbing service"""
    try:
        # Add basic logging
        logger.info("sieve_dub endpoint called")
        
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract required parameters
        job_id = data.get('jobId')
        segment_id = data.get('segmentId')
        language = data.get('language', 'spanish')  # Default to Spanish
        voice_engine = data.get('voiceEngine', 'elevenlabs (voice cloning)')
        enable_lipsyncing = data.get('enableLipsyncing', False)
        
        logger.info(f"Processing dubbing request for job {job_id}, segment {segment_id}, language {language}")
        
        if not job_id or not segment_id:
            return jsonify({"error": "jobId and segmentId are required"}), 400
            
        # Simplified file search logic
        segment_vid_path = None
        shorts_dir = "shorts_output"
        segment_num = segment_id.replace("short-", "").replace("short_", "")
        
        # Look for the most likely file patterns
        possible_filenames = [
            f"{job_id}_short_{segment_num}.mp4",
            f"short_{segment_num}.mp4"
        ]
        
        for filename in possible_filenames:
            filepath = os.path.join(shorts_dir, filename)
            if os.path.exists(filepath):
                segment_vid_path = filepath
                logger.info(f"Found segment video at: {segment_vid_path}")
                break
        
        # If not found, try broader search
        if not segment_vid_path:
            for file in os.listdir(shorts_dir):
                if file.endswith(".mp4") and (segment_num in file or job_id in file):
                    segment_vid_path = os.path.join(shorts_dir, file)
                    logger.info(f"Found video with broader search: {segment_vid_path}")
                    break
                
        if not segment_vid_path:
            error_msg = f"Video file not found for job {job_id}, segment {segment_id}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 404
            
        # Create a unique ID for this dubbing job
        dubbing_id = str(uuid.uuid4())
        
        # Create a directory to store dubbing output
        dubbing_dir = os.path.join(shorts_dir, "dubbed")
        os.makedirs(dubbing_dir, exist_ok=True)
        
        # Create output path for dubbed file
        output_filename = f"{os.path.splitext(os.path.basename(segment_vid_path))[0]}_{language}_{dubbing_id}.mp4"
        output_path = os.path.join(dubbing_dir, output_filename)
        
        # Initialize job status
        dubbing_jobs[dubbing_id] = {
            "status": "processing",
            "message": "Initiating dubbing process",
            "jobId": job_id,
            "segmentId": segment_id,
            "language": language,
            "startTime": datetime.datetime.now().isoformat()
        }
        
        # Use a simpler process function based on the example
        thread = threading.Thread(
            target=simplified_sieve_dubbing,
            args=(dubbing_id, segment_vid_path, language, voice_engine, enable_lipsyncing, output_path),
            daemon=True
        )
        thread.start()
        
        logger.info(f"Started Sieve dubbing job {dubbing_id} for segment {segment_id}")
        
        # Return the dubbing ID for status polling
        return jsonify({
            "status": "processing",
            "message": "Dubbing job submitted successfully",
            "dubbingId": dubbing_id
        })
        
    except Exception as e:
        logger.exception(f"Error processing sieve-dub: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Simplified function that only uses the core sieve functionality
def simplified_sieve_dubbing(dubbing_id, video_path, language, voice_engine, enable_lipsyncing, output_path):
    """Minimalist version of the Sieve dubbing function"""
    try:
        logger.info(f"Starting simplified Sieve dubbing with hardcoded API key")
        
        # Update the job status
        dubbing_jobs[dubbing_id]["message"] = "Initializing Sieve API"
        
        # HARDCODE EVERYTHING - Japanese language, no options
        target_language = "jpn"
        logger.info(f"Using hardcoded Japanese language (jpn)")
        
        # Create Sieve File object with minimal code
        source_file = sieve.File(path=video_path)
        logger.info(f"Created Sieve File from {video_path}")
        
        # Get the dubbing function WITHOUT passing api_key parameter
        dubbing = sieve.function.get("sieve/dubbing")  # No api_key argument here
        logger.info("Obtained Sieve dubbing function")
        
        # Update status
        dubbing_jobs[dubbing_id]["message"] = "Submitting to Sieve Dubbing API"
        
        # Call with MINIMAL parameters
        output = dubbing.push(
            source_file,     # source_file (required)
            target_language, # target_language (required)  
            "gpt4",          # translation_engine (required)
            voice_engine,    # voice_engine (passed from the request)
            "whisper-zero",  # transcription_engine (required)
            "voice-dubbing", # output_mode (required)
            [],              # edit_segments (required but can be empty)
            False,           # return_transcript (required)
            True,            # preserve_background_audio (required)
            "",              # safewords (required but can be empty)
            "",              # translation_dictionary (required but can be empty)
            0,               # start_time (required)
            -1,              # end_time (required)
            enable_lipsyncing, # enable_lipsyncing (passed from the request)
            "sievesync-1.1", # lipsync_backend (required)
            "default"        # lipsync_enhance (required)
        )
        
        logger.info("Dubbing job submitted successfully, waiting for result")
        dubbing_jobs[dubbing_id]["message"] = "Dubbing in progress at Sieve"
        
        # Wait for the result
        result = output.result()
        logger.info("Received result from Sieve")
        
        # Download the dubbed video
        dubbed_video = None
        for output_object in result:
            if isinstance(output_object, sieve.File):
                dubbed_video = output_object
                break
        
        if not dubbed_video:
            raise Exception("No dubbed video file returned from Sieve")
        
        # Download the file locally
        logger.info(f"Downloading dubbed video to {output_path}")
        dubbed_video.download(output_path)
        
        # Generate a thumbnail
        thumbnail_path = output_path.replace(".mp4", ".jpg")
        try:
            import subprocess
            cmd = [
                'ffmpeg', '-y',
                '-i', output_path,
                '-ss', '00:00:01',
                '-vframes', '1',
                '-q:v', '2',
                thumbnail_path
            ]
            subprocess.run(cmd, check=True)
            logger.info(f"Created thumbnail at {thumbnail_path}")
        except Exception as e:
            logger.error(f"Failed to create thumbnail: {str(e)}")
            # Continue anyway, this is not critical
        
        # Update the job status
        dubbing_jobs[dubbing_id]["status"] = "completed"
        dubbing_jobs[dubbing_id]["message"] = "Dubbing completed successfully"
        dubbing_jobs[dubbing_id]["videoUrl"] = f"/shorts_output/dubbed/{os.path.basename(output_path)}"
        dubbing_jobs[dubbing_id]["thumbnailUrl"] = f"/shorts_output/dubbed/{os.path.basename(thumbnail_path)}"
        
        logger.info(f"Sieve dubbing completed successfully")
        
    except Exception as e:
        logger.exception(f"Error in simplified_sieve_dubbing: {str(e)}")
        dubbing_jobs[dubbing_id]["status"] = "error"
        dubbing_jobs[dubbing_id]["message"] = f"Error during dubbing: {str(e)}"

# Add or update the status endpoint
@upload_bp.route('/api/sieve-dub-status/<dubbing_id>', methods=['GET'])
def sieve_dub_status(dubbing_id):
    """Get the status of a Sieve dubbing job"""
    logger.info(f"Status check for dubbing job: {dubbing_id}")
    
    if dubbing_id not in dubbing_jobs:
        logger.error(f"Dubbing job not found: {dubbing_id}")
        return jsonify({"error": "Dubbing job not found"}), 404
        
    job = dubbing_jobs[dubbing_id]
    
    # For completed jobs, include the video URL
    if job["status"] == "completed":
        return jsonify({
            "status": job["status"],
            "message": job["message"],
            "videoUrl": job.get("videoUrl"),
            "thumbnailUrl": job.get("thumbnailUrl")
        })
    else:
        return jsonify({
            "status": job["status"],
            "message": job["message"]
        })