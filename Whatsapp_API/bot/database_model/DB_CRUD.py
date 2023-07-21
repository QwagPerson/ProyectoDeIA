from sqlalchemy.orm import Session
import datetime

from . import database_models, schemas


def get_user(db: Session, id_user: int):
    return db.query(database_models.User).filter(database_models.User.id_user == id_user).first()


def get_user_by_number(db: Session, cellphone: str):
    return db.query(database_models.User).filter(database_models.User.cellphone == cellphone).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database_models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = database_models.User(cellphone=user.cellphone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_hour(db: Session, hour_id: datetime):
    return db.query(database_models.Hour).filter(database_models.Hour.hour_id == hour_id).first()


def get_hour_by_datetime(db: Session, time: int):
    return db.query(database_models.Hour).filter(database_models.Hour.time == time).first()


def get_hours(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database_models.Hour).offset(skip).limit(limit).all()


def create_user_item(db: Session, hour: schemas.HourCreate):
    db_hour = database_models.Hour(time=hour.time)
    db.add(db_hour)
    db.commit()
    db.refresh(db_hour)
    return db_hour
