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
import sys

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

# Add parent directory to path to import callout functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import real calling functions
from callout import make_appointment_call, batch_call_doctors, generate_call_script
from calloutbound import create_outbound_call

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
        
        # Prepare patient and insurance info for calling
        # Get patient name from insurance details or frontend query
        patient_name = None
        
        # Try to get name from insurance details first
        dependent_name = insurance_details.get("dependent_name")
        insured_name = insurance_details.get("insured_name")
        
        if dependent_name and dependent_name != "null" and dependent_name != "N/A":
            patient_name = dependent_name
        elif insured_name and insured_name != "null" and insured_name != "N/A":
            patient_name = insured_name
        else:
            # Fallback to frontend query or default
            patient_name = query_json.get('patient_name', 'Patient')
        
        # Debug patient name extraction
        print(f"\nPATIENT NAME DEBUG:")
        print(f"  dependent_name: '{insurance_details.get('dependent_name')}' (type: {type(insurance_details.get('dependent_name'))})")
        print(f"  insured_name: '{insurance_details.get('insured_name')}' (type: {type(insurance_details.get('insured_name'))})")
        print(f"  frontend patient_name: '{query_json.get('patient_name')}'")
        print(f"  final patient_name: '{patient_name}'")
        
        # Add the resolved patient name to the insurance_details dictionary for the frontend
        insurance_details['patient_name'] = patient_name
        
        # Step 2: Use extracted insurance details and frontend query to search for doctors
        insurance_provider = insurance_details.get("insurance_company", "")
        location = query_json.get('location', 'Boston, MA')  # Use location from frontend query
        doctor_type = query_json.get('doctor_type', 'General Physician')  # Use doctor type from frontend query
        
        print(f"\nSEARCHING FOR DOCTORS...")
        print(f"Insurance Provider: {insurance_provider}")
        print(f"Location: {location}")
        print(f"Doctor Type: {doctor_type}")
        
        doctors = search_doctors(insurance_provider, location, doctor_type)
        
        patient_info = {
            "name": patient_name,
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
                call_result = await make_appointment_call(selected_doctor, patient_info, insurance_info)
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
        
        call_result = await make_appointment_call(doctor_info, patient_info, insurance_info)
        
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
                result = await make_appointment_call(doctor, patient_info, insurance_info)
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