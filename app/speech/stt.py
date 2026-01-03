import os
import requests
from openai import OpenAI
from app.utils.logger import get_logger

logger = get_logger("stt")


def transcribe_from_url(recording_url: str) -> str:
    """Download audio from `recording_url` and transcribe using OpenAI Whisper.
    
    Args:
        recording_url: URL to the audio file (usually from Twilio)
    
    Returns:
        Transcribed text
    """
    try:
        logger.info(f"Downloading audio from {recording_url}")
        
        # Download the audio file
        response = requests.get(recording_url, timeout=30)
        response.raise_for_status()
        
        # Save temporarily
        temp_file = "/tmp/recording.wav"
        with open(temp_file, "wb") as f:
            f.write(response.content)
        
        logger.info("Transcribing audio with Whisper...")
        
        # Use OpenAI Whisper API
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        with open(temp_file, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        transcribed_text = transcript.text
        logger.info(f"Transcription: {transcribed_text}")
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return transcribed_text
    
    except Exception as e:
        logger.exception(f"Error transcribing audio: {e}")
        return ""
