from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import subprocess
import uuid
import threading
import logging

# Import from our new processing module instead of app.py
from processing import process_video_job

# Set up logging
logger = logging.getLogger('youtube-shorts-upload')

upload_bp = Blueprint('upload', __name__)

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