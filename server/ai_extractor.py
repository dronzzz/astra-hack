import openai
import json
import os
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger('ai-extractor')


def extract_important_parts(transcript, model="llama-3.3-70b-versatile"):
    """Use AI to extract key timestamps for Shorts."""
    # Check if we have API keys
    Groq_key = os.getenv("groq_api_key")
    OpenAI_key = os.getenv("OPENAI_API_KEY")

    # If no API keys are available, use rule-based approach
    if (not Groq_key or Groq_key == "YOUR_GROQ_API_KEY") and (not OpenAI_key or OpenAI_key == "YOUR_OPENAI_API_KEY"):
        logger.warning("No valid API keys found. Using rule-based approach.")
        return extract_segments_rule_based(transcript)

    # Try to use Groq if available
    if Groq_key and Groq_key != "YOUR_GROQ_API_KEY":
        try:
            client = openai.OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=Groq_key)
            transcript_text = "\n".join(
                [f"[{entry['start']}] {entry['text']}" for entry in transcript])

            prompt = f"""
            Analyze the following transcript and identify 2-3 engaging segments that would work well for YouTube Shorts (max 60 seconds each).
            Return the response in this exact JSON format:
            [
                {{
                    "start_time": <number>,
                    "end_time": <number>,
                    "reason": "<why this segment is engaging>"
                }}
            ]
            
            IMPORTANT: Each segment MUST have both start_time and end_time as numeric values, with end_time greater than start_time.
            The difference between end_time and start_time should be less than 60 seconds.
            
            Transcript:
            {transcript_text}
            
            Remember to return ONLY valid JSON, no additional text.
            """

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that returns only valid JSON responses."},
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.choices[0].message.content.strip()

            try:
                segments = json.loads(content)
                valid_segments = validate_segments(segments)
                if valid_segments:
                    return valid_segments
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                logger.error(f"Raw response: {content}")
        except Exception as e:
            logger.error(f"Error using Groq API: {e}")

    # Try to use OpenAI if available and Groq failed
    if OpenAI_key and OpenAI_key != "YOUR_OPENAI_API_KEY":
        try:
            client = openai.OpenAI(api_key=OpenAI_key)
            transcript_text = "\n".join(
                [f"[{entry['start']}] {entry['text']}" for entry in transcript])

            prompt = f"""
            Analyze the following transcript and identify 2-3 engaging segments that would work well for YouTube Shorts (max 60 seconds each).
            Return the response in this exact JSON format:
            [
                {{
                    "start_time": <number>,
                    "end_time": <number>,
                    "reason": "<why this segment is engaging>"
                }}
            ]
            
            IMPORTANT: Each segment MUST have both start_time and end_time as numeric values, with end_time greater than start_time.
            The difference between end_time and start_time should be less than 60 seconds.
            
            Transcript:
            {transcript_text}
            
            Remember to return ONLY valid JSON, no additional text.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that returns only valid JSON responses."},
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.choices[0].message.content.strip()

            try:
                segments = json.loads(content)
                valid_segments = validate_segments(segments)
                if valid_segments:
                    return valid_segments
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                logger.error(f"Raw response: {content}")
        except Exception as e:
            logger.error(f"Error using OpenAI API: {e}")

    # If all API methods failed, fall back to rule-based approach
    logger.warning("All AI API attempts failed. Using rule-based approach.")
    return extract_segments_rule_based(transcript)


def validate_segments(segments):
    """Validate and fix segments returned by AI."""
    valid_segments = []
    for i, segment in enumerate(segments):
        if not isinstance(segment, dict):
            logger.warning(f"Skipping segment {i+1}: Not a valid dictionary")
            continue

        if 'start_time' not in segment or 'end_time' not in segment:
            logger.warning(
                f"Skipping segment {i+1}: Missing start_time or end_time")
            continue

        try:
            start = float(segment['start_time'])
            end = float(segment['end_time'])

            if end <= start:
                logger.warning(
                    f"Fixing segment {i+1}: end_time ({end}) must be greater than start_time ({start})")
                end = start + 30

            if end - start > 60:
                logger.warning(
                    f"Fixing segment {i+1}: Duration too long ({end-start}s), limiting to 60s")
                end = start + 60

            segment['start_time'] = start
            segment['end_time'] = end

            valid_segments.append(segment)
        except (ValueError, TypeError):
            logger.warning(
                f"Skipping segment {i+1}: Invalid numeric values for start_time or end_time")
            continue

    return valid_segments


def extract_segments_rule_based(transcript):
    """Extract segments using simple rules when AI is not available."""
    if not transcript:
        return [{
            "start_time": 0.0,
            "end_time": 60.0,
            "reason": "Default segment (first minute of video)"
        }]

    # Get total duration
    total_duration = max(entry['start'] + entry['duration']
                         for entry in transcript)

    # If video is short enough, use the entire thing
    if total_duration <= 60:
        return [{
            "start_time": 0.0,
            "end_time": total_duration,
            "reason": "Short video (entire content)"
        }]

    segments = []

    # 1. First segment: Start of the video (first 60 seconds)
    segments.append({
        "start_time": 0.0,
        "end_time": min(60.0, total_duration / 3),
        "reason": "Introduction/opening segment"
    })

    # 2. Middle segment: Around 40-50% of the video
    mid_point = total_duration * 0.45
    segments.append({
        "start_time": max(0, mid_point - 30),
        "end_time": min(total_duration, mid_point + 30),
        "reason": "Middle segment with key content"
    })

    # 3. Final segment: Last part of the video
    if total_duration > 120:
        segments.append({
            "start_time": max(0, total_duration - 60),
            "end_time": total_duration,
            "reason": "Conclusion/closing segment"
        })

    return segments
