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
    "EN": "english",
    "HI": "hindi",
    "PT": "portuguese",
    "ZH": "mandarin",  # Chinese
    "ES": "spanish",
    "FR": "french",
    "DE": "german",
    "JP": "japanese",
    "AR": "arabic",
    "RU": "russian",
    "KR": "korean",
    "ID": "indonesian",
    "IT": "italian",
    "NL": "dutch",
    "TR": "turkish",
    "PL": "polish",
    "SV": "swedish",
    "TL": "tagalog",  # Filipino
    "MS": "malay",
    "RO": "romanian",
    "UK": "ukrainian",
    "EL": "greek",
    "CS": "czech",
    "DA": "danish",
    "FI": "finnish",
    "BG": "bulgarian",
    "HR": "croatian",
    "SK": "slovak",
    "TA": "tamil"
}


def dub_video(video_path, target_language_code, job_id, segment_id):
    """
    Process a video file for dubbing using Sieve API

    Args:
        video_path (str): Path to the video file
        target_language_code (str): Language code (e.g., "ES" for Spanish)
        job_id (str): Job ID for tracking and output path
        segment_id (str): Segment ID for the specific video

    Returns:
        dict: Response with status and output path information
    """
    try:
        # Convert language code to Sieve format
        if target_language_code not in LANGUAGE_MAP:
            return {"status": "error", "message": f"Unsupported language code: {target_language_code}"}

        target_language = LANGUAGE_MAP[target_language_code]

        # Ensure the video file exists
        if not os.path.exists(video_path):
            return {"status": "error", "message": f"Video file not found: {video_path}"}

        logger.info(f"Starting dubbing for {video_path} to {target_language}")

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

        # For now, we'll mock the Sieve API call since we don't have the actual implementation
        # In a real implementation, you would use the Sieve SDK or API

        # Create output directories
        output_base_dir = os.path.join("shorts_output", job_id, "dubbed")
        os.makedirs(output_base_dir, exist_ok=True)

        # Create the output filename
        output_filename = f"{segment_id}_{target_language_code.lower()}.mp4"
        output_path = os.path.join(output_base_dir, output_filename)

        # For demonstration, we'll just copy the original file to the destination
        # In a real implementation, you would process with Sieve API
        shutil.copy(video_path, output_path)

        # Generate URL path for the frontend
        url_path = f"/shorts_output/{job_id}/dubbed/{output_filename}"

        logger.info(f"Dubbing completed: {output_path}")

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
