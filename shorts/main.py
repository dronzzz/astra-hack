import os
import concurrent.futures
import time
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

    # Font size selection
    font_size = input("Enter font size for subtitles (default: 42): ").strip()
    try:
        font_size = int(font_size)
    except (ValueError, TypeError):
        font_size = 42

    # Create output directory
    output_dir = "shorts_output"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nDownloading video from YouTube...")
    video_path = download_video(youtube_url)
    if not video_path:
        print("Failed to download video.")
        return

    # Determine number of workers (you can adjust this based on your system)
    max_workers = min(len(segments), os.cpu_count() or 4)
    print(f"\nUsing {max_workers} workers for parallel processing")

    # Process segments in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Start timer
        start_time = time.time()

        # Create futures for each segment
        futures = {}
        for i, segment in enumerate(segments):
            output_filename = f"{output_dir}/short_{i+1}.mp4"

            # Submit the task to the process pool
            future = executor.submit(
                process_segment,
                video_path=video_path,
                segment=segment,
                transcript_data=transcript,
                aspect_ratio=aspect_ratio,
                output_path=output_filename,
                font_size=font_size,
                segment_id=i+1,
                total_segments=len(segments)
            )

            futures[future] = (i+1, output_filename)

        # Process results as they complete (not waiting for all to finish)
        for future in concurrent.futures.as_completed(futures):
            segment_num, output_file = futures[future]
            try:
                success = future.result()
                if success:
                    # Calculate elapsed time for this segment
                    print(
                        f"\n✅ Short {segment_num}/{len(segments)} is ready! File: {output_file}")
                    print(
                        f"   You can watch it now while other segments are still processing.")
                else:
                    print(f"\n❌ Failed to process segment {segment_num}.")
            except Exception as e:
                print(f"\n❌ Error processing segment {segment_num}: {e}")

        # Print total time
        total_time = time.time() - start_time
        print(f"\nAll processing completed in {total_time:.2f} seconds")
        print(f"Output videos are available in the '{output_dir}' directory")


if __name__ == "__main__":
    main()
