import openai
import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

class ContentAnalyzer:
    def __init__(self):
        # Get API key from environment variable
        self.api_key = os.getenv("groq_api_key")
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set in environment variables")
            raise ValueError("GROQ_API_KEY is required but not set.")

        # Initialize OpenAI client for Groq
        self.client = openai.OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=self.api_key
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def analyze_transcript(self, transcript, metadata):
        """
        Analyze the transcript to identify the most impactful segments.
        Returns a list of segments sorted by impact score.
        """
        logger.info(f"Analyzing transcript for video: {metadata['title']}")
        
        # Combine transcript entries into chunks for better context
        video_length = metadata['length']  # in seconds
        
        # Prepare transcript for analysis
        transcript_text = self._format_transcript_for_analysis(transcript)
        
        # Create prompt for OpenAI
        prompt = f"""
        You are analyzing a YouTube video to create a short-form content clip (30-60 seconds).
        
        Video title: {metadata['title']}
        Channel: {metadata['channel']}
        Video length: {self._format_duration(video_length)}
        
        I need you to identify the most impactful or interesting segment that would work well as a standalone short.
        Consider segments that:
        1. Have a clear and complete thought or idea
        2. Would be engaging without additional context
        3. Contain memorable quotes, surprising facts, or emotional moments
        4. Would make viewers want to watch the full video
        
        Here's the transcript with timestamps:
        
        {transcript_text}
        
        Please identify the 3 best segments for a short-form video, providing:
        1. Start and end timestamps (in seconds)
        2. The exact transcript of the segment
        3. A score from 1-10 on how impactful this segment would be as a short
        4. A brief explanation of why you selected this segment
        
        Format your response as a JSON array of objects with keys: start_time, end_time, transcript, impact_score, and reasoning.
        """
        
        try:
            response = self.client.ChatCompletion.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a video editing assistant that helps identify the most engaging clips from longer videos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract and parse the response
            import json
            content = response.choices[0].message.content
            
            # Try to find and parse JSON in the response
            try:
                # Look for JSON array in the response
                import re
                json_match = re.search(r'\[\s*\{.*\}\s*\]', content, re.DOTALL)
                if json_match:
                    segments = json.loads(json_match.group(0))
                else:
                    # Try parsing the entire response as JSON
                    segments = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {e}")
                logger.debug(f"Response content: {content}")
                # Fallback to a simple segment
                segments = [{
                    "start_time": transcript[0]['start_time'],
                    "end_time": min(transcript[0]['start_time'] + 60, transcript[-1]['end_time']),
                    "transcript": "Failed to parse segments properly. Using default segment.",
                    "impact_score": 5,
                    "reasoning": "Fallback segment due to parsing error."
                }]
            
            # Sort segments by impact score (descending)
            segments.sort(key=lambda x: x.get('impact_score', 0), reverse=True)
            
            logger.info(f"Identified {len(segments)} potential segments")
            return segments
            
        except Exception as e:
            logger.error(f"Error during OpenAI API call: {str(e)}", exc_info=True)
            raise Exception(f"Failed to analyze transcript: {str(e)}")
    
    def _format_transcript_for_analysis(self, transcript):
        """Format transcript entries for the OpenAI prompt"""
        formatted = ""
        for entry in transcript:
            start_time = self._format_time(entry['start_time'])
            end_time = self._format_time(entry['end_time'])
            formatted += f"[{start_time} - {end_time}]: {entry['text']}\n"
        return formatted
    
    def _format_time(self, seconds):
        """Format seconds as MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
        
    def _format_duration(self, seconds):
        """Format seconds as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}" 
