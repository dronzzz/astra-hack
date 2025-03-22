import os
import tempfile
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip


def add_captions_to_video(video_path, output_path=None, model_size="tiny", device="cpu",
                          font_size=24, font_color="white"):
    """
    A simplified version that doesn't use OpenCV, only MoviePy and Whisper
    """
    # Set output path if not provided
    if output_path is None:
        base_name = os.path.splitext(video_path)[0]
        output_path = f"{base_name}_captioned.mp4"

    print(f"Processing video: {video_path}")

    # Load video using MoviePy
    video_clip = VideoFileClip(video_path)

    # Extract audio to a temporary file
    temp_dir = tempfile.mkdtemp()
    temp_audio_path = os.path.join(temp_dir, "temp_audio.wav")
    video_clip.audio.write_audiofile(
        temp_audio_path, codec='pcm_s16le', verbose=False, logger=None)

    print("Audio extracted, starting transcription...")

    # Load the Whisper model
    model = WhisperModel(model_size, device=device, compute_type="int8")

    # Transcribe the audio
    segments, info = model.transcribe(
        temp_audio_path, beam_size=5, word_timestamps=True)

    print(f"Transcription complete. Language detected: {info.language}")

    # Group words into sensible caption chunks
    grouped_captions = []
    current_words = []
    current_start = None
    current_end = None
    word_count = 0

    for segment in segments:
        for word in segment.words:
            if current_start is None:
                current_start = word.start

            current_words.append(word.word)
            current_end = word.end
            word_count += 1

            # Start a new segment after ~5 words or punctuation
            if word_count >= 5 or any(word.word.strip().endswith(p) for p in ['.', '?', '!', ',', ';', ':', '-']):
                if current_words:
                    text = ' '.join(current_words)
                    grouped_captions.append((current_start, current_end, text))
                    current_words = []
                    current_start = None
                    current_end = None
                    word_count = 0

    # Add any remaining words
    if current_words:
        text = ' '.join(current_words)
        grouped_captions.append((current_start, current_end, text))

    print(f"Generated {len(grouped_captions)} caption segments")

    # Create subtitle clips
    subtitle_clips = []
    for start_time, end_time, text in grouped_captions:
        subtitle = TextClip(
            text,
            fontsize=font_size,
            color=font_color,
            bg_color='black',
            font='Arial-Bold',
            method='caption',
            align='center',
            size=(video_clip.w * 0.9, None)  # 90% of video width
        )

        subtitle = subtitle.set_position(
            ('center', 'bottom')).margin(bottom=20, opacity=0)
        subtitle = subtitle.set_start(start_time).set_end(end_time)
        subtitle_clips.append(subtitle)

    # Combine video with subtitles
    final_clip = CompositeVideoClip([video_clip] + subtitle_clips)

    # Write output file
    print(f"Writing captioned video to {output_path}")
    final_clip.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile=os.path.join(temp_dir, 'temp_audio.m4a'),
        remove_temp=True
    )

    # Clean up
    video_clip.close()
    final_clip.close()
    os.remove(temp_audio_path)
    os.rmdir(temp_dir)

    return output_path


# Example usage
if __name__ == "__main__":
    input_video = "C:\Users\mayan\OneDrive\Desktop\ongoing_projects\recursion-6\server\shorts_output\short-625.mp4"

    captioned_video = add_captions_to_video(
        input_video,
        model_size="tiny",
        font_size=28,
        font_color="#FFFF00"  # Yellow text
    )

    print(f"Captioned video saved to: {captioned_video}")
