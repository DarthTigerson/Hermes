from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Employment

router = APIRouter(
    prefix="/employment",
    tags=["employment"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class Employment_Class(BaseModel):
    id: int
    name: str

@router.get("/", status_code=status.HTTP_200_OK)
async def return_all_employment(db: db_dependency):
    return db.query(Employment).all()

@router.get("/{employment_id}", status_code=status.HTTP_200_OK)
async def return_employment_by_id(employment_id: int, db: db_dependency):
    employment_data = db.query(Employment).filter(Employment.id == employment_id).first()

    if employment_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employment not found")
    return employment_data

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_employment(employment: Employment_Class, db: db_dependency):
    new_employment = Employment(**employment.model_dump())

    new_employment.id = employment.id
    new_employment.name = employment.name
    new_employment.description = employment.description
    db.add(new_employment)
    db.commit()

@router.put("/{employment_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_employment_by_id(employment_id: int, employment: Employment_Class, db: db_dependency):
    employment_to_update = db.query(Employment).filter(Employment.id == employment_id).first()

    if employment_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employment not found")
    
    employment_to_update.name = employment.name
    employment_to_update.description = employment.description
    db.add(employment_to_update)
    db.commit()

@router.delete("/{employment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employment_by_id(employment_id: int, db: db_dependency):
    employment_to_delete = db.query(Employment).filter(Employment.id == employment_id).first()

    if employment_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employment not found")
    
    db.delete(employment_to_delete)
    db.commit()