from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Status

router = APIRouter(
    prefix="/status",
    tags=["status"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class Status_Class(BaseModel):
    id: int
    name: str

@router.get("/", status_code=status.HTTP_200_OK)
async def return_all_status(db: db_dependency):
    return db.query(Status).all()

@router.get("/{status_id}", status_code=status.HTTP_200_OK)
async def return_status_by_id(status_id: int, db: db_dependency):
    status_data = db.query(Status).filter(Status.id == status_id).first()

    if status_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    return status_data

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_status(status: Status_Class, db: db_dependency):
    new_status = Status(**status.model_dump())

    new_status.name = status.name
    new_status.description = status.description
    db.add(new_status)
    db.commit()

@router.put("/{status_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_status_by_id(status_id: int, status: Status_Class, db: db_dependency):
    status_to_update = db.query(Status).filter(Status.id == status_id).first()

    if status_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    
    status_to_update.name = status.name
    status_to_update.description = status.description
    db.add(status_to_update)
    db.commit()

@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_status_by_id(status_id: int, db: db_dependency):
    status_to_delete = db.query(Status).filter(Status.id == status_id).first()

    if status_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    
    db.delete(status_to_delete)
    db.commit()