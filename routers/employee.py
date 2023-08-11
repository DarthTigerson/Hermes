from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Employees

router = APIRouter(
    prefix="/employee",
    tags=["employee"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class Employee_Class(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    gender: str
    date_of_birth: str
    nationality: str
    supplier: str
    entity_to_be_billed: str
    employer_id: int
    company_email: str
    job_title: str
    direct_manager_id: int
    second_level_manager_id: int
    third_level_manager_id: int
    start_date: str
    end_date: str
    site_id: int
    country_of_origin: str
    working_country: str
    department_id: int
    product_code: str
    brand_code: str
    business_unit: str
    business_vertical: str
    salary_currency_id: int
    salary: float
    salary_period: str
    hr_team_id: int
    working_hours: int
    employment_contract_id: int
    employment_type_id: int
    employment_status_id: int

@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency):
    return db.query(Employees).all()

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_employee(id: int, db: db_dependency):
    return db.query(Employees).filter(Employees.id == id).first()

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_employee(employee: Employee_Class, db: db_dependency):
    new_employee = Employees(**employee.model_dump())
    new_employee.full_name = employee.first_name + " " + employee.last_name
    
    db.add(new_employee)
    db.commit()