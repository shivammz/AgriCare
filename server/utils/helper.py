import re
from fastapi import Request, HTTPException

def extract_phone(phone_number: str) -> str:
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone_number)

    return digits_only[-10:]

def request_to_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    return auth_header.split(" ")[1]
