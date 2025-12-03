# AgriCare/server/api/chat.py

from fastapi import APIRouter, Depends, HTTPException, Request
from server.utils.firebase import create_firebase_custom_token
from server.utils.token import token_to_user_id, request_to_token
from sqlalchemy.orm import Session
from server.db import get_db

chat_router = APIRouter(prefix="/api")

@chat_router.post("/firebase-token", tags=["Chat"])
async def get_firebase_token(request: Request, db: Session = Depends(get_db)):
    token = request_to_token(request)
    user_id = token_to_user_id(db, token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Could not identify user")

    token = create_firebase_custom_token(f"user_{user_id}")

    return {"firebase_token": token}