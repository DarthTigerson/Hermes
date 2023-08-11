from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Departments

router = APIRouter(
    prefix="/departments",
    tags=["departments"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class Department(BaseModel):
    id: int
    name: str
    description: str

@router.get("/", status_code=status.HTTP_200_OK)
async def return_all_departments(db: db_dependency):
    return db.query(Departments).all()

@router.get("/{department_id}", status_code=status.HTTP_200_OK)
async def return_department_by_id(department_id: int, db: db_dependency):
    department_data = db.query(Departments).filter(Departments.id == department_id).first()

    if department_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return department_data

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_department(department: Department, db: db_dependency):
    new_department = Departments(name=department.name, description=department.description)

    new_department.id = department.id
    new_department.name = department.name
    new_department.description = department.description
    db.add(new_department)
    db.commit()

@router.put("/{department_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_department_by_id(department_id: int, department: Department, db: db_dependency):
    department_to_update = db.query(Departments).filter(Departments.id == department_id).first()

    if department_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    
    department_to_update.name = department.name
    department_to_update.description = department.description
    db.add(department_to_update)
    db.commit()

@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department_by_id(department_id: int, db: db_dependency):
    department_to_delete = db.query(Departments).filter(Departments.id == department_id).first()

    if department_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    
    db.delete(department_to_delete)
    db.commit()