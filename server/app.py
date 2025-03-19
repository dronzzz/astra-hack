from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import logging
import datetime
from routes.upload import upload_bp
from processing import get_job_status, processing_jobs
import requests
import tempfile
import json
import subprocess
import shutil
import uuid
import glob
import re
from textblob import TextBlob
from pytrends.request import TrendReq

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('youtube-shorts-server')

app = Flask(__name__)
CORS(app)

# Register upload blueprint
app.register_blueprint(upload_bp)

# Add this configuration
YOUTUBE_API_KEY = 'AIzaSyCipVUnLSuT8OiUUrKzPbrTB1H61M_YTKc'  # You might want to store this securely

# Serve static files from shorts_output
@app.route('/shorts_output/<path:filename>')
def serve_output_file(filename):
    """Serve files directly from the shorts_output directory"""
    directory = os.path.abspath("shorts_output")
    file_path = os.path.join(directory, filename)
    
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
    logger.info(f"Serving file: {file_path}, size: {os.path.getsize(file_path)} bytes")
    
    # Determine content type based on file extension
    file_extension = os.path.splitext(filename)[1].lower()
    
    if file_extension == '.mp4':
        mime_type = 'video/mp4'
    elif file_extension in ['.jpg', '.jpeg']:
        mime_type = 'image/jpeg'
    else:
        mime_type = 'application/octet-stream'
    
    # Serve the file
    return send_file(file_path, mimetype=mime_type)

# Job status endpoint
@app.route('/status/<job_id>', methods=['GET'])
def job_status(job_id):
    """Get the status of a processing job"""
    status = get_job_status(job_id)
    return jsonify(status)

# API test endpoint
@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple endpoint to verify the API is running"""
    logger.info("Test API endpoint called")
    return jsonify({
        "status": "success", 
        "message": "API is running on port 5050",
        "timestamp": str(datetime.datetime.now())
    })

# Add a new endpoint for dubbing videos
@app.route('/api/dub-segment', methods=['POST'])
def dub_segment():
    """Dub a video segment with a new language"""
    try:
        # Log the raw request data for debugging
        logger.info(f"Received dub request: {request.data}")
        
        # Parse the request data
        data = request.json
        if not data:
            logger.error("No JSON data in request")
            return jsonify({"error": "No data provided"}), 400
            
        logger.info(f"Parsed request data: {data}")
        
        # Check for required parameters
        segment_id = data.get('segmentId')
        job_id = data.get('jobId')
        language = data.get('language')
        
        if not segment_id or not job_id or not language:
            missing = []
            if not segment_id: missing.append("segmentId")
            if not job_id: missing.append("jobId")
            if not language: missing.append("language")
            error_msg = f"Missing required parameters: {', '.join(missing)}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 400
            
        logger.info(f"Processing dub request for segment {segment_id}, job {job_id}, language {language}")
        
        # Get the job status
        job_status = processing_jobs.get(job_id)
        logger.info(f"Job status found: {job_status is not None}")
        
        # If job status is not in memory, try to reconstruct from files
        if not job_status:
            logger.warning(f"Job {job_id} not found in memory, attempting to reconstruct")
            
            # Create a basic job status structure
            job_status = {
                "id": job_id,
                "status": "completed",
                "progress": 100,
                "videos": []
            }
            
            # Check for video files in the shorts_output directory
            if os.path.exists("shorts_output"):
                video_files = [f for f in os.listdir("shorts_output") if f.startswith(job_id) and f.endswith(".mp4")]
                logger.info(f"Found {len(video_files)} video files for job {job_id}")
                
                # Log all found files for debugging
                logger.info(f"Found video files: {video_files}")
                
                for video_file in video_files:
                    # Try to extract the segment number from the filename
                    try:
                        # Extract number from pattern like "jobid_short_1.mp4"
                        segment_num = video_file.split('_')[-1].split('.')[0]
                        segment_id_from_file = f"short-{segment_num}"
                        
                        video_info = {
                            "id": segment_id_from_file,
                            "title": f"Short {segment_num}",
                            "url": f"/shorts_output/{video_file}",
                            "thumbnailUrl": f"/shorts_output/{video_file.replace('.mp4', '.jpg')}"
                        }
                        job_status["videos"].append(video_info)
                        logger.info(f"Added reconstructed segment: {segment_id_from_file}")
                    except Exception as e:
                        logger.error(f"Error parsing video filename {video_file}: {e}")
                
                # Also check if there's exactly the segment ID requested
                for video_file in video_files:
                    if segment_id in video_file:
                        logger.info(f"Found exact match for segment ID in filename: {video_file}")
                        # Add this as a special case
                        video_info = {
                            "id": segment_id,
                            "title": f"Short {segment_id.replace('short-', '')}",
                            "url": f"/shorts_output/{video_file}",
                            "thumbnailUrl": f"/shorts_output/{video_file.replace('.mp4', '.jpg')}"
                        }
                        # Check if this segment is already in the videos list
                        if not any(v.get("id") == segment_id for v in job_status["videos"]):
                            job_status["videos"].append(video_info)
                            logger.info(f"Added exact match segment: {segment_id}")
        
        # Display all available segments in the job for debugging
        if job_status and "videos" in job_status:
            available_segments = [v.get("id") for v in job_status.get("videos", [])]
            logger.info(f"Available segments in job: {available_segments}")
        
        # Find the segment data
        segment = None
        for video in job_status.get("videos", []):
            if video.get("id") == segment_id:
                segment = video
                break
                
        if not segment:
            logger.error(f"Segment {segment_id} not found in job {job_id}")
            
            # Look for any segment as fallback
            if job_status and job_status.get("videos"):
                fallback_segment = job_status["videos"][0]
                logger.info(f"Using fallback segment: {fallback_segment.get('id')}")
                segment = fallback_segment
            else:
                # Look directly in the shorts_output directory
                shorts_dir = "shorts_output"
                if os.path.exists(shorts_dir):
                    # Look for MP4 files that match the job ID
                    matching_files = [f for f in os.listdir(shorts_dir) 
                                     if f.startswith(job_id) and f.endswith('.mp4')]
                    
                    if matching_files:
                        video_file = matching_files[0]
                        logger.info(f"Found video file in directory: {video_file}")
                        
                        # Create a segment from this file
                        segment = {
                            "id": segment_id,  # Use the requested segment ID
                            "title": f"Short",
                            "url": f"/shorts_output/{video_file}",
                            "thumbnailUrl": f"/shorts_output/{video_file.replace('.mp4', '.jpg')}"
                        }
                
                if not segment:
                    return jsonify({"error": f"Segment {segment_id} not found in job {job_id}"}), 404
        
        # Get the video file path
        video_basename = os.path.basename(segment.get("url", "").replace("/shorts_output/", ""))
        video_path = os.path.join("shorts_output", video_basename)
        
        logger.info(f"Video path: {video_path}")
        
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return jsonify({"error": f"Video file not found: {video_path}"}), 404
        
        # Create a unique temporary file for each request to avoid file lock issues
        temp_audio_id = str(uuid.uuid4())
        audio_temp_path = os.path.join(tempfile.gettempdir(), f"dubbed_audio_{temp_audio_id}.mp3")
        
        logger.info(f"Using temporary audio file: {audio_temp_path}")
        
        # Extract audio from the video using ffmpeg
        logger.info(f"Extracting audio from video: {video_path}")
        
        extract_cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-q:a', '0',
            '-map', 'a',
            audio_temp_path
        ]
        
        # Log the command for debugging
        logger.info(f"Running command: {' '.join(extract_cmd)}")
        
        try:
            result = subprocess.run(extract_cmd, check=True, capture_output=True, text=True)
            logger.info(f"FFmpeg output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            return jsonify({"error": f"FFmpeg error: {e.stderr}"}), 500
        
        # Get the transcript/text content for this segment
        logger.info("Looking for segment text content")
        text_content = None

        # First try to find the subtitle file for this segment
        try:
            # Look for SRT files related to this segment
            video_name_without_ext = os.path.splitext(video_basename)[0]
            
            # Create a permanent subtitle directory if it doesn't exist
            subtitle_storage_dir = os.path.join("shorts_output", "subtitles")
            os.makedirs(subtitle_storage_dir, exist_ok=True)
            
            # Check for a preserved subtitle file first
            preserved_subtitle_path = os.path.join(subtitle_storage_dir, f"{video_name_without_ext}.txt")
            
            # If we have a preserved text file, use that
            if os.path.exists(preserved_subtitle_path):
                logger.info(f"Found preserved subtitle text: {preserved_subtitle_path}")
                with open(preserved_subtitle_path, 'r', encoding='utf-8') as f:
                    text_content = f.read().strip()
                logger.info(f"Using preserved text content: {text_content[:100]}...")
            else:
                # Otherwise, check all the usual locations for SRT files
                potential_subtitle_paths = [
                    # Check in shorts_output directory
                    os.path.join("shorts_output", f"{video_name_without_ext}.srt"),
                    # Check in temp directory that might have been used during processing
                    os.path.join(f"temp_{video_name_without_ext}", "subtitles.srt"),
                    # Check for any temp directory with this segment
                    *[os.path.join(d, "subtitles.srt") for d in glob.glob(f"temp_*{job_id}*_short_{segment_id.split('-')[1]}*")],
                    # Check in any job-specific directories
                    *[os.path.join(d, "subtitles.srt") for d in glob.glob(f"temp_{job_id}*")]
                ]
                
                logger.info(f"Checking potential subtitle paths: {potential_subtitle_paths}")
                
                subtitle_file = None
                for path in potential_subtitle_paths:
                    if os.path.exists(path):
                        subtitle_file = path
                        logger.info(f"Found subtitle file: {subtitle_file}")
                        break
                
                if subtitle_file:
                    # Read the subtitle file and extract just the text without timestamps
                    subtitle_text = []
                    with open(subtitle_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    # SRT format: number, timestamps, text, blank line, repeat
                    i = 0
                    while i < len(lines):
                        line = lines[i].strip()
                        if line.isdigit():  # This is a subtitle number
                            i += 1  # Skip the timestamp line
                            i += 1
                            # Collect all text lines until we hit a blank line
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
                        logger.info(f"Extracted text from subtitle: {text_content[:100]}...")
                        
                        # Save this text for future use in case the SRT file gets deleted
                        with open(preserved_subtitle_path, 'w', encoding='utf-8') as f:
                            f.write(text_content)
                        logger.info(f"Preserved subtitle text to: {preserved_subtitle_path}")
            
            # If we still don't have text content, check for 'text' or 'reason' field in segment data
            if not text_content:
                logger.warning("No subtitle file found. Looking for text in segment data.")
                if 'text' in segment:
                    text_content = segment['text']
                    logger.info(f"Using text from segment data: {text_content[:100]}...")
                elif 'reason' in segment:
                    text_content = segment['reason']
                    logger.info(f"Using reason as fallback text: {text_content[:100]}...")
        
        except Exception as e:
            logger.exception(f"Error extracting subtitle text: {e}")
            # Continue with the process; we'll use a fallback text if needed
        
        # If we still don't have text content, use a fallback
        if not text_content:
            # Get segment number from ID for a more customized message
            try:
                segment_num = segment_id.split('-')[1]
                text_content = f"This is segment {segment_num} of the video. This is a fallback text since no subtitle was found."
            except:
                text_content = "This is a generated video segment. This is a fallback text since no subtitle was found."
            
            logger.warning(f"Using fallback text content: {text_content}")
        
        # Now call the dubbing service with the CORRECT FORMAT
        logger.info(f"Calling dubbing service for language: {language}")
        
        multilingual_url = "https://codeastra.originzero.in/generate_dubbed_audio"
        
        # FIXED: Use the simple format that actually works
        form_data = {
            "text": text_content
        }
        
        # Make sure the audio file exists
        if not os.path.exists(audio_temp_path):
            logger.error(f"Audio file not found: {audio_temp_path}")
            return jsonify({"error": "Audio file not found"}), 500
        
        # Add detailed logging about what we're sending
        audio_size = os.path.getsize(audio_temp_path)
        logger.info(f"===== DUBBING REQUEST DETAILS =====")
        logger.info(f"URL: {multilingual_url}")
        logger.info(f"Audio file: {audio_temp_path} ({audio_size} bytes)")
        logger.info(f"Text content length: {len(text_content)} characters")
        logger.info(f"Text content: {text_content[:200]}..." if len(text_content) > 200 else text_content)
        logger.info(f"Form data: {form_data}")
        logger.info(f"Audio file exists: {os.path.exists(audio_temp_path)}")
        logger.info(f"================================")
        
        try:
            # Use the exact same structure as your working example
            files = {"voice_sample": open(audio_temp_path, "rb")}
            
            # Send request to external dubbing service
            logger.info(f"Sending POST request to {multilingual_url}")
            response = requests.post(multilingual_url, data=form_data, files=files, timeout=120)
            logger.info(f"Dubbing service response status: {response.status_code}")
            
            # Try to log response content for debugging
            try:
                response_content_preview = response.content[:200]
                logger.info(f"Response preview: {response_content_preview}")
                
                # If there's an error, try to parse and log it in detail
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        logger.error(f"Full error response: {error_data}")
                    except:
                        logger.error(f"Raw error response: {response.text}")
            except:
                pass
                
        except requests.RequestException as e:
            logger.error(f"Error calling dubbing service: {e}")
            return jsonify({"error": f"Error calling dubbing service: {e}"}), 500
        finally:
            # Make sure to close the file handle
            if 'files' in locals() and 'voice_sample' in files:
                files['voice_sample'].close()
            
            # Then try to delete the temporary files
            try:
                if os.path.exists(audio_temp_path):
                    os.remove(audio_temp_path)
                    logger.info(f"Deleted temporary audio file: {audio_temp_path}")
            except Exception as e:
                logger.error(f"Error deleting temporary files: {e}")
        
        if not response or response.status_code != 200:
            error_msg = "Unknown error"
            try:
                error_data = response.json()
                error_msg = error_data.get("error", "Unknown error")
            except:
                if response:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                
            logger.error(f"Dubbing service error: {error_msg}")
            return jsonify({"error": f"Dubbing service error: {error_msg}"}), 500
        
        # Create unique paths for the dubbed files
        dubbed_id = str(uuid.uuid4())[:8]
        dubbed_path = os.path.join("shorts_output", f"{video_basename.split('.')[0]}_{language}_{dubbed_id}.wav")
        
        # Save the dubbed audio
        with open(dubbed_path, "wb") as f:
            f.write(response.content)
        
        logger.info(f"Saved dubbed audio to: {dubbed_path}")
        
        # Create a new video with the dubbed audio
        dubbed_video_path = os.path.join("shorts_output", f"{video_basename.split('.')[0]}_{language}_{dubbed_id}.mp4")
        
        dubbed_cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', dubbed_path,
            '-c:v', 'copy',
            '-c:a', 'aac', 
            '-map', '0:v', 
            '-map', '1:a', 
            '-shortest',
            dubbed_video_path
        ]
        
        logger.info(f"Running command: {' '.join(dubbed_cmd)}")
        
        try:
            subprocess.run(dubbed_cmd, check=True, capture_output=True, text=True)
            logger.info(f"Created dubbed video: {dubbed_video_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error creating dubbed video: {e.stderr}")
            return jsonify({"error": f"Error creating dubbed video: {e.stderr}"}), 500
        
        # Generate thumbnail for the dubbed video (reuse the original thumbnail)
        dubbed_thumbnail_path = os.path.join("shorts_output", f"{video_basename.split('.')[0]}_{language}_{dubbed_id}.jpg")
        original_thumbnail = os.path.join("shorts_output", f"{video_basename.split('.')[0]}.jpg")
        
        if os.path.exists(original_thumbnail):
            shutil.copy(original_thumbnail, dubbed_thumbnail_path)
            logger.info(f"Copied thumbnail to: {dubbed_thumbnail_path}")
        
        # Add dubbed video info to the job status
        dubbed_video_info = segment.copy()
        dubbed_video_info["id"] = f"{segment_id}_{language}"
        dubbed_video_info["title"] = f"{segment.get('title', 'Short')} ({language})"
        dubbed_video_info["url"] = f"/shorts_output/{os.path.basename(dubbed_video_path)}"
        dubbed_video_info["thumbnailUrl"] = f"/shorts_output/{os.path.basename(dubbed_thumbnail_path)}"
        dubbed_video_info["isTranslated"] = True
        dubbed_video_info["language"] = language
        
        # Add to job videos list
        job_status["videos"].append(dubbed_video_info)
        logger.info(f"Added dubbed video to job: {dubbed_video_info['id']}")
        
        return jsonify({
            "success": True,
            "message": f"Successfully dubbed video to {language}",
            "dubbed_video": dubbed_video_info
        })
        
    except Exception as e:
        logger.exception(f"Error processing dub request: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add this route to your app.py
@app.route('/api/analyze-trend', methods=['POST'])
def analyze_video_trend():
    try:
        data = request.json
        if not data or 'youtubeUrl' not in data:
            return jsonify({"error": "No YouTube URL provided"}), 400
            
        youtube_url = data['youtubeUrl']
        logger.info(f"Analyzing trend for YouTube URL: {youtube_url}")
        
        # Extract video ID
        video_id = extract_video_id(youtube_url)
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL format"}), 400
        
        # Fetch video details
        title, description, thumbnail_url = fetch_video_details(video_id)
        if not title:
            return jsonify({"error": "Could not fetch video details. Check API key or URL."}), 404
        
        # Analyze trends
        trend_analysis = analyze_trend(title, description)
        
        # Return complete analysis
        return jsonify({
            "success": True,
            "videoId": video_id,
            "title": title,
            "description": description[:300] + "..." if len(description) > 300 else description,
            "thumbnailUrl": thumbnail_url,
            "trendAnalysis": trend_analysis
        })
        
    except Exception as e:
        logger.exception(f"Error analyzing video trend: {str(e)}")
        return jsonify({"error": f"Error analyzing trend: {str(e)}"}), 500

# Helper functions for trend analysis
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/|/v/|/e/|embed/|shorts/|watch\?v=)([\w-]{11})", url)
    return match.group(1) if match else None

def fetch_video_details(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if 'items' in data and data['items']:
        snippet = data['items'][0]['snippet']
        return snippet['title'], snippet['description'], snippet.get('thumbnails', {}).get('high', {}).get('url')
    return None, None, None

def get_trending_keywords():
    pytrends = TrendReq()
    try:
        trending_data = pytrends.today_searches(pn='US')
        return trending_data.tolist()[:10]  # Top 10 trending keywords
    except Exception as e:
        logger.error(f"Error fetching trending keywords: {e}")
        return ["viral", "breaking news", "new release", "2025"]  # Default fallback keywords

def analyze_trend(title, description):
    text = f"{title} {description}".lower()
    blob = TextBlob(text)

    # Dynamic trending keywords
    trending_keywords = get_trending_keywords()
    keyword_score = sum(1 for word in trending_keywords if word.lower() in text)

    # Sentiment Analysis as a factor
    sentiment_score = blob.sentiment.polarity  # Ranges from -1 to 1

    # Trend Rating Calculation
    trend_score = (keyword_score * 2) + (sentiment_score * 10)
    rating = min(100, max(0, int(trend_score * 10)))

    if rating > 70:
        trend_status = "🔥 Highly Trendy"
        reason = "Contains multiple trending keywords and positive sentiment."
    elif rating > 40:
        trend_status = "📈 Moderately Trendy" 
        reason = "Might have limited trending keywords or neutral sentiment."
    else:
        trend_status = "📉 Not Trendy"
        reason = "Few or no trending keywords detected, or sentiment appears less engaging."
        
    return {
        "rating": rating,
        "status": trend_status,
        "reason": reason,
        "keywords": trending_keywords,
        "keyword_matches": keyword_score,
        "sentiment_score": sentiment_score
    }

# Add a redirect route to the trend analyzer
@app.route('/analyze-trend', methods=['GET'])
def redirect_to_trend_analyzer():
    """Redirect to the trend analyzer page in the frontend"""
    # Option 1: If your Flask app serves the frontend directly
    return send_from_directory('static', 'index.html')
    
    # Option 2: If using separate frontend/backend, redirect to frontend URL
    # return redirect('http://localhost:3000/analyze-trend')

if __name__ == "__main__":
    # Make sure the output directory exists
    os.makedirs("shorts_output", exist_ok=True)
    
    # Run the server
    logger.info("Starting Flask server on port 5050")
    app.run(debug=True, host='0.0.0.0', port=5050)
