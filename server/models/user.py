# AgriCare/server/models/user.py

from server.db import Base
from sqlalchemy import Column, Integer, String, SmallInteger
from sqlalchemy.orm import relationship

ROLE_MAP = {"farmer": 0, "labour": 1}
REVERSE_ROLE_MAP = {0: "farmer", 1: "labour"}

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(25), nullable=False)
    email = Column(String(50), unique=True, nullable=True)
    phone = Column(String(10), unique=True, nullable=True)
    role = Column(SmallInteger, nullable=False)

    farmer = relationship("Farmer", back_populates="user", uselist=False)
    labour = relationship("Labour", back_populates="user", uselist=False)