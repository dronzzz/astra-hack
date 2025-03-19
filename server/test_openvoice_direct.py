import requests
import json
import os

def test_direct():
    url = "https://codeastra.originzero.in/generate_dubbed_audio"
    
    # Choose any MP3 file from your shorts_output directory
    shorts_dir = "shorts_output"
    if not os.path.exists(shorts_dir):
        print(f"Error: {shorts_dir} directory not found")
        return
        
    # Find a suitable audio file - first try any MP3s
    mp3_files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp3')]
    
    if not mp3_files:
        # If no MP3s, use ffmpeg to extract audio from an MP4
        mp4_files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
        if not mp4_files:
            print("No audio or video files found")
            return
            
        import subprocess
        audio_path = "test_audio.mp3"
        cmd = [
            'ffmpeg', '-y',
            '-i', os.path.join(shorts_dir, mp4_files[0]),
            '-q:a', '0',
            '-map', 'a',
            audio_path
        ]
        subprocess.run(cmd, check=True)
        print(f"Extracted audio to: {audio_path}")
    else:
        audio_path = os.path.join(shorts_dir, mp3_files[0])
    
    # Use exact format from your working example
    data = {
        "text": "This is a test of the dubbing system. If you can hear this message, the API is working correctly."
    }
    
    # Use exact file handling from your example
    files = {"voice_sample": open(audio_path, "rb")}
    
    print(f"Sending request to {url}")
    print(f"Audio file: {audio_path}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, data=data, files=files, timeout=120)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            output_path = "test_dubbed.wav"
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"Dubbed audio saved to: {output_path}")
        else:
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Error: {response.text}")
    finally:
        # Close the file handle
        files["voice_sample"].close()

if __name__ == "__main__":
    test_direct() 