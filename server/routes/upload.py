from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import subprocess
from app import process_video_job  # Import the processing function from app.py
import uuid

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' in request.files:
        # Handle file upload case
        file = request.files['file']
        # ... your existing file handling code ...
        
    elif 'youtubeUrl' in request.form:
        # Handle YouTube URL case
        youtube_url = request.form.get('youtubeUrl')
        aspect_ratio = request.form.get('aspectRatio', '9:16')
        words_per_subtitle = int(request.form.get('wordsPerSubtitle', 2))
        font_size = int(request.form.get('fontSize', 36))
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Start processing in background
        process_video_job(job_id, youtube_url, aspect_ratio, words_per_subtitle, font_size)
        
        return jsonify({
            "success": True,
            "jobId": job_id,
            "message": "YouTube processing started"
        })
    
    else:
        return jsonify({"error": "No file or YouTube URL provided"}), 400 