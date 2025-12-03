# AgriCare/server/utils/location.py

from config import Config
from utils.httpx import get_http_client

GOOGLE_MAPS_API_KEY = Config.GOOGLE_MAPS_API_KEY

async def reverse_geocode(latitude: float, longitude: float) -> str:
    """Reverse geocode coordinates to address. Returns fallback if API fails."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{latitude},{longitude}",
        "key": GOOGLE_MAPS_API_KEY
    }

    try:
        client = get_http_client()
        response = await client.get(url=url, params=params)
        data = response.json()

        if data.get("status") == "OK":
            return data['results'][0]['formatted_address'][:100]
        else:
            print(f"⚠️ Google Maps API error: {data.get('status')} - {data.get('error_message', 'No error message')}")
            # Return fallback location string
            return f"Location: {latitude:.4f}, {longitude:.4f}"
    except Exception as e:
        print(f"⚠️ Reverse geocoding failed: {e}")
        # Return fallback location string
        return f"Location: {latitude:.4f}, {longitude:.4f}"



