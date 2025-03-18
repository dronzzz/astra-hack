import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi


def get_video_id(youtube_url):
    """Extract video ID from YouTube URL."""
    if "v=" in youtube_url:
        return youtube_url.split("v=")[1].split("&")[0]
    return None


def fetch_transcript(video_id):
    """Fetch transcript of a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print("Error fetching transcript:", e)
        return None


def download_video(youtube_url, output_path="video.mp4"):
    """Download a YouTube video."""
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return output_path
    except Exception as e:
        print("Error downloading video:", e)
        return None
