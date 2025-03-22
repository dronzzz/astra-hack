import os
import shutil
import sieve


def main():
    # Define the local source file and parameters for dubbing
    source_file = sieve.File(
        path="C:/Users/mayan/OneDrive/Desktop/ongoing_projects/recursion-6/server/shorts_output/short-3dd.mp4")

    target_language = "spanish"
    translation_engine = "gpt4"
    voice_engine = "elevenlabs (voice cloning)"
    transcription_engine = "whisper-zero"
    output_mode = "voice-dubbing"
    edit_segments = list()
    return_transcript = False
    preserve_background_audio = True
    safewords = ""
    translation_dictionary = ""
    start_time = 0
    end_time = -1
    enable_lipsyncing = False
    lipsync_backend = "sievesync-1.1"
    lipsync_enhance = "default"

    # Initialize the dubbing function and start the job
    dubbing = sieve.function.get("sieve/dubbing")
    output = dubbing.push(
        source_file,
        target_language,
        translation_engine,
        voice_engine,
        transcription_engine,
        output_mode,
        edit_segments,
        return_transcript,
        preserve_background_audio,
        safewords,
        translation_dictionary,
        start_time,
        end_time,
        enable_lipsyncing,
        lipsync_backend,
        lipsync_enhance
    )

    print('Job started in the background. Waiting for results...')

    # Process the output and move the dubbed video to the desired directory
    for output_object in output.result():
        # Get the temporary file path of the dubbed video
        tmp_path = output_object.path
        print("Dubbed video downloaded to:", tmp_path)

        # Define the destination folder and filename
        dest_folder = "./dubbed"
        dest_filename = "dubbed_video.mp4"  # change this to your desired filename

        # Create the destination folder if it does not exist
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
            print(f"Created directory: {dest_folder}")

        dest_path = os.path.join(dest_folder, dest_filename)

        # Move the file from the temporary location to the destination
        shutil.move(tmp_path, dest_path)
        print("Dubbed video moved to:", dest_path)


if __name__ == "__main__":
    main()
