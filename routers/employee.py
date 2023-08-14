from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
import models

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette import status
from starlette.responses import RedirectResponse

router = APIRouter(
    prefix="/employee",
    tags=["employee"],
)

templates = Jinja2Templates(directory='templates')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/")
async def get_employee(request: Request, db: Session = Depends(get_db)):
    employees = db.query(models.Employees).all()

    return templates.TemplateResponse("employee.html", {"request": request, "employees": employees})

@router.get("/add_employee")
async def add_employee(request: Request):
    return templates.TemplateResponse("add-employee.html", {"request": request})

@router.post("/add_employee", response_class=HTMLResponse)
async def create_employee(request: Request, email: str = Form(...), first_name: str = Form(...), last_name: str = Form(...), full_name: str = Form(...), date_of_birth: str = Form(...), gender: str = Form(...), nationality: str = Form(...), country_of_origin: str = Form(...), working_country: str = Form(...), job_title: str = Form(...), direct_manager_id:str = Form(...), start_date: str = Form(...), end_date: str = Form(...), site_id: int = Form(...), department_id: int = Form(...), product_code: str = Form(...), brand_code: str = Form(...),business_unit: str = Form(...), business_verticle: str = Form(...), salary_currency_id: int = Form(...), salary: str = Form(...), salary_period: str = Form(...), hr_team_id: int = Form(...),  working_hours: str = Form(...), employment_contract_id: int = Form(...), employment_type_id: int = Form(...), supplier: str = Form(...), entity_to_be_billed: str = Form(...), employer_id: int = Form(...), company_email: str = Form(...), db: Session = Depends(get_db)):
    employee_model = models.Employees()

    employee_model.email = email
    employee_model.first_name = first_name
    employee_model.last_name = last_name
    employee_model.full_name = full_name
    employee_model.gender = gender
    employee_model.date_of_birth = date_of_birth
    employee_model.nationality = nationality
    employee_model.supplier = supplier
    employee_model.entity_to_be_billed = entity_to_be_billed
    employee_model.employer_id = employer_id
    employee_model.company_email = company_email
    employee_model.job_title = job_title
    employee_model.direct_manager_id = direct_manager_id
    employee_model.second_level_manager_id = None
    employee_model.third_level_manager_id = None
    employee_model.start_date = start_date
    employee_model.end_date = end_date
    employee_model.site_id = site_id
    employee_model.country_of_origin_id = country_of_origin
    employee_model.working_country_id = working_country
    employee_model.department_id = department_id
    employee_model.product_code = product_code
    employee_model.brand_code = brand_code
    employee_model.business_unit = business_unit
    employee_model.business_verticle = business_verticle
    employee_model.salary_currency_id = salary_currency_id
    employee_model.salary = salary
    employee_model.salary_period = salary_period
    employee_model.hr_team_id = hr_team_id
    employee_model.working_hours = working_hours
    employee_model.employment_contract_id = employment_contract_id
    employee_model.employment_type_id = employment_type_id
    employee_model.employment_status_id = 1

    db.add(employee_model)
    db.commit()

    return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)