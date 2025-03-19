import os
import uuid
import json
import tempfile
import subprocess
import requests
import shutil
import logging
import argparse
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('dubbing-test')

def setup_test_directories():
    """Create directories to store test files"""
    permanent_dirs = ['test_files', 'test_files/originals', 'test_files/dubbed']
    for dir_path in permanent_dirs:
        os.makedirs(dir_path, exist_ok=True)
    return permanent_dirs[0]

def extract_audio(video_path, output_audio_path):
    """Extract audio from a video file"""
    logger.info(f"Extracting audio from video: {video_path}")
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-q:a', '0',
        '-map', 'a',
        output_audio_path
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Successfully extracted audio to {output_audio_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr}")
        return False

def dub_audio(audio_path, text_content, language, output_path):
    """Send request to the dubbing service"""
    multilingual_url = "https://codeastra.originzero.in/generate_dubbed_audio"
    
    messages = [{
        "role": "user", 
        "content": text_content, 
        "language": language
    }]
    
    form_data = {
        "messages": json.dumps(messages)
    }
    
    with open(audio_path, "rb") as audio_file:
        files = {
            "voice_sample": audio_file
        }
        
        logger.info(f"Sending dubbing request for language {language}")
        logger.info(f"Text for translation: {text_content[:100]}...")
        
        try:
            response = requests.post(multilingual_url, data=form_data, files=files, timeout=120)
            logger.info(f"Dubbing service response status: {response.status_code}")
            
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Successfully saved dubbed audio to {output_path}")
                return True
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", "Unknown error")
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                
                logger.error(f"Dubbing service error: {error_msg}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error calling dubbing service: {e}")
            return False

def create_dubbed_video(video_path, dubbed_audio_path, output_video_path):
    """Combine original video with dubbed audio"""
    logger.info(f"Creating dubbed video from {video_path} and {dubbed_audio_path}")
    
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', dubbed_audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac', 
        '-map', '0:v', 
        '-map', '1:a', 
        '-shortest',
        output_video_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Successfully created dubbed video: {output_video_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error creating dubbed video: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test multilingual dubbing')
    parser.add_argument('--video', help='Path to the video file to test with', required=False)
    parser.add_argument('--language', default='JP', help='Language code to test (EN, JP, KR, ZH, FR, ES)')
    parser.add_argument('--text', help='Text content to translate', 
                        default="This is a test of the multilingual dubbing service. We are converting this speech to another language while maintaining the original voice characteristics.")
    parser.add_argument('--use-existing', action='store_true', help='Use an existing video from temp directories')
    
    args = parser.parse_args()
    
    # Setup test directories
    test_dir = setup_test_directories()
    
    # Create unique name for test outputs
    unique_id = str(uuid.uuid4())[:8]
    
    # Get video path (either user-provided or find one from temp directories)
    video_path = args.video
    if not video_path or not os.path.exists(video_path):
        if args.use_existing:
            # Look for video files in temp_download directories
            potential_videos = []
            for temp_dir in [d for d in os.listdir('.') if d.startswith('temp_download_')]:
                for file in os.listdir(temp_dir):
                    if file.endswith('.mp4'):
                        potential_videos.append(os.path.join(temp_dir, file))
            
            # Also check shorts_output directory
            if os.path.exists('shorts_output'):
                for file in os.listdir('shorts_output'):
                    if file.endswith('.mp4'):
                        potential_videos.append(os.path.join('shorts_output', file))
            
            if potential_videos:
                # Use the largest video file (likely the highest quality)
                video_path = max(potential_videos, key=os.path.getsize)
                logger.info(f"Using existing video file: {video_path}")
            else:
                logger.error("No video files found in temp directories")
                return False
        else:
            logger.error("No video path provided")
            return False
    
    # Save a copy of the original video to our test directory
    permanent_video_path = os.path.join(test_dir, 'originals', f"original_{unique_id}.mp4")
    shutil.copy(video_path, permanent_video_path)
    logger.info(f"Saved permanent copy of video to {permanent_video_path}")
    
    # Extract audio from video
    audio_path = os.path.join(test_dir, 'originals', f"audio_{unique_id}.mp3")
    if not extract_audio(permanent_video_path, audio_path):
        logger.error("Failed to extract audio")
        return False
    
    # Create dubbed audio
    dubbed_audio_path = os.path.join(test_dir, 'dubbed', f"dubbed_audio_{args.language}_{unique_id}.wav")
    if not dub_audio(audio_path, args.text, args.language, dubbed_audio_path):
        logger.error("Failed to create dubbed audio")
        return False
    
    # Create final dubbed video
    final_video_path = os.path.join(test_dir, 'dubbed', f"dubbed_video_{args.language}_{unique_id}.mp4")
    if not create_dubbed_video(permanent_video_path, dubbed_audio_path, final_video_path):
        logger.error("Failed to create dubbed video")
        return False
    
    # Create thumbnail
    thumbnail_path = os.path.join(test_dir, 'dubbed', f"dubbed_video_{args.language}_{unique_id}.jpg")
    thumbnail_cmd = [
        'ffmpeg', '-y',
        '-i', final_video_path,
        '-ss', '00:00:01',  # Take frame at 1 second
        '-vframes', '1',
        '-q:v', '2',        # High quality
        thumbnail_path
    ]
    try:
        subprocess.run(thumbnail_cmd, check=True)
        logger.info(f"Generated thumbnail: {thumbnail_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate thumbnail: {e}")
    
    logger.info("\n" + "="*50)
    logger.info(f"SUCCESS! Dubbing test completed successfully")
    logger.info(f"Original video: {permanent_video_path}")
    logger.info(f"Dubbed video ({args.language}): {final_video_path}")
    logger.info(f"Thumbnail: {thumbnail_path}")
    logger.info("="*50)
    
    # Print command to test the API endpoint directly
    print("\nTo test with curl command:")
    print(f'curl -X POST https://codeastra.originzero.in/generate_dubbed_audio \\\n'
          f'  -F "messages=[{{\'role\': \'user\', \'content\': \'{args.text}\', \'language\': \'{args.language}\'}}]" \\\n'
          f'  -F "voice_sample=@{audio_path}" \\\n'
          f'  --output test_dubbed_audio.wav')
    
    return True

if __name__ == "__main__":
    main() 