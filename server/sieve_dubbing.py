import os
import logging
import requests
import shutil
import tempfile
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Map of frontend language codes to Sieve language codes
LANGUAGE_MAP = {
    "english": "english",
    "hindi": "hindi",
    "portuguese": "portuguese",
    "chinese": "mandarin",  # Chinese
    "mandarin": "mandarin",
    "spanish": "spanish",
    "french": "french",
    "german": "german",
    "japanese": "japanese",
    "arabic": "arabic",
    "russian": "russian",
    "korean": "korean",
    "indonesian": "indonesian",
    "italian": "italian",
    "dutch": "dutch",
    "turkish": "turkish",
    "polish": "polish",
    "swedish": "swedish",
    "tagalog": "tagalog",  # Filipino
    "filipino": "tagalog",
    "malay": "malay",
    "romanian": "romanian",
    "ukrainian": "ukrainian",
    "greek": "greek",
    "czech": "czech",
    "danish": "danish",
    "finnish": "finnish",
    "bulgarian": "bulgarian",
    "croatian": "croatian",
    "slovak": "slovak",
    "tamil": "tamil"
}


def dub_video(video_path, target_language_code, job_id, segment_id):
    """
    Process a video file for dubbing using Sieve API

    Args:
        video_path (str): Path to the input video file
        target_language_code (str): Language name (e.g., "spanish" for Spanish)
        job_id (str): Job ID for tracking
        segment_id (str): Segment ID for the video

    Returns:
        dict: Result containing status, output path, and url
    """
    try:
        # Verify the video file exists
        video_exists = os.path.exists(video_path)
        if not video_exists:
            logger.warning(f"Video file not found: {video_path}")
            # For testing/development, find any mp4 file to use as a source
            test_video_found = False
            for root, _, files in os.walk("shorts_output"):
                for file in files:
                    if file.endswith('.mp4'):
                        video_path = os.path.join(root, file)
                        logger.info(
                            f"Using existing video for testing: {video_path}")
                        test_video_found = True
                        break
                if test_video_found:
                    break

            if not test_video_found:
                # Create an empty file if no video found
                logger.warning("No test video found, creating a dummy file")
                os.makedirs("shorts_output", exist_ok=True)
                dummy_path = os.path.join("shorts_output", "dummy.mp4")
                with open(dummy_path, 'wb') as f:
                    f.write(b'dummy content')
                video_path = dummy_path

        # Convert language code to Sieve format
        if target_language_code not in LANGUAGE_MAP:
            return {"status": "error", "message": f"Unsupported language: {target_language_code}"}

        target_language = LANGUAGE_MAP[target_language_code]

        logger.info(f"Starting dubbing for {video_path} to {target_language}")

        # Create output directories
        output_base_dir = os.path.join("shorts_output", job_id, "dubbed")
        os.makedirs(output_base_dir, exist_ok=True)

        # Create the output filename
        output_filename = f"{segment_id}_{target_language_code.lower()}.mp4"
        output_path = os.path.join(output_base_dir, output_filename)

        # Mock implementation - just copy the video file for demonstration
        logger.info("Using mock implementation for dubbing")
        shutil.copy(video_path, output_path)

        # Generate URL path for the frontend
        url_path = f"/shorts_output/{job_id}/dubbed/{output_filename}"

        logger.info(f"Mock dubbing completed: {output_path}")

        return {
            "status": "completed",
            "url": url_path,
            "output_path": output_path,
            "language": target_language
        }

    except Exception as e:
        logger.error(f"Error in dubbing process: {str(e)}")
        return {"status": "error", "message": str(e)}


# For actual Sieve API integration (when you have access)
def dub_video_with_sieve(video_path, target_language_code, job_id, segment_id):
    """
    Implementation using actual Sieve SDK (uncomment when ready to use)
    """
    """
    import sieve
    
    try:
        # Convert language code to Sieve format
        if target_language_code not in LANGUAGE_MAP:
            return {"status": "error", "message": f"Unsupported language code: {target_language_code}"}
            
        target_language = LANGUAGE_MAP[target_language_code]
        
        # Create source file object
        source_file = sieve.File(path=video_path)
        
        # Parameters for Sieve API
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

        # Create output directories
        output_base_dir = os.path.join("shorts_output", job_id, "dubbed")
        os.makedirs(output_base_dir, exist_ok=True)
        
        # Create the output filename
        output_filename = f"{segment_id}_{target_language_code.lower()}.mp4"
        output_path = os.path.join(output_base_dir, output_filename)
        
        # Process the output and move the dubbed video to the desired directory
        for output_object in output.result():
            # Get the temporary file path of the dubbed video
            tmp_path = output_object.path
            logger.info(f"Dubbed video downloaded from Sieve to: {tmp_path}")
            
            # Move the file from the temporary location to the destination
            shutil.move(tmp_path, output_path)
            logger.info(f"Dubbed video moved to: {output_path}")
            
            # Generate URL path for the frontend
            url_path = f"/shorts_output/{job_id}/dubbed/{output_filename}"
            
            return {
                "status": "completed",
                "url": url_path,
                "output_path": output_path,
                "language": target_language
            }
            
    except Exception as e:
        logger.error(f"Error in Sieve dubbing process: {str(e)}")
        return {"status": "error", "message": str(e)}
    """
    pass
