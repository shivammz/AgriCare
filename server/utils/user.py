# AgriCare/server/utils/user.py

from sqlalchemy.orm import Session
from models.user import User, ROLE_MAP
from models.farmer import Farmer
from models.labour import Labour
from schemas.user import UserBase
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

def get_user_by_email(email: str, db: Session):
    return db.query(User).filter_by(email=email).first()

def get_user_by_phone(phone: str, db: Session):
    return db.query(User).filter_by(phone=phone).first()

def create_user(user_data: UserBase, db: Session):
    try:
        new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        role=ROLE_MAP[user_data.role])

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        if user_data.role == "farmer":
            new_farmer = Farmer(user_id=new_user.id)
            db.add(new_farmer)
        elif user_data.role == "labour":
            new_labour = Labour(user_id=new_user.id)
            db.add(new_labour)

        db.commit()
        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail="Database error. Please try again later.")
