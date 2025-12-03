# AgriCare/server/models/job.py

from db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Float, Numeric, ARRAY, DateTime, SmallInteger
from sqlalchemy.orm import relationship

STATUS_MAP = {"closed": 0, "open": 1}

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    title = Column(String(30), nullable=False)
    description = Column(Text, nullable=False)
    number_of_labourers = Column(Integer, nullable=False)
    required_skills = Column(ARRAY(String), nullable=True)
    location = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    h3_index = Column(String(16), nullable=False, index=True)
    daily_wage = Column(Numeric, nullable=False)
    perks = Column(ARRAY(String), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(SmallInteger, nullable=False, default=1)

    farmer = relationship("Farmer", back_populates="jobs", uselist=False)


