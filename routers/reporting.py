from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func
from typing import Annotated, Optional
from database import SessionLocal
from pydantic import BaseModel, Field
from routers.admin import get_current_user
from routers.logging import create_log, Log
from routers.messaging import slack_send_message, email_send_message
from datetime import datetime, date, timedelta
import models

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette import status
from starlette.responses import RedirectResponse

router = APIRouter(
    prefix="/reporting",
    tags=["reporting"],
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
async def get_reporting(request: Request, report_type: Optional[int] = 0, start_date: Optional[datetime] = date.today() - timedelta(days=30), end_date: Optional[datetime] = date.today(), manager: Optional[str] = None, departmentValue: Optional[int] = None, countryValue: Optional[int] = None, siteValue: Optional[int] = None, employmentValue: Optional[int] = None, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    header_value = {
        "report_type": report_type,
        "start_date": start_date,
        "end_date": end_date
    }

    # Convert start_date and end_date to strings in the 'YYYY-MM-DD' format
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    if report_type == 1:
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 0)\
            .all()
        report_data = [employee for employee in report_data if start_date_str <= datetime.strptime(employee.start_date, '%Y-%m-%d').strftime('%Y-%m-%d') <= end_date_str]
    elif report_type == 2:
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 1)\
            .all()
        report_data = [employee for employee in report_data if start_date_str <= datetime.strptime(employee.end_date, '%Y-%m-%d').strftime('%Y-%m-%d') <= end_date_str]
    elif report_type == 3:
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 0)\
            .all()
    elif report_type == 4:
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 0)\
            .filter(models.Employees.direct_manager.like(manager))\
            .all()
    elif report_type == 5:
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 0)\
            .filter(models.Employees.department_id == departmentValue)\
            .all()
    elif report_type == 6:
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 0)\
            .filter(models.Employees.country_of_origin_id == countryValue)\
            .all()
    elif report_type == 7:
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 0)\
            .filter(models.Employees.working_country_id == countryValue)\
            .all()
    elif report_type == 8:
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 0)\
            .filter(models.Employees.site_id == siteValue)\
            .all()
    elif report_type == 9:
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 0)\
            .filter(models.Employees.employment_contract_id == employmentValue)\
            .all()
    else:
        report_data = None

    if manager == None:
        manager = ''
    if departmentValue == None:
        departmentValue = 0
    if countryValue == None:
        countryValue = 0
    if siteValue == None:
        siteValue = 0
    if employmentValue == None:
        employmentValue = 0
    
    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()
    
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
    
    return templates.TemplateResponse("reporting.html", {"request": request, "logged_in_user": user, "role_state": role_state, "nav": 'reporting', "header_value": header_value, "report_data": report_data, "countries": countries, "sites": sites, "departments": departments, "currencies": currencies, "employment_contracts": employment_contracts, "employment_types": employment_types, "employers": employers, "hr_teams": hr_teams, "salary_pay_frequency": salary_pay_frequency, "settings": settings, "manager": manager, "departmentValue": departmentValue, "countryValue": countryValue, "siteValue": siteValue, "employmentValue": employmentValue})

@router.get("/download_csv/{report_type}/{start_date}/{end_date}")
async def download_csv(request: Request, report_type: int, start_date: datetime, end_date: datetime, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()
    
    countries = db.query(models.Country).order_by(models.Country.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    currencies = db.query(models.Currency).order_by(models.Currency.name).all()
    employment_contracts = db.query(models.Contracts).order_by(models.Contracts.name).all()
    employment_types = db.query(models.Employment).order_by(models.Employment.name).all()
    employers = db.query(models.Employers).order_by(models.Employers.name).all()
    hr_teams = db.query(models.Teams).order_by(models.Teams.name).all()
    salary_pay_frequency = db.query(models.PayFrequency).order_by(models.PayFrequency.name).all()

    # Convert start_date and end_date to strings in the 'YYYY-MM-DD' format
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    now_date_time_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    if report_type == 1:
        file_name = f"Onboarded_Report_{now_date_time_str}"
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 0)\
            .all()

        # Filter the data in Python
        report_data = [employee for employee in report_data if start_date_str <= datetime.strptime(employee.start_date, '%Y-%m-%d').strftime('%Y-%m-%d') <= end_date_str]
    elif report_type == 2:
        file_name = f"Offboarded_Report_{now_date_time_str}"
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 1)\
            .all()

        # Filter the data in Python
        report_data = [employee for employee in report_data if start_date_str <= datetime.strptime(employee.end_date, '%Y-%m-%d').strftime('%Y-%m-%d') <= end_date_str]
    elif report_type == 3:
        file_name = f"All_Current_Employees_{now_date_time_str}"
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 0)\
            .all()
    else:
        return None

    if role_state.payroll == True:
        csv = "ID,E-mail,Name,Surname,Full_Name,Dath_of_Birth,Gender,Nationality,Country_of_Origin,Working_Country,Personal_E-mail,Job_Title,Manager,HR_Team,Start_Date,End_Date,Site,Department,Product_Code,Brand_Code,Business_Unit,Business_Vertical,Contract,Currency,Base_Salary,Salary_Period,Working_Hours,Employment_Type,Net_Salary,Change_Reason,Increase_Percentage,Salary_Pay_Frequency,Supplier,Entity_to_be_Billed,Emlpoyer,Supplier_E-mail,Employment_Status\n"
        for employee in report_data:
            local_data = {}
            for country in countries:
                if country.id == employee.country_of_origin_id:
                    tempName = country.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['country_of_origin'] = tempName
                if country.id == employee.working_country_id:
                    tempName = country.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['working_country'] = tempName
            for site in sites:
                if site.id == employee.site_id:
                    tempName = site.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['site'] = tempName
            for department in departments:
                if department.id == employee.department_id:
                    tempName = department.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['department'] = tempName
            for currency in currencies:
                if currency.id == employee.salary_currency_id:
                    tempName = currency.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['currency'] = tempName
            for contract in employment_contracts:
                if contract.id == employee.employment_contract_id:
                    tempName = contract.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['contract'] = tempName
            for types in employment_types:
                if types.id == employee.employment_type_id:
                    tempName = types.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['employment_type'] = tempName
            for employer in employers:
                if employer.id == employee.employer_id:
                    tempName = employer.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['employer'] = tempName
            for salary_frequency in salary_pay_frequency:
                if salary_frequency.id == employee.salary_pay_frequency_id:
                    tempName = salary_frequency.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['salary_pay_frequency'] = tempName

            if employee.gender == 0:
                local_data['gender'] = 'Male'
            elif employee.gender == 1:
                local_data['gender'] = 'Female'
            else:
                local_data['gender'] = 'Other'

            if employee.employment_status_id == 0:
                local_data['employment_status'] = 'Onboarded'
            else:
                local_data['employment_status'] = 'Offboarded'

            if employee.hr_team_id == 0:
                local_data['hr_team'] = 'No Team'
            else:
                for team in hr_teams:
                    if team.id == employee.hr_team_id:
                        tempName = team.name.replace('\n', '')
                        tempName = tempName.replace(',', '')
                        local_data['hr_team'] = tempName

            local_data['salary'] = employee.salary.replace(',', '')

            csv += f"{employee.id},{employee.email},{employee.first_name},{employee.last_name},{employee.full_name},{employee.date_of_birth},{local_data['gender']},{employee.nationality},{local_data['country_of_origin']},{local_data['working_country']},{employee.personal_email},{employee.job_title},{employee.direct_manager},{local_data['hr_team']},{employee.start_date},{employee.end_date},{local_data['site']},{local_data['department']},{employee.product_code},{employee.brand_code},{employee.business_unit},{employee.business_verticle},{local_data['contract']},{local_data['currency']},{employee.salary},{employee.salary_period},{employee.working_hours},{local_data['employment_type']},{employee.net_monthly_salary},{employee.change_reason},{employee.increase_percentage},{local_data['salary_pay_frequency']},{employee.supplier},{employee.entity_to_be_billed},{local_data['employer']},{employee.company_email},{local_data['employment_status']}\n"
    else:
        csv = "ID,E-mail,Name,Surname,Full_Name,Dath_of_Birth,Gender,Nationality,Country_of_Origin,Working_Country,Personal_E-mail,Job_Title,Manager,HR_Team,Start_Date,End_Date,Site,Department,Product_Code,Brand_Code,Business_Unit,Business_Vertical,Contract,Supplier,Entity_to_be_Billed,Emlpoyer,Supplier_E-mail,Employment_Status\n"
        
        for employee in report_data:
            local_data = {}
            for country in countries:
                if country.id == employee.country_of_origin_id:
                    tempName = country.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['country_of_origin'] = tempName
                if country.id == employee.working_country_id:
                    tempName = country.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['working_country'] = tempName
            for site in sites:
                if site.id == employee.site_id:
                    tempName = site.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['site'] = tempName
            for department in departments:
                if department.id == employee.department_id:
                    tempName = department.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['department'] = tempName
            for contract in employment_contracts:
                if contract.id == employee.employment_contract_id:
                    tempName = contract.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['contract'] = tempName
            for employer in employers:
                if employer.id == employee.employer_id:
                    tempName = employer.name.replace('\n', '')
                    tempName = tempName.replace(',', '')
                    local_data['employer'] = tempName

            if employee.gender == 0:
                local_data['gender'] = 'Male'
            elif employee.gender == 1:
                local_data['gender'] = 'Female'
            else:
                local_data['gender'] = 'Other'

            if employee.employment_status_id == 0:
                local_data['employment_status'] = 'Onboarded'
            else:
                local_data['employment_status'] = 'Offboarded'

            if employee.hr_team_id == 0:
                local_data['hr_team'] = 'No Team'
            else:
                for team in hr_teams:
                    if team.id == employee.hr_team_id:
                        tempName = team.name.replace('\n', '')
                        tempName = tempName.replace(',', '')
                        local_data['hr_team'] = tempName

            csv += f"{employee.id},{employee.email},{employee.first_name},{employee.last_name},{employee.full_name},{employee.date_of_birth},{local_data['gender']},{employee.nationality},{local_data['country_of_origin']},{local_data['working_country']},{employee.personal_email},{employee.job_title},{employee.direct_manager},{local_data['hr_team']},{employee.start_date},{employee.end_date},{local_data['site']},{local_data['department']},{employee.product_code},{employee.brand_code},{employee.business_unit},{employee.business_verticle},{local_data['contract']},{employee.supplier},{employee.entity_to_be_billed},{local_data['employer']},{employee.company_email},{local_data['employment_status']}\n"

    
    return Response(content=csv, media_type='text/csv', headers={'Content-Disposition': f'attachment; filename={file_name}.csv'})