#!/usr/bin/env python3
"""Examples for using the outbound calling API."""

import requests
import json

# Base URL - change this to your server URL
BASE_URL = "http://localhost:8000"

# Example 1: Simple Reminder Call
def example_reminder():
    """Send a reminder call to a single number."""
    print("Example 1: Reminder Call")
    print("-" * 50)
    
    payload = {
        "to_number": "+15551234567",  # Replace with real number
        "org_name": "sample_org",
        "call_type": "reminder",
        "message": "Your appointment is tomorrow at 2 PM. Please call us if you need to reschedule.",
        "gather_response": False
    }
    
    response = requests.post(f"{BASE_URL}/voice/outbound", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


# Example 2: Awareness Campaign Call
def example_awareness():
    """Send an awareness/announcement call."""
    print("Example 2: Awareness Call")
    print("-" * 50)
    
    payload = {
        "to_number": "+15551234567",
        "org_name": "sample_org",
        "call_type": "awareness",
        "message": "We have new operating hours starting next week. We will now be open from 8 AM to 6 PM.",
        "gather_response": False
    }
    
    response = requests.post(f"{BASE_URL}/voice/outbound", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


# Example 3: Survey Call (with response gathering)
def example_survey():
    """Send a survey call and record response."""
    print("Example 3: Survey Call")
    print("-" * 50)
    
    payload = {
        "to_number": "+15551234567",
        "org_name": "sample_org",
        "call_type": "survey",
        "message": "How satisfied are you with our services? Please rate from 1 to 5.",
        "gather_response": True  # Will record user's spoken response
    }
    
    response = requests.post(f"{BASE_URL}/voice/outbound", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


# Example 4: Bulk Calls (Multiple Recipients)
def example_bulk():
    """Send the same message to multiple numbers."""
    print("Example 4: Bulk Outbound Calls")
    print("-" * 50)
    
    payload = {
        "to_numbers": [
            "+15551234567",
            "+15559876543",
            "+15555555555"
        ],
        "org_name": "sample_org",
        "call_type": "awareness",
        "message": "This is an important update from our organization. Please visit our website for more details."
    }
    
    response = requests.post(f"{BASE_URL}/voice/outbound/bulk", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


# Example 5: Test TwiML Response
def example_test_twiml():
    """Test the TwiML response generation without making a call."""
    print("Example 5: Test TwiML Generation")
    print("-" * 50)
    
    # Test reminder TwiML
    response = requests.post(
        f"{BASE_URL}/voice/outbound-response",
        params={
            "type": "reminder",
            "org": "sample_org",
            "message": "Test reminder message",
            "gather": "false"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"TwiML Response:\n{response.text}")
    print()


def print_usage():
    """Print usage instructions."""
    print("=" * 70)
    print("AI Voice Calling Agent - Outbound Calling Examples")
    print("=" * 70)
    print()
    print("Before running these examples:")
    print("1. Make sure your server is running: uvicorn app.main:app --reload")
    print("2. Configure Twilio credentials in .env:")
    print("   - TWILIO_ACCOUNT_SID")
    print("   - TWILIO_AUTH_TOKEN")
    print("   - TWILIO_PHONE_NUMBER")
    print("   - BASE_URL (your ngrok or server URL)")
    print()
    print("3. Replace '+15551234567' with real phone numbers")
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    print_usage()
    
    print("Choose an example to run:")
    print("1. Reminder Call")
    print("2. Awareness Call")
    print("3. Survey Call (with recording)")
    print("4. Bulk Calls")
    print("5. Test TwiML (no actual call)")
    print("0. Run all examples")
    print()
    
    choice = input("Enter choice (0-5): ").strip()
    
    if choice == "1":
        example_reminder()
    elif choice == "2":
        example_awareness()
    elif choice == "3":
        example_survey()
    elif choice == "4":
        example_bulk()
    elif choice == "5":
        example_test_twiml()
    elif choice == "0":
        example_reminder()
        example_awareness()
        example_survey()
        example_bulk()
        example_test_twiml()
    else:
        print("Invalid choice")
    
    print("\n✅ Example completed!")
    print("\nCheck your Twilio console for call status:")
    print("https://console.twilio.com/us1/monitor/logs/calls")
