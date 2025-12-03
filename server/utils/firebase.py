# AgriCare/server/utils/firebase.py

import os
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException
from pathlib import Path


if not firebase_admin._apps:
    # Try to load service account key
    service_account_path = Path(__file__).parent.parent / "serviceAccountKey.json"
    
    if service_account_path.exists():
        cred = credentials.Certificate(str(service_account_path))
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin initialized with service account")
    else:
        # Fallback to default credentials (works on Google Cloud)
        firebase_admin.initialize_app()
        print("⚠️ Firebase Admin initialized with default credentials")


def create_firebase_custom_token(uid: str) -> str:
    try:
        custom_token = auth.create_custom_token(uid)
        # Convert bytes to string if necessary
        if isinstance(custom_token, bytes):
            return custom_token.decode('utf-8')
        return custom_token
    except Exception as e:
       raise HTTPException(status_code=500, detail=f"Error creating firebase token: {e}")
