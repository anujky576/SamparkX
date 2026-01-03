from fastapi import APIRouter, Request, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from app.utils.logger import get_logger
from app.speech.stt import transcribe_from_url
from typing import Optional

router = APIRouter()
logger = get_logger("inbound")


@router.post("/voice/inbound")
async def inbound_call(request: Request):
    """Handle inbound calls from Twilio and prompt user to speak."""
    try:
        vr = VoiceResponse()
        vr.say("Hello. This is the AI voice agent. Please speak your question after the beep.")
        
        # Record user speech with callback
        vr.record(
            max_length=30,
            transcribe=False,
            action="/voice/recording-callback",
            method="POST"
        )
        
        logger.info("Responding to inbound call with recording prompt")
        return Response(content=str(vr), media_type="application/xml")
    except Exception as e:
        logger.exception("Error handling inbound call: %s", e)
        vr = VoiceResponse()
        vr.say("Sorry, an error occurred.")
        return Response(content=str(vr), media_type="application/xml")


@router.post("/voice/recording-callback")
async def recording_callback(
    RecordingUrl: Optional[str] = Form(None),
    CallSid: Optional[str] = Form(None)
):
    """Handle recording callback from Twilio, transcribe, generate AI response, and return audio."""
    try:
        logger.info(f"Recording callback for call {CallSid}")
        logger.info(f"Recording URL: {RecordingUrl}")
        
        if RecordingUrl:
            # Step 1: Transcribe the recording
            transcribed_text = transcribe_from_url(RecordingUrl)
            logger.info(f"User said: {transcribed_text}")
            
            if not transcribed_text or len(transcribed_text.strip()) == 0:
                vr = VoiceResponse()
                vr.say("I'm sorry, I didn't catch that. Could you please repeat your question?")
                return Response(content=str(vr), media_type="application/xml")
            
            # Step 2: Retrieve relevant context from RAG (if available)
            from app.rag.retrieve import retrieve_relevant_chunks
            context_chunks = retrieve_relevant_chunks(transcribed_text, k=3)
            
            # Step 3: Generate AI response using LLM
            from app.llm.responder import generate_response
            ai_response = generate_response(transcribed_text, context_chunks=context_chunks if context_chunks else None)
            logger.info(f"AI response: {ai_response}")
            
            # Step 4: Convert response to speech (optional - requires AWS credentials)
            # For now, use Twilio's built-in TTS with <Say>
            # If you want to use Polly, uncomment below and use <Play> verb instead
            # from app.speech.tts import text_to_speech_bytes
            # audio_bytes = text_to_speech_bytes(ai_response)
            # # Save audio and serve via <Play> URL
            
            vr = VoiceResponse()
            vr.say(ai_response)
        else:
            vr = VoiceResponse()
            vr.say("Sorry, I didn't catch that. Please try again.")
        
        return Response(content=str(vr), media_type="application/xml")
    
    except Exception as e:
        logger.exception("Error in recording callback: %s", e)
        vr = VoiceResponse()
        vr.say("Sorry, an error occurred while processing your request.")
        return Response(content=str(vr), media_type="application/xml")
