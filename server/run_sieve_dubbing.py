#!/usr/bin/env python
import os
import sys
import sieve

# Set API key
os.environ["SIEVE_API_KEY"] = "DwOcdC4CPfwP-U1djJIqD0npN5ERMoGiSp6K7-cdHqk" 
sieve.api_key = "DwOcdC4CPfwP-U1djJIqD0npN5ERMoGiSp6K7-cdHqk"

def main():
    if len(sys.argv) != 4:
        print("Usage: python run_sieve_dubbing.py <input_video_path> <output_video_path> <language>")
        return

    input_video = sys.argv[1]
    output_video = sys.argv[2]
    language = sys.argv[3]
    
    print(f"Running Sieve dubbing on {input_video} to {output_video} with language {language}")
    
    # Create Sieve File
    source_file = sieve.File(path=input_video)
    
    # Get dubbing function
    dubbing = sieve.function.get("sieve/dubbing")
    
    # Run dubbing
    output = dubbing.push(
        source_file,                  # source_file
        language,                     # target_language  
        "gpt4",                       # translation_engine
        "elevenlabs (voice cloning)", # voice_engine
        "whisper-zero",               # transcription_engine
        "voice-dubbing",              # output_mode
        [],                           # edit_segments (empty)
        False,                        # return_transcript
        True,                         # preserve_background_audio
        "",                           # safewords
        "",                           # translation_dictionary
        0,                            # start_time
        -1,                           # end_time
        False,                        # enable_lipsyncing
        "sievesync-1.1",              # lipsync_backend
        "default"                     # lipsync_enhance
    )
    
    # Process result
    result = output.result()
    
    # Download file
    for output_object in result:
        if isinstance(output_object, sieve.File):
            output_object.download(output_video)
            print(f"Successfully downloaded dubbed video to {output_video}")
            return
    
    print("No file output found in result")

if __name__ == "__main__":
    main() 