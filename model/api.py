# api.py
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dotenv import load_dotenv
import io
from PIL import Image
import base64
import json

load_dotenv()

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your Gemini API Key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")


GEMINI_API_URL = os.getenv("GEMINI_API_URL")


async def detect_disease_with_gemini(image_bytes: bytes, language: str = "English"):
    """
    Send image to Gemini API for plant disease detection
    """
    try:
        # Convert image to base64
        img_base64 = base64.b64encode(image_bytes).decode("utf-8")
        
        # Determine MIME type
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image_format = image.format.lower()
            if image_format == 'jpeg' or image_format == 'jpg':
                mime_type = "image/jpeg"
            elif image_format == 'png':
                mime_type = "image/png"
            elif image_format == 'webp':
                mime_type = "image/webp"
            else:
                mime_type = "image/jpeg"
        except:
            mime_type = "image/jpeg"
        
        # Create prompt for disease detection
        prompt = f"""You are an expert agricultural AI assistant specializing in plant disease diagnosis.

Analyze this image of a plant/crop and provide a detailed disease diagnosis.

Instructions:
1. Identify the crop/plant type
2. Detect if there is any disease present
3. If disease found, identify the specific disease name
4. Provide detailed information in {language} language

Respond in JSON format with these exact keys:
{{
    "result": true/false,
    "message": "Brief status message",
    "crop": "Name of the crop/plant",
    "disease": "Name of the disease (or 'Healthy' if no disease)",
    "precautions": "Detailed advice including: \\n1) Disease description\\n2) Causes\\n3) Symptoms\\n4) Treatment (chemical and organic)\\n5) Prevention methods\\n6) Early detection tips"
}}

If the image is not a plant/crop, set result to false and provide appropriate message.
Provide all advice in {language} language in simple words suitable for farmers."""

        # Prepare request payload with image
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        },
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": img_base64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 2048,
            }
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }

        # Call Gemini API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(GEMINI_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()

        # Extract response
        candidates = result.get('candidates', [])
        if not candidates:
            return {
                "result": False,
                "message": "No response from Gemini AI",
                "crop": "Unknown",
                "disease": "Unknown",
                "precautions": ""
            }

        # Get text content
        content = candidates[0].get('content', {})
        parts = content.get('parts', [])
        text_response = "".join([part.get('text', '') for part in parts])

        # Parse JSON response
        # Remove markdown code blocks if present
        text_response = text_response.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.startswith("```"):
            text_response = text_response[3:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
        text_response = text_response.strip()

        # Parse JSON
        try:
            parsed_result = json.loads(text_response)
            return {
                "result": parsed_result.get("result", True),
                "message": parsed_result.get("message", "Analysis complete"),
                "crop": parsed_result.get("crop", "Unknown"),
                "disease": parsed_result.get("disease", "Unknown"),
                "precautions": parsed_result.get("precautions", text_response)
            }
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw response
            return {
                "result": True,
                "message": "Analysis complete (raw format)",
                "crop": "See precautions",
                "disease": "See precautions",
                "precautions": text_response
            }

    except httpx.HTTPStatusError as e:
        return {
            "result": False,
            "message": f"API Error: {e.response.status_code} - {e.response.text}",
            "crop": "Error",
            "disease": "Error",
            "precautions": ""
        }
    except Exception as e:
        return {
            "result": False,
            "message": f"Error: {str(e)}",
            "crop": "Error",
            "disease": "Error",
            "precautions": ""
        }


@app.post("/predict/{language}")
async def predict(language: str, file: UploadFile = File(...)):
    """
    Main endpoint for disease prediction using Gemini AI
    """
    image_bytes = await file.read()
    result = await detect_disease_with_gemini(image_bytes, language)
    return result


@app.get("/")
async def root():
    return {
        "message": "Plant Disease Detection API with Gemini AI",
        "status": "running",
        "endpoint": "/predict/{language}"
    }
