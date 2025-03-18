import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import json


def get_video_id(youtube_url):

    if "v=" in youtube_url:
        return youtube_url.split("v=")[1].split("&")[0]
    return None


def fetch_transcript(video_id):

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print("Error fetching transcript:", e)
        return None


def extract_important_parts(transcript):

    segments = []
    last_time = 0
    for entry in transcript:
        start_time = entry['start']
        if start_time - last_time > 30:
            segments.append({
                "start_time": last_time,
                "end_time": start_time,
                "reason": "Significant gap, possibly a scene change."
            })
            last_time = start_time

    return segments


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
