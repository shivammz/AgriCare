# AgriCare/server/api/auth/signup.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from utils.user import get_user_by_email, get_user_by_phone, create_user
from schemas.user import UserBase
from utils.helper import extract_phone

signup_router = APIRouter(prefix="/api", tags=["Auth"])

@signup_router.post("/signup", status_code=201)
async def signup(user_data: UserBase, db: Session = Depends(get_db)):
    if user_data.email and get_user_by_email(user_data.email, db):
        raise HTTPException(400, "Email Address is already in use!")

    if user_data.phone:
        user_data.phone = extract_phone(user_data.phone)
        if get_user_by_phone(user_data.phone, db):
            raise HTTPException(400, "Phone number is already in use!")
    
    if user_data.role not in ["farmer", "labour"]:
        raise HTTPException(400, detail="Invalid role!")
    
    create_user(user_data, db)
    return {"message": "Signup successfull!"}

