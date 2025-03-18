import os
import concurrent.futures
import time
import uuid
from youtube_utils import get_video_id, fetch_transcript, download_video_segment
from ai_extractor import extract_important_parts
from video_processor import process_segment
import json


def process_individual_segment(segment, segment_id, total_segments, youtube_url, transcript_data, aspect_ratio, font_size, words_per_subtitle=2):
    """Process a single segment completely independently"""
    try:
        # Create unique IDs for this segment's files
        unique_id = str(uuid.uuid4())[:8]
        temp_dir = f"temp_{segment_id}_{unique_id}"
        os.makedirs(temp_dir, exist_ok=True)

        # Output path for final video
        output_dir = "shorts_output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/short_{segment_id}.mp4"

        # Get segment timestamps
        start_time = float(segment.get('start_time', 0))
        end_time = float(segment.get('end_time', start_time + 30))

        # Validate segment duration
        if end_time <= start_time:
            print(
                f"[Segment {segment_id}] Warning: Invalid segment times. Using default 30 second duration.")
            end_time = start_time + 30

        duration = end_time - start_time
        print(
            f"[Segment {segment_id}/{total_segments}] Processing clip of duration: {duration:.2f}s")

        # Download only this segment
        raw_segment = f"{temp_dir}/raw_segment.mp4"
        if not download_video_segment(youtube_url, start_time, end_time, raw_segment):
            raise Exception("Failed to download segment")

        # Process the segment
        result = process_segment(
            video_path=raw_segment,
            segment=segment,
            transcript_data=transcript_data,
            aspect_ratio=aspect_ratio,
            output_path=output_path,
            font_size=font_size,
            words_per_subtitle=words_per_subtitle,
            segment_id=segment_id,
            total_segments=total_segments,
            temp_dir=temp_dir
        )

        # Clean up temporary directory
        try:
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
        except Exception as e:
            print(
                f"[Segment {segment_id}] Warning: Could not clean up temp directory: {e}")

        return result
    except Exception as e:
        print(f"[Segment {segment_id}] Error in segment processing: {e}")
        return False


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

    # Words per subtitle
    words_per_subtitle = input(
        "Enter number of words per subtitle (default: 2): ").strip()
    try:
        words_per_subtitle = int(words_per_subtitle)
    except (ValueError, TypeError):
        words_per_subtitle = 2

    # Create output directory
    output_dir = "shorts_output"
    os.makedirs(output_dir, exist_ok=True)

    # Determine number of workers
    max_workers = min(len(segments), os.cpu_count() or 4)
    print(f"\nUsing {max_workers} workers for parallel processing")

    # Process segments in parallel - each worker handles everything including download
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Start timer
        start_time = time.time()

        # Submit tasks
        futures = {}
        for i, segment in enumerate(segments):
            future = executor.submit(
                process_individual_segment,
                segment=segment,
                segment_id=i+1,
                total_segments=len(segments),
                youtube_url=youtube_url,
                transcript_data=transcript,
                aspect_ratio=aspect_ratio,
                font_size=font_size,
                words_per_subtitle=words_per_subtitle
            )
            futures[future] = i+1

        # Process results as they complete
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            segment_id = futures[future]
            output_file = f"{output_dir}/short_{segment_id}.mp4"

            try:
                success = future.result()
                completed += 1

                if success:
                    print(
                        f"\n✅ Short {segment_id}/{len(segments)} is ready! File: {output_file}")
                    print(
                        f"   [{completed}/{len(segments)}] segments completed")
                else:
                    print(f"\n❌ Failed to process segment {segment_id}.")
            except Exception as e:
                print(f"\n❌ Error processing segment {segment_id}: {e}")

        # Print total time
        total_time = time.time() - start_time
        print(f"\nAll processing completed in {total_time:.2f} seconds")
        print(f"Output videos are available in the '{output_dir}' directory")


if __name__ == "__main__":
    main()
