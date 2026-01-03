import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from app.utils.logger import get_logger

logger = get_logger("tts")


def text_to_speech_bytes(text: str, voice_id: str = "Joanna") -> bytes:
    """Convert text to speech bytes using Amazon Polly.
    
    Args:
        text: The text to convert to speech
        voice_id: Polly voice ID (default: Joanna)
    
    Returns:
        MP3 audio bytes
    """
    try:
        logger.info(f"Converting text to speech: {text[:50]}...")
        
        # Initialize Polly client
        polly_client = boto3.client(
            'polly',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        # Request speech synthesis
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_id,
            Engine='neural'  # Use neural engine for better quality
        )
        
        # Read audio stream
        if "AudioStream" in response:
            audio_bytes = response["AudioStream"].read()
            logger.info(f"Generated {len(audio_bytes)} bytes of audio")
            return audio_bytes
        else:
            logger.error("No AudioStream in Polly response")
            return b""
    
    except (BotoCoreError, ClientError) as e:
        logger.exception(f"Error with Polly TTS: {e}")
        # Fallback: return empty bytes
        return b""
