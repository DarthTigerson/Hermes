from datetime import datetime
from io import BytesIO
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session, aliased
from starlette import status
from starlette.responses import RedirectResponse

import gzip
import models
from database import SessionLocal
from routers.admin import get_current_user
from routers.logging import create_log, Log
from routers.messaging import slack_send_message, email_send_template

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
async def get_employee(request: Request, employee_search: Optional[str] = None, db: Session = Depends(get_db)):
    
    logged_in_user = await get_current_user(request)
    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    if employee_search is None:
        employees = db.query(models.Employees).order_by(models.Employees.first_name).filter(models.Employees.employment_status_id == 0).all()

    else:
        employees = db.query(models.Employees).order_by(models.Employees.first_name).filter(models.Employees.employment_status_id == 0).filter(models.Employees.full_name.ilike(f"%{employee_search}%")).all()

    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    contracts = db.query(models.Contracts).order_by(models.Contracts.name).all()
    countries = db.query(models.Country).order_by(models.Country.name).all()

    role_state = db.query(models.Roles).filter(models.Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(models.Users.users_profile).filter(models.Users.id == logged_in_user['id']).scalar()

    log = Log(action="Info",user=logged_in_user['username'],description="Viewed the employee page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("employee.html", {"request": request, "employees": employees, "departments": departments, "sites": sites, "contracts": contracts, "logged_in_user": logged_in_user, "role_state": role_state, "employee_search": employee_search, "countries": countries, "nav": 'employee', "settings": settings, "nav_profile_load": nav_profile_load})

@router.get("/offboarded_employee")
async def get_offboarded_employee(request: Request, offboarded_employee_search: Optional[str] = None, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)
    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(models.Roles).filter(models.Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(models.Users.users_profile).filter(models.Users.id == logged_in_user['id']).scalar()

    if role_state.offboarding == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)
    
    if offboarded_employee_search is None:
        employees = db.query(models.Employees).order_by(models.Employees.first_name).filter(models.Employees.employment_status_id == 1).all()
    else:
        employees = db.query(models.Employees).order_by(models.Employees.first_name).filter(models.Employees.employment_status_id == 1).filter(models.Employees.full_name.ilike(f"%{offboarded_employee_search}%")).all()

    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    contracts = db.query(models.Contracts).order_by(models.Contracts.name).all()

    log = Log(action="Info",user=logged_in_user['username'],description="Viewed the offboarded users page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("offboarded-employee.html", {"request": request, "employees": employees, "departments": departments, "sites": sites, "contracts": contracts, "logged_in_user": logged_in_user, "role_state": role_state, "offboarded_employee_search": offboarded_employee_search, "nav": 'employee', "settings": settings, "nav_profile_load": nav_profile_load})

@router.get("/details/{employee_id}")
async def get_employee_details(request: Request, employee_id: int, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)
    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(models.Roles).filter(models.Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(models.Users.users_profile).filter(models.Users.id == logged_in_user['id']).scalar()

    users = db.query(models.Users).order_by(models.Users.username).all()    
    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    employee_data = db.query(models.Employees).filter(models.Employees.id == employee_id).first()
    countries = db.query(models.Country).order_by(models.Country.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    currencies = db.query(models.Currency).order_by(models.Currency.name).all()
    employment_contracts = db.query(models.Contracts).order_by(models.Contracts.name).all()
    employment_types = db.query(models.Employment).order_by(models.Employment.name).all()
    employers = db.query(models.Employers).order_by(models.Employers.name).all()
    hr_teams = db.query(models.Teams).order_by(models.Teams.name).all()
    salary_pay_frequency = db.query(models.PayFrequency).order_by(models.PayFrequency.name).all()
    employee_contracts = db.query(models.Employee_Contracts).order_by(desc(models.Employee_Contracts.id)).filter(models.Employee_Contracts.employee_id == employee_id).all()
    
    return templates.TemplateResponse("employee-details.html", {"request": request, "employee_data": employee_data, "departments": departments, "sites": sites , "countries": countries, "currencies": currencies, "employment_contracts": employment_contracts, "employment_types": employment_types, "employers": employers, "hr_teams": hr_teams, "salary_pay_frequencies": salary_pay_frequency, "logged_in_user": logged_in_user, "role_state": role_state, "nav": 'employee', "settings": settings, "employee_contracts": employee_contracts, "users": users, "nav_profile_load": nav_profile_load})

@router.get("/add_employee")
async def add_employee(request: Request, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)
    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(models.Roles).filter(models.Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(models.Users.users_profile).filter(models.Users.id == logged_in_user['id']).scalar()

    if role_state.onboarding == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)
    
    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    countries = db.query(models.Country).order_by(models.Country.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    currencies = db.query(models.Currency).order_by(models.Currency.name).all()
    employment_contracts = db.query(models.Contracts).order_by(models.Contracts.name).all()
    employment_types = db.query(models.Employment).order_by(models.Employment.name).all()
    employers = db.query(models.Employers).order_by(models.Employers.name).all()
    hr_teams = db.query(models.Teams).order_by(models.Teams.name).all()
    salary_pay_frequency = db.query(models.PayFrequency).order_by(models.PayFrequency.name).all()

    log = Log(action="Info",user=logged_in_user['username'],description="Viewed the add employee page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("add-employee.html", {"request": request, "departments": departments, "sites": sites , "countries": countries, "currencies": currencies, "employment_contracts": employment_contracts, "employment_types": employment_types, "employers": employers, "hr_teams": hr_teams, "salary_pay_frequencies": salary_pay_frequency, "logged_in_user": logged_in_user, "role_state": role_state, "nav": 'employee', "settings": settings, "nav_profile_load": nav_profile_load})

@router.post("/add_employee", response_class=HTMLResponse)
async def create_employee(request: Request, email: str = Form(None), first_name: str = Form(None), last_name: str = Form(None), full_name: str = Form(None), date_of_birth: str = Form(None), gender: int = Form(0), nationality: str = Form(None), country_of_origin_id: int = Form(0), working_country_id: int = Form(0), job_title: str = Form(None), direct_manager:str = Form(None), start_date: str = Form(None), site_id: int = Form(0), department_id: int = Form(0), product_code: str = Form(None), brand_code: str = Form(None),business_unit: str = Form(None), business_verticle: str = Form(None), salary_currency_id: int = Form(0), salary: str = Form(None), salary_period: str = Form(None), hr_team_id: int = Form(0),  working_hours: str = Form(None), employment_contract_id: int = Form(0), employment_type_id: int = Form(0), supplier: str = Form(None), entity_to_be_billed: str = Form(None), employer_id: int = Form(0), company_email: str = Form(None), end_date: str = Form(None), personal_email: str = Form(None), net_monthly_salary: str = Form(None), change_reason: str = Form(None), increase_percent: str = Form(None), salary_pay_frequency_id: int = Form(0), db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()

    if role_state.onboarding == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)
    
    employee = db.query(models.Employees).filter(models.Employees.email == email).first()

    if employee:
        return RedirectResponse(url="/employee/user_exists/" + str(employee.id), status_code=status.HTTP_302_FOUND)
    
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
    employee_model.direct_manager = direct_manager
    employee_model.start_date = start_date
    employee_model.end_date = end_date
    employee_model.site_id = site_id
    employee_model.country_of_origin_id = country_of_origin_id
    employee_model.working_country_id = working_country_id
    employee_model.personal_email = personal_email
    employee_model.department_id = department_id
    employee_model.product_code = product_code
    employee_model.brand_code = brand_code
    employee_model.business_unit = business_unit
    employee_model.business_verticle = business_verticle
    employee_model.salary_currency_id = salary_currency_id
    employee_model.salary = salary
    employee_model.salary_period = salary_period
    employee_model.salary_pay_frequency_id = salary_pay_frequency_id
    employee_model.net_monthly_salary = net_monthly_salary
    employee_model.change_reason = change_reason
    employee_model.increase_percentage = increase_percent
    employee_model.hr_team_id = hr_team_id
    employee_model.working_hours = working_hours
    employee_model.employment_contract_id = employment_contract_id
    employee_model.employment_type_id = employment_type_id
    employee_model.employment_status_id = 0
    employee_model.created_date = datetime.now()
    employee_model.modified_date = datetime.now()

    db.add(employee_model)
    db.commit()

    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    current_employer = db.query(models.Employers).filter(models.Employers.id == employer_id).first()
    employment_contract = db.query(models.Contracts).filter(models.Contracts.id == employment_contract_id).first()
    employment_type = db.query(models.Employment).filter(models.Employment.id == employment_type_id).first()
    site = db.query(models.Sites).filter(models.Sites.id == site_id).first()
    hr_department = db.query(models.Teams).filter(models.Teams.id == hr_team_id).first()
    if hr_department != None:
        hr_department = hr_department.name
    else:
        hr_department = "N/A"
    department = db.query(models.Departments).filter(models.Departments.id == department_id).first()
    
    if settings.slack_webhook_channel != None and settings.email_new_employee == True:
        await slack_send_message(message=f"New employee added: {employee_model.full_name} ({employee_model.email})", db=db)
    if settings.email_list != None and settings.email_new_employee == True:
        await email_send_template(template=1, employee_id=employee_model.id, db=db)

    log = Log(action="Info",user=user['username'],description=f"Added a new employee with the email {email}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)

@router.get("/edit_employee/{employee_id}")
async def edit_employee(request: Request, employee_id: int, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)
    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(models.Roles).filter(models.Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(models.Users.users_profile).filter(models.Users.id == logged_in_user['id']).scalar()

    if role_state.employee_updates == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)
    
    employee_data = db.query(models.Employees).filter(models.Employees.id == employee_id).first()

    if employee_data.employment_status_id == 1:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)

    users = db.query(models.Users).order_by(models.Users.username).all()
    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    countries = db.query(models.Country).order_by(models.Country.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    currencies = db.query(models.Currency).order_by(models.Currency.name).all()
    employment_contracts = db.query(models.Contracts).order_by(models.Contracts.name).all()
    employment_types = db.query(models.Employment).order_by(models.Employment.name).all()
    employers = db.query(models.Employers).order_by(models.Employers.name).all()
    hr_teams = db.query(models.Teams).order_by(models.Teams.name).all()
    salary_pay_frequency = db.query(models.PayFrequency).order_by(models.PayFrequency.name).all()
    employee_contracts = db.query(models.Employee_Contracts).order_by(desc(models.Employee_Contracts.id)).filter(models.Employee_Contracts.employee_id == employee_id).all()

    log = Log(action="Info",user=logged_in_user['username'],description=f"Viewed the edit employee page for the employee with the email {employee_data.email}")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("edit-employee.html", {"request": request, "employee_data": employee_data, "departments": departments, "sites": sites , "countries": countries, "currencies": currencies, "employment_contracts": employment_contracts, "employment_types": employment_types, "employers": employers, "hr_teams": hr_teams, "salary_pay_frequencies": salary_pay_frequency, "logged_in_user": logged_in_user, "role_state": role_state, "nav": 'employee', "settings": settings, "employee_contracts": employee_contracts, "users": users, "nav_profile_load": nav_profile_load})

@router.post("/edit_employee/{employee_id}", response_class=HTMLResponse)
async def update_employee(request: Request, employee_id: int, email: str = Form(None), first_name: str = Form(None), last_name: str = Form(None), full_name: str = Form(None), date_of_birth: str = Form(None), gender: int = Form(0), nationality: str = Form(None), country_of_origin_id: int = Form(0), working_country_id: int = Form(0), job_title: str = Form(None), direct_manager:str = Form(None), start_date: str = Form(None), end_date: str = Form(None), site_id: int = Form(0), department_id: int = Form(0), product_code: str = Form(None), brand_code: str = Form(None),business_unit: str = Form(None), business_verticle: str = Form(None), salary_currency_id: int = Form(None), salary: str = Form(None), salary_period: str = Form(None), hr_team_id: int = Form(None),  working_hours: str = Form(None), employment_contract_id: int = Form(None), employment_type_id: int = Form(None), supplier: str = Form(None), entity_to_be_billed: str = Form(None), employer_id: int = Form(0), company_email: str = Form(None), personal_email: str = Form(None), net_monthly_salary: str = Form(None), change_reason: str = Form(None), increase_percent: str = Form(None), salary_pay_frequency_id: int = Form(None), employment_status_id: int = Form(0), db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()

    if role_state.employee_updates == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)
    
    employee = db.query(models.Employees).filter(models.Employees.email == email).first()

    if employee == True and employee.id != employee_id:
        return RedirectResponse(url="/employee/user_exists/" + str(employee.id), status_code=status.HTTP_302_FOUND)
    
    if employee.employment_status_id == 1:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)
    
    employee_model = db.query(models.Employees).filter(models.Employees.id == employee_id).first()

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
    employee_model.direct_manager = direct_manager
    employee_model.start_date = start_date
    employee_model.end_date = end_date
    employee_model.site_id = site_id
    employee_model.country_of_origin_id = country_of_origin_id
    employee_model.working_country_id = working_country_id
    employee_model.personal_email = personal_email
    employee_model.department_id = department_id
    employee_model.product_code = product_code
    employee_model.brand_code = brand_code
    employee_model.business_unit = business_unit
    employee_model.business_verticle = business_verticle
    employee_model.employment_contract_id = employment_contract_id
    if role_state.payroll == True:
        employee_model.salary_currency_id = salary_currency_id
        employee_model.salary = salary
        employee_model.salary_period = salary_period
        employee_model.salary_pay_frequency_id = salary_pay_frequency_id
        employee_model.net_monthly_salary = net_monthly_salary
        employee_model.change_reason = change_reason
        employee_model.increase_percentage = increase_percent
        employee_model.working_hours = working_hours
        employee_model.employment_type_id = employment_type_id
    if hr_team_id != 0:
        employee_model.hr_team_id = hr_team_id
    employee_model.employment_status_id = 0
    employee_model.modified_date = datetime.now()
    db.add(employee_model)
    db.commit()

    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    current_employer = db.query(models.Employers).filter(models.Employers.id == employer_id).first()
    employment_contract = db.query(models.Contracts).filter(models.Contracts.id == employment_contract_id).first()
    employment_type = db.query(models.Employment).filter(models.Employment.id == employment_type_id).first()
    site = db.query(models.Sites).filter(models.Sites.id == site_id).first()
    hr_department = db.query(models.Teams).filter(models.Teams.id == hr_team_id).first()
    if hr_department != None:
        hr_department = hr_department.name
    else:
        hr_department = "N/A"
    department = db.query(models.Departments).filter(models.Departments.id == department_id).first()

    if settings.slack_webhook_channel != None and settings.email_updated_employee == True:
        await slack_send_message(message=f"Employee updated: {employee_model.full_name} ({employee_model.email})", db=db)
    if settings.email_list != None and settings.email_updated_employee == True:
        await email_send_template(template=2, employee_id=employee_model.id, db=db)

    log = Log(action="Info",user=user['username'],description=f"Updated the employee with the email {email}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)

@router.get("/user_exists/{employee_id}")
async def user_exists(request: Request, employee_id: str, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)
    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    employee = db.query(models.Employees).filter(models.Employees.id == employee_id).first()
    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    employments = db.query(models.Employment).order_by(models.Employment.name).all()

    role_state = db.query(models.Roles).filter(models.Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(models.Users.users_profile).filter(models.Users.id == logged_in_user['id']).scalar()

    log = Log(action="Warn",user=logged_in_user['username'],description=f"Attempted to create a new employee with the email {employee.email} but it already exists.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("empoyee-exists.html", {"request": request, "employee": employee, "departments": departments, "sites": sites, "employments": employments, "role_state": role_state, "logged_in_user": logged_in_user, "nav": 'employee', "settings": settings, "nav_profile_load": nav_profile_load})

@router.get("/offboard_employee/{employee_id}")
async def offboard_employee(request: Request, employee_id: int, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)
    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(models.Roles).filter(models.Roles.id == logged_in_user['role_id']).first()

    if role_state.offboarding == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)
    
    employee_model = db.query(models.Employees).filter(models.Employees.id == employee_id).first()

    if employee_model is None:
        raise RedirectResponse(url="/employee", status_code=status.HTTP_404_NOT_FOUND)
    
    employee_model.end_date = datetime.now().date()
    employee_model.employment_status_id = 1

    db.add(employee_model)
    db.commit()

    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    current_employer = db.query(models.Employers).filter(models.Employers.id == employee_model.employer_id).first()
    employment_contract = db.query(models.Contracts).filter(models.Contracts.id == employee_model.employment_contract_id).first()
    employment_type = db.query(models.Employment).filter(models.Employment.id == employee_model.employment_type_id).first()
    site = db.query(models.Sites).filter(models.Sites.id == employee_model.site_id).first()
    hr_department = db.query(models.Teams).filter(models.Teams.id == employee_model.hr_team_id).first()
    if hr_department is not None:
        hr_department = hr_department.name
    else:
        hr_department = "N/A"
    department = db.query(models.Departments).filter(models.Departments.id == employee_model.department_id).first()

    if settings.slack_webhook_channel is not None and settings.email_offboarded_employee:
        await slack_send_message(message=f"Employee offboarded: {employee_model.full_name} ({employee_model.email})", db=db)
    if settings.email_list is not None and settings.email_offboarded_employee:
        await email_send_template(template=3, employee_id=employee_model.id, db=db)

    log = Log(action="Info",user=logged_in_user['username'],description=f"Offboarded the employee with the email {employee_model.email}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)

@router.get("/reboard_employee/{employee_id}")
async def reboard_employee(request: Request, employee_id: int, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)
    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(models.Roles).filter(models.Roles.id == logged_in_user['role_id']).first()

    if role_state.onboarding == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)
    
    employee_model = db.query(models.Employees).filter(models.Employees.id == employee_id).first()

    if employee_model is None:
        raise RedirectResponse(url="/employee", status_code=status.HTTP_404_NOT_FOUND)
    
    employee_model.employment_status_id = 0

    db.add(employee_model)
    db.commit()

    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    current_employer = db.query(models.Employers).filter(models.Employers.id == employee_model.employer_id).first()
    employment_contract = db.query(models.Contracts).filter(models.Contracts.id == employee_model.employment_contract_id).first()
    employment_type = db.query(models.Employment).filter(models.Employment.id == employee_model.employment_type_id).first()
    site = db.query(models.Sites).filter(models.Sites.id == employee_model.site_id).first()
    hr_department = db.query(models.Teams).filter(models.Teams.id == employee_model.hr_team_id).first()
    if hr_department is not None:
        hr_department = hr_department.name
    else:
        hr_department = "N/A"
    department = db.query(models.Departments).filter(models.Departments.id == employee_model.department_id).first()

    if settings.slack_webhook_channel is not None and settings.email_updated_employee:
        await slack_send_message(message=f"Employee Re-Onboarded: {employee_model.full_name} ({employee_model.email})", db=db)
    if settings.email_list is not None and settings.email_offboarded_employee:
        await email_send_template(template=1, employee_id=employee_model.id, db=db)


    log = Log(action="Info",user=logged_in_user['username'],description=f"Reboarded the employee with the email {employee_model.email}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/employee/offboarded_employee", status_code=status.HTTP_302_FOUND)

@router.get("/api_employees_return/")
async def api_employees_return(db: Session = Depends(get_db)):
    working_country = aliased(models.Country)
    country_of_origin = aliased(models.Country)

    employees = db.query(
        working_country.name.label('working_country'),
        models.Employees.end_date,
        models.Employees.email,
        models.Employees.first_name,
        models.Employees.last_name,
        models.Employees.job_title,
        models.Sites.name.label('site'),
        models.Departments.name.label('department'),
        models.Employees.direct_manager,
        country_of_origin.name.label('country_of_origin'),
        models.Employment.name.label('employment_type'),
        models.Employees.business_unit,
        models.Contracts.name.label('employment_contract')
    ).join(
        models.Sites, models.Sites.id == models.Employees.site_id
    ).join(
        models.Departments, models.Departments.id == models.Employees.department_id
    ).join(
        models.Employment, models.Employment.id == models.Employees.employment_type_id
    ).join(
        models.Contracts, models.Contracts.id == models.Employees.employment_contract_id
    ).join(
        working_country, working_country.id == models.Employees.working_country_id
    ).join(
        country_of_origin, country_of_origin.id == models.Employees.country_of_origin_id
    ).filter(
        models.Employees.employment_status_id == 0
    ).order_by(
        models.Employees.email
    ).all()
    return employees

@router.get("/add_employee_contract/{employee_id}")
async def add_employee_contract(request: Request, employee_id: int, db: Session = Depends(get_db)):
    
    logged_in_user = await get_current_user(request)
    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    employee = db.query(models.Employees).filter(models.Employees.id == employee_id).first()
    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    role_state = db.query(models.Roles).filter(models.Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(models.Users.users_profile).filter(models.Users.id == logged_in_user['id']).scalar()

    if role_state.payroll == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("add-employee-contract.html", {"request": request, "employee": employee, "logged_in_user": logged_in_user, "role_state": role_state, "nav": 'employee', "settings": settings, "nav_profile_load": nav_profile_load})

@router.post("/add_employee_contract/{employee_id}", response_class=HTMLResponse)
async def add_employee_contract(request: Request, employee_id: int, db: Session = Depends(get_db), start_date: str = Form(None), end_date: str = Form(None), contract_name: str = Form(None), notes: str = Form(None), contract_file: UploadFile = File(...)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()

    if role_state.payroll == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)
    
    contract_model = models.Employee_Contracts()
    contract_model.employee_id = employee_id
    contract_model.user_id = user['id']
    contract_model.start_date = start_date
    contract_model.end_date = end_date
    contract_model.contract_name = contract_name
    contract_model.notes = notes

    # Read the uploaded file content
    file_content = contract_file.file.read()

    # Save the file content
    compressed_content = gzip.compress(file_content)
    contract_model.contract_file = compressed_content

    db.add(contract_model)
    db.commit()

    return RedirectResponse(url="/employee/edit_employee/" + str(employee_id), status_code=status.HTTP_302_FOUND)

@router.get("/edit_employee_contract/{employee_id}/{employee_contract_id}")
async def edit_employee_contract(request: Request, employee_id: int, employee_contract_id:int, db: Session = Depends(get_db)):
    
    logged_in_user = await get_current_user(request)
    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    employee_contract = db.query(models.Employee_Contracts).filter(models.Employee_Contracts.id == employee_contract_id).first()

    if employee_contract is None:
        return RedirectResponse(url="/employee_details/{employee_id}", status_code=status.HTTP_302_FOUND)

    employee = db.query(models.Employees).filter(models.Employees.id == employee_id).first()
    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    role_state = db.query(models.Roles).filter(models.Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(models.Users.users_profile).filter(models.Users.id == logged_in_user['id']).scalar()

    if role_state.payroll == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("edit-employee-contract.html", {"request": request, "employee": employee, "logged_in_user": logged_in_user, "role_state": role_state, "nav": 'employee', "settings": settings, "employee_contract": employee_contract, "nav_profile_load": nav_profile_load})

@router.post("/edit_employee_contract/{employee_id}/{employee_contract_id}", response_class=HTMLResponse)
async def edit_employee_contract(request: Request, employee_id: int, employee_contract_id: int, db: Session = Depends(get_db), start_date: str = Form(None), end_date: str = Form(None), contract_name: str = Form(None), notes: str = Form(None)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()

    if role_state.payroll == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)
    
    contract_model = db.query(models.Employee_Contracts).filter(models.Employee_Contracts.id == employee_contract_id).first()

    contract_model.employee_id = employee_id
    contract_model.user_id = user['id']
    contract_model.start_date = start_date
    contract_model.end_date = end_date
    contract_model.contract_name = contract_name
    contract_model.notes = notes
    
    db.add(contract_model)
    db.commit()

    return RedirectResponse(url="/employee/edit_employee/" + str(employee_id), status_code=status.HTTP_302_FOUND)

@router.get("/download_employee_contract/{employee_contract_id}")
async def download_employee_contract(request: Request, employee_contract_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()

    if role_state.payroll == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)
    
    employee_contract = db.query(models.Employee_Contracts).filter(models.Employee_Contracts.id == employee_contract_id).first()

    if employee_contract is None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Get the compressed file content
    compressed_content = employee_contract.contract_file

    # Decompress the file content
    file_content = gzip.decompress(compressed_content)

    # Create a BytesIO object from the file content
    file_like = BytesIO(file_content)

    # Return a streaming response
    return StreamingResponse(file_like, media_type='application/pdf', headers={'Content-Disposition': f'attachment; filename={employee_contract.contract_name}.pdf'})

@router.get("/open_employee_contract/{employee_contract_id}")
async def open_employee_contract(request: Request, employee_contract_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()

    if role_state.payroll == False:
        return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)
    
    employee_contract = db.query(models.Employee_Contracts).filter(models.Employee_Contracts.id == employee_contract_id).first()

    if employee_contract is None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Get the compressed file content
    compressed_content = employee_contract.contract_file

    # Decompress the file content
    file_content = gzip.decompress(compressed_content)

    # Create a BytesIO object from the file content
    file_like = BytesIO(file_content)

    # Create a streaming response
    response = StreamingResponse(file_like, media_type='application/pdf')
    response.headers["Content-Disposition"] = f"inline; filename={employee_contract.contract_name}.pdf"
    return response