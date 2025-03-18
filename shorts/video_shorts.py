import openai
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import json
import os
import subprocess
import cv2
import numpy as np
from datetime import datetime, timedelta


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


def download_video(youtube_url, output_path="video.mp4"):
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


def extract_important_parts(transcript, model="gpt-4-turbo"):
    api_key = "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"

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


def create_subtitle_file(transcript_data, start_time, end_time, output_file="subtitles.srt"):
    """Create SRT subtitle file from transcript data for a specific segment"""
    with open(output_file, 'w', encoding='utf-8') as f:
        counter = 1

        # Filter transcript entries that fall within our segment
        segment_transcript = [
            entry for entry in transcript_data
            if entry['start'] >= start_time and entry['start'] < end_time
        ]

        # Process each entry in the transcript
        for entry in segment_transcript:
            # Calculate relative time within the segment
            rel_start = entry['start'] - start_time
            rel_end = min(entry['start'] + entry['duration'],
                          end_time) - start_time

            # Format timestamps for SRT
            start_ts = str(timedelta(seconds=rel_start)).replace('.', ',')
            # Ensure it has milliseconds
            if ',' not in start_ts:
                start_ts += ',000'
            else:
                # Ensure 3 decimal places for milliseconds
                parts = start_ts.split(',')
                start_ts = f"{parts[0]},{parts[1][:3].ljust(3, '0')}"

            end_ts = str(timedelta(seconds=rel_end)).replace('.', ',')
            if ',' not in end_ts:
                end_ts += ',000'
            else:
                # Ensure 3 decimal places for milliseconds
                parts = end_ts.split(',')
                end_ts = f"{parts[0]},{parts[1][:3].ljust(3, '0')}"

            # Format to ensure proper SRT timestamp format (HH:MM:SS,mmm)
            if len(start_ts.split(':')) == 2:
                start_ts = f"00:{start_ts}"
            if len(end_ts.split(':')) == 2:
                end_ts = f"00:{end_ts}"

            # Write the subtitle entry
            f.write(f"{counter}\n")
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{entry['text']}\n\n")
            counter += 1

    return output_file


def get_aspect_ratio_choice():
    """Prompt user to choose an aspect ratio"""
    print("\nChoose an aspect ratio:")
    print("1. 9:16 (Vertical - Best for Shorts/TikTok/Reels)")
    print("2. 16:9 (Horizontal - Standard Widescreen)")
    print("3. 1:1 (Square - Instagram)")
    print("4. 4:5 (Vertical - Instagram)")
    print("5. Keep original aspect ratio")

    choice = input("Enter your choice (1-5): ").strip()

    aspect_ratios = {
        "1": "9:16",
        "2": "16:9",
        "3": "1:1",
        "4": "4:5",
        "5": "original"
    }

    return aspect_ratios.get(choice, "original")


def get_video_dimensions(input_file):
    """Get video dimensions using ffprobe"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=p=0',
        input_file
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True)
        width, height = map(int, result.stdout.strip().split(','))
        return width, height
    except subprocess.CalledProcessError as e:
        print(f"Error getting video dimensions: {e}")
        return 1920, 1080  # Default fallback dimensions


def apply_aspect_ratio(input_file, output_file, aspect_ratio):
    """Apply the chosen aspect ratio to the video"""
    if aspect_ratio == "original":
        # Just copy the file if keeping original aspect ratio
        cmd = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-c', 'copy',
            output_file
        ]
        subprocess.run(cmd, check=True)
        return output_file

    # Get video dimensions
    width, height = get_video_dimensions(input_file)

    # Calculate new dimensions based on aspect ratio
    if aspect_ratio == "9:16":
        new_width = height * 9 // 16
        new_height = height
        if new_width > width:
            new_width = width
            new_height = width * 16 // 9
    elif aspect_ratio == "16:9":
        new_width = width
        new_height = width * 9 // 16
        if new_height > height:
            new_height = height
            new_width = height * 16 // 9
    elif aspect_ratio == "1:1":
        new_size = min(width, height)
        new_width = new_size
        new_height = new_size
    elif aspect_ratio == "4:5":
        new_width = height * 4 // 5
        new_height = height
        if new_width > width:
            new_width = width
            new_height = width * 5 // 4

    # Calculate padding/cropping
    x_offset = (width - new_width) // 2
    y_offset = (height - new_height) // 2

    # Apply transformation
    cmd = [
        'ffmpeg', '-y',
        '-i', input_file,
        '-vf', f'crop={new_width}:{new_height}:{x_offset}:{y_offset}',
        '-c:a', 'copy',
        output_file
    ]

    subprocess.run(cmd, check=True)
    return output_file


def track_face_and_crop(input_file, output_file, aspect_ratio="9:16"):
    cap = cv2.VideoCapture(input_file)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if aspect_ratio == "9:16":
        new_width = height * 9 // 16
        new_height = height
    else:
        new_width = width
        new_height = height

    x_offset = (width - new_width) // 2
    y_offset = (height - new_height) // 2

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (new_width, new_height))

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            x_offset = max(0, min(x + w//2 - new_width//2, width - new_width))
            y_offset = max(
                0, min(y + h//2 - new_height//2, height - new_height))

        cropped_frame = frame[y_offset:y_offset +
                              new_height, x_offset:x_offset+new_width]
        out.write(cropped_frame)

    cap.release()
    out.release()


def create_shorts_ffmpeg(video_path, segments, transcript_data, aspect_ratio="9:16", output_path="shorts.mp4"):
    """Create shorts video using ffmpeg with transcript overlay and custom aspect ratio"""
    try:
        temp_files = []
        final_temp_files = []

        for i, seg in enumerate(segments):
            try:
                start = float(seg.get('start_time', 0))
                end = float(seg.get('end_time', start + 30))

                if end <= start:
                    print(
                        f"Warning: end_time {end} <= start_time {start} for segment {i+1}, using default duration")
                    end = start + 30

                duration = end - start

                raw_segment = f"temp_segment_raw_{i}.mp4"
                cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-ss', str(start),
                    '-t', str(duration),
                    '-c', 'copy',
                    raw_segment
                ]
                subprocess.run(cmd, check=True)
                temp_files.append(raw_segment)

                subtitle_file = f"subtitles_{i}.srt"
                create_subtitle_file(
                    transcript_data, start, end, subtitle_file)
                temp_files.append(subtitle_file)

                aspect_segment = f"temp_segment_{i}.mp4"
                track_face_and_crop(raw_segment, aspect_segment, aspect_ratio)
                temp_files.append(aspect_segment)

                cmd = [
                    'ffmpeg', '-y',
                    '-i', aspect_segment,
                    '-vf', f"subtitles={subtitle_file}:force_style='FontName=Arial,FontSize=30,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=2,Shadow=1,Alignment=2'",
                    '-c:a', 'copy',
                    aspect_segment
                ]
                subprocess.run(cmd, check=True)

                final_temp_files.append(aspect_segment)
                temp_files.append(aspect_segment)

                print(f"Processed segment {i+1}/{len(segments)}")

            except Exception as e:
                print(f"Error processing segment {i+1}: {e}")
                continue

        if not final_temp_files:
            raise ValueError("No segments were successfully processed")

        with open('segments.txt', 'w') as f:
            for temp_file in final_temp_files:
                f.write(f"file '{temp_file}'\n")

        concat_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', 'segments.txt',
            '-c', 'copy',
            output_path
        ]
        subprocess.run(concat_cmd, check=True)

        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        os.remove('segments.txt')

        print(f"Shorts video saved to {output_path}")
    except Exception as e:
        print(f"Error creating Shorts video: {e}")
        print("Attempting to clean up temporary files...")
        try:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            if os.path.exists('segments.txt'):
                os.remove('segments.txt')
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")


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

    # Choose aspect ratio
    aspect_ratio = get_aspect_ratio_choice()
    print(f"Using aspect ratio: {aspect_ratio}")

    # Custom output filename
    output_filename = input(
        "Enter output filename (default: shorts.mp4): ").strip()
    if not output_filename:
        output_filename = "shorts.mp4"
    if not output_filename.endswith(".mp4"):
        output_filename += ".mp4"

    video_path = download_video(youtube_url)
    if not video_path:
        print("Failed to download video.")
        return

    create_shorts_ffmpeg(video_path, segments, transcript,
                         aspect_ratio, output_filename)


if __name__ == "__main__":
    main()
