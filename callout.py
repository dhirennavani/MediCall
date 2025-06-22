import os
import requests
import json
import time
from datetime import datetime

def make_appointment_call(doctor_info, patient_info, insurance_info):
    """
    Make a phone call to schedule an appointment with a doctor
    
    Args:
        doctor_info (dict): Doctor's information including name, phone, address
        patient_info (dict): Patient information including name, preferred dates
        insurance_info (dict): Insurance details from the card
    
    Returns:
        dict: Call result with status and details
    """
    
    phone_number = doctor_info.get('phone', '')
    doctor_name = doctor_info.get('title', 'Unknown Doctor')
    doctor_address = doctor_info.get('address', 'Unknown Address')
    
    print(f"📞 Initiating call to {doctor_name}")
    print(f"📍 Location: {doctor_address}")
    print(f"☎️  Phone: {phone_number}")
    
    # Simulate call initiation
    print("🔄 Dialing...")
    time.sleep(2)
    
    # Here you would integrate with a service like Twilio, Bland AI, or similar
    # For now, we'll simulate the call process
    
    call_script = generate_call_script(doctor_info, patient_info, insurance_info)
    
    # Simulate call execution
    call_result = simulate_call_execution(phone_number, call_script)
    
    return call_result

def generate_call_script(doctor_info, patient_info, insurance_info):
    """Generate a script for the appointment booking call"""
    
    # script = f"""
    # Hello, I'm calling to schedule an appointment for {patient_info.get('name', 'a patient')}.
    
    # Patient Information:
    # - Name: {patient_info.get('name', 'Not provided')}
    # - Insurance: {insurance_info.get('insurance_company', 'Not provided')}
    # - Member ID: {insurance_info.get('member_id', 'Not provided')}
    # - Plan Type: {insurance_info.get('plan_type', 'Not specified')}
    
    # We're looking for the earliest available appointment for a {patient_info.get('appointment_type', 'general consultation')}.
    
    # Preferred times: {patient_info.get('preferred_times', 'Flexible with scheduling')}
    
    # Is there anything specific I should know about your scheduling process or requirements?
    # """

    agent_prompt = f"""
        You are an AI assistant acting as a representative for {insurance_info.get('insured_name', 'Unknown Name')}.
        Your primary goal is to call the office of {doctor_info.get('title', 'Unknown Doctor')} to schedule a new patient appointment for {insurance_info.get('insured_name', 'Unknown Name')}.

        **Your Task:**
        You will be connected to the doctor's office. Your task is to navigate the conversation to book an appointment.

        **Patient Information:**
        {patient_info}
        **Insurance Details (Provide these when asked):**
        {insurance_info}
        **Doctor Information:**
        {doctor_info}
        **Conversation Flow:**
        1.  **Introduction:** When the call is answered, introduce yourself politely. For example: "Hello, my name is Alex. I'm calling to schedule a new patient appointment for {insurance_details['insured_name']}."
        2.  **State Your Goal:** Clearly state that you are looking to book a new patient appointment with {doctor_name}.
        3.  **Provide Information:** Answer any questions the receptionist has. Use the insurance details provided above. Be prepared to spell out names and numbers if necessary.
        4.  **Scheduling:** Find a suitable date and time for the appointment. If you are not given specific availability, you can suggest a general timeframe, like "next Tuesday afternoon."
        5.  **Confirmation:** Before ending the call, confirm the appointment details: date, time, location, and that the appointment is with {doctor_name}.
        6.  **Contingency:** If the office is not accepting new patients, politely thank them and end the call.

        **Your Persona:**
        - Be friendly, patient, and professional.
        - Speak clearly and concisely.
        - If you don't understand something, it's okay to ask for clarification.
        - If you are not able to book an appointment, thank them and end the call.
        """
    
    return agent_prompt.strip()

def simulate_call_execution(phone_number, script):
    """Simulate the execution of a phone call"""
    
    print("📋 Call script prepared:")
    print("-" * 40)
    print(script)
    print("-" * 40)
    
    # Simulate call duration
    print("⏳ Call in progress...")
    time.sleep(3)
    
    # Simulate different call outcomes
    import random
    outcomes = [
        {
            "status": "success",
            "message": "Appointment scheduled successfully",
            "appointment_date": "2024-01-15 10:30 AM",
            "confirmation_number": f"APPT-{random.randint(1000, 9999)}"
        },
        {
            "status": "voicemail",
            "message": "Left voicemail with callback request",
            "follow_up_needed": True
        },
        {
            "status": "busy",
            "message": "Line busy, will retry later",
            "retry_scheduled": True
        },
        {
            "status": "no_availability",
            "message": "No immediate availability, added to waiting list",
            "waiting_list_position": random.randint(1, 10)
        }
    ]
    
    result = random.choice(outcomes)
    result["call_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result["phone_number"] = phone_number
    
    print(f"✅ Call completed: {result['message']}")
    
    return result

def integrate_with_calling_service(phone_number, script):
    """
    Placeholder for integration with actual calling services like:
    - Twilio Voice API
    - Bland AI
    - Vapi
    - OpenAI Realtime API
    """
    
    # Example Twilio integration (commented out):
    """
    from twilio.rest import Client
    
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    
    call = client.calls.create(
        twiml=f'<Response><Say>{script}</Say></Response>',
        to=phone_number,
        from_='+1234567890'  # Your Twilio number
    )
    
    return call.sid
    """
    
    # Example Bland AI integration (commented out):
    """
    bland_api_key = os.getenv('BLAND_API_KEY')
    
    response = requests.post(
        'https://api.bland.ai/v1/calls',
        headers={
            'Authorization': f'Bearer {bland_api_key}',
            'Content-Type': 'application/json'
        },
        json={
            'phone_number': phone_number,
            'task': script,
            'voice': 'maya',
            'language': 'en'
        }
    )
    
    return response.json()
    """
    
    pass

def log_call_result(call_result, log_file="call_log.json"):
    """Log call results to a file for tracking"""
    
    try:
        # Read existing log
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = {"calls": []}
        
        # Add new call result
        log_data["calls"].append(call_result)
        
        # Write back to file
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
            
        print(f"📝 Call result logged to {log_file}")
        
    except Exception as e:
        print(f"❌ Error logging call result: {e}")

def batch_call_doctors(doctors_list, patient_info, insurance_info):
    """Make calls to multiple doctors in sequence"""
    
    results = []
    
    for i, doctor in enumerate(doctors_list, 1):
        print(f"\n{'='*50}")
        print(f"📞 Call {i}/{len(doctors_list)}")
        print(f"{'='*50}")
        
        try:
            result = make_appointment_call(doctor, patient_info, insurance_info)
            result["doctor_info"] = doctor
            results.append(result)
            
            # Log each call
            log_call_result(result)
            
            # Add delay between calls
            if i < len(doctors_list):
                print("⏸️  Waiting before next call...")
                time.sleep(5)
                
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Call failed: {str(e)}",
                "doctor_info": doctor,
                "call_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            results.append(error_result)
            print(f"❌ Error calling {doctor.get('title', 'Unknown')}: {e}")
    
    return results