import requests
import re
import os 
import base64
import json
import time
from callout import batch_call_doctors, make_appointment_call

serp_api_key = os.getenv("SERP_API_KEY")
# Replace with your actual SerpAPI key
endpoint = "https://serpapi.com/search"

def serp_search(query, location):
    print(query, location)
    params = {
        "q": query,
        "location": location,
        "hl": "en",
        "gl": "us",
        "num": 15,
        "api_key": serp_api_key,
        # Add parameters to get more local results
        "tbm": "lcl",  # Force local search
        "near": location,  # Specify near parameter
        "start": 0  # Start from first result
    }
    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    return response.json()

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
            response = requests.get(endpoint, params=params)
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
            import traceback
            traceback.print_exc()
            break
    
    return all_doctors

def search_doctors(insurance_provider, location, doctor_type):
    query = f"{doctor_type} doctors accepting {insurance_provider} insurance in {location}"
    
    print(f"Searching for {query}")
    
    # Use the multi-page function to get more results
    doctors = get_multiple_pages_local_results(query, max_pages=3)
    
    if not doctors:
        print("No search results found.")
        return []

    print(f"Total unique doctors found: {len(doctors)}")
    return doctors

def image_to_base64(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")

def get_inurance_card_data():
    base64_image = image_to_base64("image3.jpeg")
    response = requests.post(
        url="https://api.llama.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('LLAMA_API_KEY')}"
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
                                "description": "Name of the person receiving care if different from insured (e.g., child or spouse). Might sayReturn null if not listed."
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
        }
    )
    response_data = response.json()
    parsed_data = {}
    # Extract and print the text content
    if 'completion_message' in response_data and 'content' in response_data['completion_message']:
        extracted_text = response_data['completion_message']['content']['text']        
        # Parse the JSON text
        try:
            parsed_data = json.loads(extracted_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
    return parsed_data


def main():
    # Sample input — replace with actual values
    print("Starting the appointment booking process...")
    print("-" * 50)
    print("Extracting insurance details from the card...")
    print("-" * 50)

    insurance_details = get_inurance_card_data()
    insurance_provider = insurance_details.get("insurance_company", "")
    insurance_id = insurance_details.get("member_id", "")
    insurer_name = insurance_details.get("insurance_company", "")
    dependent_name = insurance_details.get("dependent_name", "Self")
    plan_type = insurance_details.get("plan_type", "General")
    location = "Boston, MA"
    doctor_type = "pediatrician"
    
    print(f"Found Insurance Provider: {insurance_provider}")
    print("-" * 50)
    
    doctors = search_doctors(insurance_provider, location, doctor_type)
    print("-" * 50)
    
    # Prepare patient info structure
    patient_info = {
        "name": dependent_name,
        "appointment_type": f"{doctor_type} consultation",
        "preferred_times": "Flexible with scheduling"
    }
    
    # Prepare insurance info structure
    insurance_info = {
        "insurance_company": insurance_provider,
        "member_id": insurance_id,
        "plan_type": plan_type
    }
    
    print("-" * 50)
    
    # Option 1: Call doctors one by one
    for doctor in doctors[0:1]:
        print(f"Trying to book appointment with {doctor['title']} at {doctor['address']} for {dependent_name} with ({insurance_provider})")
        result = make_appointment_call(doctor, patient_info, insurance_info)
        print(f"Result: {result}")
        time.sleep(5)
        print("-" * 50)
    
    # Option 2: Batch call all doctors (uncomment to use instead)
    # results = batch_call_doctors(doctors, patient_info, insurance_info)
    # print(f"\nCompleted {len(results)} calls:")
    # for result in results:
    #     doctor_name = result.get('doctor_info', {}).get('title', 'Unknown')
    #     print(f"- {doctor_name}: {result['status']} - {result['message']}")
    
    print("Appointment booking process completed.")
if __name__ == "__main__":
    main()
