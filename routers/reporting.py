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
    
    return templates.TemplateResponse("reporting.html", {"request": request, "logged_in_user": user, "role_state": role_state, "nav": 'reporting', "header_value": header_value, "report_data": report_data})