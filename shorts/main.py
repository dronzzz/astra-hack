import os
from youtube_utils import get_video_id, fetch_transcript, download_video
from ai_extractor import extract_important_parts
from video_processor import process_segment
import json


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

    print("Analyzing transcript to find engaging segments...")
    segments = extract_important_parts(transcript)
    print("Extracted segments:", json.dumps(segments, indent=2))

    # Choose aspect ratio
    print("\nChoose an aspect ratio:")
    print("1. 9:16 (Vertical - Best for Shorts/TikTok/Reels)")
    print("2. 1:1 (Square - Instagram)")
    print("3. 4:5 (Vertical - Instagram)")

    choice = input("Enter your choice (default: 1): ").strip()
    aspect_ratios = {
        "1": "9:16",
        "2": "1:1",
        "3": "4:5"
    }
    aspect_ratio = aspect_ratios.get(choice, "9:16")
    print(f"Using aspect ratio: {aspect_ratio}")

    # Create output directory if it doesn't exist
    output_dir = "shorts_output"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nDownloading video from YouTube...")
    video_path = download_video(youtube_url)
    if not video_path:
        print("Failed to download video.")
        return

    # Process each segment as a separate short video
    for i, segment in enumerate(segments):
        output_filename = f"{output_dir}/short_{i+1}.mp4"
        print(f"\nProcessing segment {i+1}/{len(segments)}...")

        process_segment(
            video_path=video_path,
            segment=segment,
            transcript_data=transcript,
            aspect_ratio=aspect_ratio,
            output_path=output_filename
        )

        print(f"Short {i+1} saved to {output_filename}")

    print("\nAll shorts have been created successfully!")


if __name__ == "__main__":
    main()
