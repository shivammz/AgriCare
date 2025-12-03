# AgriCare/server/models/service.py

from server.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Float, Numeric, SmallInteger
from sqlalchemy.orm import relationship

SERVICE_STATUS = {"inactive": 0, "active": 1}

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    service_name = Column(String(30), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    h3_index = Column(String(16), nullable=False, index=True)
    cost = Column(Numeric, nullable=False)
    status = Column(SmallInteger, nullable=False, default=1)

    farmer = relationship("Farmer", back_populates="services", uselist=False)
