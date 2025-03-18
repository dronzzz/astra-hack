import openai
import json
import os
from dotenv import load_dotenv
load_dotenv()
def extract_important_parts(transcript, model="llama-3.3-70b-versatile"):
    """Use AI to extract key timestamps for Shorts."""

    Groq_key = os.getenv("groq_api_key")

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

    try:
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
            valid_segments = []
            for i, segment in enumerate(segments):
                if not isinstance(segment, dict):
                    print(f"Skipping segment {i+1}: Not a valid dictionary")
                    continue

                if 'start_time' not in segment or 'end_time' not in segment:
                    print(
                        f"Skipping segment {i+1}: Missing start_time or end_time")
                    continue

                try:
                    start = float(segment['start_time'])
                    end = float(segment['end_time'])

                    if end <= start:
                        print(
                            f"Fixing segment {i+1}: end_time ({end}) must be greater than start_time ({start})")
                        end = start + 30

                    if end - start > 60:
                        print(
                            f"Fixing segment {i+1}: Duration too long ({end-start}s), limiting to 60s")
                        end = start + 60

                    segment['start_time'] = start
                    segment['end_time'] = end

                    valid_segments.append(segment)
                except (ValueError, TypeError):
                    print(
                        f"Skipping segment {i+1}: Invalid numeric values for start_time or end_time")
                    continue

            if not valid_segments:
                print("No valid segments found. Creating a default segment.")
                valid_segments = [{
                    "start_time": 0.0,
                    "end_time": 60.0,
                    "reason": "Default segment (first minute of video)"
                }]

            return valid_segments

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {content}")
            return [{
                "start_time": 0.0,
                "end_time": 60.0,
                "reason": "Default segment (first minute of video)"
            }]
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return [{
            "start_time": 0.0,
            "end_time": 60.0,
            "reason": "Default segment (first minute of video)"
        }]
