from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import database_models, schemas, DB_CRUD
from .database import SessionLocal, engine

database_models.Base.metadata.create_all(bind=engine)


# app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/hours/", response_model=schemas.Hour)
def read_hours(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    hours = DB_CRUD.get_hours(db, skip=skip, limit=limit)
    return hours