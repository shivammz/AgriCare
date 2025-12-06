# AgriCare/server/api/auth/login.py

from fastapi import APIRouter, Depends, HTTPException
from schemas.user import EmailRequest, EmailOTPRequest, PhoneTokenRequest
from sqlalchemy.orm import Session
from db import get_db
from utils.user import get_user_by_email, get_user_by_phone
from utils.helper import extract_phone
from utils.otp import check_rate_limit, send_otp_to_email, verify_email_otp
from utils.token import create_token
from firebase_admin import auth
from models.user import REVERSE_ROLE_MAP

login_router = APIRouter(prefix="/api", tags=['Auth'])

@login_router.post("/login/email")
async def login_via_email(request: EmailRequest, db: Session = Depends(get_db)):
    email = request.email
    if not get_user_by_email(email, db):
        raise HTTPException(400, "Account does not exist!")
    
    otp = await check_rate_limit(email)
    try:
        await send_otp_to_email(email, otp)
        return {"message": "OTP sent successfully!"}
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        raise HTTPException(500, f"Failed to send OTP email: {str(e)}")
    

@login_router.post("/login/email/verify")
async def verify_email(request: EmailOTPRequest, db: Session = Depends(get_db)):
    email = request.email
    is_valid = await verify_email_otp(email, request.otp)
    if is_valid:
        user = get_user_by_email(email, db)
        if user:
            if user.role == 0:
                user_id = user.farmer.id
            elif user.role == 1:
                user_id = user.labour.id
        
            payload = {"id": str(user_id), "name": user.name, "email": user.email, "role": REVERSE_ROLE_MAP.get(user.role)}
            token = create_token(payload)
            return {"token" : token}
        raise HTTPException(status_code=401, detail="Account does not exist!")
    else:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP.")
    

@login_router.post("/login/phone/verify")
async def verify_phone(request: PhoneTokenRequest, db: Session = Depends(get_db)):
    try:
        decoded_token = auth.verify_id_token(request.id_token)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
    
    phone = decoded_token.get("phone_number")
    if phone:
        extracted_phone = extract_phone(phone)
        user = get_user_by_phone(extracted_phone, db)
        if user:
            if user.role == 0:
                user_id = user.farmer.id
            elif user.role == 1:
                user_id = user.labour.id
                
            payload = {"id": str(user_id), "name": user.name, "phone": user.phone, "role": REVERSE_ROLE_MAP.get(user.role)}
            token = create_token(payload)
            return {"token" : token}
        raise HTTPException(status_code=401, detail="Account does not exist!")
    else:
        raise HTTPException(status_code=401, detail="Phone number not found in token")
