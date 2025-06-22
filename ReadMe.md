# MediCall - Insurance Card Processing

A web application for processing insurance cards and booking medical appointments with AI-powered query analysis.

## Setup

### Backend (FastAPI)

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run the FastAPI server:**
   ```bash
   cd backend
   python main.py
   ```

   The server will start at `http://localhost:8000`
   - API documentation: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Frontend (React + Vite)

1. **Set up environment variables:**
   Create a `.env` file in the `frontend` directory:
   ```bash
   cd frontend
   echo "VITE_LLAMA_API_KEY=your_llama_api_key_here" > .env
   ```
   
   **Note:** In Vite, environment variables must be prefixed with `VITE_` to be accessible in the frontend code.

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

   The frontend will start at `http://localhost:5173`

## Usage

1. Start both the backend and frontend servers
2. Open `http://localhost:5173` in your browser
3. Enter your appointment request (e.g., "I need to see a dermatologist in Boston next week")
4. Upload your insurance card image
5. The system will:
   - Use Llama AI to extract structured data from your query
   - Send both the image and structured JSON to the backend
   - Print detailed information in the backend console

## Features

- ✅ FastAPI backend with CORS support
- ✅ Image upload handling with blob support
- ✅ Llama AI integration for query analysis
- ✅ Structured JSON extraction (doctor type, location, date)
- ✅ Frontend integration with query input
- ✅ Error handling and validation
- ✅ Console logging of received data

## API Endpoints

- `POST /upload-insurance` - Upload insurance card image with structured query data
- `GET /health` - Health check
- `GET /` - Root endpoint

## Example Output

When you upload an image with a query like "I need to see a dermatologist in Boston next week", the backend will print:

```
==================================================
IMAGE DETAILS:
Image received: insurance_card.jpg
Content type: image/jpeg
File size: 123456 bytes
Image blob received - length: 123456 bytes

STRUCTURED QUERY DETAILS:
Original Query: I need to see a dermatologist in Boston next week
Doctor Type: dermatologist
Location: Boston
Date: next week
Insurance Provider: N/A
==================================================
```
