from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from typing import Optional

app = FastAPI(title="MediCall API", description="Insurance card processing API")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "MediCall API is running"}

@app.post("/upload-insurance")
async def upload_insurance(
    file: UploadFile = File(...),
    query_data: str = Form(...)
):
    """
    Upload insurance card image with structured query data
    """
    try:
        # Check if file is an image
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Parse the structured JSON data
        try:
            query_json = json.loads(query_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON data")
        
        # Print image details
        print("=" * 50)
        print("IMAGE DETAILS:")
        print(f"Image received: {file.filename}")
        print(f"Content type: {file.content_type}")
        print(f"File size: {file.size} bytes")
        
        # Read the file content as blob
        content = await file.read()
        print(f"Image blob received - length: {len(content)} bytes")
        
        # Print structured query details
        print("\nSTRUCTURED QUERY DETAILS:")
        print(f"Original Query: {query_json.get('original_query', 'N/A')}")
        print(f"Doctor Type: {query_json.get('doctor_type', 'N/A')}")
        print(f"Location: {query_json.get('location', 'N/A')}")
        print(f"Date: {query_json.get('date', 'N/A')}")
        print(f"Insurance Provider: {query_json.get('insurance_provider', 'N/A')}")
        print("=" * 50)
        
        # Simulate finding an appointment
        appointment_details = {
            "doctor_name": "Dr. Susan Bones",
            "specialty": query_json.get('doctor_type', 'General Physician'),
            "location": query_json.get('location', 'N/A'),
            "address": "123 Health St, Medical City",
            "appointment_time": "2024-10-28T10:00:00Z",
            "notes": "Please bring your insurance card and a form of ID."
        }

        return {
            "message": "Appointment successfully found",
            "appointment_details": appointment_details,
            "image": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": file.size,
                "blob_size": len(content)
            },
            "query_data": query_json
        }
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 