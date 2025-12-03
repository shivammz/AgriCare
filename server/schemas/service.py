# AgriCare/server/schemas/service.py

from pydantic import BaseModel, Field
from typing import Optional

class ServiceBase(BaseModel):
    service_name: str = Field(..., max_length=30)
    description: Optional[str] = None
    latitude: float
    longitude: float
    cost: float
    status: Optional[int] = 1

class ServiceResponse(ServiceBase):
    id: int
    location: str
    h3_index: str
    farmer_id: int
    farmer_name: str

    class Config:
        from_attributes = True
