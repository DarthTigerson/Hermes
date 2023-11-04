from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
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
async def get_reporting(request: Request, report_type: Optional[int] = 0, start_date: Optional[datetime] = date.today() - timedelta(days=30), end_date: Optional[datetime] = date.today(), db: Session = Depends(get_db)):

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

        # Filter the data in Python
        report_data = [employee for employee in report_data if start_date_str <= datetime.strptime(employee.start_date, '%Y-%m-%d').strftime('%Y-%m-%d') <= end_date_str]
    elif report_type == 2:
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 1)\
            .all()

        # Filter the data in Python
        report_data = [employee for employee in report_data if start_date_str <= datetime.strptime(employee.end_date, '%Y-%m-%d').strftime('%Y-%m-%d') <= end_date_str]
    else:
        report_data = None
    
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
    
    return templates.TemplateResponse("reporting.html", {"request": request, "logged_in_user": user, "role_state": role_state, "nav": 'reporting', "header_value": header_value, "report_data": report_data, "countries": countries, "sites": sites, "departments": departments, "currencies": currencies, "employment_contracts": employment_contracts, "employment_types": employment_types, "employers": employers, "hr_teams": hr_teams, "salary_pay_frequency": salary_pay_frequency})

@router.get("/download_csv/{report_type}/{start_date}/{end_date}")
async def download_csv(request: Request, report_type: int, start_date: datetime, end_date: datetime, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    # Convert start_date and end_date to strings in the 'YYYY-MM-DD' format
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    if report_type == 1:
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 0)\
            .all()

        # Filter the data in Python
        report_data = [employee for employee in report_data if start_date_str <= datetime.strptime(employee.start_date, '%Y-%m-%d').strftime('%Y-%m-%d') <= end_date_str]
    elif report_type == 2:
        report_data = db.query(models.Employees)\
            .filter(models.Employees.employment_status_id == 1)\
            .all()

        # Filter the data in Python
        report_data = [employee for employee in report_data if start_date_str <= datetime.strptime(employee.end_date, '%Y-%m-%d').strftime('%Y-%m-%d') <= end_date_str]
    else:
        report_data = None

    