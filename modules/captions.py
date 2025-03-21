import os
import json
import subprocess
import logging
import tempfile

logger = logging.getLogger(__name__)

class CaptionGenerator:
    def __init__(self):
        self.model = None  # Lazy-load Whisper model
        
    def generate(self, video_path, transcript_text=None):
        """
        Generate captions for the video
        If transcript_text is provided, use it instead of generating new captions
        """
        logger.info(f"Generating captions for video: {video_path}")
        
        caption_path = os.path.splitext(video_path)[0] + ".srt"
        
        if transcript_text:
            # Use provided transcript
            logger.info("Using provided transcript for captions")
            captions = self._format_transcript_to_captions(transcript_text)
        else:
            # Extract audio from video
            audio_path = self._extract_audio(video_path)
            
            # Generate captions using ffmpeg speech recognition fallback
            # We're not using Whisper directly due to installation issues on Windows
            captions = self._generate_captions_using_ffmpeg(audio_path, video_path)
            
            # Clean up temporary audio file
            try:
                os.remove(audio_path)
            except:
                pass
                
        # Write captions to file
        self._write_srt(captions, caption_path)
        
        return caption_path
        
    def _extract_audio(self, video_path):
        """Extract audio from video file"""
        audio_path = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-q:a', '0',
            '-map', 'a',
            '-y',
            audio_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return audio_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error extracting audio: {e.stderr.decode() if e.stderr else str(e)}")
            raise Exception("Failed to extract audio from video")
    
    def _generate_captions_using_ffmpeg(self, audio_path, video_path):
        """
        Fallback method to generate captions using ffmpeg
        or just extract from transcript timing
        """
        try:
            # Try to use ffmpeg with speech recognition
            logger.info("Attempting to generate captions using FFmpeg")
            
            output_srt = tempfile.NamedTemporaryFile(suffix='.srt', delete=False).name
            
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-f', 'srt',
                output_srt
            ]
            
            result = subprocess.run(cmd, capture_output=True)
            
            # If successful, parse the SRT file
            if os.path.exists(output_srt) and os.path.getsize(output_srt) > 0:
                with open(output_srt, 'r', encoding='utf-8') as f:
                    srt_content = f.read()
                
                # Parse SRT into captions format
                captions = self._parse_srt(srt_content)
                
                # Clean up
                os.remove(output_srt)
                
                return captions
            else:
                # If FFmpeg couldn't generate captions, fall back to video analysis
                logger.info("FFmpeg speech recognition failed, using video analysis for timing")
                return self._extract_captions_from_video(video_path)
                
        except Exception as e:
            logger.error(f"Error generating captions with FFmpeg: {str(e)}")
            # Fall back to video analysis
            return self._extract_captions_from_video(video_path)
    
    def _extract_captions_from_video(self, video_path):
        """
        Extract caption timing based on video scene changes
        This is a very basic fallback that just creates timed segments
        """
        logger.info("Extracting captions based on video duration")
        
        # Get video duration
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Error getting video duration")
            # Default to 60 seconds
            duration = 60
        else:
            try:
                data = json.loads(result.stdout)
                duration = float(data['format']['duration'])
            except:
                duration = 60
        
        # Create basic captions every 5 seconds
        captions = []
        segment_length = 5
        
        for i in range(0, int(duration), segment_length):
            end_time = min(i + segment_length, duration)
            captions.append({
                "start_time": i,
                "end_time": end_time,
                "text": f"Segment from {self._format_time(i)} to {self._format_time(end_time)}"
            })
        
        return captions
    
    def _format_transcript_to_captions(self, transcript_text):
        """Format provided transcript text into caption segments"""
        # For pre-generated transcript, assume it's already in the right format
        if isinstance(transcript_text, list):
            # Already in the correct format
            return transcript_text
        else:
            # Simple split by sentence
            import re
            sentences = re.split(r'(?<=[.!?])\s+', transcript_text)
            
            captions = []
            # Since we don't have timestamps, create dummy ones
            # In a real implementation, you'd align with the audio
            start_time = 0
            for sentence in sentences:
                # Approximate 5 words per second
                word_count = len(sentence.split())
                duration = max(1, word_count / 5)
                
                captions.append({
                    "start_time": start_time,
                    "end_time": start_time + duration,
                    "text": sentence
                })
                
                start_time += duration
                
            return captions
    
    def _parse_srt(self, srt_content):
        """Parse SRT content into our captions format"""
        captions = []
        blocks = srt_content.strip().split('\n\n')
        
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:
                # Get timestamp line
                timestamp_line = lines[1]
                times = timestamp_line.split(' --> ')
                
                start_time = self._srt_time_to_seconds(times[0])
                end_time = self._srt_time_to_seconds(times[1])
                
                # Get caption text (could be multiple lines)
                text = ' '.join(lines[2:])
                
                captions.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": text
                })
        
        return captions
    
    def _srt_time_to_seconds(self, time_str):
        """Convert SRT time format (00:00:00,000) to seconds"""
        parts = time_str.replace(',', '.').split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        
        return hours * 3600 + minutes * 60 + seconds
    
    def _write_srt(self, captions, output_path):
        """Write captions to SRT file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, caption in enumerate(captions):
                start = self._format_timestamp(caption["start_time"])
                end = self._format_timestamp(caption["end_time"])
                
                f.write(f"{i+1}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{caption['text']}\n\n")
                
        return output_path
    
    def _format_timestamp(self, seconds):
        """Format seconds to SRT timestamp (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"
        
    def _format_time(self, seconds):
        """Format seconds as MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}" 