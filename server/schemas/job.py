# AgriCare/server/schemas/job.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class JobBase(BaseModel):
    title: str = Field(..., max_length=30)
    description: str
    number_of_labourers: int
    required_skills: Optional[List[str]] = None
    latitude: float
    longitude: float
    daily_wage: float
    perks: Optional[List[str]] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    status: Optional[int] = 1

class JobResponse(JobBase):
    id: int
    location: str
    h3_index: str
    farmer_id: int
    farmer_name: str

    class Config:
        from_attributes = True
