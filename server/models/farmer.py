# AgriCare/server/models/farmer.py

from db import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    user = relationship("User", back_populates="farmer")
    jobs = relationship("Job", back_populates="farmer")
    services = relationship("Service", back_populates="farmer")