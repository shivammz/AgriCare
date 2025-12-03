import httpx
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

async def test_geocoding():
    """Test Google Maps Geocoding API"""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    # Test coordinates from Jalandhar
    params = {
        "latlng": "31.2510782,75.6997394",
        "key": GOOGLE_MAPS_API_KEY
    }
    
    print(f"🔍 Testing Geocoding API...")
    print(f"📍 Coordinates: {params['latlng']}")
    print(f"🔑 API Key: {GOOGLE_MAPS_API_KEY[:20]}...")
    print()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            data = response.json()
            
            print(f"📡 Response Status: {response.status_code}")
            print(f"🎯 API Status: {data.get('status')}")
            
            if data.get('status') == 'OK':
                print(f"✅ SUCCESS!")
                print(f"📍 Address: {data['results'][0]['formatted_address']}")
            else:
                print(f"❌ ERROR!")
                print(f"🔴 Error Message: {data.get('error_message', 'No error message')}")
                print(f"📄 Full Response: {data}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_geocoding())
