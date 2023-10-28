from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from sqlalchemy.orm import Session, aliased
from typing import Annotated, Optional
from database import SessionLocal
from pydantic import BaseModel, Field
from routers.admin import get_current_user
from routers.logging import create_log, Log
from routers.messaging import slack_send_message, email_send_message
from datetime import datetime
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
async def get_employee(request: Request, employee_search: Optional[str] = None, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    if employee_search is None:
        employees = db.query(models.Employees).order_by(models.Employees.first_name).filter(models.Employees.employment_status_id == 0).all()

    else:
        employees = db.query(models.Employees).order_by(models.Employees.first_name).filter(models.Employees.employment_status_id == 0).filter(models.Employees.full_name.ilike(f"%{employee_search}%")).all()

    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    employments = db.query(models.Employment).order_by(models.Employment.name).all()

    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()

    log = Log(action="Info",user=user['username'],description="Viewed the employee page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("employee.html", {"request": request, "employees": employees, "departments": departments, "sites": sites, "employments": employments, "logged_in_user": user, "role_state": role_state})

@router.get("/offboarded_employee")
async def get_offboarded_employee(request: Request, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    employees = db.query(models.Employees).order_by(models.Employees.first_name).filter(models.Employees.employment_status_id == 1).all()
    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    employments = db.query(models.Employment).order_by(models.Employment.name).all()

    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()

    log = Log(action="Info",user=user['username'],description="Viewed the offboarded users page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("offboarded-employee.html", {"request": request, "employees": employees, "departments": departments, "sites": sites, "employments": employments, "logged_in_user": user, "role_state": role_state})

@router.get("/add_employee")
async def add_employee(request: Request, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    countries = db.query(models.Country).order_by(models.Country.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    currencies = db.query(models.Currency).order_by(models.Currency.name).all()
    employment_contracts = db.query(models.Contracts).order_by(models.Contracts.name).all()
    employment_types = db.query(models.Employment).order_by(models.Employment.name).all()
    employers = db.query(models.Employers).order_by(models.Employers.name).all()
    hr_teams = db.query(models.Teams).order_by(models.Teams.name).all()
    salary_pay_frequency = db.query(models.PayFrequency).order_by(models.PayFrequency.name).all()

    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()

    log = Log(action="Info",user=user['username'],description="Viewed the add employee page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("add-employee.html", {"request": request, "departments": departments, "sites": sites , "countries": countries, "currencies": currencies, "employment_contracts": employment_contracts, "employment_types": employment_types, "employers": employers, "hr_teams": hr_teams, "salary_pay_frequencies": salary_pay_frequency, "logged_in_user": user, "role_state": role_state})

@router.post("/add_employee", response_class=HTMLResponse)
async def create_employee(request: Request, email: str = Form(None), first_name: str = Form(None), last_name: str = Form(None), full_name: str = Form(None), date_of_birth: str = Form(None), gender: int = Form(0), nationality: str = Form(None), country_of_origin_id: int = Form(0), working_country_id: int = Form(0), job_title: str = Form(None), direct_manager:str = Form(None), start_date: str = Form(None), site_id: int = Form(0), department_id: int = Form(0), product_code: str = Form(None), brand_code: str = Form(None),business_unit: str = Form(None), business_verticle: str = Form(None), salary_currency_id: int = Form(0), salary: str = Form(None), salary_period: str = Form(None), hr_team_id: int = Form(0),  working_hours: str = Form(None), employment_contract_id: int = Form(0), employment_type_id: int = Form(0), supplier: str = Form(None), entity_to_be_billed: str = Form(None), employer_id: int = Form(0), company_email: str = Form(None), end_date: str = Form(None), personal_email: str = Form(None), net_monthly_salary: str = Form(None), change_reason: str = Form(None), increase_percent: str = Form(None), salary_pay_frequency_id: int = Form(0), db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
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

    preferences = db.query(models.Preferences).order_by(models.Preferences.id.desc()).first()
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
    
    if preferences.slack_webhook_channel != None and preferences.email_new_employee == True:
        await slack_send_message(message=f"New employee added: {employee_model.full_name} ({employee_model.email})", db=db)
    if preferences.email_list != None and preferences.email_new_employee == True:
        await email_send_message(subject=f"New Onboarding: {employee_model.full_name}", message=f"Hermes\nNew Employee Onboarding: {employee_model.full_name}\n\nThis email is to notify you of the following new employee:\n\nFull name: {employee_model.full_name}\nStart date: {employee_model.start_date}\nPersonal email: {employee_model.personal_email}\nEmail: {employee_model.company_email}\nJob title: {employee_model.job_title}\nCurrent Employer: {current_employer.name}\nReports to: {employee_model.direct_manager}\nEmployment contract: {employment_contract.name}\nEmployment type: {employment_type.name}\nSite: {site.name}\nHR Department: {hr_department}\nBusiness Unit: {employee_model.business_unit}\n Business Vertical: {employee_model.business_verticle}\nBrand Code: {employee_model.brand_code}\nProduct Code: {employee_model.product_code}\nDepartment: {department.name}\n\nPlease contact the HR Department if you have further questions.\n\nThanks & Regards,\nHR Team.", db=db)

    log = Log(action="Info",user=user['username'],description=f"Added a new employee with the email {email}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)

@router.get("/edit_employee/{employee_id}")
async def edit_employee(request: Request, employee_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
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

    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()

    log = Log(action="Info",user=user['username'],description=f"Viewed the edit employee page for the employee with the email {employee_data.email}")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("edit-employee.html", {"request": request, "employee_data": employee_data, "departments": departments, "sites": sites , "countries": countries, "currencies": currencies, "employment_contracts": employment_contracts, "employment_types": employment_types, "employers": employers, "hr_teams": hr_teams, "salary_pay_frequencies": salary_pay_frequency, "logged_in_user": user, "role_state": role_state})

@router.post("/edit_employee/{employee_id}", response_class=HTMLResponse)
async def update_employee(request: Request, employee_id: int, email: str = Form(None), first_name: str = Form(None), last_name: str = Form(None), full_name: str = Form(None), date_of_birth: str = Form(None), gender: int = Form(0), nationality: str = Form(None), country_of_origin_id: int = Form(0), working_country_id: int = Form(0), job_title: str = Form(None), direct_manager:str = Form(None), start_date: str = Form(None), end_date: str = Form(None), site_id: int = Form(0), department_id: int = Form(0), product_code: str = Form(None), brand_code: str = Form(None),business_unit: str = Form(None), business_verticle: str = Form(None), salary_currency_id: int = Form(None), salary: str = Form(None), salary_period: str = Form(None), hr_team_id: int = Form(None),  working_hours: str = Form(None), employment_contract_id: int = Form(None), employment_type_id: int = Form(None), supplier: str = Form(None), entity_to_be_billed: str = Form(None), employer_id: int = Form(0), company_email: str = Form(None), personal_email: str = Form(None), net_monthly_salary: str = Form(None), change_reason: str = Form(None), increase_percent: str = Form(None), salary_pay_frequency_id: int = Form(None), employment_status_id: int = Form(0), db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    employee = db.query(models.Employees).filter(models.Employees.email == email).first()

    if employee == True and employee.id != employee_id:
        return RedirectResponse(url="/employee/user_exists/" + str(employee.id), status_code=status.HTTP_302_FOUND)
    
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
    if salary_currency_id != 0:
        employee_model.salary_currency_id = salary_currency_id
    if salary != None:
        employee_model.salary = salary
    if salary_period != None:
        employee_model.salary_period = salary_period
    if salary_pay_frequency_id != 0:
        employee_model.salary_pay_frequency_id = salary_pay_frequency_id
    if net_monthly_salary != None:
        employee_model.net_monthly_salary = net_monthly_salary
    if change_reason != None:
        employee_model.change_reason = change_reason
    if increase_percent != None:
        employee_model.increase_percentage = increase_percent
    if hr_team_id != 0:
        employee_model.hr_team_id = hr_team_id
    if working_hours != None:
        employee_model.working_hours = working_hours
    if employment_contract_id != 0:
        employee_model.employment_contract_id = employment_contract_id
    if employment_type_id != 0:
        employee_model.employment_type_id = employment_type_id
    employee_model.employment_status_id = 0
    employee_model.modified_date = datetime.now()

    db.add(employee_model)
    db.commit()

    preferences = db.query(models.Preferences).order_by(models.Preferences.id.desc()).first()
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

    if preferences.slack_webhook_channel != None and preferences.email_updated_employee == True:
        await slack_send_message(message=f"Employee updated: {employee_model.full_name} ({employee_model.email})", db=db)
    if preferences.email_list != None and preferences.email_updated_employee == True:
        await email_send_message(subject=f"Employee Update: {employee_model.full_name}", message=f"Hermes\nEmployee update: {employee_model.full_name}\n\nThis email is to notify you of the following employee update:\n\nFull name: {employee_model.full_name}\nStart date: {employee_model.start_date}\nPersonal email: {employee_model.personal_email}\nEmail: {employee_model.company_email}\nJob title: {employee_model.job_title}\nCurrent Employer: {current_employer.name}\nReports to: {employee_model.direct_manager}\nEmployment contract: {employment_contract.name}\nEmployment type: {employment_type.name}\nSite: {site.name}\nHR Department: {hr_department}\nBusiness Unit: {employee_model.business_unit}\n Business Vertical: {employee_model.business_verticle}\nBrand Code: {employee_model.brand_code}\nProduct Code: {employee_model.product_code}\nDepartment: {department.name}\n\nPlease contact the HR Department if you have further questions.\n\nThanks & Regards,\nHR Team.", db=db)

    log = Log(action="Info",user=user['username'],description=f"Updated the employee with the email {email}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)

@router.get("/user_exists/{employee_id}")
async def user_exists(request: Request, employee_id: str, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    employee = db.query(models.Employees).filter(models.Employees.id == employee_id).first()
    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    employments = db.query(models.Employment).order_by(models.Employment.name).all()

    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()

    log = Log(action="Warn",user=user['username'],description=f"Attempted to create a new employee with the email {employee.email} but it already exists.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("empoyee-exists.html", {"request": request, "employee": employee, "departments": departments, "sites": sites, "employments": employments, "role_state": role_state, "logged_in_user": user})

@router.get("/offboard_employee/{employee_id}")
async def offboard_employee(request: Request, employee_id: int, db: Session =Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    employee_model = db.query(models.Employees).filter(models.Employees.id == employee_id).first()

    if employee_model is None:
        raise RedirectResponse(url="/employee", status_code=status.HTTP_404_NOT_FOUND)
    
    employee_model.employment_status_id = 1

    db.add(employee_model)
    db.commit()

    preferences = db.query(models.Preferences).order_by(models.Preferences.id.desc()).first()
    current_employer = db.query(models.Employers).filter(models.Employers.id == employee_model.employer_id).first()
    employment_contract = db.query(models.Contracts).filter(models.Contracts.id == employee_model.employment_contract_id).first()
    employment_type = db.query(models.Employment).filter(models.Employment.id == employee_model.employment_type_id).first()
    site = db.query(models.Sites).filter(models.Sites.id == employee_model.site_id).first()
    hr_department = db.query(models.Teams).filter(models.Teams.id == employee_model.hr_team_id).first()
    if hr_department != None:
        hr_department = hr_department.name
    else:
        hr_department = "N/A"
    department = db.query(models.Departments).filter(models.Departments.id == employee_model.department_id).first()

    if preferences.slack_webhook_channel != None and preferences.email_offboarded_employee == True:
        await slack_send_message(message=f"Employee offboarded: {employee_model.full_name} ({employee_model.email})", db=db)
    if preferences.email_list != None and preferences.email_offboarded_employee == True:
        await email_send_message(subject=f"Employee Offboarding: {employee_model.full_name}", message=f"Hermes\nOffboarding notification for: {employee_model.full_name}\n\nThis email is to notify you of the following employee leaving our organization:\n\nFull name: {employee_model.full_name}\nStart date: {employee_model.start_date}\nPersonal email: {employee_model.personal_email}\nEmail: {employee_model.company_email}\nJob title: {employee_model.job_title}\nCurrent Employer: {current_employer.name}\nReports to: {employee_model.direct_manager}\nEmployment contract: {employment_contract.name}\nEmployment type: {employment_type.name}\nSite: {site.name}\nHR Department: {hr_department}\nBusiness Unit: {employee_model.business_unit}\n Business Vertical: {employee_model.business_verticle}\nBrand Code: {employee_model.brand_code}\nProduct Code: {employee_model.product_code}\nDepartment: {department.name}\n\nlease disable all accesses provided on the specified above date (unless otherwise instructed) and contact the HR Department if you have further questions.\n\nThanks & Regards,\nHR Team.", db=db)

    log = Log(action="Info",user=user['username'],description=f"Offboarded the employee with the email {employee_model.email}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/employee", status_code=status.HTTP_302_FOUND)

@router.get("/reboard_employee/{employee_id}")
async def reboard_employee(request: Request, employee_id: int, db: Session =Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    employee_model = db.query(models.Employees).filter(models.Employees.id == employee_id).first()

    if employee_model is None:
        raise RedirectResponse(url="/employee", status_code=status.HTTP_404_NOT_FOUND)
    
    employee_model.employment_status_id = 0

    db.add(employee_model)
    db.commit()

    preferences = db.query(models.Preferences).order_by(models.Preferences.id.desc()).first()
    current_employer = db.query(models.Employers).filter(models.Employers.id == employee_model.employer_id).first()
    employment_contract = db.query(models.Contracts).filter(models.Contracts.id == employee_model.employment_contract_id).first()
    employment_type = db.query(models.Employment).filter(models.Employment.id == employee_model.employment_type_id).first()
    site = db.query(models.Sites).filter(models.Sites.id == employee_model.site_id).first()
    hr_department = db.query(models.Teams).filter(models.Teams.id == employee_model.hr_team_id).first()
    if hr_department != None:
        hr_department = hr_department.name
    else:
        hr_department = "N/A"
    department = db.query(models.Departments).filter(models.Departments.id == employee_model.department_id).first()

    if preferences.slack_webhook_channel != None and preferences.email_updated_employee == True:
        await slack_send_message(message=f"Employee Re-Onboarded: {employee_model.full_name} ({employee_model.email})", db=db)
    if preferences.email_list != None and preferences.email_offboarded_employee == True:
        await email_send_message(subject=f"Re-Onboarding: {employee_model.full_name}", message=f"Hermes\nEmployee Re-Onboarding: {employee_model.full_name}\n\nThis email is to notify you of the following Re-Onboarding:\n\nFull name: {employee_model.full_name}\nStart date: {employee_model.start_date}\nPersonal email: {employee_model.personal_email}\nEmail: {employee_model.company_email}\nJob title: {employee_model.job_title}\nCurrent Employer: {current_employer.name}\nReports to: {employee_model.direct_manager}\nEmployment contract: {employment_contract.name}\nEmployment type: {employment_type.name}\nSite: {site.name}\nHR Department: {hr_department}\nBusiness Unit: {employee_model.business_unit}\n Business Vertical: {employee_model.business_verticle}\nBrand Code: {employee_model.brand_code}\nProduct Code: {employee_model.product_code}\nDepartment: {department.name}\n\nPlease contact the HR Department if you have further questions.\n\nThanks & Regards,\nHR Team.", db=db)


    log = Log(action="Info",user=user['username'],description=f"Reboarded the employee with the email {employee_model.email}.")
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
