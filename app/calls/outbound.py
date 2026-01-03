import os
from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from typing import Optional, List
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from fastapi.responses import Response
from app.utils.logger import get_logger
from app.config.loader import load_org_config

router = APIRouter()
logger = get_logger("outbound")


class OutboundCallRequest(BaseModel):
    """Request model for triggering outbound calls."""
    to_number: str  # Phone number to call (E.164 format: +1234567890)
    org_name: str = "sample_org"  # Organization identifier
    call_type: str = "reminder"  # reminder, awareness, or survey
    message: Optional[str] = None  # Custom message (optional)
    gather_response: bool = False  # Whether to record response


class BulkOutboundRequest(BaseModel):
    """Request model for bulk outbound calls."""
    to_numbers: List[str]  # List of phone numbers
    org_name: str = "sample_org"
    call_type: str = "awareness"
    message: Optional[str] = None


def get_twilio_client() -> Client:
    """Get Twilio client from environment variables."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        raise HTTPException(
            status_code=500,
            detail="Twilio credentials not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env"
        )
    
    return Client(account_sid, auth_token)


def generate_twiml_url(call_type: str, org_name: str, message: Optional[str] = None, gather: bool = False) -> str:
    """Generate TwiML URL for outbound call based on type.
    
    In production, this would point to your server's /voice/outbound-response endpoint.
    For now, we'll use inline TwiML.
    """
    # Get base URL from environment or construct it
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    
    # Build query parameters
    params = f"?type={call_type}&org={org_name}"
    if message:
        params += f"&message={message}"
    if gather:
        params += "&gather=true"
    
    return f"{base_url}/voice/outbound-response{params}"


@router.post("/voice/outbound")
async def trigger_outbound_call(request: OutboundCallRequest):
    """Trigger a single outbound call via Twilio REST API.
    
    Use cases:
    - Reminder: Appointment reminders, payment due dates
    - Awareness: Announcements, updates, alerts
    - Survey: Collect feedback, conduct polls
    
    Example:
    ```
    POST /voice/outbound
    {
        "to_number": "+15551234567",
        "org_name": "sample_org",
        "call_type": "reminder",
        "message": "Your appointment is tomorrow at 2 PM",
        "gather_response": false
    }
    ```
    """
    try:
        logger.info(f"Triggering outbound call to {request.to_number} for {request.org_name}")
        
        # Load organization config
        config = load_org_config(request.org_name)
        
        # Get Twilio client
        client = get_twilio_client()
        from_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not from_number:
            raise HTTPException(
                status_code=500,
                detail="TWILIO_PHONE_NUMBER not configured in .env"
            )
        
        # Generate TwiML URL for the call
        twiml_url = generate_twiml_url(
            call_type=request.call_type,
            org_name=request.org_name,
            message=request.message,
            gather=request.gather_response
        )
        
        # Make the call
        call = client.calls.create(
            to=request.to_number,
            from_=from_number,
            url=twiml_url,
            method="POST",
            status_callback=f"{os.getenv('BASE_URL', 'http://localhost:8000')}/voice/outbound-status",
            status_callback_event=["completed"],
            status_callback_method="POST"
        )
        
        logger.info(f"Outbound call initiated: {call.sid}")
        
        return {
            "status": "success",
            "call_sid": call.sid,
            "to": request.to_number,
            "org_name": request.org_name,
            "call_type": request.call_type,
            "message": f"Call initiated to {request.to_number}"
        }
    
    except Exception as e:
        logger.exception(f"Error triggering outbound call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/outbound/bulk")
async def trigger_bulk_outbound_calls(request: BulkOutboundRequest):
    """Trigger multiple outbound calls (bulk operation).
    
    Example:
    ```
    POST /voice/outbound/bulk
    {
        "to_numbers": ["+15551234567", "+15559876543"],
        "org_name": "sample_org",
        "call_type": "awareness",
        "message": "Important update about our services"
    }
    ```
    """
    try:
        logger.info(f"Triggering bulk outbound calls: {len(request.to_numbers)} recipients")
        
        results = []
        client = get_twilio_client()
        from_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not from_number:
            raise HTTPException(
                status_code=500,
                detail="TWILIO_PHONE_NUMBER not configured"
            )
        
        twiml_url = generate_twiml_url(
            call_type=request.call_type,
            org_name=request.org_name,
            message=request.message
        )
        
        # Initiate calls for each number
        for to_number in request.to_numbers:
            try:
                call = client.calls.create(
                    to=to_number,
                    from_=from_number,
                    url=twiml_url,
                    method="POST"
                )
                
                results.append({
                    "to": to_number,
                    "status": "initiated",
                    "call_sid": call.sid
                })
                logger.info(f"Call initiated to {to_number}: {call.sid}")
            
            except Exception as e:
                results.append({
                    "to": to_number,
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"Failed to call {to_number}: {e}")
        
        successful = len([r for r in results if r["status"] == "initiated"])
        failed = len([r for r in results if r["status"] == "failed"])
        
        return {
            "status": "completed",
            "total": len(request.to_numbers),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    except Exception as e:
        logger.exception(f"Error in bulk outbound calls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/outbound-response")
async def outbound_response(
    type: str = "reminder",
    org: str = "sample_org",
    message: Optional[str] = None,
    gather: str = "false"
):
    """Generate TwiML response for outbound calls.
    
    This endpoint is called by Twilio when the outbound call connects.
    """
    from twilio.twiml.voice_response import VoiceResponse
    from fastapi.responses import Response
    
    try:
        config = load_org_config(org)
        vr = VoiceResponse()
        
        # Build greeting based on org config
        greeting = f"Hello, this is {config.get('org_name', 'our organization')}'s {config.get('assistant_role', 'assistant')}. "
        
        # Add call type specific content
        if type == "reminder":
            content = message or "This is a friendly reminder about your upcoming appointment."
        elif type == "awareness":
            content = message or "We have an important update to share with you."
        elif type == "survey":
            content = message or "We would like to get your feedback."
        else:
            content = message or "Thank you for your time."
        
        vr.say(greeting + content)
        
        # If gathering response (for surveys)
        if gather == "true":
            vr.say("Please speak your response after the beep.")
            vr.record(
                max_length=30,
                transcribe=False,
                action="/voice/outbound-survey-response",
                method="POST"
            )
        else:
            vr.say("Thank you. Goodbye.")
        
        logger.info(f"Generated outbound TwiML for {org} - {type}")
        return Response(content=str(vr), media_type="application/xml")
    
    except Exception as e:
        logger.exception(f"Error generating outbound TwiML: {e}")
        vr = VoiceResponse()
        vr.say("Sorry, an error occurred.")
        return Response(content=str(vr), media_type="application/xml")


@router.post("/voice/outbound-survey-response")
async def outbound_survey_response(
    RecordingUrl: Optional[str] = None,
    CallSid: Optional[str] = None
):
    """Handle recorded survey responses from outbound calls."""
    from twilio.twiml.voice_response import VoiceResponse
    from fastapi.responses import Response
    from fastapi import Form
    
    try:
        logger.info(f"Survey response received for call {CallSid}")
        
        if RecordingUrl:
            # In production, you would:
            # 1. Transcribe the response
            # 2. Store in database
            # 3. Analyze sentiment
            logger.info(f"Recording URL: {RecordingUrl}")
            
            # For now, just acknowledge
            vr = VoiceResponse()
            vr.say("Thank you for your feedback. Have a great day!")
        else:
            vr = VoiceResponse()
            vr.say("No response recorded. Goodbye.")
        
        return Response(content=str(vr), media_type="application/xml")
    
    except Exception as e:
        logger.exception(f"Error handling survey response: {e}")
        vr = VoiceResponse()
        vr.say("Thank you. Goodbye.")
        return Response(content=str(vr), media_type="application/xml")


@router.post("/voice/outbound-status")
async def outbound_status_callback(
    CallSid: Optional[str] = None,
    CallStatus: Optional[str] = None,
    CallDuration: Optional[str] = None
):
    """Receive status updates for outbound calls.
    
    Called by Twilio when call completes.
    """
    from fastapi import Form
    
    try:
        logger.info(f"Outbound call {CallSid} status: {CallStatus}, duration: {CallDuration}s")
        
        # In production, you would:
        # - Store call metrics in database
        # - Update campaign statistics
        # - Trigger follow-up actions
        # - Send notifications
        
        return {"status": "received"}
    
    except Exception as e:
        logger.exception(f"Error in status callback: {e}")
        return {"status": "error", "error": str(e)}
