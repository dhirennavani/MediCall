import requests
import re
import os 
serp_api_key = os.getenv("SERP_API_KEY")
# Replace with your actual SerpAPI key
endpoint = "https://serpapi.com/search"

def serp_search(query, location):
    params = {
        "q": query,
        "location": location,
        "hl": "en",
        "gl": "us",
        "num": 15,
        "api_key": serp_api_key,
        # Add parameters to get more local results
        "tbm": "lcl",  # Force local search
        "ll": "@40.7128,-74.0060,14z",  # New York coordinates with zoom
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

def get_multiple_pages_local_results(query, location, max_pages=3):
    """Get multiple pages of local results to increase the number of doctors found"""
    all_doctors = []
    
    for page in range(max_pages):
        params = {
            "q": query,
            "location": location,
            "hl": "en",
            "gl": "us",
            "api_key": serp_api_key,
            "tbm": "lcl",  # Force local search
            "ll": "@40.7128,-74.0060,14z",  # New York coordinates with zoom
            "near": location,
            "start": page * 20  # Pagination
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            results = response.json()
            
            print(f"Page {page + 1} response keys: {list(results.keys())}")
            
            # Handle different possible response structures
            places = []
            if "local_results" in results:
                local_results = results["local_results"]
                print(f"Local results type: {type(local_results)}")
                
                if isinstance(local_results, dict):
                    print(f"Local results keys: {list(local_results.keys())}")
                    if "places" in local_results:
                        places = local_results["places"]
                elif isinstance(local_results, list):
                    print(f"Local results is a list with {len(local_results)} items")
                    places = local_results
            elif "places" in results:
                places = results["places"]
            
            if places:
                print(f"Page {page + 1}: Found {len(places)} places")
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
            else:
                print(f"Page {page + 1}: No places found in response")
            
        except Exception as e:
            print(f"Error on page {page + 1}: {e}")
            import traceback
            traceback.print_exc()
            break
    
    return all_doctors

def search_doctors(insurance_provider, location, doctor_type):
    query = f"{doctor_type} doctors accepting {insurance_provider} insurance"
    
    print(f"Searching SerpAPI for: {query} in {location}")
    
    # Use the multi-page function to get more results
    doctors = get_multiple_pages_local_results(query, location, max_pages=3)
    
    if not doctors:
        print("No search results found.")
        return []

    print(f"Total unique doctors found: {len(doctors)}")
    return doctors

def main():
    # Sample input — replace with actual values
    insurance_provider = "Aetna"
    insurance_id = "123456789"
    insurer_name = "Aetna Health Inc."
    location = "New York, NY"
    doctor_type = "Primary Care Physician"
    doctors = search_doctors(insurance_provider, location, doctor_type)
    doctor_type = "Dermatologist"
    for doctor in doctors:
        print(f"Name: {doctor['title']}")
        print(f"Phone: {doctor['phone']}")
        print(f"Address: {doctor['address']}")
        print(f"Website: {doctor['website']}")
        print("-" * 50)

if __name__ == "__main__":
    main()
