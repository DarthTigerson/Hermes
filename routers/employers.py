from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Employers

router = APIRouter(
    prefix="/employers",
    tags=["employers"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class Employer(BaseModel):
    id: int
    name: str
    description: str

@router.get("/", status_code=status.HTTP_200_OK)
async def return_all_employers(db: db_dependency):
    return db.query(Employers).all()

@router.get("/{employer_id}", status_code=status.HTTP_200_OK)
async def return_employer_by_id(employer_id: int, db: db_dependency):
    employers_data = db.query(Employers).filter(Employers.id == employer_id).first()

    if employers_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employer not found")
    return employers_data

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_employer(employer: Employer, db: db_dependency):
    new_employer = Employers(**employer.model_dump())

    db.add(new_employer)
    db.commit()

@router.put("/{employer_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_employer_by_id(employer_id: int, employer: Employer, db: db_dependency):
    employer_to_update = db.query(Employers).filter(Employers.id == employer_id).first()

    if employer_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employer not found")
    
    employer_to_update.name = employer.name
    employer_to_update.description = employer.description
    db.add(employer_to_update)
    db.commit()

@router.delete("/{employer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employer_by_id(employer_id: int, db: db_dependency):
    employer_to_delete = db.query(Employers).filter(Employers.id == employer_id).first()

    if employer_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employer not found")
    
    db.delete(employer_to_delete)
    db.commit()