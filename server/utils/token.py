# AgriCare/server/utils/token.py

import jwt
import time
from datetime import timedelta
from config import Config
from fastapi import HTTPException, Depends, Request
from sqlalchemy.orm import Session
from db import get_db
from models.user import User
from models.farmer import Farmer
from models.labour import Labour
from utils.helper import request_to_token
from models.user import REVERSE_ROLE_MAP, ROLE_MAP

def create_token(data: dict) -> str:
    now = int(time.time())
    expiry = now + int(timedelta(days=Config.JWT_EXPIRE_DAYS).total_seconds())
    data.update({"exp": expiry, "iat": now, "nbf": now})
    token = jwt.encode(data, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=Config.JWT_ALGORITHM)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token has expired!")
    except:
        raise HTTPException(401, "Invalid token!")
    

def require_role(required_role: int):
    def role_checker(token: str = Depends(request_to_token)):
        payload = verify_token(token)
        if payload.get("role") != REVERSE_ROLE_MAP.get(required_role):
            raise HTTPException(status_code=403, detail="Forbidden")

    return Depends(role_checker)


def token_to_farmer_id(db: Session, token: str) -> int:
    payload = verify_token(token)
    email = payload.get("email")
    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    farmer = db.query(Farmer).filter_by(user_id=user.id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    return farmer.id

def token_to_user_id(db: Session, token: str) -> int:
    payload = verify_token(token)
    email = payload.get("email")
    phone = payload.get("phone")
    user_by_email = db.query(User).filter_by(email=email).first() if email else None
    user_by_phone = db.query(User).filter_by(phone=phone).first() if phone else None

    user = user_by_email or user_by_phone
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id