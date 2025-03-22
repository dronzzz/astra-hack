from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from requests_toolbelt.multipart import decoder
import os

import shutil
import sieve

import time
import json
import threading
import logging
import uuid
import shutil
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from sieve_dubbing import dub_video as sieve_dub_video

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('youtube-shorts-server')

app = Flask(__name__)
CORS(app)

# Dictionary to store processing jobs
processing_jobs = {}

# External processing server URL
EXTERNAL_API_URL = "https://1c16-34-139-136-172.ngrok-free.app/api/process-youtube"

# Define OAuth 2.0 scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "./client_secrets.json"
CREDENTIALS_FILE = "youtube_credentials.json"  # Stores tokens after first auth

# Valid privacy statuses
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service():
    """Authenticate with YouTube and return a service object"""
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    flow.redirect_uri = 'http://localhost:5050/oauth2callback'
    creds = flow.run_local_server(port=5050)
    return build('youtube', 'v3', credentials=creds)


# @app.route('/api/dub-video', methods=['POST'])
# def dub_video_handler():
#     """Dub a video segment into a specified language"""
#     try:
#         data = request.json

#         segment_id = data.get('segmentId')
#         job_id = data.get('jobId')
#         language_code = data.get('language')

#         logger.info(f"DUBBING REQUEST - Language: {language_code}")

#         # Find video path from job
#         if job_id in processing_jobs:
#             job_info = processing_jobs.get(job_id, {})
#             for video in job_info.get('videos', []):
#                 if video.get('id') == segment_id:
#                     video_url = video.get('url')
#                     if video_url:
#                         video_path = os.path.join(
#                             os.getcwd(), video_url.lstrip('/'))
#                         logger.info(
#                             f"DUBBING REQUEST - Video path: {video_path}")
#                     break

#         return jsonify({"success": True})

#     except Exception as e:
#         logger.exception(f"Error logging dubbing request: {e}")
#         return jsonify({"error": str(e)}), 500
@app.route('/api/dub-video', methods=['POST'])
def dub_video_handler():
    """Dub a video segment into a specified language"""
    try:
        data = request.json

        segment_id = data.get('segmentId')
        job_id = data.get('jobId')
        language_code = data.get('language')

        logger.info(f"DUBBING REQUEST - Language: {language_code}")

        video_path = None

        # Find video path from job
        if job_id in processing_jobs:
            job_info = processing_jobs.get(job_id, {})
            for video in job_info.get('videos', []):
                if video.get('id') == segment_id:
                    video_url = video.get('url')
                    if video_url:
                        video_path = os.path.join(
                            os.getcwd(), video_url.lstrip('/'))
                        logger.info(
                            f"DUBBING REQUEST - Video path: {video_path}")
                break

        # If video path not found through job info, try the direct path in shorts_output
        if not video_path:
            video_path = os.path.join(
                os.getcwd(), f"shorts_output/{segment_id}.mp4")
            if os.path.exists(video_path):
                logger.info(
                    f"DUBBING REQUEST - Video found at direct path: {video_path}")
            else:
                return jsonify({"error": "Video file not found"}), 404

        # Create sieve File object for the source video
        source_file = sieve.File(path=video_path)

        # Use language_code directly from the request
        target_language = language_code.lower()

        # Set dubbing parameters
        translation_engine = "gpt4"
        voice_engine = "elevenlabs (voice cloning)"
        transcription_engine = "whisper-zero"
        output_mode = "voice-dubbing"
        edit_segments = list()
        return_transcript = False
        preserve_background_audio = True
        safewords = ""
        translation_dictionary = ""
        start_time = 0
        end_time = -1
        enable_lipsyncing = False
        lipsync_backend = "sievesync-1.1"
        lipsync_enhance = "default"

        # Initialize the dubbing function and start the job
        dubbing = sieve.function.get("sieve/dubbing")
        output = dubbing.push(
            source_file,
            target_language,
            translation_engine,
            voice_engine,
            transcription_engine,
            output_mode,
            edit_segments,
            return_transcript,
            preserve_background_audio,
            safewords,
            translation_dictionary,
            start_time,
            end_time,
            enable_lipsyncing,
            lipsync_backend,
            lipsync_enhance
        )

        logger.info(
            f"DUBBING JOB STARTED - Segment: {segment_id}, Language: {target_language}")

        # Process the output and save the dubbed video
        result_paths = []
        for output_object in output.result():
            # Get the temporary file path of the dubbed video
            tmp_path = output_object.path
            logger.info(f"Dubbed video downloaded to: {tmp_path}")

            # Define the destination folder and filename
            dest_folder = os.path.join(os.getcwd(), "dubbed")
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
                logger.info(f"Created directory: {dest_folder}")

            # Create a unique filename with segment ID and language
            dest_filename = f"{segment_id}_{language_code}_dubbed.mp4"
            dest_path = os.path.join(dest_folder, dest_filename)

            # Move the file from the temporary location to the destination
            shutil.move(tmp_path, dest_path)
            logger.info(f"Dubbed video moved to: {dest_path}")

            # Store the relative path for the response
            result_paths.append(f"/dubbed/{dest_filename}")

        return jsonify({
            "success": True,
            "message": "Video successfully dubbed",
            "dubbed_videos": result_paths
        })

    except Exception as e:
        logger.exception(f"Error in dubbing process: {e}")
        return jsonify({"error": str(e)}), 500


def process_dubbing(video_path, target_language, output_dir, dubbing_id, job_id, segment_id):
    """Process video dubbing using Sieve API"""
    try:
        logger.info(
            f"Starting dubbing job for {video_path} to {target_language}")

        # Call the dub_video function from sieve_dubbing.py
        dubbing_result = sieve_dub_video(
            video_path, target_language, job_id, segment_id)

        if dubbing_result['status'] == 'completed':
            logger.info(f"Dubbing completed: {dubbing_result['output_path']}")
            url_path = dubbing_result['url']

            # Update the job info with the dubbed video URL
            job_info = processing_jobs.get(job_id, {})
            for video in job_info.get('videos', []):
                if video.get('id') == segment_id:
                    if 'dubbing' not in video:
                        video['dubbing'] = {}
                    video['dubbing'][target_language] = {
                        'status': 'completed',
                        'id': dubbing_id,
                        'url': url_path
                    }
                    break

            return url_path
        else:
            raise Exception(dubbing_result['message'])

    except Exception as e:
        logger.exception(f"Error in dubbing process: {e}")
        # Update job info to indicate dubbing failed
        job_info = processing_jobs.get(job_id, {})
        for video in job_info.get('videos', []):
            if video.get('id') == segment_id:
                if 'dubbing' not in video:
                    video['dubbing'] = {}
                video['dubbing'][target_language] = {
                    'status': 'failed',
                    'id': dubbing_id,
                    'error': str(e)
                }
                break
        return None


def upload_video(service, video_path, title, description, category, privacy_status):
    """Upload a video to YouTube"""
    media = MediaFileUpload(video_path, mimetype='video/mp4')
    request = service.videos().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': title,
                'description': description,
                'tags': [],
                'categoryId': category,
                'defaultLanguage': 'en'
            },
            'status': {
                'privacyStatus': privacy_status
            }
        },
        media_body=media
    )
    response = request.execute()
    return response


def get_job_status(job_id):
    """Get the status of a processing job"""
    if job_id not in processing_jobs:
        return {"status": "not_found", "message": "Job not found"}
    return processing_jobs[job_id]


@app.route('/generate-short', methods=['POST'])
def generate_short():
    """Generate short video segments from a YouTube link"""
    try:
        data = request.json
        logger.info(f"Generate short request: {data}")

        if not data or 'youtubeUrl' not in data:
            return jsonify({"error": "Missing youtubeUrl parameter"}), 400

        youtube_url = data.get('youtubeUrl')
        # Default to 9:16 for shorts
        aspect_ratio = data.get('aspectRatio', '9:16')
        words_per_subtitle = data.get('wordsPerSubtitle', 4)
        font_size = data.get('fontSize', 12)

        job_id = f"job-{int(time.time())}"
        logger.info(f"Creating job: {job_id} for video: {youtube_url}")

        # Create a new job entry
        processing_jobs[job_id] = {
            "id": job_id,
            "status": "processing",
            "message": "Starting to process the video...",
            "videos": []
        }

        # Start a background thread to call the external API
        def process_with_external_api():
            try:
                # Call the external API
                api_data = {
                    "youtubeUrl": youtube_url,
                    "aspectRatio": aspect_ratio,
                    "wordsPerSubtitle": words_per_subtitle,
                    "fontSize": font_size
                }

                processing_jobs[job_id]["message"] = "Sending request to processing server..."

                # Make the API request
                response = requests.post(
                    EXTERNAL_API_URL, json=api_data, stream=True)

                if response.status_code != 200:
                    processing_jobs[job_id]["status"] = "error"
                    processing_jobs[job_id]["message"] = f"External API error: {response.text}"
                    return

                processing_jobs[job_id]["message"] = "Processing video on external server..."

                # Get the boundary from the Content-Type header
                content_type = response.headers.get("Content-Type")
                if not content_type or "boundary=" not in content_type:
                    processing_jobs[job_id]["status"] = "error"
                    processing_jobs[job_id]["message"] = "Invalid response from external API"
                    return

                # Create output directory if it doesn't exist
                os.makedirs("shorts_output", exist_ok=True)

                # Buffer to collect the response data
                buffer = b""

                videos = []
                segment_counter = 0

                # Process the streaming response
                for chunk in response.iter_content(chunk_size=4096):
                    buffer += chunk

                    # Extract parts between boundaries
                    boundary = content_type.split("boundary=")[-1].strip()
                    boundary_bytes = (f"--{boundary}").encode()

                    while True:
                        boundary_index = buffer.find(boundary_bytes)
                        if boundary_index == -1:
                            break

                        # Extract part before boundary
                        part = buffer[:boundary_index]
                        if part.strip():
                            # Find header/content separator
                            header_end = part.find(b"\r\n\r\n")
                            if header_end != -1:
                                headers_text = part[:header_end].decode(
                                    "utf-8", errors="replace")
                                content = part[header_end + 4:]

                                # Parse headers
                                headers = {}
                                for line in headers_text.split("\r\n"):
                                    if ":" in line:
                                        key, value = line.split(":", 1)
                                        headers[key.strip()] = value.strip()

                                # Get content type and filename
                                part_content_type = headers.get(
                                    "Content-Type", "")
                                disposition = headers.get(
                                    "Content-Disposition", "")
                                filename = None
                                if "filename=" in disposition:
                                    filename = disposition.split(
                                        "filename=")[-1].strip('"')

                                # Process based on content type
                                if "video" in part_content_type:
                                    segment_counter += 1
                                    segment_id = f"short-{uuid.uuid4().hex[:3]}"
                                    video_filename = f"{segment_id}.mp4"
                                    filepath = os.path.join(
                                        "shorts_output", video_filename)

                                    with open(filepath, "wb") as f:
                                        f.write(content)

                                    # Create a video entry and add to our job
                                    video_info = {
                                        "id": segment_id,
                                        "url": f"/shorts_output/{video_filename}",
                                        "title": f"Short {segment_counter}",
                                        "description": f"Generated from {youtube_url}"
                                    }
                                    videos.append(video_info)

                                    # Update job info immediately for each video
                                    # Don't wait for all videos to complete
                                    processing_jobs[job_id]["videos"] = videos.copy(
                                    )
                                    processing_jobs[job_id][
                                        "message"] = f"Generated {len(videos)} shorts so far..."
                                    # Mark the job as in_progress to indicate videos are available
                                    # but more might still be coming
                                    processing_jobs[job_id]["status"] = "in_progress"

                                elif "image/jpeg" in part_content_type:
                                    # Handle thumbnail for the previous video (optional)
                                    if videos:
                                        thumbnail_id = videos[-1]["id"]
                                        thumb_filename = f"{thumbnail_id}_thumbnail.jpg"
                                        thumb_path = os.path.join(
                                            "shorts_output", thumb_filename)

                                        with open(thumb_path, "wb") as f:
                                            f.write(content)

                                        videos[-1]["thumbnailUrl"] = f"/shorts_output/{thumb_filename}"
                                        # Update job info immediately with the thumbnail
                                        processing_jobs[job_id]["videos"] = videos.copy(
                                        )

                        # Remove processed part and boundary from buffer
                        buffer = buffer[boundary_index + len(boundary_bytes):]

                # Update job status
                if videos:
                    processing_jobs[job_id]["status"] = "completed"
                    processing_jobs[job_id]["message"] = "All shorts created successfully!"
                    processing_jobs[job_id]["videos"] = videos
                else:
                    processing_jobs[job_id]["status"] = "error"
                    processing_jobs[job_id]["message"] = "No videos received from external API"

            except Exception as e:
                logger.exception(
                    f"Error processing video with external API: {e}")
                processing_jobs[job_id]["status"] = "error"
                processing_jobs[job_id]["message"] = f"Processing error: {str(e)}"

        # Start the processing in a background thread
        threading.Thread(target=process_with_external_api).start()

        return jsonify({
            "success": True,
            "jobId": job_id
        })

    except Exception as e:
        logger.exception(f"Error generating short: {e}")
        return jsonify({"error": f"Failed to generate short: {str(e)}"}), 500


@app.route('/status/<job_id>', methods=['GET'])
def job_status(job_id):
    """Get the status of a processing job"""
    status = get_job_status(job_id)
    return jsonify(status)


@app.route('/shorts_output/<filename>', methods=['GET'])
def serve_output_file(filename):
    """Serve files from the shorts_output directory"""
    return send_from_directory('shorts_output', filename)

# Cleanup route to free up disk space (optional)


@app.route('/cleanup/<job_id>', methods=['POST'])
def cleanup_job(job_id):
    """Clean up files associated with a job"""
    try:
        if job_id not in processing_jobs:
            return jsonify({"error": "Job not found"}), 404

        # Get videos associated with this job
        videos = processing_jobs[job_id].get("videos", [])

        # Delete video files
        for video in videos:
            file_path = video.get("url", "").replace("/shorts_output/", "")
            if file_path:
                full_path = os.path.join("shorts_output", file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)

            # Delete thumbnail if exists
            thumbnail_path = video.get(
                "thumbnailUrl", "").replace("/shorts_output/", "")
            if thumbnail_path:
                full_thumb_path = os.path.join("shorts_output", thumbnail_path)
                if os.path.exists(full_thumb_path):
                    os.remove(full_thumb_path)

        # Update job status
        processing_jobs[job_id]["status"] = "cleaned"
        processing_jobs[job_id]["message"] = "Job files cleaned up"

        return jsonify({"success": True, "message": "Job cleaned up successfully"})

    except Exception as e:
        logger.exception(f"Error cleaning up job: {e}")
        return jsonify({"error": f"Failed to clean up job: {str(e)}"}), 500


@app.route('/api/youtube-upload', methods=['POST'])
def youtube_upload_handler():
    """Upload a video segment to YouTube"""
    try:
        data = request.json
        logger.info(f"YouTube upload request: {data}")

        # Validate required parameters
        required_params = ['segmentId', 'jobId', 'title', 'description']
        for param in required_params:
            if param not in data:
                return jsonify({"error": f"Missing {param} parameter"}), 400

        segment_id = data.get('segmentId')
        job_id = data.get('jobId')
        title = data.get('title')
        description = data.get('description')
        tags = data.get('tags', [])
        category = data.get('categoryId', '22')  # 22 is 'People & Blogs'
        privacy_status = data.get('privacyStatus', 'public')

        # Check if job exists
        if job_id not in processing_jobs:
            return jsonify({"error": "Job not found"}), 404

        # Find video path from job
        job_info = processing_jobs[job_id]
        video_path = None
        for video in job_info.get('videos', []):
            if video.get('id') == segment_id:
                video_url = video.get('url')
                if video_url:
                    video_path = os.path.join(
                        os.getcwd(), video_url.lstrip('/'))
                break

        if not video_path or not os.path.exists(video_path):
            return jsonify({"error": "Video file not found"}), 404

        # Upload to YouTube using the provided script
        logger.info(
            f"Uploading video {video_path} to YouTube with title: {title}")

        # Authenticate with YouTube
        youtube = get_authenticated_service()

        # Upload the video
        response = upload_video(youtube, video_path,
                                title, description, category, privacy_status)

        if response and response.get('id'):
            video_id = response.get('id')
            video_url = f"https://youtu.be/{video_id}"

            # Update job info with YouTube URL
            for video in job_info.get('videos', []):
                if video.get('id') == segment_id:
                    video['youtubeUrl'] = video_url
                    video['youtubeId'] = video_id
                    break

        return jsonify({
            "success": True,
            "youtubeUrl": video_url,
            "youtubeId": video_id
        })
    except Exception as e:
        logger.exception(f"Error uploading to YouTube: {e}")
        return jsonify({"error": f"Failed to upload: {str(e)}"}), 500


if __name__ == "__main__":
    # Make sure the output directory exists
    os.makedirs("shorts_output", exist_ok=True)
    os.makedirs("dubbed", exist_ok=True)

    # Run the server
    logger.info("Starting Flask server on port 5050")
    app.run(debug=True, host='0.0.0.0', port=5050)
