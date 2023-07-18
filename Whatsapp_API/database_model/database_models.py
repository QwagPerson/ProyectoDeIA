from database import Base

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    cellphone = Column(String, unique=True)
    gender = Column(String)

    hour = relationship("Hour", back_populates="users", uselist=False)


class Hour(Base):
    __tablename__ = "hours"

    id_hour = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime, index=True)
    address = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    confirm = Column(Boolean, default=False)

    owner = relationship("User", back_populates="hours", uselist=False)
