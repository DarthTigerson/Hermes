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

    new_employee.email = employee.email
    new_employee.first_name = employee.first_name
    new_employee.last_name = employee.last_name
    new_employee.full_name = employee.first_name + " " + employee.last_name
    new_employee.gender = employee.gender
    new_employee.date_of_birth = employee.date_of_birth
    new_employee.nationality = employee.nationality
    new_employee.supplier = employee.supplier
    new_employee.entity_to_be_billed = employee.entity_to_be_billed
    new_employee.employer_id = employee.employer_id
    new_employee.company_email = employee.company_email
    new_employee.job_title = employee.job_title
    new_employee.direct_manager_id = employee.direct_manager_id
    new_employee.second_level_manager_id = employee.second_level_manager_id
    new_employee.third_level_manager_id = employee.third_level_manager_id
    new_employee.start_date = employee.start_date
    new_employee.end_date = employee.end_date
    new_employee.site_id = employee.site_id
    new_employee.country_of_origin = employee.country_of_origin
    new_employee.working_country = employee.working_country
    new_employee.department_id = employee.department_id
    new_employee.product_code = employee.product_code
    new_employee.brand_code = employee.brand_code
    new_employee.business_unit = employee.business_unit
    new_employee.business_vertical = employee.business_vertical
    new_employee.salary_currency_id = employee.salary_currency_id
    new_employee.salary = employee.salary
    new_employee.salary_period = employee.salary_period
    new_employee.hr_team_id = employee.hr_team_id
    new_employee.working_hours = employee.working_hours
    new_employee.employment_contract_id = employee.employment_contract_id
    new_employee.employment_type_id = employee.employment_type_id
    new_employee.employment_status_id = employee.employment_status_id
    db.add(new_employee)
    db.commit()