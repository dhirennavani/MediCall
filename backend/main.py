from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import base64
import os
import requests
import re
import time
from datetime import datetime
from typing import Optional

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed, using system environment variables")

app = FastAPI(title="MediCall API", description="Insurance card processing and doctor search API")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
serp_api_key = os.getenv("SERP_API_KEY")
llama_api_key = os.getenv("LLAMA_API_KEY")

# Check if API keys are available
if not llama_api_key:
    print("WARNING: LLAMA_API_KEY environment variable not set. Insurance card processing will use fallback data.")
if not serp_api_key:
    print("WARNING: SERP_API_KEY environment variable not set. Doctor search will not work.")

def extract_phone(text):
    """Extract phone number from snippet using regex"""
    match = re.search(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text)
    return match.group(1) if match else None

def get_multiple_pages_local_results(query, max_pages=3):
    """Get multiple pages of local results to increase the number of doctors found"""
    all_doctors = []
    
    for page in range(max_pages):
        params = {
            "q": query,
            "hl": "en",
            "gl": "us",
            "api_key": serp_api_key,
            "tbm": "lcl",  # Force local search
            "start": page * 20  # Pagination
        }
        
        try:
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            results = response.json()
                        
            # Handle different possible response structures
            places = []
            if "local_results" in results:
                local_results = results["local_results"]
                
                if isinstance(local_results, dict):
                    if "places" in local_results:
                        places = local_results["places"]
                elif isinstance(local_results, list):
                    places = local_results
            elif "places" in results:
                places = results["places"]
            
            if places:
                for place in places:
                    if isinstance(place, dict):
                        # Avoid duplicates by checking if doctor already exists
                        doctor_info = {
                            "title": place.get("title", "Unknown"),
                            "phone": place.get("phone", "N/A"),
                            "address": place.get("address", "N/A"),
                            "website": place.get("links", {}).get("website", "N/A") if "links" in place else "N/A"
                        }
                        
                        # Check if this doctor is already in our list
                        if not any(d["title"] == doctor_info["title"] and d["address"] == doctor_info["address"] for d in all_doctors):
                            all_doctors.append(doctor_info)
            
        except Exception as e:
            print(f"Error on page {page + 1}: {e}")
            break
    
    return all_doctors

def search_doctors(insurance_provider, location, doctor_type):
    if not serp_api_key:
        print("SERP_API_KEY not available, returning fallback doctors")
        return [
            {
                "title": "Dr. General Practitioner",
                "phone": "(555) 123-4567",
                "address": f"General Medical Center, {location}",
                "website": "N/A"
            }
        ]
    
    query = f"{doctor_type} doctors accepting {insurance_provider} insurance in {location}"
    
    print(f"Searching for {query}")
    
    # Use the multi-page function to get more results
    doctors = get_multiple_pages_local_results(query, max_pages=3)
    
    if not doctors:
        print("No search results found.")
        return []

    print(f"Total unique doctors found: {len(doctors)}")
    return doctors

def generate_call_script(doctor_info, patient_info, insurance_info):
    """Generate a script for the appointment booking call"""
    
    agent_prompt = f"""
        You are an AI assistant acting as a representative for {patient_info.get("name", "Unknown Name")}.
        Your primary goal is to call the office of {doctor_info.get('title', 'Unknown Doctor')} to schedule a new patient appointment for {patient_info.get("name", "Unknown Name")}.

        **Your Task:**
        You will be connected to the doctor's office. Your task is to navigate the conversation to book an appointment.

        **Patient Information:**
        {patient_info}
        **Insurance Details (Provide these when asked):**
        {insurance_info}
        **Doctor Information:**
        {doctor_info}
        **Conversation Flow:**
        1.  **Introduction:** When the call is answered, introduce yourself politely. For example: "Hello, my name is Alex. I'm calling to schedule a new patient appointment for {patient_info.get("name", "Unknown Name")}."
        2.  **State Your Goal:** Clearly state that you are looking to book a new patient appointment with {doctor_info.get("title", "Unknown Doctor")}.
        3.  **Provide Information:** Answer any questions the receptionist has. Use the insurance details provided above. Be prepared to spell out names and numbers if necessary.
        4.  **Scheduling:** Find a suitable date and time for the appointment. If you are not given specific availability, you can suggest a general timeframe, like "next Tuesday afternoon."
        5.  **Confirmation:** Before ending the call, confirm the appointment details: date, time, location, and that the appointment is with {doctor_info.get("title", "Unknown Doctor")}.
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
    
    call_script = generate_call_script(doctor_info, patient_info, insurance_info)
    print(call_script)
    
    # Simulate call execution
    call_result = simulate_call_execution(phone_number, call_script)
    
    return call_result

def get_insurance_card_data_from_blob(image_blob):
    """Extract insurance card data from image blob using Llama API"""
    try:
        # Convert blob to base64
        base64_image = base64.b64encode(image_blob).decode("utf-8")
        print(f"Image converted to base64, length: {len(base64_image)}")
        
        # Check if API key is available
        if not llama_api_key:
            print("ERROR: LLAMA_API_KEY environment variable not set")
            return {}
        
        print("Making request to Llama API...")
        response = requests.post(
            url="https://api.llama.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {llama_api_key}"
            },
            json={
                "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "This is an insurance card. Extract key insurance details required to book a medical appointment. "
                                    "Output should be a JSON object with only the requested fields. If a field is not visible or unclear, return `null`. "
                                    "Do not infer values. Follow this schema strictly."
                                )
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "InsuranceCardExtraction",
                        "description": "Extracted insurance card details required for appointment booking.",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "member_id": {
                                    "type": "string",
                                    "description": "Member ID or policy number used to identify the insured person (often labeled as ID #, Member ID, Policy #)"
                                },
                                "group_number": {
                                    "type": "string",
                                    "description": "Group or plan number (often labeled as Group # or Plan #)"
                                },
                                "insured_name": {
                                    "type": "string",
                                    "description": "Full name of the primary insured person"
                                },
                                "dependent_name": {
                                    "type": "string",
                                    "description": "Name of the person receiving care if different from insured (e.g., child or spouse). Return null if not listed."
                                },
                                "insurance_company": {
                                    "type": "string",
                                    "description": "Name of the insurance provider (e.g., Premera Blue Cross, Aetna, Cigna)"
                                },
                                "plan_type": {
                                    "type": "string",
                                    "description": "Type of plan (e.g., PPO, HMO, EPO). If not clearly stated, return null."
                                },
                                "customer_service_number": {
                                    "type": "string",
                                    "description": "Phone number on the card for provider inquiries or customer service"
                                },
                                "rx_bin": {
                                    "type": "string",
                                    "description": "RX BIN number for pharmacy processing (if available)"
                                },
                                "rx_pcn": {
                                    "type": "string",
                                    "description": "RX PCN number for pharmacy processing (if available)"
                                }
                            },
                            "required": [
                                "member_id",
                                "insured_name",
                                "insurance_company",
                                "dependent_name"
                            ]
                        }
                    }
                }
            },
            timeout=30
        )
        
        print(f"Llama API response status: {response.status_code}")
        
        if not response.ok:
            print(f"Llama API error: {response.status_code} - {response.text}")
            return {}
        
        response_data = response.json()
        print(f"Llama API response keys: {list(response_data.keys())}")
        
        parsed_data = {}
        
        # Extract and parse the JSON content
        if 'completion_message' in response_data and 'content' in response_data['completion_message']:
            extracted_text = response_data['completion_message']['content']['text']        
            print(f"Extracted text from Llama: {extracted_text[:200]}...")
            try:
                parsed_data = json.loads(extracted_text)
                print(f"Successfully parsed JSON with {len(parsed_data)} fields")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                print(f"Raw response: {extracted_text}")
        else:
            print(f"Unexpected response structure: {response_data}")
        
        return parsed_data
        
    except Exception as e:
        print(f"Exception in get_insurance_card_data_from_blob: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}

@app.get("/")
async def root():
    return {"message": "MediCall API is running"}

@app.post("/upload-insurance")
async def upload_insurance(
    file: UploadFile = File(...),
    query_data: str = Form(...),
    make_call: bool = Form(False)
):
    """
    Upload insurance card image with structured query data and process the complete booking flow
    Optionally make an appointment call if make_call is True
    """
    try:
        # Check if file is an image
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Parse the structured JSON data from frontend
        try:
            query_json = json.loads(query_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON data")
        
        # Read the file content as blob
        content = await file.read()
        
        print("=" * 50)
        print("PROCESSING INSURANCE CARD AND QUERY")
        print("=" * 50)
        
        # Print image details
        print("IMAGE DETAILS:")
        print(f"Image received: {file.filename}")
        print(f"Content type: {file.content_type}")
        print(f"File size: {file.size} bytes")
        print(f"Image blob received - length: {len(content)} bytes")
        
        # Print structured query details
        print("\nSTRUCTURED QUERY DETAILS:")
        print(f"Original Query: {query_json.get('original_query', 'N/A')}")
        print(f"Doctor Type: {query_json.get('doctor_type', 'N/A')}")
        print(f"Location: {query_json.get('location', 'N/A')}")
        print(f"Date: {query_json.get('date', 'N/A')}")
        print(f"Insurance Provider: {query_json.get('insurance_provider', 'N/A')}")
        print(f"Make Call: {make_call}")
        
        # Step 1: Extract insurance card data from the uploaded image
        print("\nEXTRACTING INSURANCE CARD DATA...")
        insurance_details = get_insurance_card_data_from_blob(content)
        
        # If insurance extraction failed, use fallback data
        if not insurance_details:
            print("Insurance extraction failed, using fallback data")
            insurance_details = {
                "member_id": "N/A",
                "insured_name": "N/A",
                "insurance_company": "General Insurance",
                "dependent_name": "N/A",
                "plan_type": "N/A",
                "customer_service_number": "N/A"
            }
        
        print("EXTRACTED INSURANCE DETAILS:")
        for key, value in insurance_details.items():
            print(f"  {key}: {value}")
        
        # Step 2: Use extracted insurance details and frontend query to search for doctors
        insurance_provider = insurance_details.get("insurance_company", "")
        location = query_json.get('location', 'Boston, MA')  # Use location from frontend query
        doctor_type = query_json.get('doctor_type', 'General Physician')  # Use doctor type from frontend query
        
        print(f"\nSEARCHING FOR DOCTORS...")
        print(f"Insurance Provider: {insurance_provider}")
        print(f"Location: {location}")
        print(f"Doctor Type: {doctor_type}")
        
        doctors = search_doctors(insurance_provider, location, doctor_type)
        
        # Prepare patient and insurance info for calling
        patient_info = {
            "name": insurance_details.get("dependent_name", insurance_details.get("insured_name", "Patient")),
            "appointment_type": f"{doctor_type} consultation",
            "preferred_times": query_json.get('date', 'Flexible with scheduling')
        }
        
        insurance_info = {
            "insurance_company": insurance_provider,
            "member_id": insurance_details.get("member_id", "N/A"),
            "plan_type": insurance_details.get("plan_type", "N/A")
        }
        
        call_result = None
        
        if not doctors:
            # If no doctors found, create a fallback appointment
            appointment_details = {
                "doctor_name": "Dr. General Practitioner",
                "specialty": doctor_type,
                "location": location,
                "address": "General Medical Center, " + location,
                "appointment_time": "2024-10-28T10:00:00Z",
                "notes": "Please bring your insurance card and a form of ID. We'll help you find a specialist if needed.",
                "available_doctors": []
            }
        else:
            # Use the first available doctor for the appointment
            selected_doctor = doctors[0]
            appointment_details = {
                "doctor_name": selected_doctor["title"],
                "specialty": doctor_type,
                "location": location,
                "address": selected_doctor["address"],
                "appointment_time": "2024-10-28T10:00:00Z",
                "notes": f"Please bring your insurance card and a form of ID. Contact: {selected_doctor['phone']}",
                "available_doctors": doctors[:5]  # Include first 5 doctors found
            }
            
            # Step 3: Make appointment call if requested
            if make_call and selected_doctor.get('phone') != 'N/A':
                print(f"\nMAKING APPOINTMENT CALL...")
                call_result = make_appointment_call(selected_doctor, patient_info, insurance_info)
            elif make_call:
                print("Cannot make call - no valid phone number available")
        
        print("\nAPPOINTMENT DETAILS CREATED:")
        print(f"Doctor: {appointment_details['doctor_name']}")
        print(f"Address: {appointment_details['address']}")
        print(f"Available doctors found: {len(appointment_details['available_doctors'])}")
        
        response_data = {
            "message": "Appointment successfully found",
            "appointment_details": appointment_details,
            "insurance_details": insurance_details,
            "image": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": file.size,
                "blob_size": len(content)
            },
            "query_data": query_json
        }
        
        if call_result:
            response_data["call_result"] = call_result
        
        return response_data
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/make-appointment-call")
async def make_appointment_call_endpoint(
    doctor_info: dict,
    patient_info: dict,
    insurance_info: dict
):
    """
    Make an appointment call to a specific doctor
    """
    try:
        print("=" * 50)
        print("MAKING APPOINTMENT CALL")
        print("=" * 50)
        
        call_result = make_appointment_call(doctor_info, patient_info, insurance_info)
        
        return {
            "message": "Call completed",
            "call_result": call_result
        }
        
    except Exception as e:
        print(f"Error making appointment call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error making appointment call: {str(e)}")

@app.post("/batch-call-doctors")
async def batch_call_doctors_endpoint(
    doctors_list: list,
    patient_info: dict,
    insurance_info: dict
):
    """
    Make calls to multiple doctors in sequence
    """
    try:
        print("=" * 50)
        print("BATCH CALLING DOCTORS")
        print("=" * 50)
        
        results = []
        
        for i, doctor in enumerate(doctors_list, 1):
            print(f"\n{'='*50}")
            print(f"📞 Call {i}/{len(doctors_list)}")
            print(f"{'='*50}")
            
            try:
                result = make_appointment_call(doctor, patient_info, insurance_info)
                result["doctor_info"] = doctor
                results.append(result)
                
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
        
        return {
            "message": "Batch calls completed",
            "results": results
        }
        
    except Exception as e:
        print(f"Error in batch calling: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in batch calling: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 