# AgriCare/server/schemas/user.py

from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: str

    @model_validator(mode="after")
    def check_email_or_phone(self) -> 'UserBase':
        if not self.email and not self.phone:
            raise ValueError("Either Email Address or Phone is required!")
        
        return self
    
class EmailRequest(BaseModel):
    email: EmailStr


class EmailOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class PhoneTokenRequest(BaseModel):
    id_token : str