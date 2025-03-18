import openai
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import json
import os


def get_video_id(youtube_url):

    if "v=" in youtube_url:
        return youtube_url.split("v=")[1].split("&")[0]
    return None


def fetch_transcript(video_id):

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = "\n".join(
            [f"[{entry['start']}] {entry['text']}" for entry in transcript])

        # Save transcript to a file
        with open("transcript.txt", "w", encoding="utf-8") as f:
            f.write(transcript_text)

        return transcript
    except Exception as e:
        print("Error fetching transcript:", e)
        return None


def extract_important_parts(transcript, model="gpt-4-turbo"):

    api_key = os.getenv(
        "OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key not set. Please set the OPENAI_API_KEY environment variable.")
        return []

    client = openai.OpenAI(api_key=api_key)

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

        # Try to parse the JSON response
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {content}")
        return []
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return []


def main():
    youtube_url = input("Enter YouTube video URL: ")
    video_id = get_video_id(youtube_url)

    if not video_id:
        print("Invalid YouTube URL.")
        return

    transcript = fetch_transcript(video_id)
    if not transcript:
        print("Could not retrieve transcript.")
        return

    segments = extract_important_parts(transcript)
    print("Extracted segments:", json.dumps(segments, indent=2))


if __name__ == "__main__":
    main()
