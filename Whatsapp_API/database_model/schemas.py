from pydantic import BaseModel
import datetime


class HourBase(BaseModel):
    address: str
    time: datetime

class HourCreate(HourBase):
    pass

class Hour(HourBase):
    id_hour: int
    confirm: bool
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    gender: str

class UserCreate(UserBase):
    cellphone: str

class User(UserBase):
    id_user: int
    hour: Hour

    class Config:
        orm_mode = True